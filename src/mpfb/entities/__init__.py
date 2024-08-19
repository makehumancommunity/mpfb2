
"""This module contains entities used in various places of the plugin."""

from ..services import LogService

_LOG = LogService.get_logger("entities.init")
_LOG.trace("initializing entities module")
