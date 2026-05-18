from ....services import LogService
_LOG = LogService.get_logger("rigifyrig.init")
_LOG.trace("initializing rigify rig module")

from .rigifyrigpanel import MPFB_PT_Rigify_Rig_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Rigify_Rig_Panel"
    ]
