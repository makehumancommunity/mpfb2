"""This module provides functionality for creating new humans."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("newhuman.init")
_LOG.trace("initializing new human module")

_ROOT = os.path.dirname(__file__)
_NEWHUMAN_OBJECT_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
_NEWHUMAN_OBJECT_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_NEWHUMAN_OBJECT_PROPERTIES_DIR)

NewHumanObjectProperties = BlenderConfigSet(_NEWHUMAN_OBJECT_PROPERTIES, bpy.types.Object, prefix="NH_") # pylint: disable=C0103

from .newhumanpanel import MPFB_PT_NewHuman_Panel
from .operators import *

__all__ = [
    "MPFB_PT_NewHuman_Panel",
    "NewHumanObjectProperties"
    ]
