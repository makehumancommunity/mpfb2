from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.rig import Rig
from mpfb._classmanager import ClassManager
import bpy, json, math
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("developer.operators.loadrig")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_Load_Rig_Operator(bpy.types.Operator, ImportHelper):
    """Load rig from definition in json"""
    bl_idname = "mpfb.load_rig"
    bl_label = "Load rig"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.json'

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        return ObjectService.object_is_basemesh(context.object)

    def execute(self, context):
        _LOG.enter()

        if context.object is None or not ObjectService.object_is_basemesh(context.object):
            self.report({'ERROR'}, "Must have basemesh as active object")
            return {'FINISHED'}

        basemesh = context.object

        absolute_file_path = bpy.path.abspath(self.filepath)
        _LOG.debug("absolute_file_path", absolute_file_path)

        rig = Rig.from_json_file_and_basemesh(absolute_file_path, basemesh)
        armature_object = rig.create_armature_and_fit_to_basemesh()

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Rig_Operator)
