from ...services import LogService
_LOG = LogService.get_logger("ui.create_assets.init")
_LOG.trace("initializing create_assets module")

from .createpanel import MPFB_PT_Create_Panel  # parent panel — must be first
from .makeskin import *
from .maketarget import *
from .makeclothes import *
from .makeweight import *
from .makepose import *
from .makerig import *
from .makeup import *
