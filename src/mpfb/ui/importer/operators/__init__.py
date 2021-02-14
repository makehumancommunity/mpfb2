
from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("importeroperators.init")
_LOG.trace("initializing importer operators")

from .importhuman import MPFB_OT_ImportHumanOperator

__all__ = [
    "MPFB_OT_ImportHumanOperator"
    ]
