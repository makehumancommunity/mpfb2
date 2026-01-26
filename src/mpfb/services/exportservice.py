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

        if len(target_stack) > 0:
            TargetService.bulk_load_targets(basemesh, target_stack)

    @staticmethod
    def bake_shapekeys_modifiers_remove_helpers(basemesh, bake_shapekeys=True, bake_masks=False, bake_subdiv=False, remove_helpers=True, also_proxy=True):
        """Bakes shape keys, modifiers and optionally remove helpers.

        Args:
        - basemesh (bpy.types.Object): The object to bake shape keys, masks, and subdivision modifiers for.
        - bake_shapekeys (bool): Whether to bake shape keys.
        - bake_masks (bool): Whether to bake masks.
        - bake_subdiv (bool): Whether to bake subdivision modifiers.
        - remove_helpers (bool): Whether to remove helper geometry
        - also_proxy (bool): Whether to also bake on the body proxy if it exists.
        """

        _LOG.enter()

        if not TargetService.has_any_shapekey(basemesh):
            _LOG.debug("No shapekeys to bake")
            bake_shapekeys = False

        if (bake_masks or bake_subdiv) and not bake_shapekeys:
            # TODO: Support baking masks and subdivision modifiers without baking shape keys
            raise NotImplementedError("Baking masks and/or subdivision modifiers without baking shape keys is not implemented yet")

        if bake_shapekeys:
            _LOG.debug("Baking shape keys")
            TargetService.bake_targets(basemesh)

        helpers_removed_by_modifier = False

        bpy.context.view_layer.objects.active = basemesh

        for modifier in basemesh.modifiers:
            if modifier.type == 'MASK' and bake_masks:
                print(modifier.vertex_group)

                if modifier.vertex_group == "body" and not modifier.invert_vertex_group:
                    # This is the modifier that hides helper geometry
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    helpers_removed_by_modifier = True
                else:
                    if modifier.vertex_group == "body" and modifier.invert_vertex_group:
                        # This is the modifier that hides the body if there is a proxy. It does not make much
                        # sense to keep this if we're baking masks, but it doesn't make sense to bake it either
                        basemesh.modifiers.remove(modifier)
                    else:
                        # This is probably a clothes delete group
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
            else:
                if modifier.type == 'SUBSURF' and bake_subdiv:
                    modifier.levels = modifier.render_levels
                    if modifier.levels == 0:
                        basemesh.modifiers.remove(modifier)
                    else:
                        bpy.ops.object.modifier_apply(modifier=modifier.name)

        if remove_helpers and not helpers_removed_by_modifier:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            ExportService._delete_vertex_group(basemesh, "HelperGeometry")
            ExportService._delete_vertex_group(basemesh, "JointCubes")

            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group == 'body' and not modifier.invert_vertex_group:
                    basemesh.modifiers.remove(modifier)

            if not bake_shapekeys:
                TargetService.reapply_all_details(basemesh)

            basemesh.select_set(True)
            ObjectService.activate_blender_object(basemesh)

            for group in basemesh.vertex_groups:
                _LOG.trace("group name", group.name)
                if group.name.startswith("helper-") or group.name.startswith("joint-") or group.name in ["Mid", "Left", "Right"]:
                    basemesh.vertex_groups.remove(group)

        if also_proxy:
            # TODO: bake modifiers that affect the body proxy
            pass

    @staticmethod
    def _delete_vertex_group(blender_object, vgroup_name):

        context = bpy.context

        _LOG.debug("Deleting vertex groups", (blender_object, vgroup_name))
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = blender_object
        blender_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        group_idx = None
        for group in blender_object.vertex_groups:
            _LOG.dump("group name", group.name)
            if vgroup_name in group.name:
                group_idx = group.index
        _LOG.dump("group index", group_idx)

        for vertex in blender_object.data.vertices:
            vertex.select = False
            for group in vertex.groups:
                if group.group == group_idx:
                    vertex.select = True
            _LOG.dump("Vertex index, selected", (vertex.index, vertex.select))

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        blender_object.select_set(False)

        # Re-query the vertex group after mesh topology changes
        group_to_remove = None
        for group in blender_object.vertex_groups:
            if vgroup_name in group.name:
                group_to_remove = group
                break

        if group_to_remove:
            _LOG.debug("Deleting vertex group", group_to_remove)
            blender_object.vertex_groups.remove(group_to_remove)