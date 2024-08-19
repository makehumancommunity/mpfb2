"""Operators for opening urls"""

from ....services import LogService
_LOG = LogService.get_logger("dirresources.operators.init")
_LOG.trace("initializing dir resources operators")

from .dirresource import MPFB_OT_Dir_Resource_Operator

__all__ = [
    "MPFB_OT_Dir_Resource_Operator"
    ]
