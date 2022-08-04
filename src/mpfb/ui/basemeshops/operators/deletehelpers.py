from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("basemeshops.operators.deletehelpers")

class MPFB_OT_Delete_Helpers_Operator(bpy.types.Operator):
    """Delete all helper geometry. This will also delete the mask operator for hiding helpers. WARNING: You will not be able to equip many clothes after doing this"""
    bl_idname = "mpfb.delete_helpers"
    bl_label = "Delete helpers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if objtype != "Basemesh":
            return

        return True

    def _delete_vertex_group(self, context, blender_object, vgroup_name):
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

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        obj = context.object

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if objtype != "Basemesh":
            self.report({'ERROR'}, "Can only delete helpers on basemesh")
            return {'FINISHED'}

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self._delete_vertex_group(context, obj, "HelperGeometry")
        self._delete_vertex_group(context, obj, "JointCubes")

        for modifier in obj.modifiers:
            if modifier.type == 'MASK' and modifier.vertex_group == 'body':
                obj.modifiers.remove(modifier)

        self.report({'INFO'}, "Helper geometry deleted")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Delete_Helpers_Operator)
