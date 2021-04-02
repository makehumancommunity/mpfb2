"""Operators for loading clothes"""

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("loadclothes.operators.init")
_LOG.trace("initializing load clothes operators")

from .loadclothes import MPFB_OT_Load_Clothes_Operator

__all__ = [
    "MPFB_OT_Load_Clothes_Operator"
    ]
