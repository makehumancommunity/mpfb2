"""Operator for copying a pose from a source rig to a number of target rigs."""

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....entities.material.makeskinmaterial import MakeSkinMaterial
from ....services import LogService
from ....services import RigService
from ....services import ObjectService
from .... import ClassManager

_LOG = LogService.get_logger("poseops.copy_pose")

class MPFB_OT_Copy_Pose_Operator(bpy.types.Operator):
    """Copy pose from active to selected. Ie, first select all targets, then select the source. You can copy to multiple targets at the same time"""
    bl_idname = "mpfb.copy_pose"
    bl_label = "Copy pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            objtype = ObjectService.get_object_type(context.active_object)
            return objtype == "Skeleton"
        return False

    def execute(self, context):
        active = context.active_object
        scn = context.scene

        from ...poseops.poseopspanel import POP_PROPERTIES
        only_rotation = POP_PROPERTIES.get_value("only_rotation", entity_reference=scn)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        selected = []

        for obj in context.selected_objects:
            if obj.type != 'ARMATURE':
                self.report({'ERROR'}, "Can only have armatures as selected/active")
                return {'FINISHED'}

            if obj != active:
                selected.append(obj)

        if len(selected) < 1:
            self.report({'ERROR'}, "Must have at least one active and one selected object")
            return {'FINISHED'}

        active_type = RigService.identify_rig(active)
        for obj in selected:
            seltype = RigService.identify_rig(obj)
            if active_type != seltype:
                self.report({'ERROR'}, "Can only copy between rigs of the same type. Active is " + activetype + " but selected is " + seltype + ".")
                return {'FINISHED'}

        for obj in selected:
            RigService.copy_pose(active, obj, only_rotation)

        for obj in selected:
            obj.select_set(True)

        ObjectService.activate_blender_object(active)

        self.report({'INFO'}, "Pose copied")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Copy_Pose_Operator)
