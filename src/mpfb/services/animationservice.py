"""Service for working with animations."""

import bpy, os
from mathutils import Matrix, Vector
from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService
from mpfb.services.mathservice import MathService
from .objectservice import ObjectService
from bpy.types import PoseBone
from mathutils import Vector
from mpfb.entities.retarget import RETARGET_INFO

_LOG = LogService.get_logger("services.animationservice")
_LOG.set_level(LogService.DEBUG)

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
    def _calculate_axis_contribution(rig, pose_bone, axis, target_head_location, shift_dist=0.001):
        # There is most likely a mathematic way to solve this with matrices etc. This approach ignores
        # all differences in rotation orders, coordinate systems etc and instead figures out a direction
        # by giving it a try, seeing what happens, and acting from there
        orig_loc = rig.matrix_world @ pose_bone.head
        original_distance = MathService.vector_distance(orig_loc, target_head_location)

        _LOG.debug("\n\n\nAXIS\n\n\n", axis)

        _LOG.debug("world space target location", target_head_location)

        _LOG.debug("original pose bone location", pose_bone.location)
        _LOG.debug("original pose bone head pose space", pose_bone.head)
        _LOG.debug("original pose bone head world space", orig_loc)
        _LOG.debug("original distance", original_distance)

        if MathService.vector_equals(orig_loc, target_head_location):
            return 0.0

        _LOG.debug("shift dist", shift_dist)

        pose_bone.location[axis] = pose_bone.location[axis] + shift_dist
        bpy.context.view_layer.update()

        shifted_loc = rig.matrix_world @ pose_bone.head
        shifted_distance = MathService.vector_distance(shifted_loc, target_head_location)

        _LOG.debug("shifted pose bone location", pose_bone.location)
        _LOG.debug("shifted pose bone head pose space", pose_bone.head)
        _LOG.debug("shifted pose bone head world space", shifted_loc)
        _LOG.debug("shifted distance", shifted_distance)

        dist_improvement = original_distance - shifted_distance
        _LOG.debug("distance improvement", dist_improvement)

        pose_bone.location[axis] = pose_bone.location[axis] - shift_dist
        bpy.context.view_layer.update()

        return dist_improvement

    @staticmethod
    def _shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_pose_bone, mpfb_pose_bone, use_mocap_tail=False, use_mpfb_tail=False):
        bone_location_before_shift = mpfb_pose_bone.location.copy()

        mocap_bone_location = mocap_rig.matrix_world @ mocap_pose_bone.head
        mpfb_bone_location = mpfb_rig.matrix_world @ mpfb_pose_bone.head

        _LOG.debug("Shifting bone, from, to", (mocap_pose_bone, mpfb_bone_location, mocap_bone_location))
        _LOG.debug("mocap_bone_location", mocap_bone_location)
        _LOG.debug("mpfb_bone_location", mocap_bone_location)

        xcontr = AnimationService._calculate_axis_contribution(mpfb_rig, mpfb_pose_bone, 0, mocap_bone_location)
        ycontr = AnimationService._calculate_axis_contribution(mpfb_rig, mpfb_pose_bone, 1, mocap_bone_location)
        zcontr = AnimationService._calculate_axis_contribution(mpfb_rig, mpfb_pose_bone, 2, mocap_bone_location)

        _LOG.dump("\n\n\naxes contributions\n\n\n", (xcontr, ycontr, zcontr))

        contr = abs(xcontr) + abs(ycontr) + abs(zcontr)

        _LOG.dump("total contribution", contr)

        original_dist = MathService.vector_distance(mocap_bone_location, mpfb_bone_location)

        shift_vector = [
            xcontr / contr * original_dist,
            ycontr / contr * original_dist,
            zcontr / contr * original_dist
            ]

        _LOG.dump("shift_vector", shift_vector)

        for i in range(3):
            mpfb_pose_bone.location[i] = mpfb_pose_bone.location[i] + shift_vector[i]

        bpy.context.view_layer.update()

        shifted_mpfb_bone_location = mpfb_rig.matrix_world @ mpfb_pose_bone.head
        shifted_dist = MathService.vector_distance(mocap_bone_location, shifted_mpfb_bone_location)

        _LOG.debug("shifted vs original mpfb_bone_location", (shifted_mpfb_bone_location, mpfb_bone_location))
        _LOG.debug("shifted vs original dist", (shifted_dist, original_dist))

        distance_covered_fraction = (original_dist - shifted_dist) / original_dist

        _LOG.dump("distance_covered_fraction", distance_covered_fraction)

        shift_vector = [
            (xcontr / contr * original_dist) / distance_covered_fraction,
            (ycontr / contr * original_dist) / distance_covered_fraction,
            (zcontr / contr * original_dist) / distance_covered_fraction
            ]

        _LOG.dump("adjusted shift_vector", shift_vector)

        for i in range(3):
            mpfb_pose_bone.location[i] = bone_location_before_shift[i] + shift_vector[i]

        bpy.context.view_layer.update()

        shifted_mpfb_bone_location = mpfb_rig.matrix_world @ mpfb_pose_bone.head
        shifted_dist = MathService.vector_distance(mocap_bone_location, mpfb_bone_location)

        _LOG.debug("final shifted_mpfb_bone_location", mocap_bone_location)
        _LOG.debug("final shifted_dist", shifted_dist)

    @staticmethod
    def retarget(mocap_rig, mpfb_rig, mocap_type="cmucgspeed"):
        mpfb_type = RigService.identify_rig(mpfb_rig)
        ObjectService.activate_blender_object(mpfb_rig, deselect_all=True)
        mpfb_rig.select_set(True)
        mocap_rig.select_set(True)

        mpfb_info = RETARGET_INFO[mpfb_type]
        mocap_info = RETARGET_INFO[mocap_type]

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        mocap_pose_root = RigService.find_pose_bone_by_name(mocap_info.get_root_bone(), mocap_rig)
        mpfb_pose_root = RigService.find_pose_bone_by_name(mpfb_info.get_root_bone(), mpfb_rig)
        AnimationService._shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_pose_root, mpfb_pose_root)

        mocap_left_hand = RigService.find_pose_bone_by_name(mocap_info.get_left_hand_bone(), mocap_rig)
        mpfb_left_hand = RigService.find_pose_bone_by_name(mpfb_info.get_left_hand_bone(), mpfb_rig)
        AnimationService._shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_left_hand, mpfb_left_hand)

        mocap_right_hand = RigService.find_pose_bone_by_name(mocap_info.get_right_hand_bone(), mocap_rig)
        mpfb_right_hand = RigService.find_pose_bone_by_name(mpfb_info.get_right_hand_bone(), mpfb_rig)
        AnimationService._shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_right_hand, mpfb_right_hand)

        mocap_left_foot = RigService.find_pose_bone_by_name(mocap_info.get_left_foot_bone(), mocap_rig)
        mpfb_left_foot = RigService.find_pose_bone_by_name(mpfb_info.get_left_foot_bone(), mpfb_rig)
        AnimationService._shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_left_foot, mpfb_left_foot)

        mocap_right_foot = RigService.find_pose_bone_by_name(mocap_info.get_right_foot_bone(), mocap_rig)
        mpfb_right_foot = RigService.find_pose_bone_by_name(mpfb_info.get_right_foot_bone(), mpfb_rig)
        AnimationService._shift_mpfb_bone_towards_mocap(mocap_rig, mpfb_rig, mocap_right_foot, mpfb_right_foot)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


