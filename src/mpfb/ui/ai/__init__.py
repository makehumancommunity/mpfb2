"""This module contains functionality for working with AI stuff."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("ai.init")
_LOG.trace("initializing ai module")

from .aipanel import MPFB_PT_Ai_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Save_Openpose_Operator",
    "MPFB_PT_Ai_Panel"
    ]
