"""Shared per-character builder for the randomize operators.

This module holds the per-character creation logic which both the single-character operator
and the batch operator use: given a randomization spec, a phenotype macro dict, a per-character
random.Random and a pre-built discovery context, it creates one human (mesh, details, rig,
skin, body parts, clothes and Rigify generation) and returns the basemesh.

The discovery context (installed asset candidate lists, pack membership and the parsed
target.json sections) is the expensive part, so it is built once via build_discovery_context()
and passed into build_character(). The batch operator builds it once for the whole batch rather
than once per character; the single-character operator builds it once per invocation.

The random draws are consumed in a fixed order -- phenotype (drawn by the caller before
build_character), then details, skin, body parts and clothes -- so that a disabled concern
consumes no draws and a given seed reproduces the same character regardless of which concerns
are enabled.
"""

import os, json, bpy
from ....services import LogService
from ....services import AssetService
from ....services import HumanService
from ....services import LocationService
from ....services import MeshService
from ....services import ModifierService
from ....services import ObjectService
from ....services import RandomizationService
from ....services import RigService
from ....services import SystemService
from ....services import TargetService
from ....entities.clothes.mhclo import Mhclo

_LOG = LogService.get_logger("ui.new_human.randomize.characterbuilder")

_SCALE_BY_FACTOR = {"METER": 0.1, "DECIMETER": 1.0, "CENTIMETER": 10.0}

# Skin types for which material instances are always forced off, mirroring the asset
# library's load-skin operator.
_NO_INSTANCE_SKIN_TYPES = ["LAYERED", "GAMEENGINE", "MAKESKIN"]

# The eyes are not randomized from a pool; the drop-down maps to these hardcoded asset
# fragments (parent-dir/basename), resolved among the installed eyes assets.
_EYES_ASSET_FRAGMENTS = {
    "HIGHPOLY": "high-poly/high-poly.mhclo",
    "LOWPOLY": "low-poly/low-poly.mhclo",
    }


def build_discovery_context() -> dict:
    """Discover the installed assets and parse target.json once, returning plain data.

    This is the expensive part of a randomized creation (scanning asset packs and every mhmat /
    mhclo asset, and reading target.json), so it is done once and shared. The batch operator
    calls this a single time for the whole batch. The returned context carries:

      - "name_to_pack": asset name -> owning pack name, resolved from the pack metadata.
      - "skin_candidates": the {name, path, pack} dicts for the installed skins.
      - "bodypart_candidates": bodypart type -> its {name, path, pack} candidate dicts (every
        type except "eyes", which is a drop-down rather than a pool).
      - "clothes_candidates": the {name, path, pack} dicts for the installed clothes.
      - "detail_sections": the target.json section name -> categories, minus "measure".
    """
    _LOG.enter()
    name_to_pack = {}
    for pack_name in AssetService.get_pack_names():
        for asset_name in AssetService.get_asset_names_in_pack(pack_name):
            name_to_pack[asset_name] = pack_name

    skin_candidates = []
    for path in AssetService.list_mhmat_assets("skins"):
        name = os.path.splitext(os.path.basename(str(path)))[0]
        skin_candidates.append({"name": name, "path": str(path), "pack": name_to_pack.get(name)})

    bodypart_candidates = {}
    for bodypart in RandomizationService.get_bodypart_types():
        if bodypart == "eyes":
            continue
        bodypart_candidates[bodypart] = _bodypart_candidates(bodypart, name_to_pack)

    clothes_candidates = _bodypart_candidates("clothes", name_to_pack)

    return {
        "name_to_pack": name_to_pack,
        "skin_candidates": skin_candidates,
        "bodypart_candidates": bodypart_candidates,
        "clothes_candidates": clothes_candidates,
        "detail_sections": _parse_detail_sections()
        }


def build_character(spec, macro_details, rng, report, discovery):
    """Create one randomized human and return its basemesh.

    The phenotype macro dict has already been drawn from rng by the caller (so the operator can
    report it before the slower creation begins). This function then creates the human and, in
    the fixed draw order, applies the random details, rig, skin, body parts, clothes and Rigify
    generation, all from the same rng. The report callable ({'WARNING'}/{'INFO'}, message) is
    threaded to the helpers so they can warn (empty asset pool, invalid rig, ...) per character.

    Args:
        spec (dict): The randomization spec.
        macro_details (dict): The phenotype macro dict already drawn from rng.
        rng (random.Random): The per-character rng, positioned after the phenotype draws.
        report: The operator report callable.
        discovery (dict): The context from build_discovery_context().

    Returns:
        The created basemesh object.
    """
    _LOG.enter()
    creation = spec["creation"]
    rig_name = creation.get("rig", "NONE")

    scale = _SCALE_BY_FACTOR.get(creation["scale_factor"], 0.1)

    # The subdiv level applied to the basemesh and every attached asset. When the option is off
    # the level is 0, which means add_mhclo_asset adds no modifier at all (and none is added to
    # the basemesh either), so the whole character stays at its base resolution.
    subdiv_levels = creation.get("subdiv_render_levels", 1) if creation.get("add_subdiv_modifier", True) else 0

    basemesh = HumanService.create_human(
        mask_helpers=creation["mask_helpers"],
        detailed_helpers=creation["detailed_helpers"],
        extra_vertex_groups=creation["extra_vertex_groups"],
        feet_on_ground=True,
        scale=scale,
        macro_detail_dict=macro_details)

    # Give the basemesh a subdiv modifier when requested (viewport level 0, render level as
    # configured), matching the modifier the attached assets already receive below.
    if subdiv_levels > 0:
        ModifierService.create_subsurf_modifier(basemesh, "Subdivision", levels=0, render_levels=subdiv_levels)

    # Detail targets are drawn after the phenotype draws and before any asset draws, and are
    # applied right after create_human (before the rig and the body parts) so that joint
    # fitting and mhclo fitting see the final shape. Disabled details consume no draws.
    _apply_random_details(spec, basemesh, rng, discovery)

    # Otherwise all targets will be set to 100% when entering edit mode
    basemesh.use_shape_key_edit_mode = True

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = basemesh
    basemesh.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    MeshService.select_all_vertices_in_vertex_group_for_active_object("body", deselect_other=True)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # The rig is added before the body parts so that add_mhclo_asset finds the Skeleton and
    # rigs each child mesh as it is attached. Adding a rig consumes no random draws.
    _add_rig(report, rig_name, basemesh)

    # The skin and body parts are picked from the shared rng after all phenotype draws, so
    # that with them disabled (no draw at all) a given seed still produces the same
    # phenotype. The body parts draw in a fixed type order after the skin.
    _apply_random_skin(report, spec, macro_details, basemesh, rng, discovery)
    _apply_random_bodyparts(report, spec, macro_details, basemesh, rng, discovery, subdiv_levels)

    # Clothes are attached after the body parts (so the clothes draws come last) but before
    # Rigify generation, so each garment is rigged as it is attached and its weights exist
    # when the meta rig is turned into the full rig.
    _apply_random_clothes(report, spec, macro_details, basemesh, rng, discovery, subdiv_levels)

    # Rigify generation happens after the body parts, so their weights and subrigs exist
    # when the meta rig is turned into the full rig.
    if str(rig_name).startswith("rigify.") and creation.get("auto_generate_rigify", True):
        _generate_rigify(report, basemesh, creation.get("meta_rig_action", "hide"))

    # Detail targets and attached assets change the mesh after create_human's initial
    # feet-on-ground, so the lowest body vertex is usually no longer at z=0. Re-ground the
    # whole character as a final step by shifting its root (the rig when present, otherwise the
    # basemesh). This adds no random draws.
    _move_feet_to_ground(basemesh)

    return basemesh


def _parse_detail_sections() -> dict:
    """Parse target.json once, returning the section name -> categories (minus "measure")."""
    targets_json = os.path.join(LocationService.get_mpfb_data("targets"), "target.json")
    with open(targets_json, "r") as json_file:
        target_data = json.load(json_file)
    return {name: section.get("categories", [])
            for name, section in target_data.items() if name != "measure"}


def _apply_random_skin(report, spec, macro_details, basemesh, rng, discovery):
    """Pick and apply a random skin when skin randomization is enabled.

    When disabled this returns immediately (drawing nothing from rng). When enabled but
    nothing matches (or no skins are installed) the human keeps its default material and a
    WARNING is reported via the passed-in operator report callable.
    """
    skin_cfg = (spec.get("assets") or {}).get("skin") or {}
    if not skin_cfg.get("enabled", False):
        return

    candidates = discovery["skin_candidates"]

    pick = RandomizationService.pick_random_skin(spec, macro_details, candidates, rng)
    if pick is None:
        report({'WARNING'}, "No matching skin was found; the human was created with the default material")
        return

    skin_type = skin_cfg.get("skin_type", "MAKESKIN")
    material_instances = skin_cfg.get("material_instances", True)
    if skin_type in _NO_INSTANCE_SKIN_TYPES:
        material_instances = False

    # There is no proxy mesh at creation time, so only the basemesh gets the material.
    HumanService.set_character_skin(pick["path"], basemesh, bodyproxy=None, skin_type=skin_type, material_instances=material_instances)

    for slot in basemesh.material_slots:
        if str(slot.material.name).lower().endswith("body"):
            basemesh.active_material_index = slot.slot_index


def _apply_random_details(spec, basemesh, rng, discovery):
    """Draw and apply random detail targets when detail randomization is enabled.

    When disabled this returns immediately (drawing nothing from rng). The target.json sections
    (minus the empty "measure" section) come pre-parsed from the discovery context and are passed
    to the pure pick as plain data; the returned stack is loaded in a single bulk_load_targets
    call. A target name that cannot be resolved to a file is skipped with a warning by
    bulk_load_targets, never a crash.
    """
    details = (spec.get("details") or {})
    if not details.get("enabled", False):
        return

    sections = discovery["detail_sections"]
    stack = RandomizationService.pick_random_details(details, sections, rng)
    if stack:
        TargetService.bulk_load_targets(basemesh, stack)


def _add_rig(report, rig_name, basemesh):
    """Add the chosen rig to the created human, before any body parts are attached.

    Mirrors HumanService._check_add_rig. With "NONE" (or an empty value) nothing is added, and
    add_mhclo_asset will then parent each body part to the basemesh rather than rigging it.
    """
    if not rig_name or str(rig_name).strip() == "" or rig_name == "NONE":
        return
    try:
        if str(rig_name).startswith("custom."):
            HumanService.add_custom_rig(basemesh, rig_name, import_weights=True)
        else:
            HumanService.add_builtin_rig(basemesh, rig_name, import_weights=True)
    except (IOError, ValueError, NotImplementedError) as problem:
        report({'WARNING'}, "Could not add the selected rig: " + str(problem))


def _generate_rigify(report, basemesh, meta_rig_action):
    """Generate the full rigify rig from the meta rig added to the created human.

    Mirrors the from-save-file operator: the meta rig is only turned into the full rig when it
    is actually a rigify meta rig and the Rigify addon is available.
    """
    rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
    if not rig:
        return
    rig_type = RigService.identify_rig(rig)
    if not rig_type or not str(rig_type).startswith("rigify."):
        return
    if not SystemService.check_for_rigify():
        report({'WARNING'}, "The created character has a rigify meta rig, but the Rigify addon is not enabled.")
        return
    bpy.context.view_layer.objects.active = rig
    basemesh.select_set(False)
    rig.select_set(True)
    rigify_object = RigService.generate_rigify_rig(rig, meta_rig_action=meta_rig_action)
    if rigify_object is None:
        report({'WARNING'}, "Rigify considers the meta rig invalid; the full rig was not generated.")


def _bodypart_candidates(bodypart, name_to_pack):
    """Build the candidate dicts for one bodypart type from the installed mhclo assets."""
    candidates = []
    for path in AssetService.list_mhclo_assets(bodypart):
        name = os.path.splitext(os.path.basename(str(path)))[0]
        candidates.append({"name": name, "path": str(path), "pack": name_to_pack.get(name)})
    return candidates


def _pick_alternative_material(report, asset_path, asset_subdir, rng):
    """Pick a random alternative material for an already-picked eyes/hair asset.

    Returns an alternative_materials dict (keyed by the asset's uuid) suitable for
    add_mhclo_asset, or None to keep the default material. An asset without a uuid cannot
    receive an alternative material through this path, so the default is kept silently.
    """
    mhclo = Mhclo()
    mhclo.load(asset_path, only_metadata=True)
    if not mhclo.uuid:
        _LOG.debug("Asset has no uuid; keeping the default material", asset_path)
        return None

    asset_fragment = AssetService.path_to_fragment(asset_path, asset_subdir=asset_subdir)
    default_fragment = None
    if mhclo.material:
        default_fragment = AssetService.path_to_fragment(mhclo.material, asset_subdir=asset_subdir)

    # The discovery can return duplicates (the eyes scan looks in two places); the service
    # de-duplicates together with the default before drawing.
    alternatives = [AssetService.path_to_fragment(mat, asset_subdir=asset_subdir)
                    for mat in AssetService.alternative_materials_for_asset(asset_fragment, asset_subdir)]

    pick = RandomizationService.pick_random_alternative_material(default_fragment, alternatives, rng)
    if not pick or pick == default_fragment:
        return None
    return {mhclo.uuid: pick}


def _apply_random_eyes(report, eyes_cfg, basemesh, rng, subdiv_levels):
    """Attach the eyes chosen in the eyes drop-down (there is no random draw for the mesh)."""
    mode = eyes_cfg.get("mode", "DONOTADD")
    fragment = _EYES_ASSET_FRAGMENTS.get(mode)
    if fragment is None:
        return

    path = AssetService.find_asset_absolute_path(fragment, "eyes")
    if not path:
        report({'WARNING'}, "The selected eyes are not installed; no eyes were added")
        return

    material_type = eyes_cfg.get("material_type", "MAKESKIN")
    alternative_materials = None
    if eyes_cfg.get("randomize_alt_materials", True) and material_type != "PROCEDURAL_EYES":
        alternative_materials = _pick_alternative_material(report, path, "eyes", rng)

    HumanService.add_mhclo_asset(path, basemesh, asset_type="eyes", subdiv_levels=subdiv_levels,
                                 material_type=material_type, alternative_materials=alternative_materials)


def _apply_random_bodyparts(report, spec, macro_details, basemesh, rng, discovery, subdiv_levels):
    """Pick and attach a body part per enabled type, in the fixed documented draw order.

    Eyes are a special case (a drop-down, no draw for the mesh). For each of the remaining
    enabled types one asset is picked from the installed assets and attached; an empty pool
    gives a WARNING and no asset. Eyes and hair may additionally get a random alternative
    material. A disabled type consumes no random draws.
    """
    assets = spec.get("assets") or {}
    material_type = assets.get("asset_material_type", "MAKESKIN")

    for bodypart in RandomizationService.get_bodypart_types():
        if bodypart == "eyes":
            _apply_random_eyes(report, assets.get("eyes") or {}, basemesh, rng, subdiv_levels)
            continue

        section = assets.get(bodypart) or {}
        if not section.get("enabled", False):
            continue

        candidates = discovery["bodypart_candidates"].get(bodypart, [])
        pick = RandomizationService.pick_random_bodypart(section, macro_details, candidates, rng)
        if pick is None:
            report({'WARNING'}, "No matching " + bodypart + " was found; none was added")
            continue

        alternative_materials = None
        if bodypart == "hair" and section.get("randomize_alt_materials", False):
            alternative_materials = _pick_alternative_material(report, pick["path"], bodypart, rng)

        HumanService.add_mhclo_asset(pick["path"], basemesh, asset_type=bodypart, subdiv_levels=subdiv_levels,
                                     material_type=material_type, alternative_materials=alternative_materials)


def _apply_random_clothes(report, spec, macro_details, basemesh, rng, discovery, subdiv_levels):
    """Pick and attach one garment per enabled clothes slot, in the fixed draw order.

    The pure pick_random_clothes drives all eight slots (chance draws, full-body exclusivity,
    cross-slot dedup); this wrapper only supplies the discovered clothes and attaches the picks.
    A firing slot with an empty pool gives a WARNING and no garment; when the full body slot
    fires with an empty pool the character falls back to separates (upper and lower body run per
    their own settings). When no slot is enabled nothing is drawn.
    """
    assets = spec.get("assets") or {}
    clothes_section = assets.get("clothes") or {}
    if not any((clothes_section.get(slot) or {}).get("enabled", False)
               for slot in RandomizationService.get_clothes_slots()):
        return

    material_type = assets.get("asset_material_type", "MAKESKIN")
    candidates = discovery["clothes_candidates"]

    for result in RandomizationService.pick_random_clothes(clothes_section, macro_details, candidates, rng):
        warning = result.get("warning")
        if warning == "empty_pool":
            report({'WARNING'}, "No matching clothes were found for the " + result["slot"] + " slot; none was added")
        elif warning == "full_body_empty_fallback":
            report({'WARNING'}, "No matching full body clothes were found; dressing with separates instead")

        pick = result.get("pick")
        if pick is None:
            continue

        HumanService.add_mhclo_asset(pick["path"], basemesh, asset_type="Clothes", subdiv_levels=subdiv_levels,
                                     material_type=material_type)


def _move_feet_to_ground(basemesh):
    """Shift the character's root so the lowest basemesh body vertex sits at global z=0.

    create_human grounds the character before the detail targets and assets change its shape,
    so this is done again as a final step. The root is the rig when one was added (the basemesh
    is parented to it), otherwise the basemesh itself. get_lowest_point returns the lowest body
    vertex in local coordinates with the shape keys taken into account; it is converted to a
    world z via the basemesh's world matrix (only translation and scale matter here, since the
    character has not been rotated at this point).
    """
    root = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton") or basemesh
    local_lowest = ObjectService.get_lowest_point(basemesh)
    matrix_world = basemesh.matrix_world
    lowest_world_z = matrix_world.translation.z + matrix_world.to_scale().z * local_lowest
    root.location.z -= lowest_world_z
