"""This module provides UI for saving/loading eye material settings"""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("savenodes.init")
_LOG.trace("initializing save nodes module")

from .eyesettingspanel import MPFB_PT_Eye_Settings_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Eye_Settings_Panel"
    ]
