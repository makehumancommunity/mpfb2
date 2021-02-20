
import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("armhelpers.armhelpers")

from mpfb.services.rigservice import RigService
from mpfb.ui.righelpers import RigHelpersProperties


class ArmHelpers():

    def __init__(self, which_arm, settings):
        _LOG.debug("Constructing ArmHelpers object")
        self.which_arm = which_arm
        self.settings = settings
        self._bone_info = dict()
        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object):
        _LOG.enter()

        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        if self.settings["arm_helpers_type"] == "LOWERUPPER":
            self._apply_lower_upper(armature_object)

        if self.settings["arm_helpers_type"] == "LOWERUPPERSHOULDER":
            self._apply_lower_upper_shoulder(armature_object)

        if self.settings["arm_helpers_type"] == "ARMWITHPOLE":
            self._apply_arm_with_pole(armature_object)

        if self.settings["arm_helpers_type"] == "ARMANDSHOULERWITHPOLE":
            self._remove_arm_and_shoulder_with_pole(armature_object)

        if self.settings["arm_helpers_type"] == "ARMCHAIN":
            self._apply_arm_chain(armature_object)

        if self.settings["arm_helpers_type"] == "SHOULDERCHAIN":
            self._apply_shoulder_chain(armature_object)

        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def remove_ik(self, armature_object):
        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)
        mode = str(RigHelpersProperties.get_value("arm_mode", entity_reference=armature_object)).strip()

        _LOG.debug("mode is", mode)

        if mode == "LOWERUPPER":
            _LOG.debug("pos 1")
            self._remove_lower_upper(armature_object)
            _LOG.debug("pos 2")

        if mode == "LOWERUPPERSHOULDER":
            self._remove_lower_upper_shoulder(armature_object)

        #if mode == "ARMWITHPOLE":
        #    self._remove_arm_with_pole(armature_object)

        #if mode == "ARMANDSHOULERWITHPOLE":
        #    self._remove_arm_and_shoulder_with_pole(armature_object)

        if mode == "ARMCHAIN":
            self._remove_arm_chain(armature_object)

        if mode == "SHOULDERCHAIN":
            self._remove_shoulder_chain(armature_object)

        _LOG.debug("Done")
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    @staticmethod
    def get_instance(which_arm, settings, rigtype="Default"):
        _LOG.enter()
        if rigtype == "Default":
            from mpfb.services.righelpers.armhelpers.defaultarmhelpers import DefaultArmHelpers  # pylint: disable=C0415
            return DefaultArmHelpers(which_arm, settings)
        return ArmHelpers(which_arm, settings)

    def _create_hand_ik_bone(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        hand_name = self.get_hand_name()

        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_arm + "_hand_ik")
        bone.head = self._bone_info["pose_bones"][hand_name]["head"]
        bone.tail = self._bone_info["pose_bones"][hand_name]["tail"]
        bone.roll = self._bone_info["edit_bones"][hand_name]["roll"]
        bone.matrix = self._bone_info["pose_bones"][hand_name]["matrix"]

        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_hand_ik", type="CIRCLE")

        if self.settings["arm_target_rotates_hand"]:

            constraint = RigService.add_bone_constraint_to_pose_bone(self.get_hand_name(), armature_object, "COPY_ROTATION")
            constraint.target = armature_object
            constraint.subtarget = self.which_arm + "_hand_ik"

            if self.settings["arm_target_rotates_lower_arm"]:
                lower_arm_segments = self.get_reverse_list_of_bones_in_arm(False, True, False, False)
                for name in lower_arm_segments:
                    constraint = RigService.add_bone_constraint_to_pose_bone(name, armature_object, "COPY_ROTATION")
                    constraint.target = armature_object
                    constraint.subtarget = self.which_arm + "_hand_ik"
                    constraint.use_x = False
                    constraint.use_z = False
                    constraint.influence = 0.4 / len(lower_arm_segments)

    def _create_elbow_ik_bone(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_arm + "_elbow_ik")

        bone.head = self._bone_info["pose_bones"][self.get_upper_arm_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_upper_arm_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length / 3
        bone.head = bone.head + length

        # TODO: implement parenting

        #if self.settings["arm_outmost_parent"]:
        #    lower_arm_name = self.get_lower_arm_name()
        #    lower_arm_bone = RigService.find_edit_bone_by_name(lower_arm_name, armature_object)
        #    bone.parent = lower_arm_bone

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_elbow_ik", type="SPHERE")

    def _create_shoulder_ik_bone(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bones = armature_object.data.edit_bones
        bone = bones.new(self.which_arm + "_shoulder_ik")

        bone.head = self._bone_info["pose_bones"][self.get_shoulder_name()]["head"]
        bone.tail = self._bone_info["pose_bones"][self.get_shoulder_name()]["tail"]

        length = bone.tail - bone.head
        bone.tail = bone.tail + length * 0.65
        bone.head = bone.head + length

        # TODO: implement parenting

        #if self.settings["arm_outmost_parent"]:
        #    lower_arm_name = self.get_lower_arm_name()
        #    lower_arm_bone = RigService.find_edit_bone_by_name(lower_arm_name, armature_object)
        #    bone.parent = lower_arm_bone

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        RigService.display_pose_bone_as_empty(armature_object, self.which_arm + "_shoulder_ik", type="SPHERE")


    def _set_lower_arm_ik_target(self, armature_object, chain_length, pole_target=None):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        lower_arm_name = self.get_lower_arm_name()
        hand_name = self.which_arm + "_hand_ik"
        hand_bone = RigService.find_pose_bone_by_name(hand_name, armature_object)
        self.add_lower_arm_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(lower_arm_name, armature_object, hand_bone, chain_length)

    def _set_upper_arm_ik_target(self, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        upper_arm_name = self.get_upper_arm_name()
        elbow_name = self.which_arm + "_elbow_ik"
        elbow_bone = RigService.find_pose_bone_by_name(elbow_name, armature_object)
        self.add_upper_arm_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(upper_arm_name, armature_object, elbow_bone, chain_length)

    def _set_shoulder_ik_target(self, armature_object, chain_length):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        shoulder_name = self.get_shoulder_name()
        shoulder_ik_name = self.which_arm + "_shoulder_ik"
        shoulder_bone = RigService.find_pose_bone_by_name(shoulder_ik_name, armature_object)
        self.add_shoulder_rotation_constraints(armature_object)
        RigService.add_ik_constraint_to_pose_bone(shoulder_name, armature_object, shoulder_bone, chain_length)

    def _clear_lower_arm_ik_target(self, armature_object, pole_target=None):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones_to_clear = self.get_reverse_list_of_bones_in_arm(True, True, False, False)
        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone_name = self.which_arm + "_hand_ik"
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        armature_object.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _clear_upper_arm_ik_target(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones_to_clear = self.get_reverse_list_of_bones_in_arm(False, False, True, False)
        for bone_name in bones_to_clear:
            _LOG.debug("Will attempt to clear constraints from", bone_name)
            RigService.remove_all_constraints_from_pose_bone(bone_name, armature_object)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bone_name = self.which_arm + "_elbow_ik"
        bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
        armature_object.data.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _hide_bones(self, armature_object, bone_list):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for name in bone_list:
            bone = armature_object.data.bones.get(name)
            bone.hide = True

    def _show_bones(self, armature_object, bone_list):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for name in bone_list:
            bone = armature_object.data.bones.get(name)
            bone.hide = False

    def _apply_lower_upper(self, armature_object):
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        self._create_elbow_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        self._set_upper_arm_ik_target(armature_object, self.get_upper_arm_count())
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_lower_upper_shoulder(self, armature_object):
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

    def _apply_arm_with_pole(self, armature_object):
        pass

    def _apply_arm_and_shoulder_with_pole(self, armature_object):
        pass

    def _apply_arm_chain(self, armature_object):
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, False)
            self._hide_bones(armature_object, bones_to_hide)

    def _apply_shoulder_chain(self, armature_object):
        _LOG.enter()
        self._create_hand_ik_bone(armature_object)
        chain_length_entire_arm = self.get_lower_arm_count() + self.get_upper_arm_count() + self.get_shoulder_count()
        self._set_lower_arm_ik_target(armature_object, chain_length_entire_arm)
        if self.settings["hide_fk"]:
            bones_to_hide = self.get_reverse_list_of_bones_in_arm(True, True, True, True)
            self._hide_bones(armature_object, bones_to_hide)

    def _reset_bones(self, bone_names, armature_object):
        _LOG.debug("preserve ik", self.settings["preserve_ik"])
        for bone_name in bone_names:
            bone = RigService.find_pose_bone_by_name(bone_name, armature_object)
            # TODO: figure out how to set local rotation based on what the IK resulting rotation was

    def _remove_lower_upper(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bones_to_show = self.get_reverse_list_of_bones_in_arm(True, True, True, False)
        self._show_bones(armature_object, bones_to_show)
        self._clear_upper_arm_ik_target(armature_object)
        self._clear_lower_arm_ik_target(armature_object)
        # self._reset_bones(bones_to_show, armature_object)

    def _remove_lower_upper_shoulder(self, armature_object):
        pass

    def _remove_arm_with_pole(self, armature_object):
        pass

    def _remove_arm_and_shoulder_with_pole(self, armature_object):
        pass

    def _remove_arm_chain(self, armature_object):
        pass

    def _remove_shoulder_chain(self, armature_object):
        pass

    def get_lower_arm_name(self):
        raise NotImplementedError("the get_lower_arm_name() method must be overriden by the rig class")

    def get_upper_arm_name(self):
        raise NotImplementedError("the get_upper_arm_name() method must be overriden by the rig class")

    def get_shoulder_name(self):
        raise NotImplementedError("the get_shoulder_name() method must be overriden by the rig class")

    def get_hand_name(self):
        raise NotImplementedError("the get_hand_name() method must be overriden by the rig class")

    def get_lower_arm_count(self):
        raise NotImplementedError("the get_lower_arm_count() method must be overriden by the rig class")

    def get_upper_arm_count(self):
        raise NotImplementedError("the get_upper_arm_count() method must be overriden by the rig class")

    def get_shoulder_count(self):
        raise NotImplementedError("the get_lower_arm_count() method must be overriden by the rig class")

    def add_lower_arm_rotation_constraints(self, armature_object):
        raise NotImplementedError("the add_lower_arm_rotation_constraints() method must be overriden by the rig class")

    def add_upper_arm_rotation_constraints(self, armature_object):
        raise NotImplementedError("the add_upper_arm_rotation_constraints() method must be overriden by the rig class")

    def add_shoulder_rotation_constraints(self, armature_object):
        raise NotImplementedError("the add_shoulder_rotation_constraints() method must be overriden by the rig class")

    def get_reverse_list_of_bones_in_arm(self, include_hand=True, include_lower_arm=True, include_upper_arm=True, include_shoulder=True):
        raise NotImplementedError("the get_reverse_list_of_bones_in_arm() method must be overriden by the rig class")
