from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("ui.humanpresets")
_LOG.trace("initializing save nodes module")

from .humanpresetspanel import MPFB_PT_Human_Presets_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Human_Presets_Panel"
    ]
