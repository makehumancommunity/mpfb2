"""This module provides functionality for creating new humans."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("newhuman.init")
_LOG.trace("initializing new human module")

from .frompresetspanel import MPFB_PT_From_Presets_Panel
from .newhumanpanel import MPFB_PT_NewHuman_Panel
from .operators import *

__all__ = [
    "MPFB_PT_NewHuman_Panel",
    "MPFB_PT_From_Presets_Panel"
    ]
