"""Operators for MakePose."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("makepose.operators")
_LOG.trace("initializing makepose operators module")

from .savepose import MPFB_OT_Save_Pose_Operator

__all__ = [
    "MPFB_OT_Save_Pose_Operator"
]
