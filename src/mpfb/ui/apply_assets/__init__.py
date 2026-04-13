from ...services import LogService
_LOG = LogService.get_logger("ui.apply_assets.init")
_LOG.trace("initializing apply_assets module")

from .assetspanel import MPFB_PT_Assets_Panel  # parent panel — must be first
from .assetlibrary import *
from .loadclothes import *
