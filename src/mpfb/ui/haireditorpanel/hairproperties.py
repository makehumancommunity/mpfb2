from ...services.logservice import LogService
from ...services.objectservice import ObjectService
from ...services.materialservice import MaterialService
from ...services.nodeservice import NodeService
from ...services.dynamicconfigset import DynamicConfigSet
from ...services.haireditorservices import HairEditorService
from ...services.modifierservice import ModifierService
from ...services.hairbakeservice import HairBakeService
from ...services.haircardservice import (CARDS_MODE_ITEMS, CARDS_MODE_TILES, CARDS_MODE_CLUSTER_RIBBON,
                                         CLUSTER_RIBBON_PROFILE_STEPS, SELECTION_METHOD_ITEMS,
                                         SELECTION_METHOD_RANDOM, BAKE_TARGET_ITEMS, BAKE_TARGET_CARDS,
                                         LIGHT_MODE_ITEMS, LIGHT_MODE_FIXED, LIGHT_MODE_BBOX)

import bpy, os, re, json

_LOG = LogService.get_logger("ui.hairproperties")
#_LOG.set_level(LogService.DEBUG)

DYNAMIC_PREFIX="DHAI_"
DYNAMIC_PREFIX_FUR="DFAI_"

DYNAMIC_HAIR_PROPS_DEFINITIONS = {
        "length": ("Set Hair Curve Profile", "Socket_1", (0.0, 10.0)),
        "density": ("Set Hair Curve Profile", "Socket_0", (0.0, 1.0)),
        "thickness": ("Set Hair Curve Profile", "Input_3", (0.0, 0.003)),
        "frizz": ("Frizz Hair Curves", "Input_3", (0.0,1.0)),
        "roll": ("Roll Hair Curves", "Input_10", (0.0,1.0)),
        "roll_radius": ("Roll Hair Curves", "Input_3", (0.001, 0.005)),
        "roll_length": ("Roll Hair Curves", "Input_2", (0.001, 0.1)),
        "clump": ("Clump Hair Curves", "Input_7", (0.0,1.0)),
        "clump_distance": ("Clump Hair Curves", "Input_9", (0.003, 0.05)),
        "clump_shape": ("Clump Hair Curves", "Input_6", (-1.0,1.0)),
        "clump_tip_spread": ("Clump Hair Curves", "Input_10", (0.0, 0.02)),
        "noise": ("Hair Curves Noise", "Input_3", (0.0, 1.0)),
        "noise_distance": ("Hair Curves Noise", "Input_14", (0.0, 0.01)),
        "noise_scale": ("Hair Curves Noise", "Input_11", (0.0, 20)),
        "noise_shape": ("Hair Curves Noise", "Input_2", (0.0, 1.0)),
        "curl": ("Curl Hair Curves", "Input_2", (0.0, 1.0)),
        "curl_guide_distance": ("Curl Hair Curves", "Input_4", (0.0, 0.1)),
        "curl_radius": ("Curl Hair Curves", "Input_7", (0.0, 0.1)),
        "curl_frequency": ("Curl Hair Curves", "Input_11", (0.0, 20.0))
        }

DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS = {
        "color1": ("Color 1", (0.117, 0.093, 0.047, 1.0)),
        "color2": ("Color 2", (0.031, 0.016, 0.004, 1.0)),
        "color_noise_scale": ("Noise Scale", (0.0, 500.0)),
        "darken_root": ("Darken root", (0.0, 1.0)),
        "root_color_length": ("Root color length", (0.0, 1.0))
        }

DYNAMIC_FUR_PROPS_DEFINITIONS = {
        "length": ("Set Hair Curve Profile", "Socket_1", (0.0, 20.0)),
        "density": ("Set Hair Curve Profile", "Socket_0", (0.0, 1.0)),
        "thickness": ("Set Hair Curve Profile", "Input_3", (0.0, 0.003)),
        "frizz": ("Frizz Hair Curves", "Input_3", (0.0,1.0)),
        "roll": ("Roll Hair Curves", "Input_10", (0.0,1.0)),
        "roll_radius": ("Roll Hair Curves", "Input_3", (0.001, 0.1)),
        "roll_length": ("Roll Hair Curves", "Input_2", (0.001, 0.1)),
        "clump": ("Clump Hair Curves", "Input_7", (0.0,1.0)),
        "clump_distance": ("Clump Hair Curves", "Input_9", (0.003, 0.05)),
        "clump_shape": ("Clump Hair Curves", "Input_6", (-1.0,1.0)),
        "clump_tip_spread": ("Clump Hair Curves", "Input_10", (0.0, 0.02)),
        "noise": ("Hair Curves Noise", "Input_3", (0.0, 1.0)),
        "noise_distance": ("Hair Curves Noise", "Input_14", (0.0, 0.1)),
        "noise_scale": ("Hair Curves Noise", "Input_11", (0.0, 20)),
        "noise_shape": ("Hair Curves Noise", "Input_2", (0.0, 1.0)),
        "curl": ("Curl Hair Curves", "Input_2", (0.0, 1.0)),
        "curl_guide_distance": ("Curl Hair Curves", "Input_4", (0.0, 0.1)),
        "curl_radius": ("Curl Hair Curves", "Input_7", (0.0, 0.1)),
        "curl_frequency": ("Curl Hair Curves", "Input_11", (0.0, 20.0)),
        "holes": ("Set Hair Curve Profile", "Socket_2", (0.0, 1.0)),
        "holes_scale": ("Set Hair Curve Profile", "Socket_3", (0.0, 200.0))
        }

DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS = {
        "color1": ("Color 1", (0.117, 0.093, 0.047, 1.0)),
        "color2": ("Color 2", (0.031, 0.016, 0.004, 1.0)),
        "color_noise_scale": ("Noise Scale", (0.0, 500.0)),
        "darken_root": ("Darken root", (0.0, 1.0)),
        "root_color_length": ("Root color length", (0.0, 1.0)),
        "use_texture": ("Use Texture Instead of Colors", False),
        "texture_path": ("Texture File Path", "")
        }

# The card object is a sibling of the hair object, named after it, with a geometry nodes modifier that makes the cards
CARDS_OBJECT_SUFFIX = "_cards"
CARDS_MODIFIER_NAME = "HairCards"

# Custom property on the loaded hair/fur object with its name in the asset pack blend file. The object itself
# can get a deduplicated name ("name.001") when the asset is applied again, and everything else is keyed off that name.
PACK_NAME_PROPERTY = "mpfb_pack_asset"

def get_pack_asset_name(hair_obj, fallback=None):
    """Look up the name the given hair/fur object had in its asset pack blend file, or ``fallback`` if it has none."""
    if hair_obj is None:
        return fallback
    return hair_obj.get(PACK_NAME_PROPERTY, fallback)

# Sockets of the geometry node group built by the generate cards operator, matched by name since the group is created at run time.
# A property whose socket does not exist in the active mode reads back its default and ignores writes.
# Mapping is property name -> (socket name, (min, max) or None, default)
DYNAMIC_CARDS_PROPS_DEFINITIONS = {
        # Assets can have tens of thousands of strands, so only a small fraction becomes cards
        "cards_density": ("Density", (0.0, 1.0), 0.01),
        "cards_seed": ("Seed", (0, 9999), 0),
        "cards_vertex_group": ("Weight vertex group", None, ""),
        "cards_cluster_strength": ("Cluster strength", (0.0, 1.0), 0.0),
        "cards_offset": ("Offset", (0.0, 0.1), 0.0),
        "cards_jitter": ("Jitter", (0.0, 1.0), 0.15),
        "cards_poisson_radius": ("Poisson radius", (0.001, 0.2), 0.02),
        # Tiles mode only
        "cards_segments": ("Segments", (2, 64), 8),
        "cards_scale": ("Scale", (0.01, 5.0), 1.0),
        "cards_width": ("Card width", (0.001, 0.5), 0.03),
        "cards_length": ("Card length", (0.001, 0.5), 0.03),
        "cards_width_random": ("Width random", (0.0, 1.0), 0.0),
        "cards_length_random": ("Length random", (0.0, 1.0), 0.0),
        "cards_tilt_random": ("Tilt random", (0.0, 1.0), 0.0),
        # Ribbon / cluster ribbon modes only
        "cards_profile_steps": ("Profile steps", (2, 64), 16),
        "cards_extend_tip": ("Extend tip", (0.0, 0.1), 0.0),
        "cards_taper": ("Taper", (0.0, 1.0), 0.3),
        "cards_twist": ("Twist", (-4.0, 4.0), 0.0),
        # Cluster ribbon mode only
        "cards_cluster_width_match": ("Width from cluster", (0.0, 1.0), 0.6),
        # Body shell target only
        "cards_body_height": ("Height", (0.0, 0.2), 0.006),
        "cards_body_normal_smooth": ("Normal smoothing", (0, 20), 3),
        # Shell mode only
        "cards_shell_volume_density": ("Volume density", (0.0, 1.0), 0.05),
        "cards_shell_voxel_size": ("Voxel size", (0.001, 0.05), 0.008),
        "cards_shell_radius": ("Strand radius", (0.001, 0.05), 0.015),
        "cards_shell_samples": ("Strand samples", (2, 128), 32),
        "cards_shell_hug": ("Hug strands", (0.0, 1.0), 0.7),
        "cards_shell_adaptivity": ("Adaptivity", (0.0, 1.0), 0.3),
        "cards_shell_smooth": ("Smooth iterations", (0, 5), 2),
        }

# Per mode overrides of the defaults above, has to match the defaults in the node group builders
CARDS_MODE_DEFAULT_OVERRIDES = {
        CARDS_MODE_CLUSTER_RIBBON: {"cards_profile_steps": CLUSTER_RIBBON_PROFILE_STEPS},
        }

# Settings for the bake operator, remembered per asset and not bound to anything live in the scene.
# Mapping is property name -> (property type, (min, max) or None, default or None, description)
def _enum_items_with_index(items):
    return [[key, label, description, index] for index, (key, label, description) in enumerate(items)]

DYNAMIC_CARDS_BAKE_PROPS_DEFINITIONS = {
        "cards_glossy": ("boolean", None, True, "Bake the glossy pass, which looks better in high resolutions, instead of faster and more stable diffuse pass"),
        "cards_bake_normal": ("boolean", None, False, "Also bake a normal map alongside the color texture. !! This is an OBJECT space map, not the tangent space map most engines expect by default !!"),
        "cards_bake_ao": ("boolean", None, False, "Also bake an ambient occlusion map alongside the color texture"),
        "cards_bake_root_tip": ("boolean", None, False, "Also bake a root/tip mask (black at the root, white at the tip) alongside the color texture"),
        "cards_bake_flow": ("boolean", None, False, "Also bake a flow map holding the hair direction in object space, which an anisotropic hair shader needs to put its highlight in the right place"),
        "cards_bake_side_on": ("boolean", None, False, "Also bake a map of how side-on each bit of hair was captured - white where the strand crossed the capture ray, black where the ray looked straight down its length. Baking it adds a slider to Appearance for fading them out"),
        "cards_bake_depth": ("boolean", None, False, "Also bake a depth map holding how far behind the card each bit of hair was, scaled by the ray range below"),
        "cards_samples": ("int", (1, 4096), 8, "Render samples used when baking"),
        "cards_custom_mesh": ("string", None, "", "Name of the mesh in the scene to bake onto. It needs a UV layout of its own"),
        "cards_resolution": ("int", (64, 8192), 1024, "Resolution of the baked texture, ideally a power of two"),
        "cards_atlas_enabled": ("boolean", None, False, "Share one baked texture between several cards. When off, every card is baked at its own UVs"),
        "cards_atlas_fraction": ("float", (0.01, 1.0), 1.0, "Fraction of the cards which are actually baked into the atlas; the rest reuse one of the baked variants. Lower values give each baked card more texture resolution to work with, at the cost of visible repetition"),
        "cards_analytic_uvs": ("boolean", None, True, "Use the UV layout the generator already produced - one 0..1 rectangle per card, hair running along V - packed into columns of the atlas. Turn this off to unwrap the cards from scratch with Smart UV Project instead. The shell modes have no generated layout and are always unwrapped"),
        "cards_double_sided": ("boolean", None, False, "Capture the hair on both sides of a card or body shell instead of only one. The capture ray only travels one way, so hair on the other side is missed. Costs one more bake pass, and on cards it can double-count hair that neighbouring cards already represent"),
        "cards_limit_ray_range": ("boolean", None, False, "Ignore hair further behind the card than the range below, so that a card cannot pick up hair from the far side of the head"),
        "cards_ray_range": ("float", (0.005, 2.0), 0.1, "Maximum distance behind a card that hair is captured from, and the distance the depth map is scaled by"),
        "cards_body_edge_fade": ("boolean", None, False, "Fade the shell's alpha to nothing at the edge of the patch, so that the asset does not end with a hard cut"),
        "cards_body_edge_fade_width": ("int", (1, 8), 2, "How many rings of faces the fade is spread over."),
        "cards_body_shadows": ("boolean", None, False, "Let the body cast shadows onto the hair while it is baked. The bake lights are the only light in the scene and the background is black, so a shadow the body throws lands as a hard dark band on the cards. Off by default; turn it on only if the asset is meant to read as shaded by the body it sits on"),
        "cards_light_mode": ("enum", _enum_items_with_index(LIGHT_MODE_ITEMS), LIGHT_MODE_FIXED, "How the hair is lit while it is baked"),
        "cards_light_strength": ("float", (0.0, 10.0), 1.0, "How strongly the hair is lit, as a multiple of whatever the chosen lighting mode treats as full strengt (The modes need different wattages)"),
        "cards_texture_dst": ("dir_path", None, None, "Directory to write the baked texture to")
        }

# Regenerate required settings: changing these rebuilds the node group instead of updating a live modifier input.
# They are plain persisted values, not geometry node sockets, and are read by the generate cards operator.
# Mapping is property name -> (property type, items/(min,max)/None, default, description)
DYNAMIC_CARDS_CONFIG_PROPS_DEFINITIONS = {
        "cards_bake_target": ("enum", _enum_items_with_index(BAKE_TARGET_ITEMS), BAKE_TARGET_CARDS,
                              "What the hair is baked onto: generated cards, the body's own texture, or a shell duplicated from the body"),
        "cards_mode": ("enum", _enum_items_with_index(CARDS_MODE_ITEMS), CARDS_MODE_TILES, "How the hair cards are generated"),
        "cards_body_face_dilation": ("int", (0, 8), 1,
                                     "How many rings of neighbouring body faces to add around the ones the asset actually grows from (body shell target only)"),
        "cards_selection_method": ("enum", _enum_items_with_index(SELECTION_METHOD_ITEMS), SELECTION_METHOD_RANDOM,
                                   "How strands are chosen to become cards (random tiles / ribbon modes only)"),
        "cards_cluster_count": ("int", (4, 500), 40, "Number of cluster cards to generate (cluster modes only)"),
        "cards_cluster_min_strands": ("int", (1, 50), 3, "Minimum strands required to form a cluster card (cluster modes only)"),
        "cards_cluster_seed": ("int", (0, 9999), 0, "Random seed for the clustering (cluster modes only)"),
        "cards_cluster_samples": ("int", (2, 128), 24, "How many points each bundle's averaged curve is built from (cluster ribbon mode only)"),
        }

def create_cards_config_properties(config_set, basemesh, asset_name):
    """Create the persistent per-asset mode/selection-method settings. Idempotent, so existing values are kept."""
    for name, (proptype, extra, default, description) in DYNAMIC_CARDS_CONFIG_PROPS_DEFINITIONS.items():
        propname = f"{asset_name}_{name}"
        propdef = {
            "name": propname,
            "type": proptype,
            "description": description,
            "label": name.replace("cards_", "").replace("_", " ").capitalize(),
            "default": default
            }
        if proptype == "enum":
            propdef["items"] = extra
        elif extra is not None:
            propdef["min"] = extra[0]
            propdef["max"] = extra[1]
        current = config_set.get_value(propname, default, entity_reference=basemesh)
        if proptype == "enum" and current not in {item[0] for item in extra}:
            # A file saved by an older version can hold a mode which no longer exists, writing it back would raise exception
            _LOG.warn("Stored value is no longer a valid option, resetting", (propname, current, default))
            current = default
        config_set.set_value_dynamic(propname, current, propdef, entity_reference=basemesh)

def get_atlas_fraction(config_set, basemesh, asset_name):
    """The fraction of cards to actually bake, or 1.0 when sharing is switched off."""
    if not config_set.get_value(f"{asset_name}_cards_atlas_enabled", False, entity_reference=basemesh):
        return 1.0
    return config_set.get_value(f"{asset_name}_cards_atlas_fraction", 1.0, entity_reference=basemesh)

def get_bake_target(config_set, basemesh, asset_name):
    target = config_set.get_value(f"{asset_name}_cards_bake_target", BAKE_TARGET_CARDS, entity_reference=basemesh)
    if target not in {item[0] for item in BAKE_TARGET_ITEMS}:
        return BAKE_TARGET_CARDS
    return target

def resolve_body_surface(basemesh):
    """The mesh a body bake should land on - the body proxy if there is one, since the basemesh is hidden behind it."""
    for child in ObjectService.get_list_of_children(basemesh):
        if ObjectService.object_is_body_proxy(child):
            return child
    return basemesh

def resolve_custom_surface(config_set, basemesh, asset_name):
    """The mesh a custom-target bake should land on, or None if it is missing (the name is stored as text) or not a mesh."""
    name = config_set.get_value(f"{asset_name}_cards_custom_mesh", "", entity_reference=basemesh)
    if not name:
        return None
    surface = bpy.data.objects.get(name)
    if surface is None or surface.type != 'MESH':
        return None
    return surface


# Written on a custom bake target so that unbaking can give it its materials back.
# A plain custom property, since it belongs to that mesh and has to survive a reload.
CUSTOM_MESH_MATERIALS_PROPERTY = "mpfb_materials_before_bake"


def remember_custom_mesh_materials(surface):
    """Remember the mesh material slots before the baked material replaces them."""
    surface[CUSTOM_MESH_MATERIALS_PROPERTY] = [slot.material.name if slot.material else ""
                                               for slot in surface.material_slots]


def restore_custom_mesh_materials(surface):
    """Put back the materials the mesh had before the bake. True if anything was remembered.

    A material that was deleted in the meantime comes back as an empty slot.
    """
    remembered = surface.get(CUSTOM_MESH_MATERIALS_PROPERTY)
    if remembered is None:
        return False
    surface.data.materials.clear()
    for name in list(remembered):
        surface.data.materials.append(bpy.data.materials.get(name) if name else None)
    del surface[CUSTOM_MESH_MATERIALS_PROPERTY]
    return True


def body_surfaces_to_hide_behind(basemesh):
    """Every body mesh (basemesh and proxy) that has to be a holdout while baking, so it does not end up in the texture."""
    surfaces = [basemesh]
    for child in ObjectService.get_list_of_children(basemesh):
        if ObjectService.object_is_body_proxy(child):
            surfaces.append(child)
    return surfaces

def body_has_material(surface_obj):
    return surface_obj is not None and any(slot.material is not None for slot in surface_obj.material_slots)

def get_cards_mode(config_set, basemesh, asset_name):
    mode = config_set.get_value(f"{asset_name}_cards_mode", CARDS_MODE_TILES, entity_reference=basemesh)
    if mode not in {item[0] for item in CARDS_MODE_ITEMS}:
        # A file from an older version can name a mode which no longer exists
        return CARDS_MODE_TILES
    return mode

def get_cards_selection_method(config_set, basemesh, asset_name):
    return config_set.get_value(f"{asset_name}_cards_selection_method", SELECTION_METHOD_RANDOM, entity_reference=basemesh)

def find_cards_socket_identifier(node_group, socket_name):
    """Find the identifier of a named input socket in the generated hair cards node group."""
    if node_group is None:
        return None
    for item in node_group.interface.items_tree:
        if getattr(item, "item_type", None) != "SOCKET":
            continue
        if item.in_out == "INPUT" and item.name == socket_name:
            return item.identifier
    return None


# Card placement/shape values live in the sockets of the generated node group, so they are lost on regenerate, mode switch and bake.
# They are also remembered in a custom property on the basemesh, so that they come back after unbake or switching modes.
CARDS_SETTINGS_PROPERTY_PREFIX = "mpfb_cards_settings_"

def cards_settings_property_name(asset_name):
    return f"{CARDS_SETTINGS_PROPERTY_PREFIX}{asset_name}"

def read_cards_settings(basemesh, asset_name):
    """The remembered placement/shape values for an asset, or an empty dict if there are none."""
    raw = basemesh.get(cards_settings_property_name(asset_name)) if basemesh else None
    if not raw:
        return {}
    try:
        stored = json.loads(raw)
    except Exception as e:
        _LOG.warn("Could not parse the remembered card settings", (asset_name, e))
        return {}
    return stored if isinstance(stored, dict) else {}

def remember_cards_settings(basemesh, asset_name, values):
    """Merge freshly read values into what is already remembered, and return the merged result.

    Merged, since a snapshot only has the sockets of the current mode.
    """
    if basemesh is None:
        return dict(values)
    merged = read_cards_settings(basemesh, asset_name)
    merged.update(values)
    basemesh[cards_settings_property_name(asset_name)] = json.dumps(merged)
    return merged

def forget_cards_settings(basemesh, asset_name):
    name = cards_settings_property_name(asset_name)
    if basemesh is not None and name in basemesh:
        del basemesh[name]

def snapshot_cards_properties(config_set, basemesh, asset_name):
    """Read back the card placement/shape values which the current generator holds.

    Properties without a socket in the active mode are left out, so they do not overwrite remembered values with defaults.
    """
    card_obj = get_cards_object(asset_name)
    modifier = card_obj.modifiers.get(CARDS_MODIFIER_NAME) if card_obj is not None else None
    node_group = modifier.node_group if modifier is not None else None
    if node_group is None:
        return {}

    values = {}
    for name, (socket_name, _value_range, default) in DYNAMIC_CARDS_PROPS_DEFINITIONS.items():
        if find_cards_socket_identifier(node_group, socket_name) is None:
            continue
        value = config_set.get_value(f"{asset_name}_{name}", default, entity_reference=basemesh)
        # Plain python types for json
        if isinstance(default, str):
            values[name] = str(value)
        elif isinstance(default, bool):
            values[name] = bool(value)
        elif isinstance(default, int):
            values[name] = int(value)
        else:
            values[name] = float(value)
    return values

def create_cards_properties(config_set, basemesh, asset_name, values=None, mode=None):
    """Create the persistent per-asset properties which drive the hair cards node group.

    ``values`` optionally overrides the initial values (see snapshot_cards_properties).
    ``mode`` selects the default overrides in CARDS_MODE_DEFAULT_OVERRIDES, ``values`` still wins over them.
    """
    overrides = CARDS_MODE_DEFAULT_OVERRIDES.get(mode, {})
    for name, (socket_name, value_range, default) in DYNAMIC_CARDS_PROPS_DEFINITIONS.items():
        default = overrides.get(name, default)
        propname = f"{asset_name}_{name}"
        initial_value = default if values is None else values.get(name, default)
        if isinstance(default, str):
            proptype = "string"
        elif isinstance(default, int):
            proptype = "int"
        else:
            proptype = "float"
        propdef = {
            "name": propname,
            "type": proptype,
            "description": socket_name,
            "label": socket_name,
            "default": default
            }
        if value_range is not None:
            propdef["min"] = value_range[0]
            propdef["max"] = value_range[1]
        config_set.set_value_dynamic(propname, initial_value, propdef, entity_reference=basemesh)

def _migrate_light_from_bbox(config_set, basemesh, asset_name):
    """Convert the legacy "Lights from bounding box" checkbox of older files to the light mode. The legacy key is removed afterwards."""
    legacy = f"{asset_name}_cards_light_from_bbox"
    if not config_set.has_key(legacy, entity_reference=basemesh):
        return
    was_from_bbox = bool(config_set.get_value(legacy, False, entity_reference=basemesh))
    _LOG.debug("Migrating the legacy bounding box light setting", (asset_name, was_from_bbox))
    if was_from_bbox:
        propname = f"{asset_name}_cards_light_mode"
        propdef = {
            "name": propname,
            "type": "enum",
            "items": _enum_items_with_index(LIGHT_MODE_ITEMS),
            "description": "How the hair is lit while it is baked",
            "label": "Light mode",
            "default": LIGHT_MODE_FIXED,
            }
        config_set.set_value_dynamic(propname, LIGHT_MODE_BBOX, propdef, entity_reference=basemesh)
    config_set.remove_dynamic_key(legacy, basemesh)


def _migrate_light_intensity(config_set, basemesh, asset_name):
    """Convert the legacy light wattage of older files (default 1000) to the strength multiplier. The legacy key is removed afterwards."""
    legacy = f"{asset_name}_cards_light_intensity"
    if not config_set.has_key(legacy, entity_reference=basemesh):
        return
    watts = float(config_set.get_value(legacy, 1000.0, entity_reference=basemesh))
    strength = max(0.0, min(10.0, watts / 1000.0))
    _LOG.debug("Migrating the legacy light intensity", (asset_name, watts, strength))
    propname = f"{asset_name}_cards_light_strength"
    propdef = {
        "name": propname,
        "type": "float",
        "min": 0.0,
        "max": 10.0,
        "description": "How strongly the hair is lit, as a multiple of the mode's full strength",
        "label": "Light strength",
        "default": 1.0,
        }
    config_set.set_value_dynamic(propname, strength, propdef, entity_reference=basemesh)
    config_set.remove_dynamic_key(legacy, basemesh)


def get_light_strength(config_set, basemesh, asset_name):
    """How strongly to light the bake, as a multiple of the mode's own full strength."""
    return float(config_set.get_value(f"{asset_name}_cards_light_strength", 1.0,
                                      entity_reference=basemesh))


def get_light_mode(config_set, basemesh, asset_name):
    """Which lighting setup the bake should use. Falls back to the default."""
    mode = config_set.get_value(f"{asset_name}_cards_light_mode", LIGHT_MODE_FIXED,
                                entity_reference=basemesh)
    if mode not in {item[0] for item in LIGHT_MODE_ITEMS}:
        return LIGHT_MODE_FIXED
    return mode


def create_cards_bake_properties(config_set, basemesh, asset_name):
    """Create the persistent per-asset settings which are used when baking the cards texture. Idempotent, so existing values are kept."""
    _migrate_light_from_bbox(config_set, basemesh, asset_name)
    _migrate_light_intensity(config_set, basemesh, asset_name)

    for name, (proptype, value_range, default, description) in DYNAMIC_CARDS_BAKE_PROPS_DEFINITIONS.items():
        if default is None:
            default = HairBakeService.get_default_bake_directory()
        propname = f"{asset_name}_{name}"
        current = config_set.get_value(propname, default, entity_reference=basemesh)
        propdef = {
            "name": propname,
            "type": proptype,
            "description": description,
            "label": name.replace("cards_", "").replace("_", " ").capitalize(),
            "default": default
            }
        if proptype == "enum":
            propdef["items"] = value_range
            if current not in {item[0] for item in value_range}:
                # A file written by an older version can hold an option which no longer exists, writing it back would raise an exception
                _LOG.warn("Stored value is no longer a valid option, resetting", (propname, current, default))
                current = default
        elif value_range is not None:
            propdef["min"] = value_range[0]
            propdef["max"] = value_range[1]
        config_set.set_value_dynamic(propname, current, propdef, entity_reference=basemesh)

def asset_property_suffixes(kind):
    """Every setting an asset can have, as the part of its name after "<asset>_"."""
    fur = kind == "fur"
    suffixes = set(DYNAMIC_FUR_PROPS_DEFINITIONS if fur else DYNAMIC_HAIR_PROPS_DEFINITIONS)
    suffixes |= set(DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS if fur else DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS)
    suffixes |= set(DYNAMIC_CARDS_PROPS_DEFINITIONS)
    suffixes |= set(DYNAMIC_CARDS_CONFIG_PROPS_DEFINITIONS)
    suffixes |= set(DYNAMIC_CARDS_BAKE_PROPS_DEFINITIONS)
    suffixes |= {f"{kind}_asset_open", f"{kind}_cards_are_generated", f"{kind}_cards_are_baked"}
    return suffixes

def is_asset_property(key, asset_name, kind):
    """Whether a dynamic property (short name) belongs to this asset."""
    prefix = f"{asset_name}_"
    if not key.startswith(prefix):
        return False
    rest = key[len(prefix):]
    # Everything about the cards is named cards_..., this catches settings of older versions no longer defined
    return rest in asset_property_suffixes(kind) or rest.startswith("cards_")

def remove_asset_properties(config_set, basemesh, asset_name, kind):
    """Remove every setting of one asset from the basemesh, and nothing of any other asset. Returns the removed names."""
    dynamic_prefix = config_set.dynamic_prefix
    names = set()
    for prop in basemesh.bl_rna.properties:
        if prop.identifier.startswith(dynamic_prefix):
            names.add(prop.identifier[len(dynamic_prefix):])
    # Not yet registered (right after loading a file), or only the serialized definition is left
    for key in basemesh.keys():
        name = str(key).replace("$", "")
        if name.startswith(dynamic_prefix):
            names.add(name[len(dynamic_prefix):])
    removed = sorted(name for name in names if is_asset_property(name, asset_name, kind))
    for name in removed:
        config_set.remove_dynamic_key(name, basemesh)
    return removed

# Suffixes of the extra maps the bake operator can produce alongside the main color texture
BAKED_EXTRA_MAP_KEYS = ("normal", "ao", "root_tip", "flow", "depth", "side_on")

def baked_image_names(asset_name):
    """Every image datablock a bake of the given asset may have left in the file."""
    names = [f"{asset_name}_cards_texture"]
    names.extend(f"{asset_name}_cards_{key}" for key in BAKED_EXTRA_MAP_KEYS)
    return names

def get_cards_object(asset_name):
    """Find the card object belonging to the given hair or fur asset, if there is one."""
    return bpy.data.objects.get(asset_name + CARDS_OBJECT_SUFFIX)

def has_cards_generator(asset_name):
    """Check if the cards of the given asset are driven by a generated node group (cluster boxes are not)."""
    card_obj = get_cards_object(asset_name)
    return card_obj is not None and CARDS_MODIFIER_NAME in card_obj.modifiers

def set_cards_flag(config_set, basemesh, asset_name, kind, flag, value):
    """Remember whether the cards of an asset have been generated or baked.

    Args:
        config_set: HAIR_PROPERTIES or FUR_PROPERTIES.
        basemesh: The basemesh the properties are stored on.
        asset_name (str): Name of the hair or fur asset.
        kind (str): Either "hair" or "fur".
        flag (str): Either "generated" or "baked".
        value (bool): The value to store.
    """
    propname = f"{asset_name}_{kind}_cards_are_{flag}"
    propdef = {
        "name": propname,
        "type": "boolean",
        "label": propname,
        "description": f"Cards of this asset have been {flag}",
        "default": False
        }
    config_set.set_value_dynamic(propname, value, propdef, entity_reference=basemesh)

def get_cards_flag(config_set, basemesh, asset_name, kind, flag):
    """Read back a flag written by set_cards_flag."""
    return config_set.get_value(f"{asset_name}_{kind}_cards_are_{flag}", False, entity_reference=basemesh)

class HairGetterSetterFactory():
    """Works out what a dynamic hair/fur property drives from its name, and makes the getter and setter for it.

    The name is "<prefix><asset>_<setting>", and both the asset and the setting can contain underscores.
    The name alone can be read in more ways: "afro_roll_length" is the "roll_length" of "afro" or the "length" of
    "afro_roll". Every reading is kept as a candidate. The most specific one (longest setting name) is the default, and
    the getter and setter pick the candidate whose asset is actually on the character.
    """

    def __init__(self, name, prefix=DYNAMIC_PREFIX, fur=False, _candidate=None):
        self.prefix = prefix
        self.full_property_name = name
        self.short_property_name = None
        self.property_metadata = None
        self.hair_object_name = None
        self.managed_to_deduce_property = False
        self.modifier_name = None
        self.modifier_attribute = None
        self.socket_name = None
        self.max = 0.0
        self.min = 0.0
        self.default_value = None
        self.is_hair_property = False
        self.is_material_property = False
        self.is_texture_property = False
        self.is_cards_property = False
        self.is_fur = fur

        self.base_prop_definitions = None
        self.base_prop_material_definition = None

        if fur:
            self.base_prop_definitions = DYNAMIC_FUR_PROPS_DEFINITIONS
            self.base_prop_material_definition = DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS
        else:
            self.base_prop_definitions = DYNAMIC_HAIR_PROPS_DEFINITIONS
            self.base_prop_material_definition = DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS

        self.candidates = [_candidate] if _candidate is not None else self._find_candidates()
        if self.candidates:
            self._apply_candidate(self.candidates[0])

    def _find_candidates(self):
        """Every kind/setting/definition the name can be read as, the most specific first."""
        body = re.sub("^" + self.prefix, "", self.full_property_name)
        candidates = []
        for kind, definitions in (("cards", DYNAMIC_CARDS_PROPS_DEFINITIONS), ("hair", self.base_prop_definitions),
                                  ("material", self.base_prop_material_definition)):
            for key, definition in definitions.items():
                # The asset name in front of the setting cannot be empty
                if body.endswith("_" + key) and len(body) > len(key) + 1:
                    candidates.append((kind, key, definition))
        # "cards_density" before the hair "density", "roll_length" before "length"
        kind_order = {"cards": 0, "hair": 1, "material": 2}
        candidates.sort(key=lambda candidate: (-len(candidate[1]), kind_order[candidate[0]]))
        return candidates

    def _apply_candidate(self, candidate):
        kind, key, definition = candidate
        self.short_property_name = key
        self.managed_to_deduce_property = True
        if kind == "cards":
            self.socket_name = definition[0]
            if definition[1] is not None:
                self.min = definition[1][0]
                self.max = definition[1][1]
            self.default_value = definition[2]
            self.is_cards_property = True
        elif kind == "hair":
            self.modifier_name = definition[0]
            self.modifier_attribute = definition[1]
            self.min = definition[2][0]
            self.max = definition[2][1]
            self.default_value = self.min
            self.is_hair_property = True
        else:
            self.modifier_name = definition[0]
            self.modifier_attribute = definition[1]
            if key in ["use_texture", "texture_path"]:
                self.is_texture_property = True
            else:
                self.is_material_property = True
            self.default_value = self._deduce_material_default(self.modifier_attribute)
        self._interpolate_hair_object_name()

    def _deduce_material_default(self, specification):
        """Work out a fallback value of the right type, so that a getter never returns None."""
        if isinstance(specification, (bool, str)):
            return specification
        if len(specification) > 2:
            return list(specification)
        self.min = specification[0]
        self.max = specification[1]
        return (self.min + self.max) / 2.0

    def _interpolate_hair_object_name(self):
        hair_name = re.sub("^" + self.prefix, "", self.full_property_name)
        self.hair_object_name = hair_name[:-(len(self.short_property_name) + 1)]

    def _readings(self):
        """One factory per way the name can be read, in order they are tried."""
        return [self] + [HairGetterSetterFactory(self.full_property_name, prefix=self.prefix, fur=self.is_fur,
                                                 _candidate=candidate) for candidate in self.candidates[1:]]

    def resolve(self, source):
        """The reading of the name whose asset is on the character ``source``, or default if none is."""
        for reading in self._readings():
            if reading._get_hair_object(source) is not None:
                return reading
        return self

    def _get_hair_object(self, source):
        """Find the hair/fur object belonging to this property, amongst the children of the basemesh ``source``.

        Not looked up globally, since the same asset can be applied to several characters (names like "name.001").
        """
        if not self.hair_object_name:
            return None
        if isinstance(source, bpy.types.Object):
            for child in ObjectService.get_list_of_children(source):
                if child.name == self.hair_object_name:
                    return child
            return None
        # Should not happen, dynamic properties are accessed through the basemesh. Global lookup as a fallback
        return bpy.data.objects.get(self.hair_object_name)

    def _get_card_object(self, source):
        if not self.hair_object_name:
            return None
        card_name = self.hair_object_name + CARDS_OBJECT_SUFFIX
        if isinstance(source, bpy.types.Object):
            for child in ObjectService.get_list_of_children(source):
                if child.name == card_name:
                    return child
            return None
        return bpy.data.objects.get(card_name)

    def _material_getter(self):
        _LOG.debug("Generating material getter for", self.full_property_name)
        def getter(source):
            # This is very chatty, using "trace" rather than "debug" for this method
            _LOG.debug("Invoking getter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute
                ))

            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.debug("No hair object found for", self.hair_object_name)
                return self.default_value

            material = MaterialService.get_material(hair_obj)
            if material is None:
                _LOG.error("No material found for", hair_obj.name)
                return self.default_value

            group_node = None
            for node in material.node_tree.nodes:
                if hasattr(node, "node_tree") and node.node_tree and str(node.node_tree.name).startswith("Hair shader EEVEE"):
                    group_node = node
                    break

            if group_node is None:
                _LOG.error("There is no group node in this material", (hair_obj.name, material, material.node_tree))
                return self.default_value

            socket = NodeService.find_input_socket_by_identifier_or_name(
                group_node,
                socket_identifier=self.modifier_name,
                socket_name=self.modifier_name
                )
            if socket is None:
                _LOG.error("No such socket found in this group node", (hair_obj.name, self.modifier_name, group_node.inputs))
                return self.default_value

            _LOG.debug("Returning socket default value", (socket, socket.default_value))
            return socket.default_value

        return getter

    def _material_setter(self):
        _LOG.debug("Generating material setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking setter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute,
                value
                ))

            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return

            material = MaterialService.get_material(hair_obj)
            if material is None:
                _LOG.error("No material found for", hair_obj.name)
                return

            group_node = None
            for node in material.node_tree.nodes:
                if hasattr(node, "node_tree") and node.node_tree and str(node.node_tree.name).startswith("Hair shader EEVEE"):
                    group_node = node
                    break

            if group_node is None:
                _LOG.error("There is no group node in this material", (hair_obj.name, material, material.node_tree))
                return

            socket = NodeService.find_input_socket_by_identifier_or_name(
                group_node,
                socket_identifier=self.modifier_name,
                socket_name=self.modifier_name
                )
            if socket is None:
                _LOG.error("No such socket found in this group node", (hair_obj.name, self.modifier_name, group_node.inputs))
                return

            socket.default_value = value

        return setter

    def _texture_getter(self):
        _LOG.debug("Generating texture getter for", self.full_property_name)
        def getter(source):
            _LOG.debug("Invoking texture getter for", (
                source,
                self.full_property_name,
                self.short_property_name
            ))

            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.debug("No hair object found for", self.hair_object_name)
                return self.default_value

            mat = MaterialService.get_material(hair_obj)
            if mat is None or not mat.use_nodes:
                _LOG.error("No usable material on", hair_obj.name)
                return self.default_value

            # find material group node
            group_node = next(
                (n for n in mat.node_tree.nodes
                 if hasattr(n, "node_tree")
                 and n.node_tree
                 and n.node_tree.name.startswith("Hair shader EEVEE")),
                None
            )
            if group_node is None:
                _LOG.error("No hair shader group node in material", mat.name)
                return self.default_value

            gtree = group_node.node_tree
            nodes = gtree.nodes
            links = gtree.links
            img_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)

            # TEXTURE PATH PROPERTY: look for the image node inside the group
            if self.short_property_name == "texture_path":
                if img_node and img_node.image:
                    return bpy.path.abspath(img_node.image.filepath)
                return "Select texture path"

            # USE TEXTURE PROPERTY: simply read the group‐node input default
            else:
                if not img_node:
                    _LOG.debug("No image node found - texture is not used.")
                    return False

                # Check if image node is linked to any shader base color inputs
                shader_nodes = [
                    n for n in nodes
                    if n.bl_idname in ('ShaderNodeBsdfPrincipled', 'ShaderNodeBsdfHairPrincipled')
                ]

                for shader in shader_nodes:
                    inp = shader.inputs[0]  # 'Base Color'
                    for ln in inp.links:
                        if ln.from_node == img_node and ln.from_socket.name == "Color":
                            _LOG.debug("Texture node is actively linked.")
                            return True

                _LOG.debug("No texture link found.")
                return False
        return getter

    def _texture_setter(self):
        _LOG.debug("Generating texture setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking texture setter for", (
                source,
                self.full_property_name,
                self.short_property_name
            ))

            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.error("No hair object found for", self.hair_object_name)
                return

            mat = MaterialService.get_material(hair_obj)
            if mat is None or not mat.use_nodes:
                _LOG.error("No usable material on", hair_obj.name)
                return

            # find our group node (Despite its name, group node also supports cycles)
            group_node = next(
                (n for n in mat.node_tree.nodes
                 if hasattr(n, "node_tree")
                 and n.node_tree
                 and n.node_tree.name.startswith("Hair shader EEVEE")),
                None
            )
            if group_node is None:
                _LOG.error("No hair shader group node in material", mat.name)
                return

            # key for saving previous links from shader nodes
            storage_key = "_saved_base_color_links"

            # TEXTURE PATH: load the image and insert a new image texture node
            gtree = group_node.node_tree
            nodes = gtree.nodes
            links = gtree.links

            # find all principled/hair-principled shader nodes
            shader_nodes = [
                n for n in nodes if n.bl_idname in ('ShaderNodeBsdfPrincipled', 'ShaderNodeBsdfHairPrincipled')
            ]

            if self.short_property_name == "texture_path":
                # Store previous texture node to delete it later
                previous_tex_node = None
                for node in list(nodes):
                    if node.type == 'TEX_IMAGE':
                        previous_tex_node = node
                # Disconnect texture
                if previous_tex_node:
                    HairEditorService.restore_shader_links(previous_tex_node, shader_nodes, group_node, nodes, links, storage_key)

                # Remove texture
                if previous_tex_node:
                    nodes.remove(previous_tex_node)

                path = bpy.path.abspath(value)
                if not path or not os.path.isfile(path):
                    _LOG.info("Texture path invalid")
                    return
                try:
                    img = bpy.data.images.load(path, check_existing=True)
                except Exception as e:
                    _LOG.error("Cannot load image '%s': %s", path, e)
                    return

                tex_node = gtree.nodes.new('ShaderNodeTexImage')
                tex_node.image = img
                tex_node.label = os.path.basename(path)
                tex_node.location = (300, 200)

                # Join node to material
                store_links = storage_key not in group_node
                HairEditorService.join_texture_node_to_shader(tex_node, shader_nodes, group_node, links, storage_key, store_links)

                _LOG.debug("Added texture node %s", tex_node.name)
                return

            # USE TEXTURE: flip links on/off
            # find the texture IMG node
            img_node = next((n for n in nodes if (n.type == 'TEX_IMAGE')), None)

            if value:
                # return in case of no available texture, so it does not break the material
                if not img_node:
                    return
                # Already in use: storing again would save the texture links as the colour links to restore
                if any(link.from_node == img_node for shader in shader_nodes for link in shader.inputs[0].links):
                    return
                # store and remove existing links
                store_links=True
                HairEditorService.join_texture_node_to_shader(img_node, shader_nodes, group_node, links, storage_key, store_links)

            else:
                # disconnect texture and restore links to color inputs
                HairEditorService.restore_shader_links(img_node, shader_nodes, group_node, nodes, links, storage_key)

        return setter

    def _cards_getter(self):
        _LOG.debug("Generating cards getter for", self.full_property_name)
        def getter(source):
            _LOG.trace("Invoking cards getter for", (source, self.full_property_name, self.socket_name))
            card_obj = self._get_card_object(source)
            if card_obj is None:
                _LOG.debug("No card object found for", self.hair_object_name)
                return self.default_value
            modifier = card_obj.modifiers.get(CARDS_MODIFIER_NAME)
            if modifier is None:
                _LOG.debug("Card object has no hair cards modifier (expected for cluster boxes)", card_obj.name)
                return self.default_value
            identifier = find_cards_socket_identifier(modifier.node_group, self.socket_name)
            if identifier is None:
                _LOG.debug("No such socket in the hair cards node group (expected if this mode does not use it)", (self.socket_name, card_obj.name))
                return self.default_value
            return ModifierService.get_node_group_input(modifier, identifier)
        return getter

    def _cards_setter(self):
        _LOG.debug("Generating cards setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking cards setter for", (source, self.full_property_name, self.socket_name, value))
            card_obj = self._get_card_object(source)
            if card_obj is None:
                _LOG.debug("No card object found for", self.hair_object_name)
                return
            modifier = card_obj.modifiers.get(CARDS_MODIFIER_NAME)
            if modifier is None:
                _LOG.debug("Card object has no hair cards modifier (expected for cluster boxes)", card_obj.name)
                return
            identifier = find_cards_socket_identifier(modifier.node_group, self.socket_name)
            if identifier is None:
                _LOG.debug("No such socket in the hair cards node group (expected if this mode does not use it)", (self.socket_name, card_obj.name))
                return
            ModifierService.set_node_group_input(modifier, identifier, value)
            # Geometry nodes ignore a changed input until the object is tagged for update
            card_obj.update_tag()
            if modifier.node_group:
                modifier.node_group.interface_update(bpy.context)
        return setter

    def _hair_getter(self):
        _LOG.debug("Generating hair getter for", self.full_property_name)
        def getter(source):
            # This is very chatty, using "trace" rather than "debug" for this method
            _LOG.trace("Invoking getter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute
                ))
            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.debug("No hair object found for", self.hair_object_name)
                return self.default_value
            modifier = hair_obj.modifiers.get(self.modifier_name)
            if modifier is None:
                _LOG.error("No such modifier on the hair object", (hair_obj.name, self.modifier_name))
                return self.default_value
            value = ModifierService.get_node_group_input(modifier, self.modifier_attribute)
            _LOG.trace("Modifier, value", (modifier, value))
            return value
        return getter

    def _hair_setter(self):
        _LOG.debug("Generating hair setter for", self.full_property_name)
        def setter(source, value):
            _LOG.debug("Invoking setter for", (
                source,
                self.full_property_name,
                self.short_property_name,
                self.modifier_name,
                self.modifier_attribute,
                value
                ))
            hair_obj = self._get_hair_object(source)
            if hair_obj is None:
                _LOG.debug("No hair object found for", self.hair_object_name)
                return
            modifier = hair_obj.modifiers.get(self.modifier_name)
            if modifier is None:
                _LOG.error("No such modifier on the hair object", (hair_obj.name, self.modifier_name))
                return
            _LOG.debug("Modifier, value before", (modifier, ModifierService.get_node_group_input(modifier, self.modifier_attribute)))
            ModifierService.set_node_group_input(modifier, self.modifier_attribute, value)
            _LOG.debug("Modifier, value mid", (modifier, ModifierService.get_node_group_input(modifier, self.modifier_attribute)))
            hair_obj.update_tag()
            bpy.context.view_layer.update()
            hair_obj.hide_viewport = True
            hair_obj.hide_viewport = False
            if hasattr(modifier, "node_group") and modifier.node_group:
                modifier.node_group.interface_update(bpy.context)
            _LOG.debug("Modifier, value after", (modifier, ModifierService.get_node_group_input(modifier, self.modifier_attribute)))
        return setter

    def _own_getter(self):
        if self.is_cards_property:
            return self._cards_getter()
        if self.is_hair_property:
            return self._hair_getter()
        if self.is_material_property:
            return self._material_getter()
        if self.is_texture_property:
            return self._texture_getter()
        return None

    def _own_setter(self):
        if self.is_cards_property:
            return self._cards_setter()
        if self.is_hair_property:
            return self._hair_setter()
        if self.is_material_property:
            return self._material_setter()
        if self.is_texture_property:
            return self._texture_setter()
        return None

    def generate_getter(self):
        if not self.managed_to_deduce_property:
            return None
        if len(self.candidates) == 1:
            return self._own_getter()
        readings = [(reading, reading._own_getter()) for reading in self._readings()]

        def getter(source):
            for reading, reading_getter in readings:
                if reading._get_hair_object(source) is not None:
                    return reading_getter(source)
            return readings[0][1](source)
        return getter

    def generate_setter(self):
        if not self.managed_to_deduce_property:
            return None
        if len(self.candidates) == 1:
            return self._own_setter()
        readings = [(reading, reading._own_setter()) for reading in self._readings()]

        def setter(source, value):
            for reading, reading_setter in readings:
                if reading._get_hair_object(source) is not None:
                    return reading_setter(source, value)
            return readings[0][1](source, value)
        return setter

def dynamic_setter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_setter()

def dynamic_getter_factory(configset, name):
    factory = HairGetterSetterFactory(name)
    return factory.generate_getter()

def dynamic_setter_factory_fur(configset, name):
    factory = HairGetterSetterFactory(name, prefix=DYNAMIC_PREFIX_FUR, fur=True)
    return factory.generate_setter()

def dynamic_getter_factory_fur(configset, name):
    factory = HairGetterSetterFactory(name, prefix=DYNAMIC_PREFIX_FUR, fur=True)
    return factory.generate_getter()

_LOC = os.path.dirname(__file__)
HAIR_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HAIR_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(
    HAIR_PROPERTIES_DIR,
    prefix="HAI_",
    dynamic_prefix=DYNAMIC_PREFIX,
    setter_factory=dynamic_setter_factory,
    getter_factory=dynamic_getter_factory
    )

FUR_PROPERTIES = DynamicConfigSet(
    [],
    prefix="FAI_",
    dynamic_prefix=DYNAMIC_PREFIX_FUR,
    setter_factory=dynamic_setter_factory_fur,
    getter_factory=dynamic_getter_factory_fur
    )
