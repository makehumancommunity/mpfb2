"""This module contains the default rig's implementation of the eye helpers class"""

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

    """The rig specific implementation of eye helpers matching the Default and Default-no-toes rigs."""

    def __init__(self, settings):
        """Get a new instance of the class. You should not call this directly. Instead, use the get_instance()
        method in the abstract base class."""

        _LOG.debug("Constructing DefaultEyeHelpers object")
        EyeHelpers.__init__(self, settings)

    def get_head_name(self):
        return "head"

    def get_root_name(self):
        return "root"

    def get_eye_name(self, right_side=True):
        if right_side:
            return "eye.R"
        return "eye.L"

    def get_eye_lower_lid_name(self, right_side=True):
        if right_side:
            return "orbicularis04.R"
        return "orbicularis04.L"

    def get_eye_upper_lid_name(self, right_side=True):
        if right_side:
            return "orbicularis03.R"
        return "orbicularis03.L"

    def add_eye_rotation_constraints(self, armature_object):
        pass

    def _sided_rotation_limit(self, unsided_name, armature_object):
        # TODO: consider whether rotation limits are even relevant
        pass

    def _sided_rotation_lock(self, unsided_name, armature_object):
        # TODO: consider whether rotation locks are even relevant
        pass
