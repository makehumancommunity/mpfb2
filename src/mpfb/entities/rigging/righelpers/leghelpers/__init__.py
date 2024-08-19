"""This module hierarchy provides utility classes for adding and
removing helper bones (for example IK targets, grip rotation handles etc)
to the hip/legs/feet section of a makehuman rig."""

from .....services import LogService

_LOG = LogService.get_logger("leghelpers.init")
_LOG.trace("initializing leghelpers module")

from .leghelpers import LegHelpers
from .defaultleghelpers import DefaultLegHelpers

__all__ = ["LegHelpers", "DefaultLegHelpers"]
