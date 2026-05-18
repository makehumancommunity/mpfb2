from ....services import LogService
_LOG = LogService.get_logger("customrig.init")
_LOG.trace("initializing custom rig module")

from .customrigpanel import MPFB_PT_Custom_Rig_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Custom_Rig_Panel"
    ]
