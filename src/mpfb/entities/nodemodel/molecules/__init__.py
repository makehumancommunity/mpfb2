
from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel.atoms import AtomNodeManager
_LOG = LogService.get_logger("nodemodel.atoms")
_LOG.trace("initializing nodemodel atoms module")

from .eyeconstants import MpfbEyeConstants
from .withindistance import MpfbWithinDistance
from .withindistanceofeither import MpfbWithinDistanceOfEither

class MoleculeNodeManager(AtomNodeManager):
    def __init__(self, node_tree):
        _LOG.trace("Constructing MoleculeNodeManager with node_tree", node_tree)
        AtomNodeManager.__init__(self, node_tree)

        self._MpfbEyeConstants = MpfbEyeConstants()
        self._MpfbWithinDistance = MpfbWithinDistance()
        self._MpfbWithinDistanceOfEither = MpfbWithinDistanceOfEither()





