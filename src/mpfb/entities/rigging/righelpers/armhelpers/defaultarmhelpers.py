"""This module contains the default rig's implementation of the arm helpers class"""

import bpy

from .....services import LogService
_LOG = LogService.get_logger("armhelpers.defaultarmhelpers")

from .....services import RigService
from mpfb.entities.rigging.righelpers.armhelpers.armhelpers import ArmHelpers

_ROTATION_LIMITS = {
        "lowerarm01": {
            "X": [-40, 125],
            "Y": [-45, 45]
            },
        "lowerarm02": {
            "Y": [-45, 45]
            },
        "upperarm01": {
            "X": [-45, 90],
            "Y": [-45, 45]
            },
        "upperarm02": {
            "Y": [-45, 45]
            },
        "shoulder01": {
            "X": [-30, 60],
            "Y": [-60, 60],
            "Z": [-20, 40]
            },
        "clavicle": {
            "X":[-20, 30],
            "Y":[-20, 20],
            "Z":[-40, 5]
            }
    }

_ROTATION_LOCKS = {
        "lowerarm02": {
            "X": True,
            "Z": True
            },
        "upperarm02": {
            "X": True,
            "Z": True
            }
    }


class DefaultArmHelpers(ArmHelpers):

    """The rig specific implementation of arm helpers matching the Default and Default-no-toes rigs."""

    def __init__(self, which_arm, settings):
        """Get a new instance of the class. You should not call this directly. Instead, use the get_instance()
        method in the abstract base class."""

        _LOG.debug("Constructing DefaultArmHelpers object")
        ArmHelpers.__init__(self, which_arm, settings)

    def _sided(self, name):
        if self.which_arm == "right":
            return name + ".R"
        return name + ".L"

    def get_lower_arm_name(self):
        return self._sided("lowerarm02")

    def get_upper_arm_name(self):
        return self._sided("upperarm02")

    def get_shoulder_name(self):
        return self._sided("shoulder01")

    def get_hand_name(self):
        return self._sided("wrist")

    def get_shoulders_immediate_parent(self):
        return "spine01"

    def get_root(self):
        return "root"

    def get_lower_arm_count(self):
        return 2

    def get_upper_arm_count(self):
        return 2

    def get_shoulder_count(self):
        return 2

    def _sided_rotation_limit(self, unsided_name, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if unsided_name in _ROTATION_LIMITS:
            for axis_name in _ROTATION_LIMITS[unsided_name].keys():
                name = self._sided(unsided_name)
                limits = _ROTATION_LIMITS[unsided_name][axis_name]
                RigService.set_ik_rotation_limits(name, armature_object, axis=axis_name, min_angle=limits[0], max_angle=limits[1])

    def _sided_rotation_lock(self, unsided_name, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if unsided_name in _ROTATION_LOCKS:
            locks = _ROTATION_LOCKS[unsided_name]
            x = "X" in locks and _ROTATION_LOCKS[unsided_name]["X"]
            y = "Y" in locks and _ROTATION_LOCKS[unsided_name]["Y"]
            z = "Z" in locks and _ROTATION_LOCKS[unsided_name]["Z"]
            name = self._sided(unsided_name)
            RigService.add_ik_rotation_lock_to_pose_bone(name, armature_object, lock_x=x, lock_y=y, lock_z=z)

    def add_lower_arm_rotation_constraints(self, armature_object):
        self._sided_rotation_lock("lowerarm02", armature_object)
        self._sided_rotation_limit("lowerarm01", armature_object)

    def add_upper_arm_rotation_constraints(self, armature_object):
        self._sided_rotation_lock("upperarm02", armature_object)
        self._sided_rotation_limit("upperarm01", armature_object)

    def add_shoulder_rotation_constraints(self, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        self._sided_rotation_limit("shoulder01", armature_object)
        self._sided_rotation_limit("clavicle", armature_object)

    def get_reverse_list_of_bones_in_arm(self, include_hand=True, include_lower_arm=True, include_upper_arm=True, include_shoulder=True):
        bone_list = []
        if include_shoulder:
            bone_list.append(self._sided("clavicle"))
            bone_list.append(self._sided("shoulder01"))
        if include_upper_arm:
            bone_list.append(self._sided("upperarm01"))
            bone_list.append(self._sided("upperarm02"))
        if include_lower_arm:
            bone_list.append(self._sided("lowerarm01"))
            bone_list.append(self._sided("lowerarm02"))
        if include_hand:
            bone_list.append(self._sided("wrist"))
        return bone_list
