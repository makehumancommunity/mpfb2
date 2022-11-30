from mpfb.services.logservice import LogService
from mpfb._classmanager import ClassManager
import bpy, json
from bpy_extras.io_utils import ImportHelper

from mpfb.services.rigifyhelpers.rigifyhelpers import RigifyHelpers

_LOG = LogService.get_logger("developer.loadrigifylayers")

class MPFB_OT_Load_Rigify_Layers_Operator(bpy.types.Operator, ImportHelper):
    """Load rigify layer definition as json"""
    bl_idname = "mpfb.load_rigify_layers"
    bl_label = "Load rigify layers"
    bl_options = {'REGISTER', 'UNDO'}

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

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        armature_object = bpy.context.active_object

        RigifyHelpers.load_rigify_ui(armature_object, absolute_file_path)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Rigify_Layers_Operator)
