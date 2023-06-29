from mpfb.services import LogService as _LogService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = _LogService.get_logger("animops.init")
_LOG.trace("initializing setup animops module")

from .animopspanel import MPFB_PT_AnimopsPanel
from .operators import *

__all__ = [
    "MPFB_PT_AnimopsPanel"
    ]
