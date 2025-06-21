"""Operator for removing all makeup from a material."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from .... import ClassManager

_LOG = LogService.get_logger("matops.removemakeup")


class MPFB_OT_Remove_Makeup_Operator(bpy.types.Operator):
    """Remove all ink layers from a material"""
    bl_idname = "mpfb.remove_makeup"
    bl_label = "Remove makeup"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(obj)
        if basemesh is None:
            _LOG.error("Could not find a basemesh for the object")
            return {'FINISHED'}

        if not MaterialService.has_materials(basemesh):
            self.report({'ERROR'}, "The selected object needs to have a material")
            return {'FINISHED'}

        material = MaterialService.get_material(obj)

        MaterialService.remove_all_makeup(material, basemesh)

        self.report({'INFO'}, "Makeup was removed")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Remove_Makeup_Operator)
