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

_LOG = LogService.get_logger("basemeshops.operators.bakeshapekeys")

class MPFB_OT_Bake_Shapekeys_Operator(bpy.types.Operator):
    """Bake all shape keys into a final mesh. WARNING: You will no longer be able to adjust targets after doing this."""
    bl_idname = "mpfb.bake_shapekeys"
    bl_label = "Bake shapekeys"
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

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        obj = context.object

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if objtype != "Basemesh":
            self.report({'ERROR'}, "Can only bake shapekeys on basemesh")
            return {'FINISHED'}

        TargetService.bake_targets(context.object)

        self.report({'INFO'}, "Bake finished")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Bake_Shapekeys_Operator)
