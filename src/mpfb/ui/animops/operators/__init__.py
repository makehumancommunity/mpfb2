from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("animops.init")
_LOG.trace("initializing animops operators")

from .mapmixamo import MPFB_OT_Map_Mixamo_Operator

__all__ = [
    "MPFB_OT_Map_Mixamo_Operator"
    ]
