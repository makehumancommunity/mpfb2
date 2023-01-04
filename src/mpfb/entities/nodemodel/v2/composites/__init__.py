from .abstractgroupwrapper import AbstractGroupWrapper

from .nodewrappermpfbadditiverange2 import NodeWrapperMpfbAdditiveRange2
from .nodewrappermpfbadditiverange3 import NodeWrapperMpfbAdditiveRange3
from .nodewrappermpfbbodyconstants import NodeWrapperMpfbBodyConstants
from .nodewrappermpfbcharacterinfo import NodeWrapperMpfbCharacterInfo
from .nodewrappermpfbcolorramp2 import NodeWrapperMpfbColorRamp2
from .nodewrappermpfbcolorramp3 import NodeWrapperMpfbColorRamp3
from .nodewrappermpfbcolorramp4 import NodeWrapperMpfbColorRamp4
from .nodewrappermpfbcolorrouter2 import NodeWrapperMpfbColorRouter2
from .nodewrappermpfbcolorrouter3 import NodeWrapperMpfbColorRouter3
from .nodewrappermpfbcolorrouter4 import NodeWrapperMpfbColorRouter4
from .nodewrappermpfbcolorrouter5 import NodeWrapperMpfbColorRouter5
from .nodewrappermpfbeyeconstants import NodeWrapperMpfbEyeConstants
from .nodewrappermpfbmassadd import NodeWrapperMpfbMassAdd
from .nodewrappermpfbnormalizevalue import NodeWrapperMpfbNormalizeValue
from .nodewrappermpfbshaderrouter2 import NodeWrapperMpfbShaderRouter2
from .nodewrappermpfbshaderrouter3 import NodeWrapperMpfbShaderRouter3
from .nodewrappermpfbshaderrouter4 import NodeWrapperMpfbShaderRouter4
from .nodewrappermpfbshaderrouter5 import NodeWrapperMpfbShaderRouter5
from .nodewrappermpfbsystemvaluetextureaureolae import NodeWrapperMpfbSystemValueTextureAureolae
from .nodewrappermpfbsystemvaluetexturecrotch import NodeWrapperMpfbSystemValueTextureCrotch
from .nodewrappermpfbsystemvaluetextureeyelids import NodeWrapperMpfbSystemValueTextureEyelids
from .nodewrappermpfbsystemvaluetextureface import NodeWrapperMpfbSystemValueTextureFace
from .nodewrappermpfbsystemvaluetexturefingernails import NodeWrapperMpfbSystemValueTextureFingernails
from .nodewrappermpfbsystemvaluetexturegenitals import NodeWrapperMpfbSystemValueTextureGenitals
from .nodewrappermpfbsystemvaluetextureinsidemouth import NodeWrapperMpfbSystemValueTextureInsideMouth
from .nodewrappermpfbsystemvaluetexturelips import NodeWrapperMpfbSystemValueTextureLips
from .nodewrappermpfbsystemvaluetexturetoenails import NodeWrapperMpfbSystemValueTextureToenails
from .nodewrappermpfbvalueramp1 import NodeWrapperMpfbValueRamp1
from .nodewrappermpfbvalueramp2 import NodeWrapperMpfbValueRamp2
from .nodewrappermpfbvalueramp3 import NodeWrapperMpfbValueRamp3
from .nodewrappermpfbvalueramp4 import NodeWrapperMpfbValueRamp4
from .nodewrappermpfbwithindistance import NodeWrapperMpfbWithinDistance
from .nodewrappermpfbwithindistanceofeither import NodeWrapperMpfbWithinDistanceOfEither

COMPOSITE_NODE_WRAPPERS = dict()
COMPOSITE_NODE_WRAPPERS["MpfbAdditiveRange2"] = NodeWrapperMpfbAdditiveRange2
COMPOSITE_NODE_WRAPPERS["MpfbAdditiveRange3"] = NodeWrapperMpfbAdditiveRange3
COMPOSITE_NODE_WRAPPERS["MpfbBodyConstants"] = NodeWrapperMpfbBodyConstants
COMPOSITE_NODE_WRAPPERS["MpfbCharacterInfo"] = NodeWrapperMpfbCharacterInfo
COMPOSITE_NODE_WRAPPERS["MpfbColorRamp2"] = NodeWrapperMpfbColorRamp2
COMPOSITE_NODE_WRAPPERS["MpfbColorRamp3"] = NodeWrapperMpfbColorRamp3
COMPOSITE_NODE_WRAPPERS["MpfbColorRamp4"] = NodeWrapperMpfbColorRamp4
COMPOSITE_NODE_WRAPPERS["MpfbColorRouter2"] = NodeWrapperMpfbColorRouter2
COMPOSITE_NODE_WRAPPERS["MpfbColorRouter3"] = NodeWrapperMpfbColorRouter3
COMPOSITE_NODE_WRAPPERS["MpfbColorRouter4"] = NodeWrapperMpfbColorRouter4
COMPOSITE_NODE_WRAPPERS["MpfbColorRouter5"] = NodeWrapperMpfbColorRouter5
COMPOSITE_NODE_WRAPPERS["MpfbEyeConstants"] = NodeWrapperMpfbEyeConstants
COMPOSITE_NODE_WRAPPERS["MpfbMassAdd"] = NodeWrapperMpfbMassAdd
COMPOSITE_NODE_WRAPPERS["MpfbNormalizeValue"] = NodeWrapperMpfbNormalizeValue
COMPOSITE_NODE_WRAPPERS["MpfbShaderRouter2"] = NodeWrapperMpfbShaderRouter2
COMPOSITE_NODE_WRAPPERS["MpfbShaderRouter3"] = NodeWrapperMpfbShaderRouter3
COMPOSITE_NODE_WRAPPERS["MpfbShaderRouter4"] = NodeWrapperMpfbShaderRouter4
COMPOSITE_NODE_WRAPPERS["MpfbShaderRouter5"] = NodeWrapperMpfbShaderRouter5
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureAureolae"] = NodeWrapperMpfbSystemValueTextureAureolae
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureCrotch"] = NodeWrapperMpfbSystemValueTextureCrotch
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureEyelids"] = NodeWrapperMpfbSystemValueTextureEyelids
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureFace"] = NodeWrapperMpfbSystemValueTextureFace
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureFingernails"] = NodeWrapperMpfbSystemValueTextureFingernails
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureGenitals"] = NodeWrapperMpfbSystemValueTextureGenitals
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureInsideMouth"] = NodeWrapperMpfbSystemValueTextureInsideMouth
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureLips"] = NodeWrapperMpfbSystemValueTextureLips
COMPOSITE_NODE_WRAPPERS["MpfbSystemValueTextureToenails"] = NodeWrapperMpfbSystemValueTextureToenails
COMPOSITE_NODE_WRAPPERS["MpfbValueRamp1"] = NodeWrapperMpfbValueRamp1
COMPOSITE_NODE_WRAPPERS["MpfbValueRamp2"] = NodeWrapperMpfbValueRamp2
COMPOSITE_NODE_WRAPPERS["MpfbValueRamp3"] = NodeWrapperMpfbValueRamp3
COMPOSITE_NODE_WRAPPERS["MpfbValueRamp4"] = NodeWrapperMpfbValueRamp4
COMPOSITE_NODE_WRAPPERS["MpfbWithinDistance"] = NodeWrapperMpfbWithinDistance
COMPOSITE_NODE_WRAPPERS["MpfbWithinDistanceOfEither"] = NodeWrapperMpfbWithinDistanceOfEither

__all__ = [
    "AbstractGroupWrapper",
    "COMPOSITE_NODE_WRAPPERS",
    "NodeWrapperMpfbAdditiveRange2",
    "NodeWrapperMpfbAdditiveRange3",
    "NodeWrapperMpfbBodyConstants",
    "NodeWrapperMpfbCharacterInfo",
    "NodeWrapperMpfbColorRamp2",
    "NodeWrapperMpfbColorRamp3",
    "NodeWrapperMpfbColorRamp4",
    "NodeWrapperMpfbColorRouter2",
    "NodeWrapperMpfbColorRouter3",
    "NodeWrapperMpfbColorRouter4",
    "NodeWrapperMpfbColorRouter5",
    "NodeWrapperMpfbEyeConstants",
    "NodeWrapperMpfbMassAdd",
    "NodeWrapperMpfbNormalizeValue",
    "NodeWrapperMpfbShaderRouter2",
    "NodeWrapperMpfbShaderRouter3",
    "NodeWrapperMpfbShaderRouter4",
    "NodeWrapperMpfbShaderRouter5",
    "NodeWrapperMpfbSystemValueTextureAureolae",
    "NodeWrapperMpfbSystemValueTextureCrotch",
    "NodeWrapperMpfbSystemValueTextureEyelids",
    "NodeWrapperMpfbSystemValueTextureFace",
    "NodeWrapperMpfbSystemValueTextureFingernails",
    "NodeWrapperMpfbSystemValueTextureGenitals",
    "NodeWrapperMpfbSystemValueTextureInsideMouth",
    "NodeWrapperMpfbSystemValueTextureLips",
    "NodeWrapperMpfbSystemValueTextureToenails",
    "NodeWrapperMpfbValueRamp1",
    "NodeWrapperMpfbValueRamp2",
    "NodeWrapperMpfbValueRamp3",
    "NodeWrapperMpfbValueRamp4",
    "NodeWrapperMpfbWithinDistance",
    "NodeWrapperMpfbWithinDistanceOfEither"
    ]
