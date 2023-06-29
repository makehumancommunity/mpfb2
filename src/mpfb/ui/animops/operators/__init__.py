from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("animops.init")
_LOG.trace("initializing animops operators")

from .mapmixamo import MPFB_OT_Map_Mixamo_Operator
from .reduceddoll import MPFB_OT_Reduced_Doll_Operator

__all__ = [
    "MPFB_OT_Map_Mixamo_Operator",
    "MPFB_OT_Reduced_Doll_Operator",
    ]
