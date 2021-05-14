"""Operators for adding rigs."""

from mpfb.services import LogService as _LogService
_LOG = _LogService.get_logger("addrig.operators")
_LOG.trace("initializing add rig module")

from .addstandardrig import MPFB_OT_AddStandardRigOperator
from .addrigifyrig import MPFB_OT_AddRigifyRigOperator
from .generaterigifyrig import MPFB_OT_GenerateRigifyRigOperator

__all__ = [
    "MPFB_OT_AddStandardRigOperator",
    "MPFB_OT_AddRigifyRigOperator",
    "MPFB_OT_GenerateRigifyRigOperator"
]
