from ...services import LogService
_LOG = LogService.get_logger("ui.rigging.init")
_LOG.trace("initializing rigging module")

from .rigpanel import MPFB_PT_Rig_Panel  # parent panel — must be first
from .addrig import *
from .rigify import *
from .righelpers import *
from .applypose import *
from .addcycle import *
