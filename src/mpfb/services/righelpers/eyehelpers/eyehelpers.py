
import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("eyehelpers.eyehelpers")

from mpfb.services.rigservice import RigService
from mpfb.ui.righelpers import RigHelpersProperties


class EyeHelpers():

    def __init__(self, settings):
        _LOG.debug("Constructing EyeHelpers object")        
        self.settings = settings
        self._bone_info = dict()

        _LOG.dump("settings", self.settings)

    def apply_ik(self, armature_object):
        _LOG.enter()
        self._bone_info = RigService.get_bone_orientation_info_as_dict(armature_object)

        self._create_eye_ik_bones(armature_object)
        self._apply_ik_constraint(armature_object)
        
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

    def remove_ik(self, armature_object):
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
        _LOG.enter()
        if rigtype == "Default":
            from mpfb.services.righelpers.eyehelpers.defaulteyehelpers import DefaultEyeHelpers  # pylint: disable=C0415
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
         
        head_bone = RigService.find_edit_bone_by_name(self.get_head_name(), armature_object)
        bone.parent = head_bone
        
        # Needed to save bone
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        RigService.display_pose_bone_as_empty(armature_object, "left_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "right_eye_ik", "CIRCLE", scale=0.5)
        RigService.display_pose_bone_as_empty(armature_object, "eye_ik", "CIRCLE", scale=1.4)        
        

    def _apply_ik_constraint(self, armature_object):
        _LOG.enter()
        right = RigService.find_pose_bone_by_name("right_eye_ik", armature_object)
        left = RigService.find_pose_bone_by_name("left_eye_ik", armature_object)
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(True), armature_object, right, chain_length=1)
        RigService.add_ik_constraint_to_pose_bone(self.get_eye_name(False), armature_object, left, chain_length=1)

    def get_head_name(self):
        raise NotImplementedError("the get_head_name() method must be overriden by the rig class")

    def get_eye_name(self, right_side=True):
        raise NotImplementedError("the get_eye_name() method must be overriden by the rig class")

    def get_eye_lower_lid_name(self, right_side=True):
        raise NotImplementedError("the get_eye_lower_lid_name() method must be overriden by the rig class")

    def get_eye_upper_lid_name(self, right_side=True):
        raise NotImplementedError("the get_eye_upper_lid_name() method must be overriden by the rig class")

    def add_eye_rotation_constraints(self, armature_object):
        raise NotImplementedError("the add_eye_rotation_constraints() method must be overriden by the rig class")

