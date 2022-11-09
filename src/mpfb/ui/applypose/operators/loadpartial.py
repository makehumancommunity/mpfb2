from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("developer.operators.loadpartial")

class MPFB_OT_Load_Partial_Operator(bpy.types.Operator):
    """Load partial pose matching rig type"""
    bl_idname = "mpfb.load_partial"
    bl_label = "Load partial pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        return True

    def execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        from mpfb.ui.applypose.applyposepanel import POSES_PROPERTIES
        name = POSES_PROPERTIES.get_value("available_partials", entity_reference=context.scene)

        if not name:
            self.report({'ERROR'}, "Must select a valid pose name")
            return {'FINISHED'}

        rig_type = RigService.identify_rig(armature_object)
        if "default" in rig_type:
            rig_type = "default"
        mode = "_partial"

        poses_root = LocationService.get_user_data("poses")
        pose_root = os.path.join(poses_root, rig_type + mode)

        absolute_file_path = bpy.path.abspath(os.path.join(pose_root, name + ".json"))
        _LOG.debug("absolute_file_path", absolute_file_path)

        if not os.path.exists(absolute_file_path):
            self.report({'ERROR'}, "The selected pose '" + name + "' for rig type '" + rigtype + mode + "' does not exist as file. You should probably report this as a bug.")
            return {'FINISHED'}

        pose = dict()

        with open(absolute_file_path, "r") as json_file:
            pose = json.load(json_file)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.set_pose_from_dict(armature_object, pose, from_rest_pose=False)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Partial_Operator)
