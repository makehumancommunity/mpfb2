"""Operators for developer stuff"""

from ....services import LogService
_LOG = LogService.get_logger("developer.operators.init")
_LOG.trace("initializing developers operators")

from .listloglevels import MPFB_OT_List_Log_Levels_Operator
from .exportlog import MPFB_OT_Export_Log_Operator
from .resetloglevels import MPFB_OT_Reset_Log_Levels_Operator
from .setloglevel import MPFB_OT_Set_Log_Level_Operator
from .savenodes import MPFB_OT_Save_Nodes_Operator
from .loadnodes import MPFB_OT_Load_Nodes_Operator
from .savetarget import MPFB_OT_Save_Target_Operator
from .loadtarget import MPFB_OT_Load_Target_Operator
from .create_groups import MPFB_OT_Create_Groups_Operator
from .destroygroups import MPFB_OT_Destroy_Groups_Operator
from .unittests import MPFB_OT_Unit_Tests_Operator
from .writecomposite import MPFB_OT_Write_Composite_Operator
from .writematerial import MPFB_OT_Write_Material_Operator
from .replacewithskin import MPFB_OT_Replace_With_Skin_Operator
from .rewritenodetypes import MPFB_OT_Rewrite_Node_Types_Operator

__all__ = [
    "MPFB_OT_List_Log_Levels_Operator",
    "MPFB_OT_Reset_Log_Levels_Operator",
    "MPFB_OT_Set_Log_Level_Operator",
    "MPFB_OT_Load_Nodes_Operator",
    "MPFB_OT_Save_Nodes_Operator",
    "MPFB_OT_Save_Target_Operator",
    "MPFB_OT_Load_Target_Operator",
    "MPFB_OT_Create_Groups_Operator",
    "MPFB_OT_Destroy_Groups_Operator",
    "MPFB_OT_Unit_Tests_Operator",
    "MPFB_OT_Write_Composite_Operator",
    "MPFB_OT_Write_Material_Operator",
    "MPFB_OT_Replace_With_Skin_Operator",
    "MPFB_OT_Rewrite_Node_Types_Operator"
    ]
