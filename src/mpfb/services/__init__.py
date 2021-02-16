
from .logservice import LogService

_LOG = LogService.get_logger("services.init")
_LOG.trace("initializing services module")
