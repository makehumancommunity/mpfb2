"""This module provides functionality for creating makehuman targets."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("maketarget.init")
_LOG.trace("initializing maketarget module")

_ROOT = os.path.dirname(__file__)
_MAKETARGET_OBJECT_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
_MAKETARGET_OBJECT_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_MAKETARGET_OBJECT_PROPERTIES_DIR)

MakeTargetObjectProperties = BlenderConfigSet(_MAKETARGET_OBJECT_PROPERTIES, bpy.types.Object, prefix="MT_") # pylint: disable=C0103

from .maketargetpanel import MPFB_PT_MakeTarget_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeTarget_Panel",
    "MakeTargetObjectProperties"
    ]
