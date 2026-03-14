from ...services import LogService
_LOG = LogService.get_logger("ui.presets.init")
_LOG.trace("initializing presets module")

from .presetspanel import MPFB_PT_Presets_Panel  # parent panel — must be first
from .humanpresets import *
from .enhancedsettings import *
from .eyesettings import *
from .makeuppresets import *
