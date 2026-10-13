"""This module provides functionality for adding helpers to eyes."""

import bpy, typing

from .....services import LogService
_LOG = LogService.get_logger("eyehelpers.eyehelpers")

from .....services import RigService
from .....types import BoneOrientationInfo, RigHelperSettings
from ..abstractrighelper import AbstractRigHelper

# The helpers are only reachable from operators which poll for an active armature, so every
# armature_object.data read below is narrowed with a cast rather than an isinstance guard.
#
# The same applies to the RigService bone finders, which return an optional because the blender
# collections they read do. Every lookup below either names a helper bone this class created a few
# lines earlier or a bone of the rig the concrete subclass was selected for, so the casts record a
# contract the caller is expected to satisfy rather than a guarantee pyright can check.
#
# PoseBone.lock_rotation and lock_scale are bpy_prop_array, which the stubs declare without
# __setitem__ although both are assignable per element at runtime; hence the narrow ignores.


class EyeHelpers(AbstractRigHelper):

    """This is the abstract rig type independent base class for working with
    helpers for eyes. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, settings: RigHelperSettings) -> None:
        """Get a new instance of EyeHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing EyeHelpers object")
        self.settings = settings
        self._bone_info: BoneOrientationInfo = dict()

        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object: bpy.types.Object) -> None:
        """Add rig helpers for eyes based on the settings that were provided
        when constructing the class."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        self._create_eye_ik_bones(armature_object)
        self._apply_ik_constraint(armature_object)

        #pose_mode()

    def remove_ik(self, armature_object: bpy.types.Object) -> None:
        """Remove rig helpers for eyes based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()
        self.pose_mode()

        for bone_name in [self.get_eye_name(True), self.get_eye_name(False)]:
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

        self.edit_mode()

        for bone_name in ["left_eye_ik", "right_eye_ik", "eye_ik"]:
            bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name(bone_name, armature_object))
            typing.cast(bpy.types.Armature, armature_object.data).edit_bones.remove(bone)

        _LOG.debug("Done")

    @staticmethod
    def get_instance(settings: RigHelperSettings, rigtype: str="Default") -> "EyeHelpers":
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from .defaulteyehelpers import DefaultEyeHelpers  # pylint: disable=C0415
            return DefaultEyeHelpers(settings)
        return EyeHelpers(settings)

    def _create_eye_ik_bones(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()

        self.edit_mode()

        bones = typing.cast(bpy.types.Armature, armature_object.data).edit_bones

        for side in ["left", "right"]:
            is_right = side == "right"
            bone_name = self.get_eye_name(is_right)

            bone = bones.new(side + "_eye_ik")
            head = self._bone_info["pose_bones"][bone_name]["head"]
            tail = self._bone_info["pose_bones"][bone_name]["tail"]
            length = tail - head

            bone.head = head + length * 4
            bone.tail = tail = tail + length * 4
            bone.roll = self._bone_info["edit_bones"][bone_name]["roll"]

        left_eye_bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name("left_eye_ik", armature_object))
        right_eye_bone = typing.cast(bpy.types.EditBone, RigService.find_edit_bone_by_name("right_eye_ik", armature_object))

        bone = bones.new("eye_ik")
        bone.head = (left_eye_bone.head + right_eye_bone.head) / 2
        bone.tail = (left_eye_bone.tail + right_eye_bone.tail) / 2
        bone.roll = left_eye_bone.roll

        left_eye_bone.parent = bone
        right_eye_bone.parent = bone

        if self.settings["eye_parenting_strategy"] == "HEAD":
            bone.parent = RigService.find_edit_bone_by_name(self.get_head_name(), armature_object)

        if self.settings["eye_parenting_strategy"] == "ROOT":
            bone.parent = RigService.find_edit_bone_by_name(self.get_root_name(), armature_object)

        self.pose_mode()

        RigService.display_pose_bone_as_empty(armature_object, "left_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "right_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "eye_ik", "CIRCLE", scale=1.4)

        for side in ["left", "right"]:
            pose_bone = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name(side + "_eye_ik", armature_object))
            for i in range(3):
                pose_bone.lock_rotation[i] = True  # pyright: ignore[reportIndexIssue]
                pose_bone.lock_scale[i] = True  # pyright: ignore[reportIndexIssue]

    def _apply_ik_constraint(self, armature_object: bpy.types.Object) -> None:
        _LOG.enter()
        right = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name("right_eye_ik", armature_object))
        left = typing.cast(bpy.types.PoseBone, RigService.find_pose_bone_by_name("left_eye_ik", armature_object))
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(True), armature_object, right, chain_length=1)
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(False), armature_object, left, chain_length=1)

    def get_head_name(self) -> str:
        """Abstract method for getting the name of the head bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_head_name() method must be overriden by the rig class")

    def get_root_name(self) -> str:
        """Abstract method for getting the name of the root bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_root_name() method must be overriden by the rig class")

    def get_eye_name(self, right_side: bool=True) -> str:
        """Abstract method for getting the name of the eye bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_name() method must be overriden by the rig class")

    def get_eye_lower_lid_name(self, right_side: bool=True) -> str:
        """Abstract method for getting the name of the lower eyelid bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_lower_lid_name() method must be overriden by the rig class")

    def get_eye_upper_lid_name(self, right_side: bool=True) -> str:
        """Abstract method for getting the name of the upper eyelid bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_upper_lid_name() method must be overriden by the rig class")

    def add_eye_rotation_constraints(self, armature_object: bpy.types.Object) -> None:
        """Abstract method for setting constraints of the eye bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_eye_rotation_constraints() method must be overriden by the rig class")

