from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("rigifyoperators.init")
_LOG.trace("initializing rigify operators")

from .converttorigify import MPFB_OT_Convert_To_Rigify_Operator

__all__ = [
    "MPFB_OT_Convert_To_Rigify_Operator"
    ]
