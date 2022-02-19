from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb.entities.rig import Rig
from mpfb._classmanager import ClassManager
import bpy, json, math, re
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("developer.operators.saveweights")

class MPFB_OT_Save_Weights_Operator(bpy.types.Operator, ExportHelper):
    """Save weights as json"""
    bl_idname = "mpfb.save_weights"
    bl_label = "Save weights"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, mpfb_type_name="Basemesh")

        if basemesh is None:
            self.report({'ERROR'}, "Could not find related basemesh. It should have been parent or child of armature object.")
            return {'FINISHED'}

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        weights = RigService.get_weights(armature_object, basemesh)

        # Strip the Rigify deform bone prefix for convenience
        weights["weights"] = {re.sub(r'^DEF-', '', k): v for k,v in weights["weights"].items()}

        with open(absolute_file_path, "w") as json_file:
            json.dump(weights, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Weights_Operator)
