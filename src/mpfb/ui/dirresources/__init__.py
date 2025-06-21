"""This module contains functionality for loading clothes."""

from ...services import LogService
_LOG = LogService.get_logger("loadclothes.init")
_LOG.trace("initializing load clothes module")

from .dirresourcespanel import MPFB_PT_Dir_Resources_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Dir_Resource_Operator"
    ]
