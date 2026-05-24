"""Operators for the standard-rig sub-panel (add standard rig, add/remove rig helpers)."""

from .....services import LogService
_LOG = LogService.get_logger("standardrig.operators")
_LOG.trace("initializing standard rig operators")

from .addstandardrig import MPFB_OT_AddStandardRigOperator
from .addhelpers import MPFB_OT_AddHelpersOperator
from .removehelpers import MPFB_OT_RemoveHelpersOperator

__all__ = [
    "MPFB_OT_AddStandardRigOperator",
    "MPFB_OT_AddHelpersOperator",
    "MPFB_OT_RemoveHelpersOperator"
    ]
