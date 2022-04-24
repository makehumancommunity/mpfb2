from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("sculptoperators.init")
_LOG.trace("initializing sculpt operators")

from .setupsculpt import MPFB_OT_Setup_Sculpt_Operator

__all__ = [
    "MPFB_OT_Setup_Sculpt_Operator"
    ]
