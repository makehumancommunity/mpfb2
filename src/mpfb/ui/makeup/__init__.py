"""This module provides functionality for working with makeup."""

import os, bpy

from ...services import LogService

_LOG = LogService.get_logger("makeup.init")
_LOG.trace("initializing makeup module")

from .makeuppanel import MPFB_PT_MakeUp_Panel
from .operators import *

__all__ = [
    "MPFB_PT_MakeUp_Panel"
    ]
