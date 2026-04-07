from .....services import LogService
from .....services import LocationService
from .....services import RigService
from ..... import ClassManager
from ....pollstrategy import pollstrategy, PollStrategy
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext
import bpy, json, os

_LOG = LogService.get_logger("developer.operators.loadpose")

@pollstrategy(PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE)
class MPFB_OT_Load_Pose_Operator(MpfbOperator):
    """Load pose matching rig type and mode"""
    bl_idname = "mpfb.load_pose"
    bl_label = "Load pose"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        from ...applypose.applyposepanel import POSES_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=POSES_PROPERTIES)

        if ctx.active_object is None or ctx.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = ctx.active_object
        name = str(ctx.available_poses).strip()

        if not name:
            self.report({'ERROR'}, "Must select a valid pose name")
            return {'FINISHED'}

        rig_type = RigService.identify_rig(armature_object)
        if "default" in rig_type:
            rig_type = "default"
        mode = "_fk"

        for bone in armature_object.data.bones:
            if str(bone.name).endswith("_ik"):
                mode = "_ik"

        poses_root = LocationService.get_user_data("poses")
        pose_root = os.path.join(poses_root, rig_type + mode)

        absolute_file_path = bpy.path.abspath(os.path.join(pose_root, name + ".json"))
        _LOG.debug("absolute_file_path", absolute_file_path)

        if not os.path.exists(absolute_file_path):
            self.report({'ERROR'}, "The selected pose '" + name + "' for rig type '" + rig_type + mode + "' does not exist as file. You should probably report this as a bug.")
            return {'FINISHED'}

        pose = dict()

        with open(absolute_file_path, "r") as json_file:
            pose = json.load(json_file)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.set_pose_from_dict(armature_object, pose)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Pose_Operator)
