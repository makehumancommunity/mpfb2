"""This module provides functionality for creating makehuman materials."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("makeskin.init")
_LOG.trace("initializing makeskin module")

_ROOT = os.path.dirname(__file__)
_MAKESKIN_OBJECT_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
_MAKESKIN_OBJECT_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_MAKESKIN_OBJECT_PROPERTIES_DIR)

MakeSkinObjectProperties = BlenderConfigSet(_MAKESKIN_OBJECT_PROPERTIES, bpy.types.Object, prefix="MS_") # pylint: disable=C0103

from .makeskinpanel import MPFB_PT_MakeSkin_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeSkin_Panel"
    ]
