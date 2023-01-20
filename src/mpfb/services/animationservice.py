"""Service for working with animations."""

import bpy, os
from mathutils import Matrix, Vector
from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService
from .objectservice import ObjectService
from bpy.types import PoseBone
from mathutils import Vector
from mpfb.entities.retarget import RETARGET_MAPS

_LOG = LogService.get_logger("services.animationservice")

class AnimationService:
    """Service with utility functions for working with animations. It only has static methods, so you don't
    need to instance it."""

    def __init__(self):
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance AnimationService. Use its static methods instead.")

    @staticmethod
    def get_key_frames_as_dict(armature_object, root_bone_translation=True, ik_bone_translation=True, fk_bone_translation=False):
        """Scan through all key frames set for pose bones and return a dict with all info."""
        _LOG.enter()

        anim = armature_object.animation_data
        _LOG.debug("animation_data", anim)

        action = anim.action
        _LOG.debug("action", action)
        _LOG.debug("action frame range", action.frame_range)

        for group in action.groups:
            _LOG.dump("Action group ", group)

        full_dict = dict()
        full_dict["animation_data"] = dict()
        animation_data = full_dict["animation_data"]

        full_dict["metadata"] = dict()
        meta = full_dict["metadata"]
        meta["rig"] = RigService.identify_rig(armature_object)

        if not "default" in meta["rig"]:
            raise ValueError('Only the default rig is supported so far')

        right_leg = ["upperleg01.R", "upperleg02.R", "lowerleg01.R", "lowerleg02.R"]

        leg_length = 0.0
        for bone_name in right_leg:
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            leg_length = leg_length + bone.length

        meta["leg_length"] = leg_length

        right_arm = ["upperarm01.R", "upperarm02.R", "lowerarm01.R", "lowerarm02.R"]
        arm_length = 0.0

        arm_length = 0.0
        for bone_name in right_arm:
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            arm_length = arm_length + bone.length

        meta["arm_length"] = arm_length

        for fcurve in action.fcurves:
            curve_name = str(fcurve.data_path).split("\"")[1]
            if curve_name not in animation_data:
                animation_data[curve_name] = dict()

            pdata = animation_data[curve_name]
            curve_type = str(fcurve.data_path).split(".")[-1]
            curve_idx = int(fcurve.array_index)

            if "quater" in curve_type:
                raise ValueError('Only XYZ euler rotation type supported. Found bone ' + curve_name + ' with data path ' + curve_type + ' which is a different rotation type.')

            _LOG.debug("name, type, idx", (curve_name, curve_type, curve_idx))

            include = True
            if "translate" in curve_type:
                if "root" in curve_name and not root_bone_translation:
                    include = False
                if "_ik" in curve_name and not ik_bone_translation:
                    include = False
                if not "_ik" in curve_name and not "root" in curve_name and not fk_bone_translation:
                    include = False

            if include:
                for keyframe in fcurve.keyframe_points:
                    frame_number = int(keyframe.co[0])
                    result = fcurve.evaluate(frame_number)
                    _LOG.dump("  -- frame_number, result", (frame_number, result))

                    if frame_number not in pdata:
                        pdata[frame_number] = dict()

                    fdata = pdata[frame_number]
                    if curve_type not in fdata:
                        fdata[curve_type] = dict()
                        fdata[curve_type]["values"] = [0.0, 0.0, 0.0]
                        fdata[curve_type]["metadata"] = [dict(), dict(), dict()]

                    metadata = fdata[curve_type]["metadata"][curve_idx]

                    fdata[curve_type]["values"][curve_idx] = result

                    metadata["interpolation"] = str(keyframe.interpolation)
                    metadata["handle_left"] = list(keyframe.handle_left)
                    metadata["handle_right"] = list(keyframe.handle_right)
                    metadata["handle_left_type"] = str(keyframe.handle_left_type)
                    metadata["handle_right_type"] = str(keyframe.handle_right_type)

        return full_dict

    @staticmethod
    def set_key_frames_from_dict(armature_object, animation_dict, root_bone_translation=True, ik_bone_translation=True, fk_bone_translation=False, frame_offset=0, bone_location_offsets=None, skip_frames=None):
        """Assign key frames for pose bones."""
        _LOG.enter()

        animation = animation_dict["animation_data"]

        for bone_name in animation.keys():
            pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            if not pose_bone:
                _LOG.error("Pose bone does not exist", pose_bone)
                raise ValueError('Tried to assign transform to non-existing bone ' + bone_name)
            bone_animation = animation[bone_name]
            for key_frame_str in bone_animation.keys():
                key_frame_idx = int(key_frame_str)
                if not skip_frames or key_frame_idx not in skip_frames:
                    key_frame = bone_animation[key_frame_str]

                    key_frame_idx = key_frame_idx + frame_offset

                    if "rotation_euler" in key_frame:
                        pose_bone.rotation_euler = key_frame["rotation_euler"]["values"]
                        pose_bone.keyframe_insert(data_path="rotation_euler", frame=key_frame_idx)
                        _LOG.dump("Setting rotation euler", (bone_name, key_frame_idx, key_frame["rotation_euler"]["values"]))

                    def fmt(val):
                        return "{:.4f}".format(val)

                    if "location" in key_frame:
                        loc = list(key_frame["location"]["values"])
                        if bone_location_offsets and bone_name in bone_location_offsets:
                            trans = bone_location_offsets[bone_name]
                            loc[0] = loc[0] + trans[0]
                            loc[1] = loc[1] + trans[1]
                            loc[2] = loc[2] + trans[2]

                        pose_bone.location = loc
                        pose_bone.keyframe_insert(data_path="location", frame=key_frame_idx)
                        _LOG.dump("Setting location", (bone_name, key_frame_idx, loc))

    @staticmethod
    def walk_cycle_from_dict(armature_object, animation_dict, iterations=4):
        """Assign key frames for pose bones."""
        _LOG.enter()

        location_offsets = dict()

        offset_bones = ["root", "left_foot_ik", "right_foot_ik", "left_elbow_ik", "right_elbow_ik", "left_knee_ik", "right_knee_ik"]

        max = 0

        animation = animation_dict["animation_data"]

        for bone_name in offset_bones:

            bone = animation[bone_name]
            bone_location_0 = bone["0"]["location"]["values"]

            for key_frame_idx in bone.keys():
                if int(key_frame_idx) > max:
                    max = int(key_frame_idx)
            bone_location_max = bone[str(max)]["location"]["values"]

            x = bone_location_max[0] - bone_location_0[0]
            y = bone_location_max[1] - bone_location_0[1]
            z = bone_location_max[2] - bone_location_0[2]

            location_offsets[bone_name] = [x, y, z]

        _LOG.dump("location_offsets", location_offsets)

        _LOG.debug("Root offset per iteration", location_offsets["root"])

        iter = 0
        while iter < iterations:
            iter_offsets = dict()
            for bone_name in location_offsets.keys():
                loc = location_offsets[bone_name]
                x = loc[0] * iter
                y = loc[1] * iter
                z = loc[2] * iter
                iter_offsets[bone_name] = [x, y, z]
            skip = None
            if iter > 0:
                skip = [0]
            AnimationService.set_key_frames_from_dict(armature_object, animation_dict, True, True, True, iter*max, iter_offsets, skip)
            iter = iter + 1

    @staticmethod
    def retarget(mocap_rig, target_rig, mocap_type="cmucgspeed"):
        target_type = RigService.identify_rig(target_rig)
        mappings = RETARGET_MAPS[mocap_type][target_type]
        ObjectService.activate_blender_object(target_rig, deselect_all=True)
        target_rig.select_set(True)
        mocap_rig.select_set(True)
        
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        for bonemap in mappings:
            target = RigService.find_pose_bone_by_name(bonemap.target_bone_name, target_rig)
            mocap = RigService.find_pose_bone_by_name(bonemap.mocap_bone_name, mocap_rig)
            constraint = RigService.add_bone_constraint_to_pose_bone(target.name, target_rig, "COPY_ROTATION")
            constraint.target = mocap_rig
            constraint.subtarget = mocap.name
            constraint.target_space = bonemap.mocap_rotation_space
            constraint.owner_space = bonemap.target_rotation_space
            constraint.mix_mode = 'BEFORE'
            
            if bonemap.translation:
                constraint = RigService.add_bone_constraint_to_pose_bone(target.name, target_rig, "COPY_LOCATION")
                constraint.target = mocap_rig
                constraint.subtarget = mocap.name
                constraint.target_space = bonemap.mocap_location_space
                constraint.owner_space = bonemap.target_location_space
                constraint.use_offset = False
            
#===============================================================================
# actposebone.constraints["CopyLoc SMPTarget"].target_space = 'LOCAL'
# actposebone.constraints["CopyLoc SMPTarget"].owner_space = 'LOCAL'
# actposebone.constraints["CopyLoc SMPTarget"].use_offset= True
# 
# bpy.ops.pose.constraint_add_with_targets(type='COPY_ROTATION')
# actposebone.constraints[-1].name = 'CopyRot SMPTarget'
# actposebone.constraints["CopyRot SMPTarget"].target_space = 'LOCAL'
# actposebone.constraints["CopyRot SMPTarget"].owner_space = 'LOCAL'
# actposebone.constraints["CopyRot SMPTarget"].mix_mode = 'BEFORE'
#===============================================================================

#===============================================================================
# 
# class BoneMap:
#     
#     translation = False
#     
#     mocap_bone_name = None
#     mocap_rotation_space = 'LOCAL'
#     mocap_location_space = 'WORLD'
#     
#     target_bone_name = None
#     target_rotation_space = 'LOCAL'
#     target_location_space = 'WORLD'
#         
#     def __init__(self, mocap_bone_name, target_bone_name, *args, **kwargs):
#         
#         self.mocap_bone_name = mocap_bone_name
#         self.target_bone_name = target_bone_name
#         
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#         
#===============================================================================