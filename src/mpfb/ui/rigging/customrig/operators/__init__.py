"""Operators for the custom-rig sub-panel."""

from .....services import LogService
_LOG = LogService.get_logger("customrig.operators")
_LOG.trace("initializing custom rig operators")

from .addcustomrig import MPFB_OT_Add_Custom_Rig_Operator

__all__ = [
    "MPFB_OT_Add_Custom_Rig_Operator"
    ]
