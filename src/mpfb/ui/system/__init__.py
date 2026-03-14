from ...services import LogService
_LOG = LogService.get_logger("ui.system.init")
_LOG.trace("initializing system module")

from .systempanel import MPFB_PT_System_Panel  # parent panel — must be first
from .webresources import *
from .dirresources import *
