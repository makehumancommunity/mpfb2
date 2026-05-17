# Part of the legacy "convert to rigify" workflow. This workflow is discouraged
# in new projects; it remains supported only because it is the only viable
# rigify path for characters imported from MakeHuman. For new characters, use
# the modern workflow on the Rigging panel (Add rigify metarig + Generate).

from .....services import LogService
_LOG = LogService.get_logger("rigopsoperators.init")
_LOG.trace("initializing rigops operators")

from .converttorigify import MPFB_OT_Convert_To_Rigify_Operator

__all__ = [
    "MPFB_OT_Convert_To_Rigify_Operator"
    ]
