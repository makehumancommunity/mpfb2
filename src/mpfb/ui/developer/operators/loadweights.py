from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb.entities.rig import Rig
from mpfb._classmanager import ClassManager
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("developer.operators.loadweights")

class MPFB_OT_Load_Weights_Operator(bpy.types.Operator, ImportHelper):
    """Load weights from definition in json. NOTE that the base mesh must have the rig in question as a parent for this to work"""
    bl_idname = "mpfb.load_weights"
    bl_label = "Load weights"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        return ObjectService.object_is_basemesh(context.object) or ObjectService.object_is_skeleton(context.object)

    def execute(self, context):
        _LOG.enter()

        if context.object is None or not (ObjectService.object_is_basemesh(context.object) or ObjectService.object_is_skeleton(context.object)):
            self.report({'ERROR'}, "Must have basemesh or rig as active object")
            return {'FINISHED'}

        obj = context.object
        if ObjectService.object_is_basemesh(context.object):
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

        weights = dict()
        with open(absolute_file_path, 'r') as json_file:
            weights = json.load(json_file)

        _LOG.dump("Weights", weights)

        RigService.apply_weights(rig, basemesh, weights, all=True)

        self.report({'INFO'}, "Weights applied")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Weights_Operator)
