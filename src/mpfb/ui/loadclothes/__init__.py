"""This module contains functionality for loading clothes."""

from ...services import LogService
_LOG = LogService.get_logger("loadclothes.init")
_LOG.trace("initializing load clothes module")

from .loadclothespanel import MPFB_PT_Load_Clothes_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Load_Clothes_Operator"
    ]
