"""This module provides functionality for adding helpers to hip/legs/feet."""

import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("leghelpers.leghelpers")

from mpfb.services.rigservice import RigService
from mpfb.ui.righelpers import RigHelpersProperties


class LegHelpers():

    """This is the abstract rig type independent base class for working with
    helpers for hips, legs and feet. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, which_leg, settings):
        """Get a new instance of LegHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing LegHelpers object")
        self.which_leg = which_leg
        self.settings = settings
        self._bone_info = dict()

        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object):
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

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def remove_ik(self, armature_object):
        """Remove rig helpers for hips, legs and feet based on the settings that were provided
        when constructing the class, and information about the current status of the
        armature object."""

        _LOG.enter()
        mode = str(RigHelpersProperties.get_value("leg_mode", entity_reference=armature_object)).strip()

        _LOG.debug("mode is", mode)

        include_hip = mode == "LOWERUPPERHIP"

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones_to_clear = self.get_reverse_list_of_bones_in_leg(True, True, True, include_hip)

        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

        self._show_bones(armature_object, bones_to_clear)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        ik_bones = [
            self.which_leg + "_foot_ik",
            self.which_leg + "_knee_ik",
            self.which_leg + "_hip_ik"
            ]

        for bone_name in ik_bones:
            bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            if bone:
                armature_object.data.edit_bones.remove(bone)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        _LOG.debug("Done")

    @staticmethod
    def get_instance(which_leg, settings, rigtype="Default"):
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from mpfb.entities.rigging.righelpers.leghelpers.defaultleghelpers import DefaultLegHelpers  # pylint: disable=C0415
            return DefaultLegHelpers(which_leg, settings)
        return LegHelpers(which_leg, settings)

    def _set_parent(self, armature_object, has_knee_ik=False, has_hip_ik=False):

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if not "leg_parenting_strategy" in self.settings:
            return

        strategy = self.settings["leg_parenting_strategy"]

        if not strategy or strategy == "NONE":
            return

        foot_ik = RigService.find_edit_bone_by_name(self.which_leg + "_foot_ik", armature_object)
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

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _create_foot_ik_bone(self, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        foot_name = self.get_foot_name()

        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_leg + "_foot_ik")
        bone.head = self._bone_info["pose_bones"][foot_name]["head"]
        bone.tail = self._bone_info["pose_bones"][foot_name]["tail"]
        bone.roll = self._bone_info["edit_bones"][foot_name]["roll"]
        bone.matrix = self._bone_info["pose_bones"][foot_name]["matrix"]

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_foot_ik", empty_type="CIRCLE")
        pose_bone = RigService.find_pose_bone_by_name(self.which_leg + "_foot_ik", armature_object)

        scale = 0.5
        if hasattr(pose_bone, "custom_shape_scale"):
            pose_bone.custom_shape_scale = scale
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]

        if self.settings["leg_target_rotates_foot"]:
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            constraint = RigService.add_bone_constraint_to_pose_bone(self.get_foot_name(), armature_object, "COPY_ROTATION")
            constraint.target = armature_object
            constraint.subtarget = self.which_leg + "_foot_ik"

            if self.settings["leg_target_rotates_lower_leg"]:
                lower_leg_segments = self.get_reverse_list_of_bones_in_leg(False, True, False, False)
                for name in lower_leg_segments:
                    constraint = RigService.add_bone_constraint_to_pose_bone(name, armature_object, "COPY_ROTATION")
                    constraint.target = armature_object
                    constraint.subtarget = self.which_leg + "_foot_ik"
                    constraint.use_x = False
                    constraint.use_z = False
                    constraint.influence = 0.4 / len(lower_leg_segments)

        for i in range(3):
            pose_bone.lock_scale[i] = True

    def _create_knee_ik_bone(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_leg + "_knee_ik")

        bone.head = self._bone_info["pose_bones"][self.get_upper_leg_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_upper_leg_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 5
        bone.head = bone.head + length

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_knee_ik", empty_type="SPHERE")

        pose_bone = RigService.find_pose_bone_by_name(self.which_leg + "_knee_ik", armature_object)
        for i in range(3):
            pose_bone.lock_scale[i] = True

    def _create_hip_ik_bone(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_leg + "_hip_ik")

        bone.head = self._bone_info["pose_bones"][self.get_hip_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_hip_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 2
        bone.head = bone.head + length

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        RigService.display_pose_bone_as_empty(armature_object, self.which_leg + "_hip_ik", empty_type="SPHERE")

        pose_bone = RigService.find_pose_bone_by_name(self.which_leg + "_hip_ik", armature_object)
        for i in range(3):
            pose_bone.lock_scale[i] = True

    def _set_lower_leg_ik_target(self, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        lower_leg_name = self.get_lower_leg_name()
        foot_name = self.which_leg + "_foot_ik"
        foot_bone = RigService.find_pose_bone_by_name(foot_name, armature_object)
        self.add_lower_leg_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(lower_leg_name, armature_object, foot_bone, chain_length)

    def _set_upper_leg_ik_target(self, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        upper_leg_name = self.get_upper_leg_name()
        knee_name = self.which_leg + "_knee_ik"
        knee_bone = RigService.find_pose_bone_by_name(knee_name, armature_object)
        self.add_upper_leg_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(upper_leg_name, armature_object, knee_bone, chain_length)

    def _set_hip_ik_target(self, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        hip_name = self.get_hip_name()
        hip_ik_name = self.which_leg + "_hip_ik"
        hip_bone = RigService.find_pose_bone_by_name(hip_ik_name, armature_object)
        self.add_hip_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(hip_name, armature_object, hip_bone, chain_length)

    def _hide_bones(self, armature_object, bone_list):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for name in bone_list:
            _LOG.debug("Will attempt to hide bone", name)
            bone = armature_object.data.bones.get(name)
            bone.hide = True

    def _show_bones(self, armature_object, bone_list):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for name in bone_list:
            _LOG.debug("Will attempt to show bone", name)
            bone = armature_object.data.bones.get(name)
            bone.hide = False

    def _apply_lower_upper(self, armature_object):
        _LOG.enter()
        self._create_foot_ik_bone(armature_object)
        self._create_knee_ik_bone(armature_object)
        chain_length_entire_leg = self.get_lower_leg_count() + self.get_upper_leg_count()
        self._set_lower_leg_ik_target(armature_object, chain_length_entire_leg)
        self._set_upper_leg_ik_target(armature_object, self.get_upper_leg_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_leg(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_lower_upper_hip(self, armature_object):
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

    def get_lower_leg_name(self):
        """Abstract method for getting the name of the last bone in the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_name() method must be overriden by the rig class")

    def get_upper_leg_name(self):
        """Abstract method for getting the name of the last bone in the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_leg_name() method must be overriden by the rig class")

    def get_hip_name(self):
        """Abstract method for getting the name of the last bone in the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_hip_name() method must be overriden by the rig class")

    def get_foot_name(self):
        """Abstract method for getting the name of the foot bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_foot_name() method must be overriden by the rig class")

    def get_root(self):
        """Abstract method for getting the name of the root bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_root() method must be overriden by the rig class")

    def get_lower_leg_count(self):
        """Abstract method for getting the number of bones in the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_count() method must be overriden by the rig class")

    def get_upper_leg_count(self):
        """Abstract method for getting the number of bones in the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_upper_leg_count() method must be overriden by the rig class")

    def get_hip_count(self):
        """Abstract method for getting the number of bones in the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_lower_leg_count() method must be overriden by the rig class")

    def add_lower_leg_rotation_constraints(self, armature_object):
        """Abstract method for setting constraints for the lower leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_lower_leg_rotation_constraints() method must be overriden by the rig class")

    def add_upper_leg_rotation_constraints(self, armature_object):
        """Abstract method for setting constraints for the upper leg, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_upper_leg_rotation_constraints() method must be overriden by the rig class")

    def add_hip_rotation_constraints(self, armature_object):
        """Abstract method for setting constraints for the hip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_hip_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_leg(self, include_foot=True, include_lower_leg=True, include_upper_leg=True, include_hip=True):
        """Abstract method for getting the bone names in the leg startin with the foot and working inwards,
        must be overriden by rig specific implementation classes"""
        raise NotImplementedError("the get_reverse_list_of_bones_in_leg() method must be overriden by the rig class")
