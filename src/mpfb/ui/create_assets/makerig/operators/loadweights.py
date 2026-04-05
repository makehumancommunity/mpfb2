from .....services import LogService
from .....services import MaterialService
from .....services import ObjectService
from .....services import RigService
from .....entities.rig import Rig
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("makerig.operators.loadweights")

class MPFB_OT_Load_Weights_Operator(MpfbOperator, ImportHelper):
    """Load weights from definition in json. NOTE that the base mesh must have the rig in question as a parent for this to work"""
    bl_idname = "mpfb.load_weights"
    bl_label = "Load weights"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.mhw'

    def get_logger(self):
        return _LOG

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.active_object is None:
            return False
        return ObjectService.object_is_any_mesh(context.active_object) or ObjectService.object_is_skeleton(context.active_object)

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None or not (ObjectService.object_is_any_mesh(context.active_object) or
                                          ObjectService.object_is_skeleton(context.active_object)):
            self.report({'ERROR'}, "Must have basemesh or rig as active object")
            return {'FINISHED'}

        obj = context.active_object
        if ObjectService.object_is_any_mesh(context.active_object):
            basemesh = obj
            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(obj, "Skeleton")
        else:
            rig = obj
            basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(obj, "Basemesh")

        if not basemesh:
            self.report({'ERROR'}, "Could not find basemesh")
            return {'FINISHED'}

        if not rig:
            self.report({'ERROR'}, "Could not find skeleton")
            return {'FINISHED'}

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        RigService.load_weights(rig, basemesh, absolute_file_path, all=True)

        self.report({'INFO'}, "Weights applied")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Weights_Operator)
