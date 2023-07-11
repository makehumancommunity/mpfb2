"""Service for working with animations."""

import bpy, os
from mathutils import Matrix, Vector
from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.rigservice import RigService
from .objectservice import ObjectService
from bpy.types import PoseBone
from mathutils import Vector

_LOG = LogService.get_logger("services.animationservice")

class AnimationService:
    """Service with utility functions for working with animations. It only has static methods, so you don't
    need to instance it."""

    def __init__(self):
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance AnimationService. Use its static methods instead.")

    @staticmethod
    def get_max_keyframe(armature_object):
        if not armature_object:
            _LOG.error("armature_object is None")
            return None

        max_keyframe = None

        anim = armature_object.animation_data
        _LOG.debug("animation_data", anim)

        action = anim.action
        _LOG.debug("action", action)
        _LOG.debug("action frame range", action.frame_range)

        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                if not max_keyframe or (keyframe and keyframe.co and keyframe.co[0] and keyframe.co[0] > max_keyframe):
                    max_keyframe = int(keyframe.co[0])
                    _LOG.debug("max_keyframe", (max_keyframe, fcurve.data_path))

        if max_keyframe is None:
            return None

        return max_keyframe

    @staticmethod
    def get_bone_movement_distance(armature_object, bone_name, start_keyframe, end_keyframe):
        start_loc = [0.0, 0.0, 0.0]
        end_loc = [0.0, 0.0, 0.0]

        scene = bpy.context.scene

        scene.frame_set(start_keyframe)
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        if not bone:
            _LOG.error("Could not find bone", bone_name)
        else:
            start_loc = bone.location.copy()

        scene.frame_set(end_keyframe)
        bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        if not bone:
            _LOG.error("Could not find bone", bone_name)
        else:
            end_loc = bone.location.copy()

        _LOG.debug("start, end", (start_loc, end_loc))

        return [end_loc[0] - start_loc[0], end_loc[1] - start_loc[1], end_loc[2] - start_loc[2]]

    @staticmethod
    def move_bone_for_all_keyframes(armature_object, bone_name, distance, start_keyframe, end_keyframe):
        if not armature_object:
            _LOG.error("armature_object is None")
            return

        scene = bpy.context.scene

        for keyframe in range(start_keyframe, end_keyframe+1):
            scene.frame_set(keyframe)
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            if not bone:
                _LOG.error("Could not find bone", bone_name)
                return
            target = [bone.location[0] + distance[0], bone.location[1] + distance[1], bone.location[2] + distance[2]]
            _LOG.debug("moving bone. Frame, from, to", (keyframe, bone.location, target))
            bone.location = target
            bone.keyframe_insert(data_path="location", frame=keyframe)

    @staticmethod
    def duplicate_keyframes(armature_object, start_duplicate_at, first_keyframe, last_keyframe):
        if not armature_object:
            _LOG.error("armature_object is None")
            return

        for source_keyframe in range(first_keyframe, last_keyframe+1):
            target_keyframe = start_duplicate_at + source_keyframe - first_keyframe
            _LOG.debug("Duplicating keyframe", (source_keyframe, target_keyframe))
            AnimationService.duplicate_keyframe(armature_object, source_keyframe, target_keyframe)

    @staticmethod
    def duplicate_keyframe(armature_object, source_keyframe, target_keyframe):
        """Duplicates a keyframe from one armature object to another.

        Args:
            armature_object (bpy.types.Object): Armature object to duplicate the keyframe from.
            source_keyframe (bpy.types.PoseBone): Keyframe to duplicate.
            target_keyframe (bpy.types.PoseBone): Keyframe to duplicate the keyframe to.
        """
        if not armature_object:
            _LOG.error("armature_object is None")
            return
        if not source_keyframe:
            _LOG.error("source_keyframe is None")
            return
        if not target_keyframe:
            _LOG.error("target_keyframe is None")
            return

        anim = armature_object.animation_data
        _LOG.dump("animation_data", anim)

        action = anim.action
        _LOG.dump("action", action)
        _LOG.dump("action frame range", action.frame_range)

        for fcurve in action.fcurves:
            if source_keyframe > len(fcurve.keyframe_points) - 1 or not fcurve.keyframe_points[source_keyframe]:
                continue

            # TODO: co.y and position in keyframe_points isn't necessarily the same.
            #       The following line should be expanded to check this and take measures
            #       if co.y does not match the intended keyframe.
            old_keyframe = fcurve.keyframe_points[source_keyframe-1]

            new_keyframe = fcurve.keyframe_points.insert(target_keyframe, old_keyframe.co.y)
            new_keyframe.amplitude = old_keyframe.amplitude
            new_keyframe.interpolation = old_keyframe.interpolation
            new_keyframe.handle_left = old_keyframe.handle_left
            new_keyframe.handle_right = old_keyframe.handle_right
            new_keyframe.handle_left_type = old_keyframe.handle_left_type
            new_keyframe.handle_right_type = old_keyframe.handle_right_type
            new_keyframe.period = old_keyframe.period
            new_keyframe.easing = old_keyframe.easing
            new_keyframe.back = old_keyframe.back


    @staticmethod
    def get_key_frames_as_dict(armature_object):
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

        for fcurve in action.fcurves:
            _LOG.debug("fcurve, data_path", (fcurve, fcurve.data_path))
            curve_name = fcurve.data_path
            if "\"" in curve_name:
                curve_name = str(fcurve.data_path).split("\"")[1]

            if curve_name not in animation_data:
                animation_data[curve_name] = dict()

            pdata = animation_data[curve_name]
            curve_type = str(fcurve.data_path).split(".")[-1]
            curve_idx = int(fcurve.array_index)

            _LOG.debug("name, type, idx", (curve_name, curve_type, curve_idx))

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

                if curve_idx > len(fdata[curve_type]["metadata"]) - 1:
                    fdata[curve_type]["metadata"].append(dict())

                if curve_idx > len(fdata[curve_type]["values"]) - 1:
                    fdata[curve_type]["values"].append(0.0)

                metadata = fdata[curve_type]["metadata"][curve_idx]

                #_LOG.debug("metadata", (curve_idx, len(fdata[curve_type]["metadata"]), fdata[curve_type]["metadata"]))

                fdata[curve_type]["values"][curve_idx] = result

                metadata["interpolation"] = str(keyframe.interpolation)
                metadata["handle_left"] = list(keyframe.handle_left)
                metadata["handle_right"] = list(keyframe.handle_right)
                metadata["handle_left_type"] = str(keyframe.handle_left_type)
                metadata["handle_right_type"] = str(keyframe.handle_right_type)

        return full_dict

    @staticmethod
    def set_key_frames_from_dict(armature_object, animation_dict, start_at_frame=0, skip_first_frame=False):
        """Assign key frames for pose bones."""
        _LOG.enter()

        animation = animation_dict["animation_data"]

        for bone_name in animation.keys():
            pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            if not pose_bone:
                _LOG.error("Pose bone does not exist", pose_bone)
                raise ValueError('Tried to assign transform to non-existing bone ' + bone_name)
            bone_animation = animation[bone_name]
            is_first = True
            for key_frame_str in bone_animation.keys():
                key_frame_idx = int(key_frame_str)
                if is_first and skip_first_frame:
                    key_frame = bone_animation[key_frame_str]

                    key_frame_idx = key_frame_idx + frame_offset

                    if "rotation_euler" in key_frame:
                        pose_bone.rotation_euler = key_frame["rotation_euler"]["values"]
                        pose_bone.keyframe_insert(data_path="rotation_euler", frame=key_frame_idx)
                        _LOG.dump("Setting rotation euler", (bone_name, key_frame_idx, key_frame["rotation_euler"]["values"]))

                    if "rotation_quaternion" in key_frame:
                        pose_bone.rotation_quaternion = key_frame["rotation_quaternion"]["values"]
                        pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=key_frame_idx)
                        _LOG.dump("Setting rotation quaternion", (bone_name, key_frame_idx, key_frame["rotation_quaternion"]["values"]))

                    def fmt(val):
                        return "{:.4f}".format(val)

                    if "location" in key_frame:
                        loc = list(key_frame["location"]["values"])
                        #=======================================================
                        # if bone_location_offsets and bone_name in bone_location_offsets:
                        #     trans = bone_location_offsets[bone_name]
                        #     loc[0] = loc[0] + trans[0]
                        #     loc[1] = loc[1] + trans[1]
                        #     loc[2] = loc[2] + trans[2]
                        #=======================================================

                        pose_bone.location = loc
                        pose_bone.keyframe_insert(data_path="location", frame=key_frame_idx)
                        _LOG.dump("Setting location", (bone_name, key_frame_idx, loc))
