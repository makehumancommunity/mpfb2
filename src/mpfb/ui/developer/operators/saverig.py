from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.rig import Rig
from mpfb._classmanager import ClassManager
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("developer.operators.saverig")

class MPFB_OT_Save_Rig_Operator(bpy.types.Operator, ExportHelper):
    """Save rig definition as json"""
    bl_idname = "mpfb.save_rig"
    bl_label = "Save rig"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check current mode
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(armature_object, mpfb_type_name="Basemesh")

        if basemesh is None:
            self.report({'ERROR'}, "Could not find related base mesh. It should have been parent or child of armature object.")
            return {'FINISHED'}

        rig = Rig.from_given_basemesh_and_armature_as_active_object(basemesh)

        _LOG.dump("final rig_definition", rig.rig_definition)

        unmatched_bone_names = rig.list_unmatched_bones()
        unmatched = len(unmatched_bone_names)

        if unmatched > 0:
            self.report({'WARNING'}, "There were " + str(unmatched) + " bones that could not be matched to cube or vertex")
            _LOG.warn("Unmatched bone names:", unmatched_bone_names)

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        with open(absolute_file_path, "w") as json_file:
            json.dump(rig.rig_definition, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Rig_Operator)
