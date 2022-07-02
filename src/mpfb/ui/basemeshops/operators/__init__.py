from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("sculptoperators.init")
_LOG.trace("initializing sculpt operators")

from .bakeshapekeys import MPFB_OT_Bake_Shapekeys_Operator

__all__ = [
    "MPFB_OT_Bake_Shapekeys_Operator"
    ]
