"""This module contains functionality for loading clothes."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("loadclothes.init")
_LOG.trace("initializing load clothes module")

from .dirresourcespanel import MPFB_PT_Dir_Resources_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Dir_Resource_Operator"
    ]
