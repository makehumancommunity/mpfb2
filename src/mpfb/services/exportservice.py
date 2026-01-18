"""
Module with logic regarding staging characters for export.

In many cases, external applications will have difficulties managing blender logic such as shape keys, materials, modifiers
and animations. This module provides a set of tools to create character copies where such logic is baked, transformed or
otherwise managed.
"""

import bpy
from .logservice import LogService
from .targetservice import TargetService
from .objectservice import ObjectService

_LOG = LogService.get_logger("services.exportservice")
_LOG.set_level(LogService.DEBUG)

META_VISEMES = [
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


class ExportService:
    """The ExportService class serves as a utility class for staging characters for export.

    Note that this class is designed to be used without instantiation. All methods are static methods that can be called directly."""

    def __init__(self):
        raise RuntimeError("You should not instance ExportService. Use its static methods instead.")

    @staticmethod
    def create_character_copy(source_object, name_suffix="_export_copy", place_in_collection=None):
        """
        Creates a deep copy of the given character, including any rig or child meshes connected to it.

        Args:
        - source_object (bpy.types.Object): The source object to create a copy of. This is usually the basemesh or the rig
        - name_suffix (str): A suffix to append to created objects' names.
        - place_in_collection (bpy.types.Collection, optional): The collection where the character copy should be placed. If not provided, the copy will be placed in the default collection.

        Returns:
        - bpy.types.Object: The created character copy.
        """

        _LOG.enter()

        _LOG.debug("source_object", source_object)

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(source_object)
        if not basemesh:
            _LOG.error("No basemesh related to the given object", source_object)
            raise ValueError("No basemesh related to the given object")

        _LOG.debug("Basemesh", basemesh)

        root_object = basemesh
        if basemesh.parent:
            root_object = basemesh.parent

        _LOG.debug("Root object", root_object)

        children = ObjectService.get_list_of_children(root_object)

        _LOG.debug("Children", children)

        new_root = ObjectService.duplicate_blender_object(root_object, collection=place_in_collection)
        new_root.name = root_object.name + name_suffix

        for child in children:
            _LOG.debug("Child", child)
            name = child.name + name_suffix
            duplicated_child = ObjectService.duplicate_blender_object(child, collection=place_in_collection, parent=new_root)
            duplicated_child.name = name
            if new_root.type == 'ARMATURE':
                # We need to make sure that any armature modifier on the child is pointed to the new root
                modifier = duplicated_child.modifiers.get("Armature") # Assuming there's only one armature modifier
                if modifier:
                    modifier.object = new_root

        return new_root

    @staticmethod
    def load_targets(basemesh, load_meta_visemes=True, load_microsoft_visemes=False, load_arkit_faceunits=False):
        """Bulk load targets, if installed. Will raise exception if target asset pack is not installed."""
        _LOG.enter()

        target_stack = []
        if load_meta_visemes:
            for target in META_VISEMES:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if len(target_stack) > 0:
            TargetService.bulk_load_targets(basemesh, target_stack)
