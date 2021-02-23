"""This module hierarchy provides utility classes for adding and
removing helper bones (for example IK targets, grip rotation handles etc)
to a makehuman rig."""

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("righelpers.init")
_LOG.trace("initializing righelpers module")
