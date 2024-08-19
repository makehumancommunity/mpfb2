"""This module contains functionality for working with AI stuff."""

from ...services import LogService
_LOG = LogService.get_logger("ai.init")
_LOG.trace("initializing ai module")

from .aipanel import MPFB_PT_Ai_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Save_Openpose_Operator",
    "MPFB_PT_Ai_Panel"
    ]
