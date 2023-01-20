"""This module contains entities used for retargeting mocaps."""

from mpfb.services.logservice import LogService
from mpfb.entities.retarget.cmucgspeed_default import MAP as cmucgspeed_default 

_LOG = LogService.get_logger("retarget.init")
_LOG.trace("initializing retarget module")

RETARGET_MAPS = dict()
RETARGET_MAPS["cmucgspeed"] = dict()
RETARGET_MAPS["cmucgspeed"]["default"] = cmucgspeed_default
RETARGET_MAPS["cmucgspeed"]["default_no_toes"] = cmucgspeed_default

__all__ = [
    "RETARGET_MAPS"
    ]
