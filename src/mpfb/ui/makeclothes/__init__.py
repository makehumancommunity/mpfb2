"""This module provides functionality for creating makehuman clothes."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("makeclothes.init")
_LOG.trace("initializing makeclothes module")

_ROOT = os.path.dirname(__file__)
_MAKECLOTHES_OBJECT_PROPERTIES_DIR = os.path.join(_ROOT, "objectproperties")
_MAKECLOTHES_OBJECT_PROPERTIES = BlenderConfigSet.get_definitions_in_json_directory(_MAKECLOTHES_OBJECT_PROPERTIES_DIR)

MakeClothesObjectProperties = BlenderConfigSet(_MAKECLOTHES_OBJECT_PROPERTIES, bpy.types.Object, prefix="MC_") # pylint: disable=C0103

from .makeclothespanel import MPFB_PT_MakeClothes_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeClothes_Panel"
    ]
