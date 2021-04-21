"""This module provides functionality adding rigs."""

import os, bpy
from mpfb.services import LogService as _LogService

_LOG = _LogService.get_logger("addrig.init")
_LOG.trace("initializing the addrig module")

from .addrigpanel import MPFB_PT_Add_Rig_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Add_Rig_Panel"
    ]
