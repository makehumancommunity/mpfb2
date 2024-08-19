"""This module provides functionality for modeling humans."""

import os, bpy

from ...services import LogService
from ...services import BlenderConfigSet

_LOG = LogService.get_logger("model.init")
_LOG.trace("initializing the model module")

from .modelpanel import MPFB_PT_Model_Panel
from mpfb.ui.model.operators import *

__all__ = [
    "MPFB_PT_Model_Panel"
    ]
