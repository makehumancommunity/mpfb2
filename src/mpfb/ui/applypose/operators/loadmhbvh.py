import bpy, json, math, os
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.animationservice import AnimationService
from mpfb.ui.mpfboperator import MpfbOperator
from mpfb._classmanager import ClassManager
from bpy_extras.io_utils import ImportHelper

_LOG = LogService.get_logger("applypose.loadmhbvh")


class MPFB_OT_Load_MH_BVH_Operator(MpfbOperator, ImportHelper):
    """Destructively load a pose from a MH BVH file. WARNING: This will change the bone rolls of all bones, making further posing a bit unpredictable."""
    bl_idname = "mpfb.load_mhbvh_pose"
    bl_label = "Import MH BVH Pose"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.bvh', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        if context.object is None:
            return False
        if context.object is None or context.object.type != 'ARMATURE':
            return False
        return True

    def __init__(self):
        MpfbOperator.__init__(self, "applypose.loadmhbvh")

    def hardened_execute(self, context):
        _LOG.enter()

        if context.object is None or context.object.type != 'ARMATURE':
            self.report({'ERROR'}, "Must have armature as active object")
            return {'FINISHED'}

        armature_object = context.object

        _LOG.debug("filepath", self.filepath)

        AnimationService.import_bvh_file_as_pose(armature_object, self.filepath)

        self.report({'INFO'}, "The pose was destructively loaded from " + self.filepath)
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_MH_BVH_Operator)
