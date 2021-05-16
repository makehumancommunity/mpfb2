"""Operators for opening urls"""

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("dirresources.operators.init")
_LOG.trace("initializing dir resources operators")

from .dirresource import MPFB_OT_Dir_Resource_Operator

__all__ = [
    "MPFB_OT_Dir_Resource_Operator"
    ]
