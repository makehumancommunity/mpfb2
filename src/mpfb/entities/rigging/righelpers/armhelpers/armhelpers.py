"""This module provides functionality for adding helpers to arms/hands."""

import bpy, typing

from .....services import LogService
_LOG = LogService.get_logger("armhelpers.armhelpers")

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
# contract the caller is expected to satisfy rather than a guarantee pyright can check. Where a
# lookup really may miss, the code already guards -- _set_parent()'s elbow and shoulder bones are
# the example -- and those guards are left alone.
#
# RigService.add_bone_constraint_to_pose_bone() returns the bpy.types.Constraint base class, which
# carries none of target, subtarget, use_x or use_z, so each result is cast to the subclass the
# constraint type string selects.

class ArmHelpers(AbstractRigHelper):

    """This is the abstract rig type independent base class for working with
    helpers for arms and hands. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, which_arm: str, settings: RigHelperSettings) -> None:
        """Get a new instance of ArmHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing ArmHelpers object")
        self.which_arm = which_arm
        self.settings = settings
        self._bone_info: BoneOrientationInfo = dict()
        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object: bpy.types.Object) -> None:
        """Add rig helpers for arms and hands based on the settings that were provided
        when constructing the class."""

        _LOG.enter()

        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        if self.settings["arm_helpers_type"] == "LOWERUPPER":
            self._apply_lower_upper(armature_object)
            self._set_parent(armature_object, has_elbow_ik=True, has_shoulder_ik=False)

        if self.settings["arm_helpers_type"] == "LOWERUPPERSHOULDER":
            self._apply_lower_upper_shoulder(armature_object)
            self._set_parent(armature_object, has_elbow_ik=True, has_shoulder_ik=True)

        if self.settings["arm_helpers_type"] == "ARMCHAIN":
            self._apply_arm_chain(armature_object)
            self._set_parent(armature_object, has_elbow_ik=False, has_shoulder_ik=False)

        if self.settings["arm_helpers_type"] == "SHOULDERCHAIN":
            self._apply_shoulder_chain(armature_object)
            self._set_parent(armature_object, has_elbow_ik=False, has_shoulder_ik=False)

        self.object_mode()

    def remove_ik(self, armature_object: bpy.types.Object) -> None:
        """Remove rig helpers for arms and hands based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        mode = str(RigHelpersProperties.get_value("arm_mode", entity_reference=armature_object)).strip()

        include_shoulder = False

        if mode == "LOWERUPPERSHOULDER":
            include_shoulder = True

        if mode == "SHOULDERCHAIN":
            include_shoulder = True

        self.pose_mode()
        bones_to_clear = self.get_reverse_list_of_bones_in_arm(True, True, True, include_shoulder)

        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

        self._show_bones(armature_object, bones_to_clear)

        self.edit_mode()

        ik_bones = [
            self.which_arm + "_hand_ik",
            self.which_arm + "_elbow_ik",
            self.which_arm + "_shoulder_ik"
            ]

        for bone_name in ik_bones:
            bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            if bone:
                typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

        self.object_mode()

        _LOG.debug("Done")

    @staticmethod
    def get_instance(which_arm: str, settings: RigHelperSettings, rigtype: str="Default") -> "ArmHelpers":
        """Get an implementation instance matching the rig type."""
        _LOG.enter()
        if rigtype == "Default":
            from .defaultarmhelpers import DefaultArmHelpers  # pylint: disable=C0415
            return DefaultArmHelpers(which_arm, settings)
        return ArmHelpers(which_arm, settings)

    def _set_parent(self, armature_object: bpy.types.Object, has_elbow_ik: bool=False, has_shoulder_ik: bool=False) -> None:
        _LOG.enter()
        self.edit_mode()

        if not "arm_parenting_strategy" in self.settings:
            return

        strategy = self.settings["arm_parenting_strategy"]

        if not strategy or strategy == "NONE":
            return

        hand_ik = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(self.which_arm + "_hand_ik", armature_object))
        elbow_ik = None
        shoulder_ik = None

        if has_elbow_ik:
            elbow_ik = RigService.find_edit_bone_by_name(self.which_arm + "_elbow_ik", armature_object)

        if has_shoulder_ik:
            shoulder_ik = RigService.find_edit_bone_by_name(self.which_arm + "_shoulder_ik", armature_object)

        if strategy == "ROOT":
            root_bone = RigService.find_edit_bone_by_name(self.get_root(), armature_object)
            hand_ik.parent = root_bone
            if elbow_ik:
                elbow_ik.parent = root_bone
            if shoulder_ik:
                shoulder_ik.parent = root_bone

        if strategy == "SPINE":
            spine_bone = RigService.find_edit_bone_by_name(self.get_shoulders_immediate_parent(), armature_object)
            hand_ik.parent = spine_bone
            if elbow_ik:
                elbow_ik.parent = spine_bone
            if shoulder_ik:
                shoulder_ik.parent = spine_bone

        if strategy == "OUTER":
            if elbow_ik:
                elbow_ik.parent = hand_ik
                if shoulder_ik:
                    shoulder_ik.parent = elbow_ik

        if strategy == "INNER":
            if elbow_ik:
                hand_ik.parent = elbow_ik
                if shoulder_ik:
                    elbow_ik.parent = shoulder_ik


    def _create_hand_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        hand_name = self.get_hand_name()

        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_arm + "_hand_ik")
        bone.head = self._bone_info["pose_bones"][hand_name]["head"]
        bone.tail = self._bone_info["pose_bones"][hand_name]["tail"]
        bone.roll = self._bone_info["edit_bones"][hand_name]["roll"]
        bone.matrix = self._bone_info["pose_bones"][hand_name]["matrix"]

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_hand_ik", empty_type="CIRCLE")

        if self.settings["arm_target_rotates_hand"]:

            constraint = typing.cast(bpy.types.CopyRotationConstraint,
                                     RigService.add_bone_constraint_to_pose_bone(self.get_hand_name(), armature_object, "COPY_ROTATION"))
            constraint.target = armature_object
            constraint.subtarget = self.which_arm + "_hand_ik"

            if self.settings["arm_target_rotates_lower_arm"]:
                lower_arm_segments = self.get_reverse_list_of_bones_in_arm(False, True, False, False)
                for name in lower_arm_segments:
                    segment_constraint = typing.cast(bpy.types.CopyRotationConstraint,
                                                     RigService.add_bone_constraint_to_pose_bone(name, armature_object, "COPY_ROTATION"))
                    segment_constraint.target = armature_object
                    segment_constraint.subtarget = self.which_arm + "_hand_ik"
                    segment_constraint.use_x = False
                    segment_constraint.use_z = False
                    segment_constraint.influence = 0.4 / len(lower_arm_segments)

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_arm + "_hand_ik", armature_object))
        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _create_elbow_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_arm + "_elbow_ik")

        bone.head = self._bone_info["pose_bones"][self.get_upper_arm_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_upper_arm_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 3
        bone.head = bone.head + length

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_elbow_ik", empty_type="SPHERE")

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_arm + "_elbow_ik", armature_object))
        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _create_shoulder_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_arm + "_shoulder_ik")

        bone.head = self._bone_info["pose_bones"][self.get_shoulder_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_shoulder_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length * 0.65
        bone.head = bone.head + length

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_shoulder_ik", empty_type="SPHERE")

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_arm + "_shoulder_ik", armature_object))
        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _set_lower_arm_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        lower_arm_name = self.get_lower_arm_name()
        hand_name = self.which_arm + "_hand_ik"
        hand_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(hand_name, armature_object))
        self.add_lower_arm_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(lower_arm_name, armature_object, hand_bone, chain_length)

    def _set_upper_arm_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        upper_arm_name = self.get_upper_arm_name()
        elbow_name = self.which_arm + "_elbow_ik"
        elbow_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(elbow_name, armature_object))
        self.add_upper_arm_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(upper_arm_name, armature_object, elbow_bone, chain_length)

    def _set_shoulder_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        shoulder_name = self.get_shoulder_name()
        shoulder_ik_name = self.which_arm + "_shoulder_ik"
        shoulder_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(shoulder_ik_name, armature_object))
        self.add_shoulder_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(shoulder_name, armature_object, shoulder_bone, chain_length)

    def _hide_bones(self, armature_object: bpy.types.Object, bone_list: list[str]) -> None:
        _LOG.enter()
        bones = typing.cast(bpy.types.Armature, armature_object.data).bones
        for name in bone_list:
            # The names come from the rig specific get_reverse_list_of_bones_in_arm(), so they are
            # bones of the rig the calling operator has already identified.
            bone = typing.cast(bpy.types.Bone, bones.get(name))
            bone.hide = True

    def _show_bones(self, armature_object: bpy.types.Object, bone_list: list[str]) -> None:
        _LOG.enter()
        bones = typing.cast(bpy.types.Armature, armature_object.data).bones
        for name in bone_list:
            # See _hide_bones() above for why the lookup result is cast rather than guarded.
            bone = typing.cast(bpy.types.Bone, bones.get(name))
            bone.hide = False

    def _apply_lower_upper(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        self._create_elbow_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        self._set_upper_arm_ik_target(armature_object, self.get_upper_arm_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_lower_upper_shoulder(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        self._create_elbow_ik_bone(armature_object)
        self._create_shoulder_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count() + self.get_shoulder_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        self._set_upper_arm_ik_target(armature_object, chain_length_entire_arm - self.get_upper_arm_count())
        self._set_shoulder_ik_target(armature_object, self.get_shoulder_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, True)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_arm_chain(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_shoulder_chain(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count() + self.get_shoulder_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, True)
            self._hide_bones(armature_object, bones_to_hide)

    def get_lower_arm_name(self) -> str:
        """Abstract method for getting the name of the last bone in the lower arm, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_arm_name() method must be overriden by the rig class")

    def get_upper_arm_name(self) -> str:
        """Abstract method for getting the name of the last bone in the upper arm, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_arm_name() method must be overriden by the rig class")

    def get_shoulder_name(self) -> str:
        """Abstract method for getting the name of the last bone in the shoulder, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_shoulder_name() method must be overriden by the rig class")

    def get_hand_name(self) -> str:
        """Abstract method for getting the name of the hand bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_hand_name() method must be overriden by the rig class")

    def get_lower_arm_count(self) -> int:
        """Abstract method for getting the number of bones in the lower arm, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_arm_count() method must be overriden by the rig class")

    def get_upper_arm_count(self) -> int:
        """Abstract method for getting the number of bones in the upper arm, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_arm_count() method must be overriden by the rig class")

    def get_shoulder_count(self) -> int:
        """Abstract method for getting the number of bones in the shoulder, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_arm_count() method must be overriden by the rig class")

    def get_shoulders_immediate_parent(self) -> str:
        """Abstract method for getting the name of the bone immediately before the shoulders,
        must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_shoulders_immediate_parent() method must be overriden by the rig class")

    def get_root(self) -> str:
        """Abstract method for getting the name of the root bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_root() method must be overriden by the rig class")

    def add_lower_arm_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for settings constraints for the bones in the lower arm."""
        raise NotImplementedError("the add_lower_arm_rotation_constraints() method must be overriden by the rig class")

    def add_upper_arm_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for settings constraints for the bones in the upper arm."""
        raise NotImplementedError("the add_upper_arm_rotation_constraints() method must be overriden by the rig class")

    def add_shoulder_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for settings constraints for the bones in the shoulder."""
        raise NotImplementedError("the add_shoulder_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_arm(self, include_hand: bool=True, include_lower_arm: bool=True,
                                         include_upper_arm: bool=True, include_shoulder: bool=True) -> list[str]:
        """Abstract method for getting a list of bone names, starting from the wrist and working inwards."""
        raise NotImplementedError("the get_reverse_list_of_bones_in_arm() method must be overriden by the rig class")
