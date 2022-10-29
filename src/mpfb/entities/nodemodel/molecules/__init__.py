import bpy
from inspect import signature
from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel.atoms import AtomNodeManager
_LOG = LogService.get_logger("nodemodel.atoms")
_LOG.trace("initializing nodemodel atoms module")

from .colorrouter2 import MpfbColorRouter2
from .colorrouter3 import MpfbColorRouter3
from .colorrouter4 import MpfbColorRouter4
from .colorrouter5 import MpfbColorRouter5
from .eyeconstants import MpfbEyeConstants
from .massadd import MpfbMassAdd
from .shaderrouter2 import MpfbShaderRouter2
from .shaderrouter3 import MpfbShaderRouter3
from .shaderrouter4 import MpfbShaderRouter4
from .shaderrouter5 import MpfbShaderRouter5
from .systemvaluetextureaureolae import MpfbSystemValueTextureAureolae
from .systemvaluetextureface import MpfbSystemValueTextureFace
from .systemvaluetexturefingernails import MpfbSystemValueTextureFingernails
from .systemvaluetexturelips import MpfbSystemValueTextureLips
from .systemvaluetexturesss import MpfbSystemValueTextureSSS
from .systemvaluetexturetoenails import MpfbSystemValueTextureToenails
from .withindistance import MpfbWithinDistance
from .withindistanceofeither import MpfbWithinDistanceOfEither

class MoleculeNodeManager(AtomNodeManager):
    def __init__(self, node_tree):
        _LOG.trace("Constructing MoleculeNodeManager with node_tree", node_tree)
        AtomNodeManager.__init__(self, node_tree)

        self._molecule_singletons = dict()

        self._molecule_singletons["MpfbColorRouter2"] = MpfbColorRouter2()
        self._molecule_singletons["MpfbColorRouter3"] = MpfbColorRouter3()
        self._molecule_singletons["MpfbColorRouter4"] = MpfbColorRouter4()
        self._molecule_singletons["MpfbColorRouter5"] = MpfbColorRouter5()
        self._molecule_singletons["MpfbEyeConstants"] = MpfbEyeConstants()
        self._molecule_singletons["MpfbMassAdd"] = MpfbMassAdd()
        self._molecule_singletons["MpfbShaderRouter2"] = MpfbShaderRouter2()
        self._molecule_singletons["MpfbShaderRouter3"] = MpfbShaderRouter3()
        self._molecule_singletons["MpfbShaderRouter4"] = MpfbShaderRouter4()
        self._molecule_singletons["MpfbShaderRouter5"] = MpfbShaderRouter5()
        self._molecule_singletons["MpfbSystemValueTextureAureolae"] = MpfbSystemValueTextureAureolae()
        self._molecule_singletons["MpfbSystemValueTextureFace"] = MpfbSystemValueTextureFace()
        self._molecule_singletons["MpfbSystemValueTextureFingernails"] = MpfbSystemValueTextureFingernails()
        self._molecule_singletons["MpfbSystemValueTextureLips"] = MpfbSystemValueTextureLips()
        self._molecule_singletons["MpfbSystemValueTextureSSS"] = MpfbSystemValueTextureSSS()
        self._molecule_singletons["MpfbSystemValueTextureToenails"] = MpfbSystemValueTextureToenails()
        self._molecule_singletons["MpfbWithinDistance"] = MpfbWithinDistance()
        self._molecule_singletons["MpfbWithinDistanceOfEither"] = MpfbWithinDistanceOfEither()

    def createMpfbColorRouter2(self, x=0.0, y=0.0, name=None, label=None, Threshold=None, Section1Color=None, Section2Color=None):
        return self._molecule_singletons["MpfbColorRouter2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Threshold=Threshold, Section1Color=Section1Color, Section2Color=Section2Color)

