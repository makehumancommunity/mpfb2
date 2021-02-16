
import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("fingerik.fingerik")

from mpfb.services.rigservice import RigService
from mpfb.ui.ikfk import IkFkProperties

_LOG.set_level(LogService.DUMP)

class FingerIk():

    def __init__(self, which_hand, settings):
        _LOG.debug("Constructing FingerIk object")
        self.which_hand = which_hand
        self.settings = settings
        self._bone_info = dict()
        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object):
        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        if self.settings["finger_ik_type"] == "GRIP":
            self._apply_finger_ik(armature_object, True)

        if self.settings["finger_ik_type"] == "MASTER":
            self._apply_finger_ik(armature_object, True)
            # TODO: Master bone

        if self.settings["finger_ik_type"] == "POINT":
            self._apply_finger_ik(armature_object, False)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def remove_ik(self, armature_object):
        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        mode = str(IkFkProperties.get_value("finger_mode", entity_reference=armature_object)).strip()

        _LOG.debug("mode is", mode)

        if mode == "GRIP":
            self._remove_finger_ik(armature_object)

        if mode == "MASTER":
            # TODO: remove master
            self._remove_finger_ik(armature_object)

        if mode == "POINT":
            self._remove_finger_ik(armature_object)

        _LOG.debug("Done")
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    @staticmethod
    def get_instance(which_hand, settings, rigtype="Default"):
        _LOG.enter()
        if rigtype == "Default":
            from mpfb.entities.fingerik.defaultfingerik import DefaultFingerIk  # pylint: disable=C0415
            return DefaultFingerIk(which_hand, settings)
        return FingerIk(which_hand, settings)

    def _get_point_ik_bone_name_for_finger(self, finger_number):
        return self.which_hand + "_finger" + str(finger_number) + "_point_ik"

    def _get_grip_ik_bone_name_for_finger(self, finger_number):
        return self.which_hand + "_finger" + str(finger_number) + "_grip_ik"

    def _get_master_ik_bone_name(self):
        return self.which_hand + "_finger_master_ik"

    def _create_point_ik_bone(self, finger_number, armature_object):
        _LOG.enter()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        hand_name = self.get_hand_name()
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
        RigService.display_pose_bone_as_empty(armature_object, bone_name, type="SPHERE")
        pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)

        scales = [0.5, 0.5, 0.5, 0.5, 0.7]
        pose_bone.custom_shape_scale = scales[finger_number - 1]
        _LOG.debug("scale", pose_bone.custom_shape_scale)

    def _create_grip_ik_bone(self, finger_number, armature_object):
        _LOG.enter()

        self._create_point_ik_bone(finger_number, armature_object)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        hand_name = self.get_hand_name()
        tip_name = self.get_last_segment_name_of_finger(finger_number)
        root_name = self.get_first_segment_name_of_finger(finger_number)

        head = self._bone_info["pose_bones"][root_name]["head"]
        tail = self._bone_info["pose_bones"][tip_name]["tail"]
        roll = self._bone_info["edit_bones"][root_name]["roll"]

        bone_name = self._get_grip_ik_bone_name_for_finger(finger_number)
        bones = armature_object.data.edit_bones
        bone = bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        bone.roll = roll

        point_name = self._get_point_ik_bone_name_for_finger(finger_number)
        point_bone = RigService.find_edit_bone_by_name(point_name, armature_object)
        point_bone.parent = bone

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        bone_name = self._get_grip_ik_bone_name_for_finger(finger_number)
        pose_bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
        pose_bone.lock_ik_x = True
        pose_bone.lock_ik_y = True
        pose_bone.lock_ik_z = True

    def _set_finger_ik_target(self, finger_number, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        tip_name = self.get_last_segment_name_of_finger(finger_number)
        ik_name = self._get_point_ik_bone_name_for_finger(finger_number)
        ik_bone = RigService.find_pose_bone_by_name(ik_name, armature_object)
        self.add_finger_rotation_constraints(finger_number, armature_object)
        RigService.add_ik_constraint_to_pose_bone(tip_name, armature_object, ik_bone, chain_length)

    def _clear_finger_ik_target(self, finger_number, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones_to_clear = self.get_reverse_list_of_bones_in_finger(finger_number)
        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone_name = self._get_point_ik_bone_name_for_finger(finger_number)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Point bone to remove, if any", bone)
        if bone:
            armature_object.data.edit_bones.remove(bone)
        bone_name = self._get_grip_ik_bone_name_for_finger(finger_number)
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        _LOG.debug("Grip bone to remove, if any", bone)
        if bone:
            armature_object.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


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

    def _apply_finger_ik(self, armature_object, grip=True):
        _LOG.enter()
        for finger_number in [1,2,3,4,5]:
            if grip:
                self._create_grip_ik_bone(finger_number, armature_object)
                ik_name = self._get_grip_ik_bone_name_for_finger(finger_number)
            else:
                self._create_point_ik_bone(finger_number, armature_object)
                ik_name = self._get_point_ik_bone_name_for_finger(finger_number)

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            parent_name = self.get_immediate_parent_name_of_finger(finger_number)
            parent_bone = RigService.find_edit_bone_by_name(parent_name, armature_object)

            ik_bone = RigService.find_edit_bone_by_name(ik_name, armature_object)
            ik_bone.parent = parent_bone

            if grip:
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                ik_name = self._get_point_ik_bone_name_for_finger(finger_number)
                bone = armature_object.data.bones.get(ik_name)
                bone.hide = True

            chain_length = self.get_finger_segment_count(finger_number)
            self._set_finger_ik_target(finger_number, armature_object, chain_length)
            if self.settings["finger_hide_fk"]:
                bones_to_hide = self.get_reverse_list_of_bones_in_finger(finger_number)
                self._hide_bones(armature_object, bones_to_hide)

    def _reset_bones(self, bone_names, armature_object):
        _LOG.debug("preserve ik", self.settings["finger_preserve_ik"])
        for bone_name in bone_names:
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            # TODO: figure out how to set local rotation based on what the IK resulting rotation was

    def _remove_finger_ik(self, armature_object):
        _LOG.enter()
        for finger_number in [1,2,3,4,5]:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            self._clear_finger_ik_target(finger_number, armature_object)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bones_to_show = self.get_reverse_list_of_bones_in_finger(finger_number)
            self._show_bones(armature_object, bones_to_show)

    def get_first_segment_name_of_finger(self, finger_number):
        raise NotImplementedError("get_first_segment_name_of_finger")

    def get_last_segment_name_of_finger(self, finger_number):
        raise NotImplementedError("get_last_segment_name_of_finger")

    def get_immediate_parent_name_of_finger(self, finger_number):
        raise NotImplementedError("the get_immediate_parent_name_of_finger() method must be overriden by the rig class")

    def get_hand_name(self):
        raise NotImplementedError("the get_hand_name() method must be overriden by the rig class")

    def get_finger_segment_count(self, finger_number):
        raise NotImplementedError("the get_finger_count() method must be overriden by the rig class")

    def add_finger_rotation_constraints(self, finger_number, armature_object):
        raise NotImplementedError("the add_finger_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_finger(self, finger_number):
        raise NotImplementedError("the get_reverse_list_of_bones_in_finger() method must be overriden by the rig class")
