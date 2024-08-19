"""This module provides UI for saving/loading eye material settings"""

from ...services import LogService
_LOG = LogService.get_logger("savenodes.init")
_LOG.trace("initializing save nodes module")

from .eyesettingspanel import MPFB_PT_Eye_Settings_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Eye_Settings_Panel"
    ]
