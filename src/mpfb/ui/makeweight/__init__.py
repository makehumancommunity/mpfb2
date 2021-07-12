"""This module provides functionality for creating makehuman weights."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("makeweight.init")
_LOG.trace("initializing makeweight module")

from .makeweightpanel import MPFB_PT_MakeWeight_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeWeight_Panel"
    ]
