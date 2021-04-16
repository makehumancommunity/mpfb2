"""This module provides functionality for modeling humans."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("model.init")
_LOG.trace("initializing the model module")

#===============================================================================
# _ROOT = os.path.dirname(__file__)
# _NEWHUMAN_OBJECT_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
# _NEWHUMAN_OBJECT_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_NEWHUMAN_OBJECT_PROPERTIES_DIR)
#
# NewHumanObjectProperties = BlenderConfigSet(_NEWHUMAN_OBJECT_PROPERTIES, bpy.types.Object, prefix="NH_") # pylint: disable=C0103
#===============================================================================

from .modelpanel import MPFB_PT_Model_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Model_Panel",
    "MPFB_OT_AddTargetOperator"
    ]
