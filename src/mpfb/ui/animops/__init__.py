from ...services import LogService
from ...services import SceneConfigSet

_LOG = LogService.get_logger("animops.init")
_LOG.trace("initializing setup animops module")

from .animopspanel import MPFB_PT_AnimopsPanel
from .operators import *

__all__ = [
    "MPFB_PT_AnimopsPanel"
    ]
