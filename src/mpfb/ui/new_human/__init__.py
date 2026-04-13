from ...services import LogService
_LOG = LogService.get_logger("ui.new_human.init")
_LOG.trace("initializing new_human module")

from .newpanel import MPFB_PT_New_Panel  # parent panel — must be first
from .newhuman import *
from .importer import *
from .importerpresets import *
