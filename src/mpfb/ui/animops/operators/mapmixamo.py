"""Functionality for snapping animation to mixamo rig"""

from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.rigservice import RigService
from mpfb._classmanager import ClassManager
from mpfb.ui.mpfboperator import MpfbOperator
import bpy, math

_LOG = LogService.get_logger("animops.mapmixamo")
_LOG.set_level(LogService.DEBUG)

_CUBE_CENTER_CACHE = {}

class MPFB_OT_Map_Mixamo_Operator(MpfbOperator):
    """Snap bones to mixamo animation"""
    bl_idname = "mpfb.map_mixamo"
    bl_label = "Map Mixamo"
    bl_options = {'REGISTER'}

    def __init__(self):
        MpfbOperator.__init__(self, "animops.mapmixamo")

    def hardened_execute(self, context):
        _LOG.enter()

        scene = context.scene

        armatures = ObjectService.get_selected_armature_objects()

        if not armatures or len(armatures) != 2:
            self.report({"ERROR"}, "Select exactly two armatures")
            return {'CANCELLED'}

        src = None
        dst = None
        bm1 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[0], "Basemesh")
        bm2 = ObjectService.find_object_of_type_amongst_nearest_relatives(armatures[1], "Basemesh")
        if bm1 and not bm2:
            src = armatures[1]
            dst = armatures[0]
        if bm2 and not bm1:
            src = armatures[0]
            dst = armatures[1]
        if not src:
            src = bpy.context.object
            if src == armatures[0]:
                dst = armatures[1]
            else:
                dst = armatures[0]

        _LOG.debug("Source, target", (src, dst))

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        if not "mixamorig:Hips" in dst.pose.bones:
            self.report({"ERROR"}, "'mixamorig:Hips' bone not found in destination. Strange bone naming?")
            return {'CANCELLED'}

        if not "mixamorig:Hips" in src.pose.bones:
            self.report({"ERROR"}, "'mixamorig:Hips' bone not found in source. Strange bone naming?")
            return {'CANCELLED'}

        for bone in dst.data.bones:
            if bone.name in src.data.bones:
                _LOG.debug("Bone", bone.name)
                constraint = RigService.add_bone_constraint_to_pose_bone(bone.name, dst, "COPY_ROTATION")
                constraint.target = src
                constraint.subtarget = bone.name

        constraint = RigService.add_bone_constraint_to_pose_bone("mixamorig:Hips", dst, "COPY_LOCATION")
        constraint.target = src
        constraint.subtarget = "mixamorig:Hips"

        self.report({"INFO"}, "Done")

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Map_Mixamo_Operator)
