"""This module hierarchy provides utility classes for adding and
removing helper bones (for example IK targets) to the arms/hands
section of a makehuman rig."""

from .....services import LogService

_LOG = LogService.get_logger("armhelpers.init")
_LOG.trace("initializing armhelpers module")

from .armhelpers import ArmHelpers
from .defaultarmhelpers import DefaultArmHelpers

__all__ = ["ArmHelpers", "DefaultArmHelpers"]
