"""Functionality for snapping animation to mixamo rig"""

from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
import bpy, math

_LOG = LogService.get_logger("animops.mapmixamo")

def _find_bone_by_name(armature, name):
    """Find bone by name, taking into account that the name might have a different prefix"""

    prefix = None

    # Find prefix
    for bone in armature.data.bones:
        if ":" in bone.name:
            prefix = bone.name.split(":")[0]
            break

    if not prefix:
        raise ValueError("This does not look like a mixamo rig, it doesn't have prefixed bone names")

    if not "mixamo" in prefix:
        raise ValueError("This does not look like a mixamo rig, the bone name prefix does not contain 'mixamo'")

    name_without_prefix = name.split(":")[1]

    expected_name = prefix + ":" + name_without_prefix
    if expected_name in armature.data.bones:
        return armature.data.bones[expected_name]

    return None

class MPFB_OT_Map_Mixamo_Operator(MpfbOperator):
    """Add bone constraints to all mixamo bones in the target rig, making them copy the location and rotation of the bones in the source rig"""
    bl_idname = "mpfb.map_mixamo"
    bl_label = "Snap to mixamo"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

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

        dst_hips = _find_bone_by_name(dst, "mixamorig:Hips")
        src_hips = _find_bone_by_name(src, "mixamorig:Hips")

        if not dst_hips:
            self.report({"ERROR"}, "Hips bone not found in destination. Is this a mixamo rig?")
            return {'CANCELLED'}

        if not src_hips:
            self.report({"ERROR"}, "Hips bone not found in source. Is this a mixamo rig?")
            return {'CANCELLED'}

        src_bone_names = []
        for bone in src.data.bones:
            src_bone_names.append(bone.name)
        src_bone_names.sort()

        _LOG.debug("Source bones", src_bone_names)

        dst_bone_names = []
        for bone in dst.data.bones:
            dst_bone_names.append(bone.name)
        dst_bone_names.sort()

        _LOG.debug("Destination bones", dst_bone_names)

        different_bones = len(src_bone_names) != len(dst_bone_names)

        for bone in dst.data.bones:
            src_bone = _find_bone_by_name(src, bone.name)
            _LOG.debug("Bone", (bone.name, src_bone))
            if src_bone is None:
                _LOG.warn("There was a bone in the destination rig that does not exist in the source rig", bone.name)
                different_bones = True
                continue
            constraint = RigService.add_bone_constraint_to_pose_bone(bone.name, dst, "COPY_ROTATION")
            constraint.target = src
            constraint.subtarget = src_bone.name


        constraint = RigService.add_bone_constraint_to_pose_bone(dst_hips.name, dst, "COPY_LOCATION")
        constraint.target = src
        constraint.subtarget = src_hips.name

        if not different_bones:
            self.report({"INFO"}, "Done")
        else:
            self.report({"WARNING"}, "The source and destination rigs do not have exactly the same set of bones. This might cause issues when animating.")

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Map_Mixamo_Operator)
