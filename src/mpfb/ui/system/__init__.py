from ...services import LogService
_LOG = LogService.get_logger("ui.system.init")
_LOG.trace("initializing system module")

from .webresources import *
from .dirresources import *
