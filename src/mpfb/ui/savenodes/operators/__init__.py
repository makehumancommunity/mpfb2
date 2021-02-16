
from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("savenodesoperators.init")
_LOG.trace("initializing save nodes operators")

from .savenodes import MPFB_OT_Save_Nodes_Operator

__all__ = [
    "MPFB_OT_Save_Nodes_Operator"
    ]
