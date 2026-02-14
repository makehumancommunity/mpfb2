"""Operators for MakeRig."""

from ....services import LogService
_LOG = LogService.get_logger("makerig.operators")
_LOG.trace("initializing makerig operators module")

from .movetocube import MPFB_OT_Move_To_Cube_Operator
from .autotransferweights import MPFB_OT_Auto_Transfer_Weights_Operator
from .loadrig import MPFB_OT_Load_Rig_Operator
from .saverig import MPFB_OT_Save_Rig_Operator
from .loadweights import MPFB_OT_Load_Weights_Operator
from .saveweights import MPFB_OT_Save_Weights_Operator

__all__ = [
    "MPFB_OT_Move_To_Cube_Operator",
    "MPFB_OT_Auto_Transfer_Weights_Operator",
    "MPFB_OT_Load_Rig_Operator",
    "MPFB_OT_Save_Rig_Operator",
    "MPFB_OT_Load_Weights_Operator",
    "MPFB_OT_Save_Weights_Operator"
]
