from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("rigify.init")
_LOG.trace("initializing rigify module")

from .rigifypanel import MPFB_PT_Rigify_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Convert_To_Rigify_Operator"
    ]
