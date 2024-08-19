"""This module contains the default rig's implementation of the finger helpers class"""

import bpy

from .....services import LogService
_LOG = LogService.get_logger("fingerhelpers.defaultfingerhelpers")

from .....services import RigService
from .fingerhelpers import FingerHelpers

_ROTATION_LIMITS = {
        "finger_first_segment": {
            "X": [-10, 90],
            "Y": [-5, 5],
            "Z": [-20, 20]
            },
        "finger_following_segments": {
            "X": [-10, 90]
            },
        "thumb_first_segment": {
            "X": [-20, 20],
            "Y": [-5, 5],
            "Z": [-50, 10]
            },
        "thumb_following_segments": {
            "X": [-5, 90]
            }
    }

_ROTATION_LOCKS = {
        "finger_first_segment": {},
        "finger_following_segments": {
            "Y": True,
            "Z": True
            },
        "thumb_first_segment": {},
        "thumb_following_segments": {
            "Y": True,
            "Z": True
            }
    }

_FINGER_PARENT = {
        1: "wrist",
        2: "metacarpal1",
        3: "metacarpal2",
        4: "metacarpal3",
        5: "metacarpal4"
    }


class DefaultFingerHelpers(FingerHelpers):

    """The rig specific implementation of finger helpers matching the Default and Default-no-toes rigs."""

    def __init__(self, which_hand, settings):
        """Get a new instance of the class. You should not call this directly. Instead, use the get_instance()
        method in the abstract base class."""

        _LOG.debug("Constructing DefaultFingerHelpers object")
        FingerHelpers.__init__(self, which_hand, settings)

    def _sided(self, name):
        if self.which_hand == "right":
            return name + ".R"
        return name + ".L"

    def _sided_rotation_limits(self, finger_number, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for segment_number in [1, 2, 3]:
            limits = {}
            if finger_number == 1:
                if segment_number == 1:
                    limits = _ROTATION_LIMITS["thumb_first_segment"]
                else:
                    limits = _ROTATION_LIMITS["thumb_following_segments"]
            else:
                if segment_number == 1:
                    limits = _ROTATION_LIMITS["finger_first_segment"]
                else:
                    limits = _ROTATION_LIMITS["finger_following_segments"]

            for axis_name in limits.keys():
                name = self._sided("finger" + str(finger_number) + "-" + str(segment_number))
                angles = limits[axis_name]
                RigService.set_ik_rotation_limits(name, armature_object, axis=axis_name, min_angle=angles[0], max_angle=angles[1])

    def _sided_rotation_locks(self, finger_number, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        for segment_number in [1, 2, 3]:
            locks = {}
            if finger_number == 1:
                if segment_number == 1:
                    locks = _ROTATION_LOCKS["thumb_first_segment"]
                else:
                    locks = _ROTATION_LOCKS["thumb_following_segments"]
            else:
                if segment_number == 1:
                    locks = _ROTATION_LOCKS["thumb_first_segment"]
                else:
                    locks = _ROTATION_LOCKS["thumb_following_segments"]

            x = "X" in locks and locks["X"]
            y = "Y" in locks and locks["Y"]
            z = "Z" in locks and locks["Z"]
            name = self._sided("finger" + str(finger_number) + "-" + str(segment_number))
            RigService.add_ik_rotation_lock_to_pose_bone(name, armature_object, lock_x=x, lock_y=y, lock_z=z)

    def add_finger_rotation_constraints(self, finger_number, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        self._sided_rotation_limits(finger_number, armature_object)
        self._sided_rotation_locks(finger_number, armature_object)

    def get_reverse_list_of_bones_in_finger(self, finger_number):
        bone_list = []
        for segment_number in [3, 2, 1]:
            bone_list.append(self._sided("finger" + str(finger_number) + "-" + str(segment_number)))
        return bone_list

    def get_first_segment_name_of_finger(self, finger_number):
        return self._sided("finger" + str(finger_number) + "-1")

    def get_last_segment_name_of_finger(self, finger_number):
        return self._sided("finger" + str(finger_number) + "-3")

    def get_immediate_parent_name_of_finger(self, finger_number):
        return self._sided(_FINGER_PARENT[finger_number])

    def get_finger_segment_count(self, finger_number):
        return 3

