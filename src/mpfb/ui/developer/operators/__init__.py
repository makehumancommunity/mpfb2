"""Operators for developer stuff"""

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("developer.operators.init")
_LOG.trace("initializing developers operators")

from .listloglevels import MPFB_OT_List_Log_Levels_Operator
from .resetloglevels import MPFB_OT_Reset_Log_Levels_Operator
from .setloglevel import MPFB_OT_Set_Log_Level_Operator
from .savenodes import MPFB_OT_Save_Nodes_Operator
from .loadnodes import MPFB_OT_Load_Nodes_Operator
from .saverig import MPFB_OT_Save_Rig_Operator
from .loadrig import MPFB_OT_Load_Rig_Operator
from .saveweights import MPFB_OT_Save_Weights_Operator

__all__ = [
    "MPFB_OT_List_Log_Levels_Operator",
    "MPFB_OT_Reset_Log_Levels_Operator",
    "MPFB_OT_Set_Log_Level_Operator",
    "MPFB_OT_Load_Nodes_Operator",
    "MPFB_OT_Save_Nodes_Operator",
    "MPFB_OT_Save_Rig_Operator",
    "MPFB_OT_Load_Rig_Operator",
    "MPFB_OT_Save_Weights_Operator"
    ]
