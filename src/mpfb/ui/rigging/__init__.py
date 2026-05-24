from ...services import LogService
_LOG = LogService.get_logger("ui.rigging.init")
_LOG.trace("initializing rigging module")

from .rigpanel import MPFB_PT_Rig_Panel  # parent panel — must be first
from .standardrig import *
from .rigifyrig import *
from .customrig import *
from .applypose import *
#from .addcycle import *  <-- This is dead code now
