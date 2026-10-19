"""This module provides functionality for adding helpers to hip/legs/feet."""

import bpy, typing

from .....services import LogService
_LOG = LogService.get_logger("leghelpers.leghelpers")

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
# lookup really may miss, the code already guards -- _set_parent()'s knee and hip bones are the
# example -- and those guards are left alone.
#
# RigService.add_bone_constraint_to_pose_bone() returns the bpy.types.Constraint base class, which
# carries none of target, subtarget, use_x or use_z, so each result is cast to the subclass the
# constraint type string selects. PoseBone.lock_scale is a bpy_prop_array, which the stubs declare
# without __setitem__ although it is assignable per element at runtime; hence the narrow ignores.


class LegHelpers(AbstractRigHelper):

    """This is the abstract rig type independent base class for working with
    helpers for hips, legs and feet. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, which_leg: str, settings: RigHelperSettings) -> None:
        """Get a new instance of LegHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing LegHelpers object")
        self.which_leg = which_leg
        self.settings = settings
        self._bone_info: BoneOrientationInfo = dict()

        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object: bpy.types.Object) -> None:
        """Add rig helpers for hip, legs and feet based on the settings that were provided
        when constructing the class."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        if self.settings["leg_helpers_type"] == "LOWERUPPER":
            self._apply_lower_upper(armature_object)
            self._set_parent(armature_object, True, False)

        if self.settings["leg_helpers_type"] == "LOWERUPPERHIP":
            self._apply_lower_upper_hip(armature_object)
            self._set_parent(armature_object, True, True)


    def remove_ik(self, armature_object: bpy.types.Object) -> None:
        """Remove rig helpers for hips, legs and feet based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()
        mode = str(RigHelpersProperties.get_value("leg_mode", entity_reference=armature_object)).strip()

        _LOG.debug("mode is", mode)

        include_hip = mode == "LOWERUPPERHIP"

        self.pose_mode()
        bones_to_clear = self.get_reverse_list_of_bones_in_leg(True, True, True, include_hip)

        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

        self._show_bones(armature_object, bones_to_clear)

        self.edit_mode()

        ik_bones = [
            self.which_leg + "_foot_ik",
            self.which_leg + "_knee_ik",
            self.which_leg + "_hip_ik"
            ]

        for bone_name in ik_bones:
            bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            if bone:
                typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

        self.object_mode()

        _LOG.debug("Done")

    @staticmethod
    def get_instance(which_leg: str, settings: RigHelperSettings, rigtype: str="Default") -> "LegHelpers":
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from .defaultleghelpers import DefaultLegHelpers  # pylint: disable=C0415
            return DefaultLegHelpers(which_leg, settings)
        return LegHelpers(which_leg, settings)

    def _set_parent(self, armature_object: bpy.types.Object, has_knee_ik: bool=False, has_hip_ik: bool=False) -> None:

        self.edit_mode()

        if not "leg_parenting_strategy" in self.settings:
            return

        strategy = self.settings["leg_parenting_strategy"]

        if not strategy or strategy == "NONE":
            return

        foot_ik = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(self.which_leg + "_foot_ik", armature_object))
        knee_ik = None
        hip_ik = None

        if has_knee_ik:
            knee_ik = RigService.find_edit_bone_by_name(self.which_leg + "_knee_ik", armature_object)

        if has_hip_ik:
            hip_ik = RigService.find_edit_bone_by_name(self.which_leg + "_hip_ik", armature_object)

        if strategy == "ROOT":
            root_bone = RigService.find_edit_bone_by_name(self.get_root(), armature_object)
            foot_ik.parent = root_bone
            if knee_ik:
                knee_ik.parent = root_bone
            if hip_ik:
                hip_ik.parent = root_bone

        if strategy == "OUTER":
            if knee_ik:
                knee_ik.parent = foot_ik
                if hip_ik:
                    hip_ik.parent = knee_ik

        if strategy == "INNER":
            if knee_ik:
                foot_ik.parent = knee_ik
                if hip_ik:
                    knee_ik.parent = hip_ik


    def _create_foot_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        self.edit_mode()
        foot_name = self.get_foot_name()

        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_leg + "_foot_ik")
        bone.head = self._bone_info["pose_bones"][foot_name]["head"]
        bone.tail = self._bone_info["pose_bones"][foot_name]["tail"]
        bone.roll = self._bone_info["edit_bones"][foot_name]["roll"]
        bone.matrix = self._bone_info["pose_bones"][foot_name]["matrix"]

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_foot_ik", empty_type="CIRCLE")
        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_leg + "_foot_ik", armature_object))

        scale = 0.5
        if hasattr(pose_bone, "custom_shape_scale"):
            # Removed from PoseBone before the oldest supported blender: absent from the RNA on both
            # 4.2.1 and 5.1, so the hasattr guard makes this branch unreachable there.
            pose_bone.custom_shape_scale = scale  # pyright: ignore[reportAttributeAccessIssue]
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]

        if self.settings["leg_target_rotates_foot"]:
            constraint = typing.cast(bpy.types.CopyRotationConstraint,
                                     RigService.add_bone_constraint_to_pose_bone(self.get_foot_name(), armature_object, "COPY_ROTATION"))
            constraint.target = armature_object
            constraint.subtarget = self.which_leg + "_foot_ik"

            if self.settings["leg_target_rotates_lower_leg"]:
                lower_leg_segments = self.get_reverse_list_of_bones_in_leg(False, True, False, False)
                for name in lower_leg_segments:
                    segment_constraint = typing.cast(bpy.types.CopyRotationConstraint,
                                                     RigService.add_bone_constraint_to_pose_bone(name, armature_object, "COPY_ROTATION"))
                    segment_constraint.target = armature_object
                    segment_constraint.subtarget = self.which_leg + "_foot_ik"
                    segment_constraint.use_x = False
                    segment_constraint.use_z = False
                    segment_constraint.influence = 0.4 / len(lower_leg_segments)

        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _create_knee_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_leg + "_knee_ik")

        bone.head = self._bone_info["pose_bones"][self.get_upper_leg_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_upper_leg_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 5
        bone.head = bone.head + length

        self.pose_mode()
        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_knee_ik", empty_type="SPHERE")

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_leg + "_knee_ik", armature_object))
        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _create_hip_ik_bone(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self.edit_mode()
        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones
        bone = bones.new(self.which_leg + "_hip_ik")

        bone.head = self._bone_info["pose_bones"][self.get_hip_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_hip_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 2
        bone.head = bone.head + length

        self.pose_mode()
        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_hip_ik", empty_type="SPHERE")

        pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(self.which_leg + "_hip_ik", armature_object))
        for i in range(3):
            pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _set_lower_leg_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        lower_leg_name = self.get_lower_leg_name()
        foot_name = self.which_leg + "_foot_ik"
        foot_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(foot_name, armature_object))
        self.add_lower_leg_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(lower_leg_name, armature_object, foot_bone, chain_length)

    def _set_upper_leg_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        upper_leg_name = self.get_upper_leg_name()
        knee_name = self.which_leg + "_knee_ik"
        knee_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(knee_name, armature_object))
        self.add_upper_leg_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(upper_leg_name, armature_object, knee_bone, chain_length)

    def _set_hip_ik_target(self, armature_object: bpy.types.Object, chain_length: int) -> None:
        _LOG.enter()
        self.pose_mode()
        hip_name = self.get_hip_name()
        hip_ik_name = self.which_leg + "_hip_ik"
        hip_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(hip_ik_name, armature_object))
        self.add_hip_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(hip_name, armature_object, hip_bone, chain_length)

    def _hide_bones(self, armature_object: bpy.types.Object, bone_list: list[str]) -> None:
        _LOG.enter()
        bones = typing.cast(bpy.types.Armature, armature_object.data).bones
        for name in bone_list:
            _LOG.debug("Will attempt to hide bone", name)
            # The names come from the rig specific get_reverse_list_of_bones_in_leg(), so they are
            # bones of the rig the calling operator has already identified.
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

    def _apply_lower_upper(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_foot_ik_bone(armature_object)
        self._create_knee_ik_bone(armature_object)
        chain_length_entire_leg = self.get_lower_leg_count() + self.get_upper_leg_count()
        self._set_lower_leg_ik_target(armature_object, chain_length_entire_leg)
        self._set_upper_leg_ik_target(armature_object, self.get_upper_leg_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_leg(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_lower_upper_hip(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        self._create_foot_ik_bone(armature_object)
        self._create_knee_ik_bone(armature_object)
        self._create_hip_ik_bone(armature_object)
        chain_length_entire_leg = self.get_lower_leg_count() + self.get_upper_leg_count() + self.get_hip_count()
        self._set_lower_leg_ik_target(armature_object, chain_length_entire_leg)
        self._set_upper_leg_ik_target(armature_object, chain_length_entire_leg - self.get_upper_leg_count())
        self._set_hip_ik_target(armature_object, self.get_hip_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_leg(True, True, True, True)
            self._hide_bones(armature_object, bones_to_hide)

    def get_lower_leg_name(self) -> str:
        """Abstract method for getting the name of the last bone in the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_name() method must be overriden by the rig class")

    def get_upper_leg_name(self) -> str:
        """Abstract method for getting the name of the last bone in the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_leg_name() method must be overriden by the rig class")

    def get_hip_name(self) -> str:
        """Abstract method for getting the name of the last bone in the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_hip_name() method must be overriden by the rig class")

    def get_foot_name(self) -> str:
        """Abstract method for getting the name of the foot bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_foot_name() method must be overriden by the rig class")

    def get_root(self) -> str:
        """Abstract method for getting the name of the root bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_root() method must be overriden by the rig class")

    def get_lower_leg_count(self) -> int:
        """Abstract method for getting the number of bones in the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_count() method must be overriden by the rig class")

    def get_upper_leg_count(self) -> int:
        """Abstract method for getting the number of bones in the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_leg_count() method must be overriden by the rig class")

    def get_hip_count(self) -> int:
        """Abstract method for getting the number of bones in the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_count() method must be overriden by the rig class")

    def add_lower_leg_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for setting constraints for the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_lower_leg_rotation_constraints() method must be overriden by the rig class")

    def add_upper_leg_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for setting constraints for the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_upper_leg_rotation_constraints() method must be overriden by the rig class")

    def add_hip_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for setting constraints for the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_hip_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_leg(self, include_foot: bool=True, include_lower_leg: bool=True,
                                         include_upper_leg: bool=True, include_hip: bool=True) -> list[str]:
        """Abstract method for getting the bone names in the leg startin with the foot and working inwards,
        must be overriden by rig specific implementation classes"""
        raise NotImplementedError("the get_reverse_list_of_bones_in_leg() method must be overriden by the rig class")
