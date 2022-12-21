"""Operators for developer stuff"""

from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("developer.operators.init")
_LOG.trace("initializing developers operators")

from .listloglevels import MPFB_OT_List_Log_Levels_Operator
from .exportlog import MPFB_OT_Export_Log_Operator
from .resetloglevels import MPFB_OT_Reset_Log_Levels_Operator
from .setloglevel import MPFB_OT_Set_Log_Level_Operator
from .savenodes import MPFB_OT_Save_Nodes_Operator
from .loadnodes import MPFB_OT_Load_Nodes_Operator
from .saverig import MPFB_OT_Save_Rig_Operator
from .loadrig import MPFB_OT_Load_Rig_Operator
from .saveweights import MPFB_OT_Save_Weights_Operator
from .loadweights import MPFB_OT_Load_Weights_Operator
from .printnodegroup import MPFB_OT_Print_Node_Group_Operator
from .create_molecules import MPFB_OT_Create_Molecules_Operator
from .create_cells import MPFB_OT_Create_Cells_Operator
from .unittests import MPFB_OT_Unit_Tests_Operator

__all__ = [
    "MPFB_OT_List_Log_Levels_Operator",
    "MPFB_OT_Reset_Log_Levels_Operator",
    "MPFB_OT_Set_Log_Level_Operator",
    "MPFB_OT_Load_Nodes_Operator",
    "MPFB_OT_Save_Nodes_Operator",
    "MPFB_OT_Save_Rig_Operator",
    "MPFB_OT_Load_Rig_Operator",
    "MPFB_OT_Save_Weights_Operator",
    "MPFB_OT_Load_Weights_Operator",
    "MPFB_OT_Print_Node_Group_Operator",
    "MPFB_OT_Create_Molecules_Operator",
    "MPFB_OT_Create_Cells_Operator",
    "MPFB_OT_Unit_Tests_Operator"
    ]
