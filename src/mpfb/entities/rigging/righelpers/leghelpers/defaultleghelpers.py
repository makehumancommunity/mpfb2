"""This module constains the rig specific implementation for the default rig."""

import bpy

from .....services import LogService
_LOG = LogService.get_logger("leghelpers.defaultleghelpers")

from .....services import RigService
from mpfb.entities.rigging.righelpers.leghelpers.leghelpers import LegHelpers

_ROTATION_LIMITS = {
        "lowerleg01": {
            "X": [-5, 150],
            "Y": [-30, 30]
            },
        "lowerleg02": {
            "Y": [-30, 30]
            },
        "upperleg01": {
            "X": [-120, 40],
            "Y": [-45, 45],
            "Z": [-130, 30]
            },
        "upperleg02": {
            "Y": [-45, 45]
            },
        "pelvis": {
            "X": [-15, 15],
            "Y": [-45, 33],
            "Z": [-10, 10]
            }
    }

_REVERSE_LIMITS = {
        "upperleg01.R": {
            "Z": True
            }
    }

_ROTATION_LOCKS = {
        "lowerleg01": {
            "Z": True
            },
        "lowerleg02": {
            "X": True,
            "Z": True
            },
        "upperleg02": {
            "X": True,
            "Z": True
            }
    }


class DefaultLegHelpers(LegHelpers):

    """The rig specific implementation of arm helpers matching the Default and Default-no-toes rigs."""

    def __init__(self, which_leg, settings):
        """Get a new instance of the class. You should not call this directly. Instead, use the get_instance()
        method in the abstract base class."""

        _LOG.debug("Constructing DefaultLegHelpers object")
        LegHelpers.__init__(self, which_leg, settings)

    def _sided(self, name):
        if self.which_leg == "right":
            return name + ".R"
        return name + ".L"

    def get_lower_leg_name(self):
        return self._sided("lowerleg02")

    def get_upper_leg_name(self):
        return self._sided("upperleg02")

    def get_hip_name(self):
        return self._sided("pelvis")

    def get_foot_name(self):
        return self._sided("foot")

    def get_lower_leg_count(self):
        return 2

    def get_upper_leg_count(self):
        return 2

    def get_hip_count(self):
        return 1

    def get_root(self):
        return "root"

    def _sided_rotation_limit(self, unsided_name, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        if unsided_name in _ROTATION_LIMITS:
            for axis_name in _ROTATION_LIMITS[unsided_name].keys():
                name = self._sided(unsided_name)
                limits = _ROTATION_LIMITS[unsided_name][axis_name]
                if name in _REVERSE_LIMITS:
                    if axis_name in _REVERSE_LIMITS[name] and _REVERSE_LIMITS[name][axis_name]:
                        limits1 = [-limits[1], -limits[0]]
                        limits = limits1
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

    def add_lower_leg_rotation_constraints(self, armature_object):
        self._sided_rotation_lock("lowerleg02", armature_object)
        self._sided_rotation_limit("lowerleg01", armature_object)

    def add_upper_leg_rotation_constraints(self, armature_object):
        self._sided_rotation_lock("upperleg02", armature_object)
        self._sided_rotation_limit("upperleg01", armature_object)

    def add_hip_rotation_constraints(self, armature_object):
        bpy.ops.object.mode_set(mode='POSE', toggle=False)

        self._sided_rotation_limit("pelvis", armature_object)
        self._sided_rotation_limit("clavicle", armature_object)

    def get_reverse_list_of_bones_in_leg(self, include_foot=True, include_lower_leg=True, include_upper_leg=True, include_hip=True):
        bone_list = []
        if include_hip:
            bone_list.append(self._sided("pelvis"))
        if include_upper_leg:
            bone_list.append(self._sided("upperleg01"))
            bone_list.append(self._sided("upperleg02"))
        if include_lower_leg:
            bone_list.append(self._sided("lowerleg01"))
            bone_list.append(self._sided("lowerleg02"))
        if include_foot:
            bone_list.append(self._sided("foot"))
        return bone_list
