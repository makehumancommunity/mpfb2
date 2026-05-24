"""Operators for the rigify-rig sub-panel."""

from .....services import LogService
_LOG = LogService.get_logger("rigifyrig.operators")
_LOG.trace("initializing rigify rig operators")

from .addrigifyrig import MPFB_OT_AddRigifyRigOperator
from .generaterigifyrig import MPFB_OT_GenerateRigifyRigOperator

__all__ = [
    "MPFB_OT_AddRigifyRigOperator",
    "MPFB_OT_GenerateRigifyRigOperator"
    ]
