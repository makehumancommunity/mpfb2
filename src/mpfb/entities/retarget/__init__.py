"""This module contains entities used for retargeting mocaps."""

from mpfb.services.logservice import LogService
from mpfb.entities.retarget.cmucgspeed import CmuCgspeed
from mpfb.entities.retarget.default import Default 

_LOG = LogService.get_logger("retarget.init")
_LOG.trace("initializing retarget module")

RETARGET_INFO = dict()
RETARGET_INFO["cmucgspeed"] = CmuCgspeed()
RETARGET_INFO["default"] = Default()
RETARGET_INFO["default_no_toes"] = Default()

__all__ = [
    "RETARGET_INFO"
    ]
