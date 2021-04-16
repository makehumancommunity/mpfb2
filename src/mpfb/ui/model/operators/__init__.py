"""Operators for modeling."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("model.operators")
_LOG.trace("initializing model module")

from .addtarget import MPFB_OT_AddTargetOperator

__all__ = [
    "MPFB_OT_AddTargetOperator"
]
