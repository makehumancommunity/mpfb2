"""Operators for opening urls"""

from ....services import LogService
_LOG = LogService.get_logger("webresources.operators.init")
_LOG.trace("initializing web resources operators")

from .webresource import MPFB_OT_Web_Resource_Operator

__all__ = [
    "MPFB_OT_Web_Resource_Operator"
    ]
