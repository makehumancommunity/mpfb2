"""
Module with logic for loading and interpolating facial animation targets (visemes and ARKit face units).
"""

from .logservice import LogService
from .targetservice import TargetService
from .objectservice import ObjectService
from .clothesservice import ClothesService
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

# If no vert was shifted more than this in a shape key, assume the shape key is not significant enough to be interpolated.
SIGNIFICANT_SHIFT_MINIMUM = 0.0001


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
