from mpfb.services import LogService as _LogService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = _LogService.get_logger("matops.init")
_LOG.trace("initializing setup matops module")

from .matopspanel import MPFB_PT_MatopsPanel
from .operators import *

__all__ = [
    "MPFB_PT_MatopsPanel"
    ]
