"""This module provides functionality for converting a rig to rigify.

The code is based on an approach suggested by Andrea Rossato in https://www.youtube.com/watch?v=zmsuLD7hAUA
"""

import bpy

from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
_LOG = LogService.get_logger("rigifyhelpers.rigifyhelpers")

from mpfb.services.rigservice import RigService

class RigifyHelpers():

    """This is the abstract rig type independent base class for working with
    rigify. You will want to call the static get_instance() method to get a
    concrete implementation for the specific rig you are working with."""

    def __init__(self, settings):
        """Get a new instance of RigifyHelpers. You should not call this directly.
        Use get_instance() instead."""

        _LOG.debug("Constructing RigifyHelpers object")
        self.settings = settings
        _LOG.dump("settings", self.settings)

    @staticmethod
    def get_instance(settings, rigtype="Default"):
        """Get an implementation instance matching the rig type."""

        _LOG.enter()
        from mpfb.services.rigifyhelpers.gameenginerigifyhelpers import GameEngineRigifyHelpers  # pylint: disable=C0415
        return GameEngineRigifyHelpers(settings)

    def convert_to_rigify(self, armature_object):
        _LOG.enter()

        self._setup_spine(armature_object)
        self._setup_arms(armature_object)
        self._setup_legs(armature_object)
        self._setup_shoulders(armature_object)
        self._setup_head(armature_object)
        self._setup_fingers(armature_object)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.pose.rigify_generate()

        rigify_object = bpy.context.active_object
        rigify_object.show_in_front = True

        child_meshes = ObjectService.get_list_of_children(armature_object)
        for child_mesh in child_meshes:
            self._adjust_mesh_for_rigify(child_mesh, rigify_object)

        bpy.data.objects.remove(armature_object, do_unlink=True)

    def _adjust_mesh_for_rigify(self, child_mesh, rigify_object):
        all_relevant_bones = []
        all_relevant_bones.extend(self.get_list_of_spine_bones())
        all_relevant_bones.extend(self.get_list_of_head_bones())
        for side in [True, False]:
            all_relevant_bones.extend(self.get_list_of_leg_bones(side))
            all_relevant_bones.extend(self.get_list_of_arm_bones(side))
            all_relevant_bones.extend(self.get_list_of_shoulder_bones(side))
            for i in range(5):
                all_relevant_bones.extend(self.get_list_of_finger_bones(i, side))

        for bone_name in all_relevant_bones:
            if bone_name in child_mesh.vertex_groups:
                vertex_group = child_mesh.vertex_groups.get(bone_name)
                _LOG.debug("Renaming vertex group", (child_mesh.name, vertex_group.name, "DEF-" + vertex_group.name))
                vertex_group.name = "DEF-" + vertex_group.name

        for modifier in child_mesh.modifiers:
            if isinstance(modifier, bpy.types.ArmatureModifier):
                modifier.object = rigify_object

        child_mesh.parent = rigify_object

    def _set_use_connect_on_bones(self, armature_object, bone_names, exclude_first=True):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if exclude_first:
            bone_names = list(bone_names) # to modify a copy rather than the source list
            bone_names.pop(0)

        for bone_name in bone_names:
            _LOG.debug("About to set use_connect on", bone_name)
            edit_bone = RigService.find_edit_bone_by_name(bone_name, armature_object)
            edit_bone.use_connect = True
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _setup_spine(self, armature_object):
        _LOG.enter()
        spine = self.get_list_of_spine_bones() # pylint: disable=E1111
        _LOG.dump("Spine", spine)
        self._set_use_connect_on_bones(armature_object, spine)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_spine_bone = RigService.find_pose_bone_by_name(spine[0], armature_object)
        first_spine_bone.rigify_type = 'spines.basic_spine'
        first_spine_bone.rigify_parameters.segments = len(spine)
        # TODO: change layers

    def _setup_arms(self, armature_object):
        _LOG.enter()
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for side in [True, False]:
            arm = self.get_list_of_arm_bones(side) # pylint: disable=E1111
            _LOG.dump("Arm", arm)
            self._set_use_connect_on_bones(armature_object, arm)
            first_arm_bone = RigService.find_pose_bone_by_name(arm[0], armature_object)
            first_arm_bone.rigify_type = 'limbs.arm'
            #first_arm_bone.rigify_parameters.segments = len(arm)
        # TODO: change layers

    def _setup_legs(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            leg = self.get_list_of_leg_bones(side) # pylint: disable=E1111
            _LOG.dump("Leg", leg)
            self._set_use_connect_on_bones(armature_object, leg)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            first_leg_bone = RigService.find_pose_bone_by_name(leg[0], armature_object)
            first_leg_bone.rigify_type = 'limbs.paw'
            #first_arm_bone.rigify_parameters.segments = len(arm)

    def _setup_shoulders(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            shoulder = self.get_list_of_shoulder_bones(side) # pylint: disable=E1111
            _LOG.dump("Shoulder", shoulder)
            self._set_use_connect_on_bones(armature_object, shoulder)
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            first_shoulder_bone = RigService.find_pose_bone_by_name(shoulder[0], armature_object)
            first_shoulder_bone.rigify_type = 'basic.super_copy'

    def _setup_head(self, armature_object):
        _LOG.enter()
        head = self.get_list_of_head_bones() # pylint: disable=E1111
        _LOG.dump("Head", head)
        self._set_use_connect_on_bones(armature_object, head)
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        first_head_bone = RigService.find_pose_bone_by_name(head[0], armature_object)
        first_head_bone.rigify_type = 'spines.super_head'

    def _setup_fingers(self, armature_object):
        _LOG.enter()
        for side in [True, False]:
            for finger_number in range(5):
                finger = self.get_list_of_finger_bones(finger_number, side) # pylint: disable=E1111
                _LOG.dump("Finger", finger)
                self._set_use_connect_on_bones(armature_object, finger)
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                first_finger_bone = RigService.find_pose_bone_by_name(finger[0], armature_object)
                first_finger_bone.rigify_type = 'limbs.super_finger'

    def get_list_of_spine_bones(self):
        """Abstract method for getting a list of bones in the spine, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_spine_bones() method must be overriden by the rig class")

    def get_list_of_arm_bones(self, left_side=True):
        """Abstract method for getting a list of bones in an arm, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_arm_bones() method must be overriden by the rig class")

    def get_list_of_leg_bones(self, left_side=True):
        """Abstract method for getting a list of bones in a leg, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_leg_bones() method must be overriden by the rig class")

    def get_list_of_shoulder_bones(self, left_side=True):
        """Abstract method for getting a list of bones in a shoulder, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_shoulder_bones() method must be overriden by the rig class")

    def get_list_of_head_bones(self):
        """Abstract method for getting a list of bones in the head, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_head_bones() method must be overriden by the rig class")

    def get_list_of_finger_bones(self, finger_number, left_side=True):
        """Abstract method for getting a list of bones in a finger, must be overriden by rig specific implementation classes."""
        _LOG.enter()
        raise NotImplementedError("the get_list_of_finger_bones() method must be overriden by the rig class")
