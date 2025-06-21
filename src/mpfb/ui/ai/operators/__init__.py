"""Operators for ai stuff"""

from ....services import LogService
_LOG = LogService.get_logger("ai.operators.init")
_LOG.trace("initializing ai operators")

from .saveopenpose import MPFB_OT_Save_Openpose_Operator
from .boundingbox import MPFB_OT_Boundingbox_Operator

__all__ = [
    "MPFB_OT_Save_Openpose_Operator",
    "MPFB_OT_Boundingbox_Operator"
    ]
