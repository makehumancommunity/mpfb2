"""This module hierarchy provides utility classes for adding and
removing helper bones (for example IK targets, grip rotation handles etc)
to the finger section of a makehuman rig."""

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("fingerhelpers.init")
_LOG.trace("initializing fingerhelpers module")

from .fingerhelpers import FingerHelpers
from .defaultfingerhelpers import DefaultFingerHelpers

__all__ = ["FingerHelpers", "DefaultFingerHelpers"]
