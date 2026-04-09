from .....services import LogService
from .....services import LocationService
from .....services import MaterialService
from .....services import ObjectService
from .....services import RigService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....pollstrategy import pollstrategy, PollStrategy
import bpy, json, math, os
from bpy.types import StringProperty
from bpy_extras.io_utils import ExportHelper

_LOG = LogService.get_logger("makepose.operators.savepose")

@pollstrategy(PollStrategy.ANY_ARMATURE_OBJECT_ACTIVE)
class MPFB_OT_Save_Pose_Operator(MpfbOperator):
    """Save pose as json"""
    bl_idname = "mpfb.save_pose"
    bl_label = "Save pose"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        if context.active_object is None or context.active_object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.active_object

        from ...makepose import MakePoseProperties
        from ....mpfbcontext import MpfbContext
        ctx = MpfbContext(context=context, scene_properties=MakePoseProperties)

        name = str(ctx.name).strip() if ctx.name else ctx.name

        if not name:
            self.report({'ERROR'}, "Must give a valid name")
            return {'FINISHED'}

        if "/" in name or "\\" in name:
            self.report({'ERROR'}, "Name must be given without path")
            return {'FINISHED'}

        if name == "." or name == "..":
            self.report({'ERROR'}, "Name is invalid, must include alphanumeric characters")
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        rig_type = RigService.identify_rig(armature_object)
        if "default" in rig_type:
            rig_type = "default"


        save_pose_as = "fk"

        if ctx.pose_type == "IKFK":
            save_pose_as = "ik"

        onlyselected = False

        if ctx.pose_type == "PARTIAL":
            save_pose_as = "partial"
            onlyselected = True

        pose = RigService.get_pose_as_dict(armature_object, ik_bone_translation=ctx.iktrans, root_bone_translation=ctx.roottrans, fk_bone_translation=ctx.fktrans, onlyselected=onlyselected)
        _LOG.dump("Pose", pose)

        if ctx.pose_type == "AUTO" and pose["has_ik_bones"]:
            save_pose_as = "ik"

        poses_root = LocationService.get_user_data("poses")
        pose_root = os.path.abspath(os.path.join(poses_root, rig_type + "_" + save_pose_as))

        if not os.path.exists(pose_root):
            _LOG.debug("Will create", pose_root)
            os.makedirs(str(pose_root))

        absolute_file_path = os.path.join(pose_root, name + ".json")
        _LOG.debug("absolute_file_path", absolute_file_path)

        if not ctx.overwrite and os.path.exists(absolute_file_path):
            self.report({'ERROR'}, "Pose file already exists: " + absolute_file_path)
            return {'FINISHED'}

        with open(absolute_file_path, "w") as json_file:
            json.dump(pose, json_file, indent=4, sort_keys=True)
            self.report({'INFO'}, "JSON file written to " + absolute_file_path)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if "rigify" in rig_type and not "generated" in rig_type:
            self.report({'WARNING'}, "Posing ungenerated rigify rigs is probably a very bad idea. Better to generate first and pose later.")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Save_Pose_Operator)
