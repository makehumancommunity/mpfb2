
import bpy

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("eyehelpers.defaulteyehelpers")

from mpfb.services.rigservice import RigService
from mpfb.services.righelpers.eyehelpers.eyehelpers import EyeHelpers

_ROTATION_LIMITS = {
        "lowereye01": {
            "X": [-5, 150],
            "Y": [-30, 30]
            },
        "lowereye02": {
            "Y": [-30, 30]
            },
        "uppereye01": {
            "X": [-120, 40],
            "Y": [-45, 45],
            "Z": [-70, 30]
            },
        "uppereye02": {
            "Y": [-45, 45]
            },
        "pelvis": {
            "X": [-15, 15],
            "Y": [-45, 33],
            "Z": [-10, 10]
            }
    }

_ROTATION_LOCKS = {
        "lowereye01": {
            "Z": True
            },
        "lowereye02": {
            "X": True,
            "Z": True
            },
        "uppereye02": {
            "X": True,
            "Z": True
            }
    }

class DefaultEyeHelpers(EyeHelpers):

    def __init__(self, settings):
        _LOG.debug("Constructing DefaultEyeHelpers object")
        EyeHelpers.__init__(self, settings)

    def get_head_name(self):
        return "head"

    def get_eye_name(self, right_side=True):
        if right_side:
            return "eye.R"
        else:
            return "eye.L"

    def get_eye_lower_lid_name(self, right_side=True):
        if right_side:
            return "orbicularis04.R"
        else:
            return "orbicularis04.L"

    def get_eye_upper_lid_name(self, right_side=True):
        if right_side:
            return "orbicularis03.R"
        else:
            return "orbicularis03.L"

    def add_eye_rotation_constraints(self, armature_object):
        pass

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
