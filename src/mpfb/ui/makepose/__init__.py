"""This module provides functionality for creating makehuman poses."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = _LogService.get_logger("makepose.init")
_LOG.trace("initializing makepose module")

_ROOT = os.path.dirname(__file__)
_MAKEPOSE_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
_MAKEPOSE_PROPERTIES = SceneConfigSet.get_definitions_in_json_directory(_MAKEPOSE_PROPERTIES_DIR)

MakePoseProperties = SceneConfigSet(_MAKEPOSE_PROPERTIES, prefix="MP_") # pylint: disable=C0103

from .makeposepanel import MPFB_PT_MakePose_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakePose_Panel",
    "MakePoseProperties"
    ]
