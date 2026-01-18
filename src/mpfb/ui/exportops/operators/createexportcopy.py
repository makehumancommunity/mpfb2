"""Functionality for creating an export copy of a character"""

from ....services import TargetService
from ....services import LogService
from ....services import ExportService
from ....services import ObjectService
from ...mpfboperator import MpfbOperator
from .... import ClassManager
import bpy

_LOG = LogService.get_logger("matops.createexportcopy")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_Create_Export_Copy_Operator(MpfbOperator):
    """Operation to create an export copy of a character"""
    bl_idname = "mpfb.export_copy"
    bl_label = "Create export copy"
    bl_options = {'REGISTER'}

    def _delete_vertex_group(self, context, blender_object, vgroup_name):

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

    @classmethod
    def poll(self, context):
        obj = context.object
        if not obj:
            return False
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            return False
        return True

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        scene = context.scene

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not deduce basemesh")
            return {'FINISHED'}

        from ..exportopspanel import EXPORTOPS_PROPERTIES
        bake_shapekeys = EXPORTOPS_PROPERTIES.get_value("bake_shapekeys", entity_reference=scene)
        remove_basemesh = EXPORTOPS_PROPERTIES.get_value("remove_basemesh", entity_reference=scene)
        delete_helpers = EXPORTOPS_PROPERTIES.get_value("delete_helpers", entity_reference=scene)
        suffix = EXPORTOPS_PROPERTIES.get_value("suffix", entity_reference=scene)
        create_collection = EXPORTOPS_PROPERTIES.get_value("collection", entity_reference=scene)
        visemes_meta = EXPORTOPS_PROPERTIES.get_value("visemes_meta", entity_reference=scene)

        if create_collection:
            if "export copy" not in bpy.data.collections:
                collection = bpy.data.collections.new("export copy")
                bpy.context.scene.collection.children.link(collection)
            else:
                collection = bpy.data.collections["export copy"]
        else:
            collection = basemesh.users_collection[0]

        _LOG.debug("collection", collection)

        export_copy = ExportService.create_character_copy(basemesh, name_suffix=suffix, place_in_collection=collection)
        new_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_copy)

        if bake_shapekeys:
            TargetService.bake_targets(new_basemesh)

        if visemes_meta:
            ExportService.load_targets(new_basemesh)

        if delete_helpers:
            context.view_layer.objects.active = new_basemesh
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self._delete_vertex_group(context, new_basemesh, "HelperGeometry")
            self._delete_vertex_group(context, new_basemesh, "JointCubes")

            for modifier in new_basemesh.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group == 'body':
                    new_basemesh.modifiers.remove(modifier)

            if not bake_shapekeys:
                TargetService.reapply_all_details(new_basemesh)

            new_basemesh.select_set(True)
            ObjectService.activate_blender_object(new_basemesh)

            for group in new_basemesh.vertex_groups:
                _LOG.debug("group name", group.name)
                if group.name.startswith("helper-") or group.name.startswith("joint-") or group.name in ["Mid", "Left", "Right"]:
                    new_basemesh.vertex_groups.remove(group)

        if remove_basemesh:
            ObjectService.delete_object(new_basemesh)

        self.report({'INFO'}, "Export copy created")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_Export_Copy_Operator)
