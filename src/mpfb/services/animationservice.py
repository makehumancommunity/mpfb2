"""Service for working with animations and poses"""

import bpy, os, typing
from typing import Any
from .logservice import LogService
from .rigservice import RigService
from .objectservice import ObjectService
from .systemservice import SystemService

_LOG = LogService.get_logger("services.animationservice")

AnimationDict = dict[str, Any]
"""A serialized animation, as produced by get_key_frames_as_dict() and read back by
set_key_frames_from_dict(). Deliberately an alias rather than a TypedDict: the frame numbers below
"animation_data" are int keys in a dict which comes straight from get_key_frames_as_dict() and str
keys in the same dict once it has been round-tripped through json, and a typed shape would have to
reject one of the two producers in order to describe the other."""

# Note on the legacy action API, referred to from the five sites which read it below.
#
# Action.fcurves and Action.groups are the pre-slotted-action properties. They were deprecated in
# blender 4.4 and removed in blender 5.0, where an action's curves are reached through its layers,
# slots and channelbags instead. The bpy stubs are generated against a 5.x build, so the attributes
# genuinely are absent from the type and the ignores below are not stub noise: every method which
# reads them works on blender 4.2 and 4.3 only. The casts beside the ignores state the element type
# the 4.x runtime yields, so that the loop bodies remain checked.

# Note on animation data, referred to from the same four methods.
#
# Object.animation_data is None for an armature which has never been animated, and
# AnimData.action is None for one whose action has been unlinked. None of the methods below
# guards against either, so they raise AttributeError rather than returning empty in those cases.
# The two casts in each of them record that, rather than asserting a guarantee which does not exist.


class AnimationService:
    """
    The AnimationService class provides a collection of static methods for working with animations and poses in Blender.
    It is not meant to be instantiated, as it only contains static methods.

    The primary purpose of the AnimationService class is to facilitate various operations related to animations and poses,
    such as importing BVH files, manipulating keyframes, making animations cyclic, and calculating bone movements.

    The class relies on other services like LogService, RigService, and ObjectService for logging, rig manipulation,
    and object management, respectively.
    """

    def __init__(self) -> None:
        """Do not instance, there are only static methods in the class"""
        raise RuntimeError("You should not instance AnimationService. Use its static methods instead.")

    @staticmethod
    def import_bvh_file_as_pose(dest_rig: bpy.types.Object, bvh_file_path: str) -> None:
        """Destructively import a bvh file as a pose for the given armature. This will ruin the roll values
           of the bones in the dest_rig.
        """

        if not os.path.exists(bvh_file_path):
            _LOG.error("bvh_file_path does not exist", bvh_file_path)
            raise IOError("BVH file does not exist " + bvh_file_path)

        if not SystemService.check_for_bvh():
            raise RuntimeError(
                "The BVH importer addon is not enabled. "
                "Go to Edit > Preferences > Add-ons and enable 'BVH format'."
            )

        # First, import the bvh file as an armature
        bpy.ops.import_anim.bvh(filepath=bvh_file_path, axis_forward='Y', axis_up='Z', rotate_mode='XYZ')
        # bpy.ops raises RuntimeError rather than returning when an operator fails, so a normal
        # return from the call above means the bvh armature exists and is the active object.
        source_rig = typing.cast(bpy.types.Object, bpy.context.object)
        _LOG.debug("source_rig", source_rig)

        # Put the source armature in edit mode
        ObjectService.activate_blender_object(source_rig, deselect_all=True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Extract all the roll values from the source armature's edit bones
        source_rolls = dict()
        for source_edit_bone in typing.cast(bpy.types.Armature, source_rig.data).edit_bones:
            source_rolls[source_edit_bone.name] = source_edit_bone.roll

        # Finally set the source armature in pose mode
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        # Then activate the destination armature and set it to edit mode
        ObjectService.activate_blender_object(dest_rig, deselect_all=True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Copy all the roll values from the source armature to the destination armature's edit bones'
        for dest_edit_bone in typing.cast(bpy.types.Armature, dest_rig.data).edit_bones:
            if dest_edit_bone.name in source_rolls:
                dest_edit_bone.roll = source_rolls[dest_edit_bone.name]

        # Finally set the destination armature in pose mode
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        # Now rotations will behave the same way as in the source armature, so we can just copy the rotations
        # Object.pose is declared optional, but it is populated for every armature object, and
        # source_rig is one by construction: bpy.ops.import_anim.bvh creates an armature.
        for source_pose_bone in typing.cast(bpy.types.Pose, source_rig.pose).bones:
            dest_pose_bone = RigService.find_pose_bone_by_name(source_pose_bone.name, dest_rig)
            if dest_pose_bone:
                dest_pose_bone.rotation_euler = source_pose_bone.rotation_euler.copy()

                # A suggested solution for compensating for roll values instead of overwriting them
                # (as is done above) is the following. However, this fails for unknown readons. The
                # character ends up in a distorted knot.
                #
                # roll_diff = source_rolls[source_pose_bone.name] - dest_rolls[dest_pose_bone.name]
                # rotation_matrix = source_pose_bone.matrix.to_3x3() @ Matrix.Rotation(roll_diff, 3, 'Y')
                # dest_pose_bone.rotation_euler = rotation_matrix.to_euler()

        # As we're finished, we can delete the source armature
        ObjectService.activate_blender_object(source_rig, deselect_all=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ObjectService.delete_object(source_rig)

        # Finally we can reactivate the destination armature and set it to object mode
        ObjectService.activate_blender_object(dest_rig, deselect_all=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    @staticmethod
    def get_max_keyframe(armature_object: bpy.types.Object | None) -> int | None:
        """
        Get the maximum keyframe number for the given armature object.

        This function scans through all the keyframes in the animation data of the provided armature object
        and returns the highest keyframe number found.

        Args:
            armature_object (bpy.types.Object | None): The armature object to scan for keyframes.

        Returns:
            int | None: The maximum keyframe number, or None if no keyframes are found or if the armature object is None.

        Raises:
            AttributeError: If the armature object has no animation data or no action assigned.
        """
        if not armature_object:
            _LOG.error("armature_object is None")
            return None

        max_keyframe: int | None = None

        # See the note on animation data at the top of this module.
        anim = typing.cast(bpy.types.AnimData, armature_object.animation_data)
        _LOG.debug("animation_data", anim)

        action = typing.cast(bpy.types.Action, anim.action)
        _LOG.debug("action", action)
        _LOG.debug("action frame range", action.frame_range)

        # See the note on the legacy action API at the top of this module.
        fcurves = typing.cast("bpy.types.bpy_prop_collection[bpy.types.FCurve]", action.fcurves)  # pyright: ignore[reportAttributeAccessIssue]
        for fcurve in fcurves:
            for keyframe in fcurve.keyframe_points:
                if not max_keyframe or (keyframe and keyframe.co and keyframe.co[0] and keyframe.co[0] > max_keyframe):
                    max_keyframe = int(keyframe.co[0])
                    _LOG.debug("max_keyframe", (max_keyframe, fcurve.data_path))

        if max_keyframe is None:
            return None

        return max_keyframe

    @staticmethod
    def make_cyclic(armature_object: bpy.types.Object, bone_with_offset: str | None = None) -> None:
        """Make an animation cyclic by adding a modifier to each fcurve. Optionally add offset parameter to one bone.

        Raises:
            AttributeError: If the armature object has no animation data or no action assigned.
        """

        # See the note on animation data at the top of this module.
        anim = typing.cast(bpy.types.AnimData, armature_object.animation_data)
        _LOG.debug("animation_data", anim)

        action = typing.cast(bpy.types.Action, anim.action)
        _LOG.debug("action", action)

        # See the note on the legacy action API at the top of this module.
        fcurves = typing.cast("bpy.types.bpy_prop_collection[bpy.types.FCurve]", action.fcurves)  # pyright: ignore[reportAttributeAccessIssue]
        for fcurve in fcurves:
            _LOG.debug("fcurve", (fcurve.group, fcurve.data_path))
            # FModifiers.new() returns the FModifier base class, and mode_after is declared on the
            # FModifierCycles subclass which the 'CYCLES' type argument selects.
            modifier = typing.cast(bpy.types.FModifierCycles, fcurve.modifiers.new(type='CYCLES'))
            if bone_with_offset and (bone_with_offset in str(fcurve) or bone_with_offset in str(fcurve.group)):
                modifier.mode_after = 'REPEAT_OFFSET'

    @staticmethod
    def get_bone_movement_distance(armature_object: bpy.types.Object, bone_name: str, start_keyframe: int, end_keyframe: int) -> list[float]:
        """
        Calculate the movement distance of a bone between two keyframes.

        This function sets the scene to the specified start and end keyframes, retrieves the bone's location
        at each keyframe, and calculates the difference in location.

        Args:
            armature_object (bpy.types.Object): The armature object containing the bone.
            bone_name (str): The name of the bone to measure movement for.
            start_keyframe (int): The starting keyframe number.
            end_keyframe (int): The ending keyframe number.

        Returns:
            list[float]: A list containing the movement distance [dx, dy, dz] of the bone between the two keyframes.
            A missing bone is logged as an error and leaves that end of the measurement at the origin
            rather than aborting, so the result is then a distance to or from [0.0, 0.0, 0.0].
        """
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
    def move_bone_for_all_keyframes(armature_object: bpy.types.Object | None, bone_name: str, distance: list[float],
                                    start_keyframe: int, end_keyframe: int) -> None:
        """
        Move a bone by a specified distance for all keyframes within a given range.

        This function iterates through each keyframe in the specified range, moves the bone by the given distance,
        and inserts a new keyframe with the updated location.

        Args:
            armature_object (bpy.types.Object | None): The armature object containing the bone. A None is logged and ignored.
            bone_name (str): The name of the bone to move.
            distance (list[float]): A list containing the distance [dx, dy, dz] to move the bone.
            start_keyframe (int): The starting keyframe number.
            end_keyframe (int): The ending keyframe number.
        """
        if not armature_object:
            _LOG.error("armature_object is None")
            return

        scene = bpy.context.scene

        for keyframe in range(start_keyframe, end_keyframe + 1):
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
    def duplicate_keyframes(armature_object: bpy.types.Object | None, start_duplicate_at: int, first_keyframe: int, last_keyframe: int) -> None:
        """
        Duplicate a range of keyframes to a new position in the timeline.

        This function iterates over each frame in the source range and calls duplicate_keyframe to copy
        it to the matching frame in the destination range.

        Args:
            armature_object (bpy.types.Object | None): The armature object with animation data. A None is logged and ignored.
            start_duplicate_at (int): The frame number where the duplicated range should begin.
            first_keyframe (int): The first frame of the source range.
            last_keyframe (int): The last frame of the source range, inclusive.
        """
        if not armature_object:
            _LOG.error("armature_object is None")
            return

        for source_keyframe in range(first_keyframe, last_keyframe + 1):
            target_keyframe = start_duplicate_at + source_keyframe - first_keyframe
            _LOG.debug("Duplicating keyframe", (source_keyframe, target_keyframe))
            AnimationService.duplicate_keyframe(armature_object, source_keyframe, target_keyframe)

    @staticmethod
    def duplicate_keyframe(armature_object: bpy.types.Object | None, source_keyframe: int, target_keyframe: int) -> None:
        """Duplicates a keyframe to another position in the timeline, for every fcurve in the action.

        Args:
            armature_object (bpy.types.Object | None): Armature object holding the keyframe. A None is logged and ignored.
            source_keyframe (int): Frame number to duplicate. A 0 is logged and ignored, since the guard tests it for truth.
            target_keyframe (int): Frame number to duplicate it to. A 0 is logged and ignored, for the same reason.

        Raises:
            AttributeError: If the armature object has no animation data or no action assigned.
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

        # See the note on animation data at the top of this module.
        anim = typing.cast(bpy.types.AnimData, armature_object.animation_data)
        _LOG.dump("animation_data", anim)

        action = typing.cast(bpy.types.Action, anim.action)
        _LOG.dump("action", action)
        _LOG.dump("action frame range", action.frame_range)

        # See the note on the legacy action API at the top of this module.
        fcurves = typing.cast("bpy.types.bpy_prop_collection[bpy.types.FCurve]", action.fcurves)  # pyright: ignore[reportAttributeAccessIssue]
        for fcurve in fcurves:
            if source_keyframe > len(fcurve.keyframe_points) - 1 or not fcurve.keyframe_points[source_keyframe]:
                continue

            # TODO: co.y and position in keyframe_points isn't necessarily the same.
            #       The following line should be expanded to check this and take measures
            #       if co.y does not match the intended keyframe.
            old_keyframe = fcurve.keyframe_points[source_keyframe - 1]

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
    def get_key_frames_as_dict(armature_object: bpy.types.Object) -> AnimationDict:
        """Scan through all key frames set for pose bones and return a dict with all info.

        Raises:
            AttributeError: If the armature object has no animation data or no action assigned.
        """
        _LOG.enter()

        # See the note on animation data at the top of this module.
        anim = typing.cast(bpy.types.AnimData, armature_object.animation_data)
        _LOG.debug("animation_data", anim)

        action = typing.cast(bpy.types.Action, anim.action)
        _LOG.debug("action", action)
        _LOG.debug("action frame range", action.frame_range)

        # See the note on the legacy action API at the top of this module.
        groups = typing.cast("bpy.types.bpy_prop_collection[bpy.types.ActionGroup]", action.groups)  # pyright: ignore[reportAttributeAccessIssue]
        for group in groups:
            _LOG.dump("Action group ", group)

        full_dict: AnimationDict = dict()
        full_dict["animation_data"] = dict()
        animation_data = full_dict["animation_data"]

        full_dict["metadata"] = dict()
        meta = full_dict["metadata"]
        meta["rig"] = RigService.identify_rig(armature_object)

        # See the note on the legacy action API at the top of this module.
        fcurves = typing.cast("bpy.types.bpy_prop_collection[bpy.types.FCurve]", action.fcurves)  # pyright: ignore[reportAttributeAccessIssue]
        for fcurve in fcurves:
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

                # _LOG.debug("metadata", (curve_idx, len(fdata[curve_type]["metadata"]), fdata[curve_type]["metadata"]))

                fdata[curve_type]["values"][curve_idx] = result

                metadata["interpolation"] = str(keyframe.interpolation)
                # mathutils.Vector declares __getitem__ and __len__ but not __iter__, so it does not
                # satisfy Iterable although list() consumes it happily at runtime.
                metadata["handle_left"] = list(keyframe.handle_left)  # pyright: ignore[reportArgumentType]
                metadata["handle_right"] = list(keyframe.handle_right)  # pyright: ignore[reportArgumentType]
                metadata["handle_left_type"] = str(keyframe.handle_left_type)
                metadata["handle_right_type"] = str(keyframe.handle_right_type)

        return full_dict

    @staticmethod
    def set_key_frames_from_dict(armature_object: bpy.types.Object, animation_dict: AnimationDict,
                                 frame_offset: int = 0, skip_first_frame: bool = False) -> None:
        """Assign key frames for pose bones.

        Note that the whole per-frame body sits behind a "skip_first_frame" test, so with the default
        False nothing is assigned at all. See the reference documentation for this service.

        Raises:
            ValueError: If the animation dict names a bone which the armature does not have.
        """
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
