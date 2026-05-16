"""
Module with logic for loading and interpolating facial animation targets (visemes and ARKit face units).
"""

import bpy, json, os
from .logservice import LogService
from .targetservice import TargetService
from .locationservice import LocationService
from .objectservice import ObjectService
from .clothesservice import ClothesService
from .systemservice import SystemService
from ..entities.clothes.mhclo import Mhclo

_LOG = LogService.get_logger("services.faceservice")

MICROSOFT_VISEMES = [
    "aa_02",
    "aa_ah_ax_01",
    "ao_03",
    "aw_09",
    "ay_11",
    "d_t_n_19",
    "er_05",
    "ey_eh_uh_04",
    "f_v_18",
    "h_12",
    "k_g_ng_20",
    "l_14",
    "ow_08",
    "oy_10",
    "p_b_m_21",
    "r_13",
    "sh_ch_jh_zh_16",
    "sil_00",
    "s_z_15",
    "th_dh_17",
    "w_uw_07",
    "y_iy_ih_ix_06"
    ]

META_VISEMES = [
    "viseme_aa",
    "viseme_CH",
    "viseme_DD",
    "viseme_E",
    "viseme_FF",
    "viseme_I",
    "viseme_kk",
    "viseme_nn",
    "viseme_O",
    "viseme_PP",
    "viseme_RR",
    "viseme_sil",
    "viseme_SS",
    "viseme_TH",
    "viseme_U"
    ]

ARKIT_FACEUNITS = [
    "browDownLeft",
    "browDownRight",
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    "eyeBlinkLeft",
    "eyeBlinkRight",
    "eyeLookDownLeft",
    "eyeLookDownRight",
    "eyeLookInLeft",
    "eyeLookInRight",
    "eyeLookOutLeft",
    "eyeLookOutRight",
    "eyeLookUpLeft",
    "eyeLookUpRight",
    "eyeSquintLeft",
    "eyeSquintRight",
    "eyeWideLeft",
    "eyeWideRight",
    "jawForward",
    "jawLeft",
    "jawOpen",
    "jawRight",
    "mouthClose",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthFrownLeft",
    "mouthFrownRight",
    "mouthFunnel",
    "mouthLeft",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthPucker",
    "mouthRight",
    "mouthRollLower",
    "mouthRollUpper",
    "mouthShrugLower",
    "mouthShrugUpper",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "noseSneerLeft",
    "noseSneerRight",
    "tongueOut"
]

# Region grouping for the 52 ARKit face units. Used by the MakeExpression composer panel to lay
# out one slider box per region so the 52 sliders are navigable. Order within each list is the
# anatomical order MakeHuman has historically used in its Expression Mixer.
FACEUNIT_REGIONS = {
    "brow": [
        "browInnerUp",
        "browDownLeft",
        "browDownRight",
        "browOuterUpLeft",
        "browOuterUpRight",
    ],
    "eye": [
        "eyeBlinkLeft",
        "eyeBlinkRight",
        "eyeSquintLeft",
        "eyeSquintRight",
        "eyeWideLeft",
        "eyeWideRight",
        "eyeLookUpLeft",
        "eyeLookUpRight",
        "eyeLookDownLeft",
        "eyeLookDownRight",
        "eyeLookInLeft",
        "eyeLookInRight",
        "eyeLookOutLeft",
        "eyeLookOutRight",
    ],
    "cheek": [
        "cheekPuff",
        "cheekSquintLeft",
        "cheekSquintRight",
    ],
    "jaw": [
        "jawOpen",
        "jawForward",
        "jawLeft",
        "jawRight",
    ],
    "mouth": [
        "mouthClose",
        "mouthFunnel",
        "mouthPucker",
        "mouthLeft",
        "mouthRight",
        "mouthSmileLeft",
        "mouthSmileRight",
        "mouthFrownLeft",
        "mouthFrownRight",
        "mouthDimpleLeft",
        "mouthDimpleRight",
        "mouthStretchLeft",
        "mouthStretchRight",
        "mouthRollLower",
        "mouthRollUpper",
        "mouthShrugLower",
        "mouthShrugUpper",
        "mouthPressLeft",
        "mouthPressRight",
        "mouthLowerDownLeft",
        "mouthLowerDownRight",
        "mouthUpperUpLeft",
        "mouthUpperUpRight",
    ],
    "nose": [
        "noseSneerLeft",
        "noseSneerRight",
    ],
    "tongue": [
        "tongueOut",
    ],
}

# Short tooltip descriptions for each ARKit face unit, suitable for Blender slider tooltips.
# Source: the ARKit blendshape reference (https://pooyadeperson.com/the-ultimate-guide-to-creating-arkits-52-facial-blendshapes/).
FACEUNIT_DESCRIPTIONS = {
    "browDownLeft":      "Lowers the inner half of the left eyebrow.",
    "browDownRight":     "Lowers the inner half of the right eyebrow.",
    "browInnerUp":       "Raises the inner halves of both eyebrows.",
    "browOuterUpLeft":   "Raises the outer half of the left eyebrow.",
    "browOuterUpRight":  "Raises the outer half of the right eyebrow.",
    "cheekPuff":         "Puffs both cheeks outwards as if filled with air.",
    "cheekSquintLeft":   "Raises and tightens the left cheek under the eye.",
    "cheekSquintRight":  "Raises and tightens the right cheek under the eye.",
    "eyeBlinkLeft":      "Closes the left eyelid.",
    "eyeBlinkRight":     "Closes the right eyelid.",
    "eyeLookDownLeft":   "Rotates the left eye downwards.",
    "eyeLookDownRight":  "Rotates the right eye downwards.",
    "eyeLookInLeft":     "Rotates the left eye inwards (towards the nose).",
    "eyeLookInRight":    "Rotates the right eye inwards (towards the nose).",
    "eyeLookOutLeft":    "Rotates the left eye outwards (away from the nose).",
    "eyeLookOutRight":   "Rotates the right eye outwards (away from the nose).",
    "eyeLookUpLeft":     "Rotates the left eye upwards.",
    "eyeLookUpRight":    "Rotates the right eye upwards.",
    "eyeSquintLeft":     "Squints the left eyelid (lower lid raised).",
    "eyeSquintRight":    "Squints the right eyelid (lower lid raised).",
    "eyeWideLeft":       "Widens the left eyelid.",
    "eyeWideRight":      "Widens the right eyelid.",
    "jawForward":        "Pushes the lower jaw forwards.",
    "jawLeft":           "Slides the lower jaw to the left.",
    "jawOpen":           "Opens the jaw, parting the lips.",
    "jawRight":          "Slides the lower jaw to the right.",
    "mouthClose":        "Closes the lips while the jaw remains open.",
    "mouthDimpleLeft":   "Pulls the left corner of the mouth backwards into a dimple.",
    "mouthDimpleRight":  "Pulls the right corner of the mouth backwards into a dimple.",
    "mouthFrownLeft":    "Pulls the left corner of the mouth downwards.",
    "mouthFrownRight":   "Pulls the right corner of the mouth downwards.",
    "mouthFunnel":       "Funnels both lips outwards into a tube shape.",
    "mouthLeft":         "Shifts both lips to the left.",
    "mouthLowerDownLeft":  "Pulls the left half of the lower lip downwards.",
    "mouthLowerDownRight": "Pulls the right half of the lower lip downwards.",
    "mouthPressLeft":    "Presses the left half of the lips together.",
    "mouthPressRight":   "Presses the right half of the lips together.",
    "mouthPucker":       "Puckers both lips inwards into a kissing shape.",
    "mouthRight":        "Shifts both lips to the right.",
    "mouthRollLower":    "Rolls the lower lip inwards over the lower teeth.",
    "mouthRollUpper":    "Rolls the upper lip inwards over the upper teeth.",
    "mouthShrugLower":   "Pushes the lower lip outwards and upwards.",
    "mouthShrugUpper":   "Pushes the upper lip outwards and upwards.",
    "mouthSmileLeft":    "Pulls the left corner of the mouth upwards into a smile.",
    "mouthSmileRight":   "Pulls the right corner of the mouth upwards into a smile.",
    "mouthStretchLeft":  "Stretches the left corner of the mouth sideways.",
    "mouthStretchRight": "Stretches the right corner of the mouth sideways.",
    "mouthUpperUpLeft":  "Pulls the left half of the upper lip upwards.",
    "mouthUpperUpRight": "Pulls the right half of the upper lip upwards.",
    "noseSneerLeft":     "Sneers the left side of the nose upwards.",
    "noseSneerRight":    "Sneers the right side of the nose upwards.",
    "tongueOut":         "Sticks the tongue out of the mouth.",
}

# On-disk JSON schema version. Bumped when a backwards-incompatible change is made to the file
# format defined in docs/fileformats/expression.md.
EXPRESSION_FORMAT_VERSION = 1

# Name of the object-level property on the basemesh that stores the JSON-encoded list of
# currently-applied expressions. Each entry is {"asset": <library-relative path>, "weight": <float>}.
APPLIED_EXPRESSIONS_PROP = "mpfb_applied_expressions"

# Cache for is_faceunits01_installed(). None means "not yet probed". Filled lazily on first call;
# can be busted by passing force_recheck=True (used by tests).
_FACEUNITS01_INSTALLED = None

# If no vert was shifted more than this in a shape key, assume the shape key is not significant enough to be interpolated.
SIGNIFICANT_SHIFT_MINIMUM = 0.0001

# Mapping from Lip Sync addon property suffixes to visemes02 (Meta/ARKit) shape key names.
# Three Lip Sync slot IDs differ from the corresponding MPFB shape key name suffix:
#   slot "ih" → shape key "viseme_I"  (Lip Sync slot uses lowercase; MPFB shape key uses uppercase I)
#   slot "oh" → shape key "viseme_O"  (Lip Sync slot uses lowercase; MPFB shape key uses uppercase O)
#   slot "ou" → shape key "viseme_U"  (Lip Sync slot uses lowercase; MPFB shape key uses uppercase U)
# "UNK" falls back to "viseme_sil" (silence) as there is no dedicated unknown-phoneme shape key.
VISEMES02_TO_LIPSYNC = {
    "sil": "viseme_sil",
    "PP":  "viseme_PP",
    "FF":  "viseme_FF",
    "TH":  "viseme_TH",
    "DD":  "viseme_DD",
    "kk":  "viseme_kk",
    "CH":  "viseme_CH",
    "SS":  "viseme_SS",
    "nn":  "viseme_nn",
    "RR":  "viseme_RR",
    "aa":  "viseme_aa",
    "E":   "viseme_E",
    "ih":  "viseme_I",
    "oh":  "viseme_O",
    "ou":  "viseme_U",
    "UNK": "viseme_sil",
}


class FaceService:
    """The FaceService class provides static methods for loading and interpolating facial animation targets.

    This covers viseme shape keys (Microsoft and Meta standards) and ARKit face unit shape keys.
    These targets can be loaded onto an MPFB basemesh and then propagated to child meshes via interpolation.

    Note that this class is designed to be used without instantiation. All methods are static methods that can be called directly."""

    def __init__(self):
        raise RuntimeError("You should not instance FaceService. Use its static methods instead.")

    @staticmethod
    def load_targets(basemesh, load_microsoft_visemes=True, load_meta_visemes=False, load_arkit_faceunits=False):
        """Bulk load targets, if installed. Will raise exception if target asset pack is not installed."""
        _LOG.enter()

        target_stack = []

        if load_microsoft_visemes:
            for target in MICROSOFT_VISEMES:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if load_meta_visemes:
            for target in META_VISEMES:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if load_arkit_faceunits:
            for target in ARKIT_FACEUNITS:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if len(target_stack) > 0:
            TargetService.bulk_load_targets(basemesh, target_stack)

    @staticmethod
    def interpolate_targets(basemesh):
        """Interpolate viseme and faceunit shape keys from the basemesh to child meshes.

        For each child mesh that has an associated MHCLO file, this method transfers all non-modelling
        shape keys from the basemesh using the MHCLO vertex correspondence data.

        Args:
            basemesh (bpy.types.Object): The basemesh object whose shape keys will be interpolated to children.
        """
        _LOG.enter()

        if not basemesh.data.shape_keys or not basemesh.data.shape_keys.key_blocks:
            _LOG.debug("No shape keys on basemesh, nothing to interpolate")
            return

        # Temporarily disable all modifiers on the basemesh. Store their state so they can be restored in the end of the function
        modifier_states = {}
        for modifier in basemesh.modifiers:
            _LOG.debug("Disabling modifier", (modifier.name, modifier.show_viewport))
            modifier_states[modifier.name] = modifier.show_viewport
            modifier.show_viewport = False

        root_object = basemesh
        if basemesh.parent:
            root_object = basemesh.parent

        children = ObjectService.get_list_of_children(root_object)
        _LOG.debug("Children to interpolate to", children)

        all_relevant_shapekey_names = list(MICROSOFT_VISEMES)
        all_relevant_shapekey_names.extend(list(META_VISEMES))
        all_relevant_shapekey_names.extend(list(ARKIT_FACEUNITS))

        shape_keys_to_interpolate = []
        for key_block in basemesh.data.shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue
            if key_block.name not in all_relevant_shapekey_names:
                continue
            shape_keys_to_interpolate.append(key_block)

        if not shape_keys_to_interpolate:
            _LOG.debug("No viseme/faceunit shape keys found to interpolate")
            return

        _LOG.debug("Shape keys to interpolate", [sk.name for sk in shape_keys_to_interpolate])

        basis_coords = [v.co.copy() for v in basemesh.data.vertices]

        for child in children:
            if child == basemesh or child.type != 'MESH':
                continue

            mhclo_path = ClothesService.find_clothes_absolute_path(child)
            if not mhclo_path:
                _LOG.debug("No MHCLO path for child, skipping", child.name)
                continue

            _LOG.debug("Interpolating shape keys to", child.name)

            mhclo = Mhclo()
            mhclo.load(mhclo_path)

            if not child.data.shape_keys:
                child.shape_key_add(name="Basis", from_mix=False)

            for source_key in shape_keys_to_interpolate:
                if source_key.name in child.data.shape_keys.key_blocks:
                    _LOG.debug("Shape key already exists on child, skipping", (child.name, source_key.name))
                    continue

                # First, calculate all interpolated offsets to check if any are significant
                significant_changes = []
                for child_vert_idx in mhclo.verts:
                    if child_vert_idx >= len(child.data.vertices):
                        break
                    mapping = mhclo.verts[child_vert_idx]
                    v0, v1, v2 = mapping["verts"]
                    w0, w1, w2 = mapping["weights"]

                    if v0 >= len(source_key.data) or v1 >= len(source_key.data) or v2 >= len(source_key.data):
                        continue

                    offset0 = source_key.data[v0].co - basis_coords[v0]
                    offset1 = source_key.data[v1].co - basis_coords[v1]
                    offset2 = source_key.data[v2].co - basis_coords[v2]

                    interpolated_offset = offset0 * w0 + offset1 * w1 + offset2 * w2

                    # Check if this offset is significant
                    if interpolated_offset.length > SIGNIFICANT_SHIFT_MINIMUM:
                        significant_changes.append((child_vert_idx, interpolated_offset))

                # Only create the shape key if there are significant changes
                if not significant_changes:
                    _LOG.debug("No significant changes for shape key, skipping", (child.name, source_key.name))
                    continue

                new_key = child.shape_key_add(name=source_key.name, from_mix=False)
                new_key.value = source_key.value

                # Apply the significant changes
                for child_vert_idx, interpolated_offset in significant_changes:
                    new_key.data[child_vert_idx].co = child.data.vertices[child_vert_idx].co + interpolated_offset

                _LOG.debug("Interpolated shape key to child", (source_key.name, child.name))

        # Restore the modifier states
        for modifier in basemesh.modifiers:
            if modifier.name in modifier_states:
                modifier.show_viewport = modifier_states[modifier.name]

    @staticmethod
    def configure_lip_sync(basemesh):
        """Map loaded visemes02 shape keys to the Lip Sync addon's property slots.

        This method automates the manual process of selecting shape keys in the Lip Sync panel
        by iterating over VISEMES02_TO_LIPSYNC and writing each mapping to the corresponding
        lipsync2d_props attribute on the basemesh object.

        Args:
            basemesh (bpy.types.Object): The basemesh to configure. Must have visemes02 shape keys
                loaded and the Lip Sync addon must be installed and initialised on this object.

        Returns:
            list: A list of viseme IDs (strings) whose target shape key was not found on the mesh.
                  An empty list means all mappings were applied successfully.

        Raises:
            ValueError: If the Lip Sync addon is not installed/enabled, if the Lip Sync properties
                have not been initialised on this object, or if visemes02 shape keys are not loaded.
        """
        _LOG.enter()

        if not SystemService.check_for_lipsync():
            raise ValueError("The Lip Sync addon (iocgpoly_lip_sync) is not enabled. Please enable it in Blender preferences.")

        if not hasattr(basemesh, "lipsync2d_props") or not basemesh.lipsync2d_props.lip_sync_2d_initialized:
            raise ValueError("Lip Sync has not been initialised on this object. Use the Lip Sync panel to initialise it first.")

        if not basemesh.data.shape_keys or "viseme_sil" not in basemesh.data.shape_keys.key_blocks:
            raise ValueError("visemes02 shape keys are not loaded on this basemesh. Load the visemes02 pack first.")

        missing = []
        for viseme_id, shape_key_name in VISEMES02_TO_LIPSYNC.items():
            prop_name = "lip_sync_2d_viseme_shape_keys_" + viseme_id
            if shape_key_name not in basemesh.data.shape_keys.key_blocks:
                _LOG.warn("Shape key not found on mesh, skipping", (shape_key_name, viseme_id))
                missing.append(viseme_id)
                continue
            _LOG.debug("Setting lip sync property", (prop_name, shape_key_name))
            setattr(basemesh.lipsync2d_props, prop_name, shape_key_name)

        return missing

    @staticmethod
    def is_faceunits01_installed(force_recheck=False):
        """Return True if the faceunits01 asset pack appears to be installed.

        Probes for a single canonical face unit target ("cheekPuff") via TargetService.target_full_path.
        The result is cached for the session because target_full_path scans several directories.
        Pass force_recheck=True to bust the cache (used by tests and after a pack install).
        """
        global _FACEUNITS01_INSTALLED
        if force_recheck:
            _FACEUNITS01_INSTALLED = None
        if _FACEUNITS01_INSTALLED is None:
            _FACEUNITS01_INSTALLED = TargetService.target_full_path("cheekPuff") is not None
        return _FACEUNITS01_INSTALLED

    @staticmethod
    def set_expression(basemesh, expression_dict):
        """Apply a partial expression to the basemesh.

        For each (face unit name, weight) pair, set the value of the matching ``!ex-{name}`` shape key.
        If the shape key does not yet exist on the basemesh, the corresponding target is loaded on
        demand from the asset pack. Unknown ARKit names are warned and skipped. The method is
        additive: face units not mentioned in ``expression_dict`` are left untouched. Use
        ``clear_expression`` to zero everything first.

        Args:
            basemesh (bpy.types.Object): The basemesh object.
            expression_dict (dict[str, float]): Bare ARKit face unit name → weight in [0, 1].
        """
        _LOG.enter()
        if basemesh is None or basemesh.data is None:
            _LOG.warn("set_expression called without a valid basemesh")
            return

        for face_unit_name, weight in expression_dict.items():
            if face_unit_name not in ARKIT_FACEUNITS:
                _LOG.warn("Unknown ARKit face unit, skipping", face_unit_name)
                continue

            shape_key_name = TargetService.expression_name_to_shapekey_name(face_unit_name)
            existing = None
            if basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks:
                existing = basemesh.data.shape_keys.key_blocks.get(shape_key_name)

            if existing is None:
                # Don't load a target on demand just to write a zero into it.
                if float(weight) == 0.0:
                    continue
                full_path = TargetService.target_full_path(face_unit_name)
                if full_path is None:
                    _LOG.warn("Target file not found for face unit, skipping", face_unit_name)
                    continue
                TargetService.load_target(basemesh, full_path, weight=float(weight), name=shape_key_name)
            else:
                existing.value = float(weight)

    @staticmethod
    def clear_expression(basemesh):
        """Set every ``!ex-{name}`` shape key on the basemesh to 0.0.

        Iterates over ARKIT_FACEUNITS; missing shape keys are silently ignored. Modeling shape keys
        and visemes are not touched.

        Args:
            basemesh (bpy.types.Object): The basemesh object.
        """
        _LOG.enter()
        if basemesh is None or basemesh.data is None:
            return
        if not basemesh.data.shape_keys or not basemesh.data.shape_keys.key_blocks:
            return

        key_blocks = basemesh.data.shape_keys.key_blocks
        for face_unit_name in ARKIT_FACEUNITS:
            shape_key_name = TargetService.expression_name_to_shapekey_name(face_unit_name)
            block = key_blocks.get(shape_key_name)
            if block is not None:
                block.value = 0.0

    @staticmethod
    def read_current_expression(basemesh):
        """Read the current ``!ex-`` shape key values into a dict keyed by bare ARKit names.

        The returned dict always contains all 52 ARKIT_FACEUNITS keys; face units whose shape key
        is missing on the basemesh are reported as 0.0. This makes it straightforward for the
        composer UI to populate sliders from the current basemesh state without missing entries.

        Args:
            basemesh (bpy.types.Object): The basemesh object.

        Returns:
            dict[str, float]: Bare ARKit face unit name → current shape key value.
        """
        _LOG.enter()
        result = {name: 0.0 for name in ARKIT_FACEUNITS}
        if basemesh is None or basemesh.data is None:
            return result
        if not basemesh.data.shape_keys or not basemesh.data.shape_keys.key_blocks:
            return result

        for block in basemesh.data.shape_keys.key_blocks:
            face_unit_name = TargetService.shapekey_name_to_expression_name(block.name)
            if face_unit_name is None:
                continue
            if face_unit_name not in ARKIT_FACEUNITS:
                continue
            result[face_unit_name] = float(block.value)
        return result

    @staticmethod
    def save_expression(filename, expression_dict, metadata):
        """Serialize an expression to a JSON file (see docs/fileformats/expression.md).

        Filters zero-valued entries and rounds weights to four decimals for stable diffs. The
        ``metadata`` dict supplies the top-level fields (``name``, ``description``, ``tags``,
        ``author``, ``copyright``, ``license``, ``homepage``); missing keys are written with
        empty-string defaults (or an empty list for ``tags``).

        If ``filename`` is a bare basename (no directory part), it is resolved under
        ``LocationService.get_user_data("expressions")`` and the directory is created on demand.

        Args:
            filename (str): Output path. Bare names resolve under ``<user_data>/expressions/``.
            expression_dict (dict[str, float]): Bare ARKit name → weight. Zero entries are dropped.
            metadata (dict): Top-level metadata fields.

        Returns:
            str: The absolute path actually written to.
        """
        _LOG.enter()
        if not filename:
            raise ValueError("save_expression requires a filename")

        if os.path.dirname(filename):
            absolute_path = os.path.abspath(filename)
        else:
            base = LocationService.get_user_data("expressions")
            os.makedirs(base, exist_ok=True)
            target_name = filename if filename.lower().endswith(".json") else filename + ".json"
            absolute_path = os.path.abspath(os.path.join(base, target_name))

        face_units = {}
        for name, weight in (expression_dict or {}).items():
            if name not in ARKIT_FACEUNITS:
                _LOG.warn("Skipping unknown face unit on save", name)
                continue
            try:
                value = float(weight)
            except (TypeError, ValueError):
                _LOG.warn("Skipping non-numeric weight on save", (name, weight))
                continue
            if value == 0.0:
                continue
            face_units[name] = round(value, 4)

        meta = metadata or {}
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        payload = {
            "format_version": EXPRESSION_FORMAT_VERSION,
            "name": str(meta.get("name", "")),
            "description": str(meta.get("description", "")),
            "tags": list(tags),
            "face_units": face_units,
            "author": str(meta.get("author", "")),
            "copyright": str(meta.get("copyright", "")),
            "license": str(meta.get("license", "")),
            "homepage": str(meta.get("homepage", "")),
        }

        with open(absolute_path, "w", encoding="utf-8") as out:
            json.dump(payload, out, indent=4, sort_keys=True)

        return absolute_path

    @staticmethod
    def load_expression(filename):
        """Load an expression JSON file (see docs/fileformats/expression.md).

        Tolerant of missing optional fields: ``description``, ``tags``, ``author``, ``copyright``,
        ``license``, ``homepage`` default to empty string (or empty list for ``tags``). Unknown
        ``face_units`` keys produce a warning and are skipped. Unknown top-level keys are ignored.

        Args:
            filename (str): Path to the JSON file.

        Returns:
            tuple[dict[str, float], dict]: (expression_dict, metadata). ``expression_dict`` only
                contains face units whose names are members of ARKIT_FACEUNITS. ``metadata``
                contains the seven top-level metadata fields with defaults.
        """
        _LOG.enter()
        if not filename or not os.path.isfile(filename):
            raise IOError("Expression file does not exist: " + str(filename))

        with open(filename, "r", encoding="utf-8") as inp:
            data = json.load(inp)

        if not isinstance(data, dict):
            raise ValueError("Expression file does not contain a JSON object: " + str(filename))

        raw_face_units = data.get("face_units", {}) or {}
        expression_dict = {}
        for name, weight in raw_face_units.items():
            if name not in ARKIT_FACEUNITS:
                _LOG.warn("Skipping unknown face unit on load", name)
                continue
            try:
                expression_dict[name] = float(weight)
            except (TypeError, ValueError):
                _LOG.warn("Skipping non-numeric weight on load", (name, weight))

        metadata = {
            "name":        str(data.get("name", "")),
            "description": str(data.get("description", "")),
            "tags":        list(data.get("tags", []) or []),
            "author":      str(data.get("author", "")),
            "copyright":   str(data.get("copyright", "")),
            "license":     str(data.get("license", "")),
            "homepage":    str(data.get("homepage", "")),
        }

        return expression_dict, metadata

    @staticmethod
    def _compute_expression_library_relative_path(absolute_path):
        """Strip the matching expressions asset root prefix from an absolute path.

        Returns a forward-slash relative path (e.g. ``"smile.json"`` or
        ``"my_collection/smile.json"``). If the path is not under any known expressions root
        the basename is returned, so callers always get a stable, transferable identifier.
        """
        # Imported lazily to avoid a service-layer import cycle at module load.
        from .assetservice import AssetService  # pylint: disable=C0415
        if not absolute_path:
            return ""
        abs_path = os.path.abspath(absolute_path)
        roots = AssetService.get_asset_roots("expressions")
        for root in roots:
            root_norm = os.path.abspath(root)
            try:
                rel = os.path.relpath(abs_path, root_norm)
            except ValueError:
                continue
            if not rel.startswith(".."):
                return rel.replace(os.sep, "/")
        return os.path.basename(abs_path)

    @staticmethod
    def list_available_expressions():
        """List every expression JSON discovered across the four standard MPFB asset roots.

        Scans ``<root>/expressions/*.json`` for every root returned by
        ``AssetService.get_asset_roots("expressions")`` (priority order: mpfb_data, mh_data,
        user_data, second_root). When the same library-relative path is present in multiple
        roots, the highest-priority root wins — matching the precedence rule used for poses.

        Returns:
            list[tuple[str, str, dict]]: A list of ``(absolute_path, library_relative_path,
                metadata)`` tuples. ``metadata`` is the dict returned by ``load_expression``.
                Files that fail to parse are skipped with a warning so a single malformed file
                does not break the picker.
        """
        _LOG.enter()
        from .assetservice import AssetService  # pylint: disable=C0415
        roots = AssetService.get_asset_roots("expressions")

        seen = {}
        for root in roots:
            root_norm = os.path.abspath(root)
            if not os.path.isdir(root_norm):
                continue
            for dirpath, _dirs, files in os.walk(root_norm):
                for name in files:
                    if not name.lower().endswith(".json"):
                        continue
                    abs_path = os.path.abspath(os.path.join(dirpath, name))
                    rel = os.path.relpath(abs_path, root_norm).replace(os.sep, "/")
                    if rel in seen:
                        continue
                    try:
                        _expr, meta = FaceService.load_expression(abs_path)
                    except (IOError, ValueError, json.JSONDecodeError) as exc:
                        _LOG.warn("Skipping unreadable expression file", (abs_path, exc))
                        continue
                    meta = dict(meta) if isinstance(meta, dict) else {}
                    raw_name = meta.get("name", "")
                    if isinstance(raw_name, str) and raw_name.strip():
                        label = raw_name.strip()
                    else:
                        basename = os.path.splitext(os.path.basename(rel))[0]
                        label = basename.replace("_", " ")
                    meta["label"] = label
                    seen[rel] = (abs_path, rel, meta)

        return [seen[rel] for rel in sorted(seen.keys())]

    @staticmethod
    def aggregate_expression_stack(stack):
        """Aggregate a list of applied-expression rows into a single clamped face-unit dict.

        Each row is a ``{"asset": <library-relative path>, "weight": <row weight>}`` dict.
        Each referenced file is loaded via ``load_expression``; per face unit, the value is the
        sum of ``loaded_weight * row_weight`` across every row, clamped to ``[0, 1]``. Rows
        whose ``asset`` cannot be resolved on disk are skipped with a warning, so a preset can
        still partially apply when one referenced file is missing.

        Args:
            stack (list[dict]): Applied-expressions list as stored in
                ``basemesh["mpfb_applied_expressions"]``.

        Returns:
            dict[str, float]: ``{face_unit_name: weight}`` containing only face units with a
                non-zero clamped value. Empty if the input stack is empty.
        """
        _LOG.enter()
        from .assetservice import AssetService  # pylint: disable=C0415

        if not stack:
            return {}

        aggregated = {}
        for row in stack:
            asset = row.get("asset") if isinstance(row, dict) else None
            if not asset:
                _LOG.warn("Skipping stack row without an asset field", row)
                continue
            try:
                row_weight = float(row.get("weight", 1.0))
            except (TypeError, ValueError):
                _LOG.warn("Skipping stack row with non-numeric weight", row)
                continue

            absolute_path = AssetService.find_asset_absolute_path(asset, asset_subdir="expressions")
            if not absolute_path or not os.path.isfile(absolute_path):
                _LOG.warn("Could not resolve expression asset, skipping", asset)
                continue

            try:
                expression_dict, _meta = FaceService.load_expression(absolute_path)
            except (IOError, ValueError, json.JSONDecodeError) as exc:
                _LOG.warn("Could not load expression asset, skipping", (asset, exc))
                continue

            for face_unit_name, value in expression_dict.items():
                if face_unit_name not in ARKIT_FACEUNITS:
                    continue
                try:
                    contribution = float(value) * row_weight
                except (TypeError, ValueError):
                    continue
                aggregated[face_unit_name] = aggregated.get(face_unit_name, 0.0) + contribution

        clamped = {}
        for name, value in aggregated.items():
            if value <= 0.0:
                continue
            clamped[name] = 1.0 if value > 1.0 else value
        return clamped

    @staticmethod
    def _read_applied_expressions(basemesh):
        """Return the applied-expressions list stored on the basemesh (empty list if absent)."""
        if basemesh is None:
            return []
        raw = basemesh.get(APPLIED_EXPRESSIONS_PROP, None)
        if not raw:
            return []
        if isinstance(raw, str):
            try:
                value = json.loads(raw)
            except (ValueError, json.JSONDecodeError):
                _LOG.warn("Could not decode mpfb_applied_expressions, treating as empty", raw)
                return []
        else:
            value = raw
        if not isinstance(value, list):
            return []
        return value

    @staticmethod
    def _write_applied_expressions(basemesh, stack):
        """Sort the stack by asset and write it as a JSON-encoded string on the basemesh."""
        if basemesh is None:
            return
        if not stack:
            basemesh[APPLIED_EXPRESSIONS_PROP] = json.dumps([])
            return
        normalized = []
        for row in stack:
            if not isinstance(row, dict):
                continue
            asset = row.get("asset")
            if not asset:
                continue
            try:
                weight = float(row.get("weight", 1.0))
            except (TypeError, ValueError):
                continue
            normalized.append({"asset": str(asset), "weight": weight})
        normalized.sort(key=lambda r: r["asset"])
        basemesh[APPLIED_EXPRESSIONS_PROP] = json.dumps(normalized)

    @staticmethod
    def apply_expression_file(basemesh, filename, weight=1.0, append=True):
        """Apply a saved expression file to the basemesh through the persistent stack.

        Retained as a low-level helper. The expressions-library panel drives the use-side via
        ``set_stack_weight`` instead. Steps:

        1. Validates the file via ``load_expression`` (so a malformed file is rejected before
           the stack is mutated).
        2. Resolves the file's library-relative path so the row is portable across machines.
        3. Updates ``basemesh[APPLIED_EXPRESSIONS_PROP]`` — appending or replacing by ``asset``
           (latest-wins per asset). When ``append`` is False the stack is replaced with a
           single row.
        4. Rebuilds the aggregated ``{face_unit: weight}`` dict via
           ``aggregate_expression_stack``, calls ``clear_expression`` then ``set_expression``.

        The auto-refit / ``HumanService.refit`` call is intentionally not done here — that
        belongs to the operator layer, which knows the panel's ``auto_refit`` toggle.

        Args:
            basemesh (bpy.types.Object): The basemesh object.
            filename (str): Absolute path to an expression JSON file.
            weight (float): Row weight for this expression. Defaults to 1.0.
            append (bool): If True (default), append/replace by asset. If False, replace the
                stack with a single row.

        Returns:
            dict[str, float]: The aggregated ``{face_unit_name: weight}`` dict that was
                written via ``set_expression``.
        """
        _LOG.enter()
        if basemesh is None:
            raise ValueError("apply_expression_file requires a basemesh")
        if not filename or not os.path.isfile(filename):
            raise IOError("Expression file does not exist: " + str(filename))

        # Validate up-front so we don't mutate the stack on a bad file.
        FaceService.load_expression(filename)

        library_path = FaceService._compute_expression_library_relative_path(filename)

        if append:
            existing = FaceService._read_applied_expressions(basemesh)
            stack = []
            for row in existing:
                if not isinstance(row, dict):
                    continue
                if row.get("asset") == library_path:
                    continue
                stack.append(row)
            stack.append({"asset": library_path, "weight": float(weight)})
        else:
            stack = [{"asset": library_path, "weight": float(weight)}]

        FaceService._write_applied_expressions(basemesh, stack)

        aggregated = FaceService.aggregate_expression_stack(
            FaceService._read_applied_expressions(basemesh)
        )

        FaceService.clear_expression(basemesh)
        if aggregated:
            FaceService.set_expression(basemesh, aggregated)

        return aggregated

    @staticmethod
    def rebuild_expression_stack(basemesh):
        """Re-aggregate ``basemesh[APPLIED_EXPRESSIONS_PROP]`` into live ``!ex-*`` values.

        Used after the stack list has been mutated externally and the live shape-key values
        need to be rebuilt from scratch.
        """
        _LOG.enter()
        if basemesh is None:
            return {}
        stack = FaceService._read_applied_expressions(basemesh)
        aggregated = FaceService.aggregate_expression_stack(stack)
        FaceService.clear_expression(basemesh)
        if aggregated:
            FaceService.set_expression(basemesh, aggregated)
        return aggregated

    @staticmethod
    def clear_applied_expressions(basemesh):
        """Empty the stack and zero every ``!ex-*`` shape key."""
        _LOG.enter()
        if basemesh is None:
            return
        basemesh[APPLIED_EXPRESSIONS_PROP] = json.dumps([])
        FaceService.clear_expression(basemesh)

    @staticmethod
    def set_stack_weight(basemesh, asset_fragment, weight):
        """Set the weight of one expression in the applied-expressions stack.

        Entry point used by the expressions-library panel's per-slider update callbacks.
        Steps:

        1. Read the current stack from ``basemesh[APPLIED_EXPRESSIONS_PROP]``.
        2. If ``weight <= 0.0``, drop any row whose ``asset`` matches ``asset_fragment``.
           Otherwise upsert ``{"asset": asset_fragment, "weight": weight}`` with latest-wins
           per asset.
        3. Write the new stack back (sorted by asset).
        4. Re-aggregate the whole stack via ``aggregate_expression_stack``, then
           ``clear_expression`` + ``set_expression`` to refresh the live ``!ex-*`` shape keys.

        Auto-refit is the caller's responsibility (the panel's update callback decides
        whether to invoke ``HumanService.refit`` based on its own scene toggle).

        Args:
            basemesh (bpy.types.Object): The basemesh object.
            asset_fragment (str): Library-relative path of the expression file.
            weight (float): New slider value in ``[0, 1]``.

        Returns:
            dict[str, float]: The aggregated ``{face_unit_name: weight}`` dict that was
                written via ``set_expression``.
        """
        _LOG.enter()
        if basemesh is None:
            raise ValueError("set_stack_weight requires a basemesh")
        if not asset_fragment:
            raise ValueError("set_stack_weight requires an asset fragment")

        try:
            new_weight = float(weight)
        except (TypeError, ValueError):
            new_weight = 0.0

        existing = FaceService._read_applied_expressions(basemesh)
        stack = []
        for row in existing:
            if not isinstance(row, dict):
                continue
            if row.get("asset") == asset_fragment:
                continue
            stack.append(row)
        if new_weight > 0.0:
            stack.append({"asset": asset_fragment, "weight": new_weight})

        FaceService._write_applied_expressions(basemesh, stack)

        aggregated = FaceService.aggregate_expression_stack(
            FaceService._read_applied_expressions(basemesh)
        )

        FaceService.clear_expression(basemesh)
        if aggregated:
            FaceService.set_expression(basemesh, aggregated)

        return aggregated
