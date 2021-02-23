"""This module hierarchy provides utility classes for adding and
removing helper bones (for example IK targets) to the arms/hands
section of a makehuman rig."""

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("armhelpers.init")
_LOG.trace("initializing armhelpers module")
