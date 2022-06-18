from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("sculptoperators.init")
_LOG.trace("initializing sculpt operators")

from .setnormalmap import MPFB_OT_Set_Normalmap_Operator

__all__ = [
    "MPFB_OT_Set_Normalmap_Operator"
    ]
