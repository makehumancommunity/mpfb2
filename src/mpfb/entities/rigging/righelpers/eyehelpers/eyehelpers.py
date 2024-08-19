"""This module provides functionality for adding helpers to eyes."""

import bpy

from .....services import LogService
_LOG = LogService.get_logger("eyehelpers.eyehelpers")

from .....services import RigService
from .....ui.righelpers import RigHelpersProperties


class EyeHelpers():

    """This is the abstract rig type independent base class for working with
    helpers for eyes. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, settings):
        """Get a new instance of EyeHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing EyeHelpers object")
        self.settings = settings
        self._bone_info = dict()

        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object):
        """Add rig helpers for eyes based on the settings that were provided
        when constructing the class."""

        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        self._create_eye_ik_bones(armature_object)
        self._apply_ik_constraint(armature_object)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def remove_ik(self, armature_object):
        """Remove rig helpers for eyes based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        for bone_name in [self.get_eye_name(True), self.get_eye_name(False)]:
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        for bone_name in ["left_eye_ik", "right_eye_ik", "eye_ik"]:
            bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            armature_object.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        _LOG.debug("Done")

    @staticmethod
    def get_instance(settings, rigtype="Default"):
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from .defaulteyehelpers import DefaultEyeHelpers  # pylint: disable=C0415
            return DefaultEyeHelpers(settings)
        return EyeHelpers(settings)

    def _create_eye_ik_bones(self, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bones = armature_object.data.edit_bones

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

        left_eye_bone = RigService.find_edit_bone_by_name("left_eye_ik", armature_object)
        right_eye_bone = RigService.find_edit_bone_by_name("right_eye_ik", armature_object)

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

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.display_pose_bone_as_empty(armature_object, "left_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "right_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "eye_ik", "CIRCLE", scale=1.4)

        for side in ["left", "right"]:
            pose_bone = RigService.find_pose_bone_by_name(side + "_eye_ik", armature_object)
            for i in range(3):
                pose_bone.lock_rotation[i] = True
                pose_bone.lock_scale[i] = True

    def _apply_ik_constraint(self, armature_object):
        _LOG.enter()
        right = RigService.find_pose_bone_by_name("right_eye_ik", armature_object)
        left = RigService.find_pose_bone_by_name("left_eye_ik", armature_object)
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(True), armature_object, right, chain_length=1)
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(False), armature_object, left, chain_length=1)

    def get_head_name(self):
        """Abstract method for getting the name of the head bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_head_name() method must be overriden by the rig class")

    def get_root_name(self):
        """Abstract method for getting the name of the root bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_root_name() method must be overriden by the rig class")

    def get_eye_name(self, right_side=True):
        """Abstract method for getting the name of the eye bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_name() method must be overriden by the rig class")

    def get_eye_lower_lid_name(self, right_side=True):
        """Abstract method for getting the name of the lower eyelid bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_lower_lid_name() method must be overriden by the rig class")

    def get_eye_upper_lid_name(self, right_side=True):
        """Abstract method for getting the name of the upper eyelid bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_eye_upper_lid_name() method must be overriden by the rig class")

    def add_eye_rotation_constraints(self, armature_object):
        """Abstract method for setting constraints of the eye bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_eye_rotation_constraints() method must be overriden by the rig class")

