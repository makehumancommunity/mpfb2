"""This module provides functionality for modeling humans."""

import os, bpy

from mpfb.services import LogService as _LogService
from mpfb.services.blenderconfigset import BlenderConfigSet

_LOG = _LogService.get_logger("model.init")
_LOG.trace("initializing the model module")

from .modelpanel import MPFB_PT_Model_Panel

__all__ = [
    "MPFB_PT_Model_Panel"
    ]
