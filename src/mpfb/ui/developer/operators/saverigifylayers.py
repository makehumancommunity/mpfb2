from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy_extras.io_utils import ExportHelper

from mpfb.services.rigifyhelpers.rigifyhelpers import RigifyHelpers

_LOG = LogService.get_logger("developer.saverigifylayers")

class MPFB_OT_Save_Rigify_Layers_Operator(bpy.types.Operator, ExportHelper):
    """Save rigify layer definition as json"""
    bl_idname = "mpfb.save_rigify_layers"
    bl_label = "Save rigify layers"
    bl_options = {'REGISTER'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        # TODO: check that it is a rigify enabled rig
        return True

    def execute(self, context):
        _LOG.enter()

        armature_object = bpy.context.active_object

        if armature_object is None or armature_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        rigify_ui = RigifyHelpers.get_rigify_ui(armature_object)

        _LOG.dump("rigify_ui", rigify_ui)

        with open(absolute_file_path, "w") as json_file:
            json.dump(rigify_ui, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Rigify_Layers_Operator)
