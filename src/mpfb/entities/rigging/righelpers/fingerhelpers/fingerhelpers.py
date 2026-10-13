"""This module provides functionality for adding helpers to fingers."""

import bpy, typing

from .....services import LogService
_LOG = LogService.get_logger("fingerhelpers.fingerhelpers")

from .....services import RigService
from .....types import BoneOrientationInfo, RigHelperSettings
from .....ui.rigging.standardrig import RigHelpersProperties
from ..abstractrighelper import AbstractRigHelper

# The helpers are only reachable from operators which poll for an active armature, so every
# armature_object.data read below is narrowed with a cast rather than an isinstance guard.
#
# The same applies to the RigService bone finders, which return an optional because the blender
# collections they read do. Every lookup below either names a helper bone this class created a few
# lines earlier or a bone of the rig the concrete subclass was selected for, so the casts record a
# contract the caller is expected to satisfy rather than a guarantee pyright can check.
#
# PoseBone.lock_location and lock_scale are bpy_prop_array, which the stubs declare without
# __setitem__ although both are assignable per element at runtime; hence the narrow ignores.


class FingerHelpers(AbstractRigHelper):

    """This is the abstract rig type independent base class for working with
    helpers for fingers. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, which_hand: str, settings: RigHelperSettings) -> None:
        """Get a new instance of FingerHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing FingerHelpers object")
        self.which_hand = which_hand
        self.settings = settings
        self._bone_info: BoneOrientationInfo = dict()
        _LOG.dump("settings", self.settings)

    # ---- METHODS FOR APPLYING AND CREATING

    def apply_ik(self, armature_object: bpy.types.Object) -> None:
        """Add rig helpers for fingers based on the settings that were provided
        when constructing the class."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        if self.settings["finger_helpers_type"] == "GRIP":
            self._apply_individual_grip(armature_object)

        if self.settings["finger_helpers_type"] == "MASTER":
            self._apply_master_grip(armature_object, assume_individual_grip=False)

        if self.settings["finger_helpers_type"] == "GRIP_AND_MASTER":
            self._apply_individual_grip(armature_object)
            self._apply_master_grip(armature_object, assume_individual_grip=True)

        if self.settings["finger_helpers_type"] == "POINT":
            self._apply_point(armature_object)


    def _apply_master_without_individual_for_finger(self, armature_object: bpy.types.Object, finger_number: int) -> None:
        master_name = self._get_master_grip_bone_name()

        finger_segments = self.get_reverse_list_of_bones_in_finger(finger_number)

        for bone_name in finger_segments:
            constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object, copy_y=False, copy_z=False)
            constraint.influence = 1.0 / len(finger_segments)

        bone_name = finger_segments[-1]

        constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object, copy_x=False)

        if self.settings["hide_fk"]:
            self._hide_bones(armature_object, finger_segments)

    def _apply_master_with_individual_for_finger(self, armature_object: bpy.types.Object, finger_number: int) -> None:
        master_name = self._get_master_grip_bone_name()
        bone_name = self._get_grip_bone_name_for_finger(finger_number)

        constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object)
        constraint.name = 'Add rotation'
        constraint.mix_mode = 'ADD'

    def _apply_master_grip(self, armature_object: bpy.types.Object, assume_individual_grip: bool=False) -> None:
        _LOG.enter()
        self._create_master_grip_bone(armature_object)

        for finger_number in [1, 2, 3, 4, 5]:
            if assume_individual_grip:
                self._apply_master_with_individual_for_finger(armature_object, finger_number)
            else:
                self._apply_master_without_individual_for_finger(armature_object, finger_number)

    def _apply_individual_grip(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        for finger_number in [1, 2, 3, 4, 5]:
            self._create_grip_bone(finger_number, armature_object)
            grip_name = self._get_grip_bone_name_for_finger(finger_number)

            self.edit_mode()

            parent_name = self.get_immediate_parent_name_of_finger(finger_number)
            parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

            grip_bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(grip_name, armature_object))
            grip_bone.parent = parent_bone

            self.pose_mode()

            finger_segments = self.get_reverse_list_of_bones_in_finger(finger_number)

            for bone_name in finger_segments:
                constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, grip_name, armature_object, copy_y=False, copy_z=False)
                constraint.influence = 1.0 / len(finger_segments)

            bone_name = finger_segments[-1]

            constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, grip_name, armature_object, copy_x=False)

            if self.settings["hide_fk"]:
                self._hide_bones(armature_object, finger_segments)

    def _apply_point(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            self._create_point_ik_bone(finger_number, armature_object)
            ik_name = self._get_point_ik_bone_name_for_finger(finger_number)

            self.edit_mode()

            parent_name = self.get_immediate_parent_name_of_finger(finger_number)
            parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

            ik_bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(ik_name, armature_object))
            ik_bone.parent = parent_bone

            chain_length = self.get_finger_segment_count(finger_number)
            self._set_finger_ik_target(finger_number, armature_object, chain_length)
            if self.settings["hide_fk"]:
                bones_to_hide = self.get_reverse_list_of_bones_in_finger(finger_number)
                self._hide_bones(armature_object, bones_to_hide)

    def _set_finger_ik_target(self, finger_number: int, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        tip_name = self.get_last_segment_name_of_finger(finger_number)
        ik_name = self._get_point_ik_bone_name_for_finger(finger_number)
        ik_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(ik_name, armature_object))
        self.add_finger_rotation_constraints(finger_number, armature_object)
        RigService.add_ik_constraint_to_pose_bone(tip_name, armature_object, ik_bone, chain_length)

    def _create_point_ik_bone(self, finger_number: int, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        self.edit_mode()

        tip_name = self.get_last_segment_name_of_finger(finger_number)

        head = self._bone_info["pose_bones"][tip_name]["head"]
        tail = self._bone_info["pose_bones"][tip_name]["tail"]
        roll = self._bone_info["edit_bones"][tip_name]["roll"]

        length = tail - head
        tail = tail + length
        head = head + length

        bone_name = self._get_point_ik_bone_name_for_finger(finger_number)
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, bone_name, empty_type="SPHERE")
        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(bone_name, armature_object))

        scales = [0.5, 0.5, 0.5, 0.5, 0.7]

        scale = scales[finger_number - 1]
        if hasattr(pose_bone, "custom_shape_scale"):
            # Removed from PoseBone before the oldest supported blender: absent from the RNA on both
            # 4.2.1 and 5.1, so the hasattr guard makes this branch unreachable there.
            pose_bone.custom_shape_scale = scale  # pyright: ignore[reportAttributeAccessIssue]
            _LOG.debug("scale", pose_bone.custom_shape_scale)  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)

    def _create_grip_bone(self, finger_number: int, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        self.edit_mode()

        tip_name = self.get_last_segment_name_of_finger(finger_number)
        root_name = self.get_first_segment_name_of_finger(finger_number)

        head = self._bone_info["edit_bones"][root_name]["head"]
        tail = self._bone_info["edit_bones"][tip_name]["tail"]
        roll = self._bone_info["edit_bones"][root_name]["roll"]

        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        self.pose_mode()

        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(bone_name, armature_object))

        root_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(root_name, armature_object))

        pose_bone.location = root_bone.location

        RigService.display_pose_bone_as_empty(armature_object, bone_name, 'CIRCLE')

        scales = [0.1, 0.15, 0.1, 0.1, 0.2]

        scale = scales[finger_number - 1]
        if hasattr(pose_bone, "custom_shape_scale"):
            # Removed from PoseBone before the oldest supported blender: absent from the RNA on both
            # 4.2.1 and 5.1, so the hasattr guard makes this branch unreachable there.
            pose_bone.custom_shape_scale = scale  # pyright: ignore[reportAttributeAccessIssue]
            _LOG.debug("scale", pose_bone.custom_shape_scale)  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)

        for i in range(3):
            pose_bone.lock_location[i] = True  # pyright: ignore[reportIndexIssue]
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _create_master_grip_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        self.edit_mode()

        finger3_tip_name = self.get_last_segment_name_of_finger(3)
        finger4_tip_name = self.get_last_segment_name_of_finger(4)

        finger3_root_name = self.get_first_segment_name_of_finger(3)
        finger4_root_name = self.get_first_segment_name_of_finger(4)

        roll = self._bone_info["edit_bones"][finger3_root_name]["roll"]

        finger3_head = self._bone_info["edit_bones"][finger3_root_name]["head"]
        finger3_tail = self._bone_info["edit_bones"][finger3_tip_name]["tail"]

        finger4_head = self._bone_info["edit_bones"][finger4_root_name]["head"]
        finger4_tail = self._bone_info["edit_bones"][finger4_tip_name]["tail"]

        head = (finger3_head + finger4_head) / 2
        tail = (finger3_tail + finger4_tail) / 2

        bone_name = self._get_master_grip_bone_name()
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        parent_name = self.get_immediate_parent_name_of_finger(3)
        parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

        bone.parent = parent_bone

        self.pose_mode()

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(bone_name, armature_object))

        root_bone3 = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(finger3_root_name, armature_object))
        root_bone4 = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(finger4_root_name, armature_object))

        pose_bone.location = (root_bone3.location + root_bone4.location) / 2

        RigService.display_pose_bone_as_empty(armature_object, bone_name, 'CIRCLE')

        scale = 0.6
        if hasattr(pose_bone, "custom_shape_scale"):
            # Removed from PoseBone before the oldest supported blender: absent from the RNA on both
            # 4.2.1 and 5.1, so the hasattr guard makes this branch unreachable there.
            pose_bone.custom_shape_scale = scale  # pyright: ignore[reportAttributeAccessIssue]
            _LOG.debug("scale", pose_bone.custom_shape_scale)  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)

        for i in range(3):
            pose_bone.lock_location[i] = True  # pyright: ignore[reportIndexIssue]
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    # ---- METHODS FOR REMOVING AND RESETTING

    def remove_ik(self, armature_object: bpy.types.Object) -> None:
        """Remove rig helpers for fingers based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        mode = str(RigHelpersProperties.get_value("finger_mode", entity_reference=armature_object)).strip()

        _LOG.debug("mode is", mode)

        if mode in ["GRIP", "MASTER", "GRIP_AND_MASTER"]:
            self._clear_all_finger_constraints(armature_object)
            self._remove_grip(armature_object)
            if mode in ["MASTER", "GRIP_AND_MASTER"]:
                self._clear_master_grip(armature_object)

        if mode == "POINT":
            self._clear_all_finger_constraints(armature_object)
            self._remove_point(armature_object)

        _LOG.debug("Done")

    def _clear_finger_grip(self, finger_number: int, armature_object: bpy.types.Object) -> None:
        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        self.edit_mode()
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Grip bone to remove, if any", bone)
        if bone:
            typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

    def _clear_master_grip(self, armature_object: bpy.types.Object) -> None:
        bone_name = self._get_master_grip_bone_name()
        self.edit_mode()
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Master grip bone to remove, if any", bone)
        if bone:
            typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

    def _clear_finger_ik(self, finger_number: int, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        bone_name = self._get_point_ik_bone_name_for_finger(finger_number)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Point bone to remove, if any", bone)
        if bone:
            typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

    def _clear_all_finger_constraints(self, armature_object: bpy.types.Object) -> None:
        self.pose_mode()
        for finger_number in [1, 2, 3, 4, 5]:
            bones_to_clear = self.get_reverse_list_of_bones_in_finger(finger_number)
            for bone_name in bones_to_clear:
                RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

    def _remove_grip(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            self.object_mode()
            self._clear_finger_grip(finger_number, armature_object)
            self.object_mode()
            bones_to_show = self.get_reverse_list_of_bones_in_finger(finger_number)
            self._show_bones(armature_object, bones_to_show)

    def _remove_point(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            self.object_mode()
            self._clear_finger_ik(finger_number, armature_object)
            self.object_mode()
            bones_to_show = self.get_reverse_list_of_bones_in_finger(finger_number)
            self._show_bones(armature_object, bones_to_show)

    # ---- BONE NAMES

    def _get_point_ik_bone_name_for_finger(self, finger_number: int) -> str:
        return self.which_hand + "_finger" + str(finger_number) + "_point_ik"

    def _get_grip_bone_name_for_finger(self, finger_number: int) -> str:
        return self.which_hand + "_finger" + str(finger_number) + "_grip"

    def _get_master_grip_bone_name(self) -> str:
        return self.which_hand + "_master_grip"

    def _get_master_ik_bone_name(self) -> str:
        return self.which_hand + "_finger_master_ik"

    # ---- GENERAL METHODS

    def _hide_bones(self, armature_object: bpy.types.Object, bone_list: list[str]) -> None:
        _LOG.enter()
        bones = typing.cast(bpy.types.Armature, armature_object.data).bones
        for name in bone_list:
            _LOG.debug("Will attempt to hide bone", name)
            # The names come from the rig specific get_reverse_list_of_bones_in_finger(), so they
            # are bones of the rig the calling operator has already identified.
            bone = typing.cast(bpy.types.Bone, bones.get(name))
            bone.hide = True

    def _show_bones(self, armature_object: bpy.types.Object, bone_list: list[str]) -> None:
        _LOG.enter()
        bones = typing.cast(bpy.types.Armature, armature_object.data).bones
        for name in bone_list:
            _LOG.debug("Will attempt to show bone", name)
            # See _hide_bones() above for why the lookup result is cast rather than guarded.
            bone = typing.cast(bpy.types.Bone, bones.get(name))
            bone.hide = False

    @staticmethod
    def get_instance(which_hand: str, settings: RigHelperSettings, rigtype: str="Default") -> "FingerHelpers":
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from .defaultfingerhelpers import DefaultFingerHelpers  # pylint: disable=C0415
            return DefaultFingerHelpers(which_hand, settings)
        return FingerHelpers(which_hand, settings)

    # ---- ABSTRACT METHODS INSTANCED PER RIG TYPE

    def get_first_segment_name_of_finger(self, finger_number: int) -> str:
        """Abstract method for getting the name of the innermost bone in a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("get_first_segment_name_of_finger")

    def get_last_segment_name_of_finger(self, finger_number: int) -> str:
        """Abstract method for getting the name of the finger tip bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("get_last_segment_name_of_finger")

    def get_immediate_parent_name_of_finger(self, finger_number: int) -> str:
        """Abstract method for getting the name of the immediate parent of a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_immediate_parent_name_of_finger() method must be overriden by the rig class")

    def get_finger_segment_count(self, finger_number: int) -> int:
        """Abstract method for getting the number of bones in a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_finger_count() method must be overriden by the rig class")

    def add_finger_rotation_constraints(self, finger_number: int, armature_object: bpy.types.Object) -> None:
        """Abstract method for setting constraints for a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_finger_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_finger(self, finger_number: int) -> list[str]:
        """Abstract method for getting a list of bones from a finger starting from the tip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_reverse_list_of_bones_in_finger() method must be overriden by the rig class")
