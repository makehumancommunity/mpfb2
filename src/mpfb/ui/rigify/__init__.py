from ...services import LogService
_LOG = LogService.get_logger("rigify.init")
_LOG.trace("initializing rigify module")

from .rigifypanel import MPFB_PT_Rigify_Panel
from .operators import *

__all__ = [
    "MPFB_OT_Convert_To_Rigify_Operator"
    ]
