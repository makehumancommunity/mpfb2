"""Operators for ai stuff"""

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("ai.operators.init")
_LOG.trace("initializing ai operators")

from .saveopenpose import MPFB_OT_Save_Openpose_Operator

__all__ = [
    "MPFB_OT_Save_Openpose_Operator"
    ]
