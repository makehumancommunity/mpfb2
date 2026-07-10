"""Operator for creating a new human with a randomized phenotype."""

import os, random, bpy
from .....services import LogService
from .....services import AssetService
from .....services import HumanService
from .....services import MeshService
from .....services import ObjectService
from .....services import RandomizationService
from .....services import RigService
from .....services import SystemService
from .....entities.clothes.mhclo import Mhclo
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.createrandomhuman")

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


class MPFB_OT_Create_Random_Human_Operator(MpfbOperator):
    """Create a new human whose phenotype has been randomized according to the settings below"""
    bl_idname = "mpfb.create_random_human"
    bl_label = "Create random human"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()
        scene = context.scene

        spec = scene_to_spec(scene)
        creation = spec["creation"]

        rig_name = creation.get("rig", "NONE")
        # Abort before creating anything if a rigify rig is requested but rigify is unavailable,
        # mirroring the from-save-file operator.
        if str(rig_name).startswith("rigify.") and not SystemService.check_for_rigify():
            self.report({'ERROR'}, "A rigify rig was selected, but the Rigify addon is not enabled.")
            return {'FINISHED'}

        seed = RANDOMIZE_PROPERTIES.get_value("seed", entity_reference=scene)
        if not seed:
            seed = random.randint(1, 2 ** 31 - 1)
        rng = random.Random(seed)

        macro_details = RandomizationService.randomize_macro_info_dict(spec, rng)
        _LOG.dump("macro_details", macro_details)

        scale = _SCALE_BY_FACTOR.get(creation["scale_factor"], 0.1)

        basemesh = HumanService.create_human(
            mask_helpers=creation["mask_helpers"],
            detailed_helpers=creation["detailed_helpers"],
            extra_vertex_groups=creation["extra_vertex_groups"],
            feet_on_ground=True,
            scale=scale,
            macro_detail_dict=macro_details)

        # Otherwise all targets will be set to 100% when entering edit mode
        basemesh.use_shape_key_edit_mode = True

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object("body", deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, RandomizationService.describe_macro_info_dict(macro_details, seed))

        # The rig is added before the body parts so that add_mhclo_asset finds the Skeleton and
        # rigs each child mesh as it is attached. Adding a rig consumes no random draws.
        _add_rig(self.report, rig_name, basemesh)

        # The skin and body parts are picked from the shared rng after all phenotype draws, so
        # that with them disabled (no draw at all) a given seed still produces the same
        # phenotype. The body parts draw in a fixed type order after the skin.
        _apply_random_skin(self.report, spec, macro_details, basemesh, rng)
        _apply_random_bodyparts(self.report, spec, macro_details, basemesh, rng)

        # Rigify generation happens after the body parts, so their weights and subrigs exist
        # when the meta rig is turned into the full rig.
        if str(rig_name).startswith("rigify.") and creation.get("auto_generate_rigify", True):
            _generate_rigify(self.report, basemesh, creation.get("meta_rig_action", "hide"))

        # When "new random seed" is enabled, advance the seed field to a fresh value so that
        # the next invocation produces a different human without further user action.
        if RANDOMIZE_PROPERTIES.get_value("new_random_seed", entity_reference=scene):
            RANDOMIZE_PROPERTIES.set_value("seed", random.randint(1, 2 ** 31 - 1), entity_reference=scene)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Create_Random_Human_Operator)


def _apply_random_skin(report, spec, macro_details, basemesh, rng):
    """Pick and apply a random skin when skin randomization is enabled.

    When disabled this returns immediately (drawing nothing from rng). When enabled but
    nothing matches (or no skins are installed) the human keeps its default material and a
    WARNING is reported via the passed-in operator report callable.
    """
    skin_cfg = (spec.get("assets") or {}).get("skin") or {}
    if not skin_cfg.get("enabled", False):
        return

    # Discover the installed skins once and resolve pack membership from the pack metadata.
    # This is the expensive part, so it happens here rather than inside the pure pick.
    name_to_pack = {}
    for pack_name in AssetService.get_pack_names():
        for asset_name in AssetService.get_asset_names_in_pack(pack_name):
            name_to_pack[asset_name] = pack_name

    candidates = []
    for path in AssetService.list_mhmat_assets("skins"):
        name = os.path.splitext(os.path.basename(str(path)))[0]
        candidates.append({"name": name, "path": str(path), "pack": name_to_pack.get(name)})

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


def _apply_random_eyes(report, eyes_cfg, basemesh, rng):
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

    HumanService.add_mhclo_asset(path, basemesh, asset_type="eyes", material_type=material_type,
                                 alternative_materials=alternative_materials)


def _apply_random_bodyparts(report, spec, macro_details, basemesh, rng):
    """Pick and attach a body part per enabled type, in the fixed documented draw order.

    Eyes are a special case (a drop-down, no draw for the mesh). For each of the remaining
    enabled types one asset is picked from the installed assets and attached; an empty pool
    gives a WARNING and no asset. Eyes and hair may additionally get a random alternative
    material. A disabled type consumes no random draws.
    """
    assets = spec.get("assets") or {}
    material_type = assets.get("asset_material_type", "MAKESKIN")

    # Resolve pack membership once, shared across every type.
    name_to_pack = {}
    for pack_name in AssetService.get_pack_names():
        for asset_name in AssetService.get_asset_names_in_pack(pack_name):
            name_to_pack[asset_name] = pack_name

    for bodypart in RandomizationService.get_bodypart_types():
        if bodypart == "eyes":
            _apply_random_eyes(report, assets.get("eyes") or {}, basemesh, rng)
            continue

        section = assets.get(bodypart) or {}
        if not section.get("enabled", False):
            continue

        candidates = _bodypart_candidates(bodypart, name_to_pack)
        pick = RandomizationService.pick_random_bodypart(section, macro_details, candidates, rng)
        if pick is None:
            report({'WARNING'}, "No matching " + bodypart + " was found; none was added")
            continue

        alternative_materials = None
        if bodypart == "hair" and section.get("randomize_alt_materials", False):
            alternative_materials = _pick_alternative_material(report, pick["path"], bodypart, rng)

        HumanService.add_mhclo_asset(pick["path"], basemesh, asset_type=bodypart, material_type=material_type,
                                     alternative_materials=alternative_materials)
