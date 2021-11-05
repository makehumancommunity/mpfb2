"""This module provides functionality for adding helpers to fingers."""

import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("fingerhelpers.fingerhelpers")

from mpfb.services.rigservice import RigService
from mpfb.ui.righelpers import RigHelpersProperties

class FingerHelpers():

    """This is the abstract rig type independent base class for working with
    helpers for fingers. You will want to call the static get_instance()
    method to get a concrete implementation for the specific rig you are
    working with."""

    def __init__(self, which_hand, settings):
        """Get a new instance of FingerHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing FingerHelpers object")
        self.which_hand = which_hand
        self.settings = settings
        self._bone_info = dict()
        _LOG.dump("settings", self.settings)



    # ---- METHODS FOR APPLYING AND CREATING

    def apply_ik(self, armature_object):
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

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def _apply_master_without_individual_for_finger(self, armature_object, finger_number):
        master_name = self._get_master_grip_bone_name()

        finger_segments = self.get_reverse_list_of_bones_in_finger(finger_number)

        for bone_name in finger_segments:
            constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object, copy_y=False, copy_z=False)
            constraint.influence = 1.0 / len(finger_segments)

        bone_name = finger_segments[-1]

        constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object, copy_x=False)

        if self.settings["hide_fk"]:
            self._hide_bones(armature_object, finger_segments)

    def _apply_master_with_individual_for_finger(self, armature_object, finger_number):
        master_name = self._get_master_grip_bone_name()
        bone_name = self._get_grip_bone_name_for_finger(finger_number)

        constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, master_name, armature_object)
        constraint.name = 'Add rotation'
        constraint.mix_mode = 'ADD'

    def _apply_master_grip(self, armature_object, assume_individual_grip=False):
        _LOG.enter()
        self._create_master_grip_bone(armature_object)

        for finger_number in [1, 2, 3, 4, 5]:
            if assume_individual_grip:
                self._apply_master_with_individual_for_finger(armature_object, finger_number)
            else:
                self._apply_master_without_individual_for_finger(armature_object, finger_number)

    def _apply_individual_grip(self, armature_object):
        _LOG.enter()

        for finger_number in [1, 2, 3, 4, 5]:
            self._create_grip_bone(finger_number, armature_object)
            grip_name = self._get_grip_bone_name_for_finger(finger_number)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            parent_name = self.get_immediate_parent_name_of_finger(finger_number)
            parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

            grip_bone = RigService.find_edit_bone_by_name(grip_name, armature_object)
            grip_bone.parent = parent_bone

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            finger_segments = self.get_reverse_list_of_bones_in_finger(finger_number)

            for bone_name in finger_segments:
                constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, grip_name, armature_object, copy_y=False, copy_z=False)
                constraint.influence = 1.0 / len(finger_segments)

            bone_name = finger_segments[-1]

            constraint = RigService.add_copy_rotation_constraint_to_pose_bone(bone_name, grip_name, armature_object, copy_x=False)

            if self.settings["hide_fk"]:
                self._hide_bones(armature_object, finger_segments)

    def _apply_point(self, armature_object):
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            self._create_point_ik_bone(finger_number, armature_object)
            ik_name = self._get_point_ik_bone_name_for_finger(finger_number)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            parent_name = self.get_immediate_parent_name_of_finger(finger_number)
            parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

            ik_bone = RigService.find_edit_bone_by_name(ik_name, armature_object)
            ik_bone.parent = parent_bone

            chain_length = self.get_finger_segment_count(finger_number)
            self._set_finger_ik_target(finger_number, armature_object, chain_length)
            if self.settings["hide_fk"]:
                bones_to_hide = self.get_reverse_list_of_bones_in_finger(finger_number)
                self._hide_bones(armature_object, bones_to_hide)

    def _set_finger_ik_target(self, finger_number, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        tip_name = self.get_last_segment_name_of_finger(finger_number)
        ik_name = self._get_point_ik_bone_name_for_finger(finger_number)
        ik_bone = RigService.find_pose_bone_by_name(ik_name, armature_object)
        self.add_finger_rotation_constraints(finger_number, armature_object)
        RigService.add_ik_constraint_to_pose_bone(tip_name, armature_object, ik_bone, chain_length)

    def _create_point_ik_bone(self, finger_number, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        tip_name = self.get_last_segment_name_of_finger(finger_number)

        head = self._bone_info["pose_bones"][tip_name]["head"]
        tail = self._bone_info["pose_bones"][tip_name]["tail"]
        roll = self._bone_info["edit_bones"][tip_name]["roll"]

        length = tail - head
        tail = tail + length
        head = head + length

        bone_name = self._get_point_ik_bone_name_for_finger(finger_number)
        bones = armature_object.data.edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        RigService.display_pose_bone_as_empty(armature_object, bone_name, empty_type="SPHERE")
        pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)

        scales = [0.5, 0.5, 0.5, 0.5, 0.7]

        scale = scales[finger_number - 1]
        if hasattr(pose_bone, "custom_shape_scale"):
            pose_bone.custom_shape_scale = scale
            _LOG.debug("scale", pose_bone.custom_shape_scale)
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)


    def _create_grip_bone(self, finger_number, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        tip_name = self.get_last_segment_name_of_finger(finger_number)
        root_name = self.get_first_segment_name_of_finger(finger_number)

        head = self._bone_info["edit_bones"][root_name]["head"]
        tail = self._bone_info["edit_bones"][tip_name]["tail"]
        roll = self._bone_info["edit_bones"][root_name]["roll"]

        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        bones = armature_object.data.edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)

        root_bone = RigService.find_pose_bone_by_name(root_name, armature_object)

        pose_bone.location = root_bone.location

        RigService.display_pose_bone_as_empty(armature_object, bone_name, 'CIRCLE')

        scales = [0.1, 0.15, 0.1, 0.1, 0.2]

        scale = scales[finger_number - 1]
        if hasattr(pose_bone, "custom_shape_scale"):
            pose_bone.custom_shape_scale = scale
            _LOG.debug("scale", pose_bone.custom_shape_scale)
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)

        for i in range(3):
            pose_bone.lock_location[i] = True
            pose_bone.lock_scale[i] = True

    def _create_master_grip_bone(self, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

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
        bones = armature_object.data.edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        parent_name = self.get_immediate_parent_name_of_finger(3)
        parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

        bone.parent = parent_bone

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)

        root_bone3 = RigService.find_pose_bone_by_name(finger3_root_name, armature_object)
        root_bone4 = RigService.find_pose_bone_by_name(finger4_root_name, armature_object)

        pose_bone.location = (root_bone3.location + root_bone4.location) / 2

        RigService.display_pose_bone_as_empty(armature_object, bone_name, 'CIRCLE')

        scale = 0.6
        if hasattr(pose_bone, "custom_shape_scale"):
            pose_bone.custom_shape_scale = scale
            _LOG.debug("scale", pose_bone.custom_shape_scale)
        if hasattr(pose_bone, "custom_shape_scale_xyz"):
            pose_bone.custom_shape_scale_xyz = [scale, scale, scale]
            _LOG.debug("scale", pose_bone.custom_shape_scale_xyz)

        for i in range(3):
            pose_bone.lock_location[i] = True
            pose_bone.lock_scale[i] = True


    # ---- METHODS FOR REMOVING AND RESETTING

    def remove_ik(self, armature_object):
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
        bpy.ops.object.mode_set(mode='POSE', toggle=False)


    def _clear_finger_grip(self, finger_number, armature_object):
        bone_name = self._get_grip_bone_name_for_finger(finger_number)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Grip bone to remove, if any", bone)
        if bone:
            armature_object.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _clear_master_grip(self, armature_object):
        bone_name = self._get_master_grip_bone_name()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Master grip bone to remove, if any", bone)
        if bone:
            armature_object.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _clear_finger_ik(self, finger_number, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone_name = self._get_point_ik_bone_name_for_finger(finger_number)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Point bone to remove, if any", bone)
        if bone:
            armature_object.data.edit_bones.remove(bone)

    def _clear_all_finger_constraints(self, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for finger_number in [1, 2, 3, 4, 5]:
            bones_to_clear = self.get_reverse_list_of_bones_in_finger(finger_number)
            for bone_name in bones_to_clear:
                RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)

    def _remove_grip(self, armature_object):
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            self._clear_finger_grip(finger_number, armature_object)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bones_to_show = self.get_reverse_list_of_bones_in_finger(finger_number)
            self._show_bones(armature_object, bones_to_show)

    def _remove_point(self, armature_object):
        _LOG.enter()
        for finger_number in [1, 2, 3, 4, 5]:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            self._clear_finger_ik(finger_number, armature_object)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bones_to_show = self.get_reverse_list_of_bones_in_finger(finger_number)
            self._show_bones(armature_object, bones_to_show)



    # ---- BONE NAMES

    def _get_point_ik_bone_name_for_finger(self, finger_number):
        return self.which_hand + "_finger" + str(finger_number) + "_point_ik"

    def _get_grip_bone_name_for_finger(self, finger_number):
        return self.which_hand + "_finger" + str(finger_number) + "_grip"

    def _get_master_grip_bone_name(self):
        return self.which_hand + "_master_grip"

    def _get_master_ik_bone_name(self):
        return self.which_hand + "_finger_master_ik"



    # ---- GENERAL METHODS

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

    @staticmethod
    def get_instance(which_hand, settings, rigtype="Default"):
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        if rigtype == "Default":
            from mpfb.services.righelpers.fingerhelpers.defaultfingerhelpers import DefaultFingerHelpers  # pylint: disable=C0415
            return DefaultFingerHelpers(which_hand, settings)
        return FingerHelpers(which_hand, settings)



    # ---- ABSTRACT METHODS INSTANCED PER RIG TYPE

    def get_first_segment_name_of_finger(self, finger_number):
        """Abstract method for getting the name of the innermost bone in a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("get_first_segment_name_of_finger")

    def get_last_segment_name_of_finger(self, finger_number):
        """Abstract method for getting the name of the finger tip bone, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("get_last_segment_name_of_finger")

    def get_immediate_parent_name_of_finger(self, finger_number):
        """Abstract method for getting the name of the immediate parent of a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_immediate_parent_name_of_finger() method must be overriden by the rig class")

    def get_finger_segment_count(self, finger_number):
        """Abstract method for getting the number of bones in a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_finger_count() method must be overriden by the rig class")

    def add_finger_rotation_constraints(self, finger_number, armature_object):
        """Abstract method for setting constraints for a finger, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the add_finger_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_finger(self, finger_number):
        """Abstract method for getting a list of bones from a finger starting from the tip, must be overriden by rig specific implementation classes."""
        raise NotImplementedError("the get_reverse_list_of_bones_in_finger() method must be overriden by the rig class")
