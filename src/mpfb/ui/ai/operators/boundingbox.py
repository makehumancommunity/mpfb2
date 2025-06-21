from ....entities.objectproperties import GeneralObjectProperties
from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from .... import ClassManager
import bpy, json, math
from mathutils import Vector, Matrix

_LOG = LogService.get_logger("ai.operators.boundingbox")

class MPFB_OT_Boundingbox_Operator(bpy.types.Operator):
    """Populate the bounding box settings from the active mesh object"""
    bl_idname = "mpfb.boundingbox"
    bl_label = "From active"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.active_object is None or context.active_object.type != 'MESH':
            return False
        return True

    def execute(self, context):
        _LOG.enter()

        if context.active_object is None or context.active_object.type != 'MESH':
            self.report({'ERROR'}, "Must have a mesh object as active object")
            return {'FINISHED'}

        obj = context.active_object

        minx = None
        maxx = None
        minz = None
        maxz = None

        for vert in obj.data.vertices:
            world_coord = obj.matrix_world @ vert.co
            _LOG.debug("world", world_coord)
            if minx is None or world_coord.x < minx:
                minx = world_coord.x
            if maxx is None or world_coord.x > maxx:
                maxx = world_coord.x
            if minz is None or world_coord.z < minz:
                minz = world_coord.z
            if maxz is None or world_coord.z > maxz:
                maxz = world_coord.z

        from ...ai.aipanel import AI_PROPERTIES

        AI_PROPERTIES.set_value("minx", minx, entity_reference=context.scene)
        AI_PROPERTIES.set_value("maxx", maxx, entity_reference=context.scene)
        AI_PROPERTIES.set_value("minz", minz, entity_reference=context.scene)
        AI_PROPERTIES.set_value("maxz", maxz, entity_reference=context.scene)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Boundingbox_Operator)
