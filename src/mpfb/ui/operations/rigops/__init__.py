# Part of the legacy "convert to rigify" workflow. This workflow is discouraged
# in new projects; it remains supported only because it is the only viable
# rigify path for characters imported from MakeHuman. For new characters, use
# the modern workflow on the Rigging panel (Add rigify metarig + Generate).

from ....services import LogService
_LOG = LogService.get_logger("rigops.init")
_LOG.trace("initializing rigops module")

from .rigopspanel import MPFB_PT_Rig_Operations_Panel
from .operators import *

__all__ = [
    "MPFB_PT_Rig_Operations_Panel",
    "MPFB_OT_Convert_To_Rigify_Operator"
    ]
