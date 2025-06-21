"""Operators for adding rigs."""

from ....services import LogService
_LOG = LogService.get_logger("addrig.operators")
_LOG.trace("initializing add rig module")

from .addstandardrig import MPFB_OT_AddStandardRigOperator
from .addrigifyrig import MPFB_OT_AddRigifyRigOperator
from .generaterigifyrig import MPFB_OT_GenerateRigifyRigOperator

__all__ = [
    "MPFB_OT_AddStandardRigOperator",
    "MPFB_OT_AddRigifyRigOperator",
    "MPFB_OT_GenerateRigifyRigOperator"
]
