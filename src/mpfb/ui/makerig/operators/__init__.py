"""Operators for MakeRig."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("makerig.operators")
_LOG.trace("initializing makerig operators module")

from .movetocube import MPFB_OT_Move_To_Cube_Operator

__all__ = [
    "MPFB_OT_Move_To_Cube_Operator"
]
