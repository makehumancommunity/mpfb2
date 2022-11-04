import bpy
from inspect import signature
from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel.atoms import AtomNodeManager
_LOG = LogService.get_logger("nodemodel.molecules")
_LOG.trace("initializing nodemodel molecule module")

from .additiverange2 import MpfbAdditiveRange2
from .additiverange3 import MpfbAdditiveRange3
from .characterinfo import MpfbCharacterInfo
from .colorramp2 import MpfbColorRamp2
from .colorramp3 import MpfbColorRamp3
from .colorramp4 import MpfbColorRamp4
from .colorrouter2 import MpfbColorRouter2
from .colorrouter3 import MpfbColorRouter3
from .colorrouter4 import MpfbColorRouter4
from .colorrouter5 import MpfbColorRouter5
from .eyeconstants import MpfbEyeConstants
from .massadd import MpfbMassAdd
from .normalizevalue import MpfbNormalizeValue
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
from .valueramp1 import MpfbValueRamp1
from .valueramp2 import MpfbValueRamp2
from .valueramp3 import MpfbValueRamp3
from .valueramp4 import MpfbValueRamp4
from .withindistance import MpfbWithinDistance
from .withindistanceofeither import MpfbWithinDistanceOfEither

class MoleculeNodeManager(AtomNodeManager):
    def __init__(self, node_tree):
        _LOG.trace("Constructing MoleculeNodeManager with node_tree", node_tree)
        AtomNodeManager.__init__(self, node_tree)

        self._molecule_singletons = dict()

        self._molecule_singletons["MpfbAdditiveRange2"] = MpfbAdditiveRange2()
        self._molecule_singletons["MpfbAdditiveRange3"] = MpfbAdditiveRange3()
        self._molecule_singletons["MpfbCharacterInfo"] = MpfbCharacterInfo()
        self._molecule_singletons["MpfbColorRamp2"] = MpfbColorRamp2()
        self._molecule_singletons["MpfbColorRamp3"] = MpfbColorRamp3()
        self._molecule_singletons["MpfbColorRamp4"] = MpfbColorRamp4()
        self._molecule_singletons["MpfbColorRouter2"] = MpfbColorRouter2()
        self._molecule_singletons["MpfbColorRouter3"] = MpfbColorRouter3()
        self._molecule_singletons["MpfbColorRouter4"] = MpfbColorRouter4()
        self._molecule_singletons["MpfbColorRouter5"] = MpfbColorRouter5()
        self._molecule_singletons["MpfbEyeConstants"] = MpfbEyeConstants()
        self._molecule_singletons["MpfbMassAdd"] = MpfbMassAdd()
        self._molecule_singletons["MpfbNormalizeValue"] = MpfbNormalizeValue()
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
        self._molecule_singletons["MpfbValueRamp1"] = MpfbValueRamp1()
        self._molecule_singletons["MpfbValueRamp2"] = MpfbValueRamp2()
        self._molecule_singletons["MpfbValueRamp3"] = MpfbValueRamp3()
        self._molecule_singletons["MpfbValueRamp4"] = MpfbValueRamp4()
        self._molecule_singletons["MpfbWithinDistance"] = MpfbWithinDistance()
        self._molecule_singletons["MpfbWithinDistanceOfEither"] = MpfbWithinDistanceOfEither()

    def createMpfbAdditiveRange2(self, x=0.0, y=0.0, name=None, label=None, Value=None, Section1Size=None, Section2Size=None):
        return self._molecule_singletons["MpfbAdditiveRange2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Section1Size=Section1Size, Section2Size=Section2Size)

    def createMpfbAdditiveRange3(self, x=0.0, y=0.0, name=None, label=None, Value=None, Section1Size=None, Section2Size=None, Section3Size=None):
        return self._molecule_singletons["MpfbAdditiveRange3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Section1Size=Section1Size, Section2Size=Section2Size, Section3Size=Section3Size)

    def createMpfbCharacterInfo(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbCharacterInfo"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbColorRamp2(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopColor=None, BetweenStep1Color=None, OneStopColor=None, BetweenStep1Pos=None):
        return self._molecule_singletons["MpfbColorRamp2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopColor=ZeroStopColor, BetweenStep1Color=BetweenStep1Color, OneStopColor=OneStopColor, BetweenStep1Pos=BetweenStep1Pos)

    def createMpfbColorRamp3(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopColor=None, BetweenStep1Color=None, BetweenStep2Color=None, OneStopColor=None, BetweenStep1Pos=None, BetweenStep2Pos=None):
        return self._molecule_singletons["MpfbColorRamp3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopColor=ZeroStopColor, BetweenStep1Color=BetweenStep1Color, BetweenStep2Color=BetweenStep2Color, OneStopColor=OneStopColor, BetweenStep1Pos=BetweenStep1Pos, BetweenStep2Pos=BetweenStep2Pos)

    def createMpfbColorRamp4(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopColor=None, BetweenStep1Color=None, BetweenStep2Color=None, BetweenStep3Color=None, OneStopColor=None, BetweenStep1Pos=None, BetweenStep2Pos=None, BetweenStep3Pos=None):
        return self._molecule_singletons["MpfbColorRamp4"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopColor=ZeroStopColor, BetweenStep1Color=BetweenStep1Color, BetweenStep2Color=BetweenStep2Color, BetweenStep3Color=BetweenStep3Color, OneStopColor=OneStopColor, BetweenStep1Pos=BetweenStep1Pos, BetweenStep2Pos=BetweenStep2Pos, BetweenStep3Pos=BetweenStep3Pos)

    def createMpfbColorRouter2(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold=None, Section1Color=None, Section2Color=None):
        return self._molecule_singletons["MpfbColorRouter2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold=Threshold, Section1Color=Section1Color, Section2Color=Section2Color)

    def createMpfbColorRouter3(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Section1Color=None, Section2Color=None, Section3Color=None):
        return self._molecule_singletons["MpfbColorRouter3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Section1Color=Section1Color, Section2Color=Section2Color, Section3Color=Section3Color)

    def createMpfbColorRouter4(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Section1Color=None, Section2Color=None, Section3Color=None, Section4Color=None):
        return self._molecule_singletons["MpfbColorRouter4"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Section1Color=Section1Color, Section2Color=Section2Color, Section3Color=Section3Color, Section4Color=Section4Color)

    def createMpfbColorRouter5(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Threshold4=None, Section1Color=None, Section2Color=None, Section3Color=None, Section4Color=None, Section5Color=None):
        return self._molecule_singletons["MpfbColorRouter5"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Threshold4=Threshold4, Section1Color=Section1Color, Section2Color=Section2Color, Section3Color=Section3Color, Section4Color=Section4Color, Section5Color=Section5Color)

    def createMpfbEyeConstants(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbEyeConstants"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbMassAdd(self, x=0.0, y=0.0, name=None, label=None, Value1=None, Value2=None, Value3=None, Value4=None, Value5=None, Value6=None, Value7=None):
        return self._molecule_singletons["MpfbMassAdd"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value1=Value1, Value2=Value2, Value3=Value3, Value4=Value4, Value5=Value5, Value6=Value6, Value7=Value7)

    def createMpfbNormalizeValue(self, x=0.0, y=0.0, name=None, label=None, Value=None, IncomingMin=None, IncomingMax=None):
        return self._molecule_singletons["MpfbNormalizeValue"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, IncomingMin=IncomingMin, IncomingMax=IncomingMax)

    def createMpfbShaderRouter2(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold=None, Section1Shader=None, Section2Shader=None):
        return self._molecule_singletons["MpfbShaderRouter2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold=Threshold, Section1Shader=Section1Shader, Section2Shader=Section2Shader)

    def createMpfbShaderRouter3(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Section1Shader=None, Section2Shader=None, Section3Shader=None):
        return self._molecule_singletons["MpfbShaderRouter3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Section1Shader=Section1Shader, Section2Shader=Section2Shader, Section3Shader=Section3Shader)

    def createMpfbShaderRouter4(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Section1Shader=None, Section2Shader=None, Section3Shader=None, Section4Shader=None):
        return self._molecule_singletons["MpfbShaderRouter4"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Section1Shader=Section1Shader, Section2Shader=Section2Shader, Section3Shader=Section3Shader, Section4Shader=Section4Shader)

    def createMpfbShaderRouter5(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Threshold4=None, Section1Shader=None, Section2Shader=None, Section3Shader=None, Section4Shader=None, Section5Shader=None):
        return self._molecule_singletons["MpfbShaderRouter5"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Threshold4=Threshold4, Section1Shader=Section1Shader, Section2Shader=Section2Shader, Section3Shader=Section3Shader, Section4Shader=Section4Shader, Section5Shader=Section5Shader)

    def createMpfbSystemValueTextureAureolae(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureAureolae"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbSystemValueTextureFace(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureFace"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbSystemValueTextureFingernails(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureFingernails"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbSystemValueTextureLips(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureLips"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbSystemValueTextureSSS(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureSSS"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbSystemValueTextureToenails(self, x=0.0, y=0.0, name=None, label=None):
        return self._molecule_singletons["MpfbSystemValueTextureToenails"].create_instance(self.node_tree, x=x, y=y, name=name, label=label)

    def createMpfbValueRamp1(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, OneStopValue=None):
        return self._molecule_singletons["MpfbValueRamp1"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, OneStopValue=OneStopValue)

    def createMpfbValueRamp2(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, BetweenStop1Value=None, OneStopValue=None, BetweenStop1Position=None):
        return self._molecule_singletons["MpfbValueRamp2"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, BetweenStop1Value=BetweenStop1Value, OneStopValue=OneStopValue, BetweenStop1Position=BetweenStop1Position)

    def createMpfbValueRamp3(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, BetweenStop1Value=None, BetweenStop2Value=None, OneStopValue=None, BetweenStop1Position=None, BetweenStop2Position=None):
        return self._molecule_singletons["MpfbValueRamp3"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, BetweenStop1Value=BetweenStop1Value, BetweenStop2Value=BetweenStop2Value, OneStopValue=OneStopValue, BetweenStop1Position=BetweenStop1Position, BetweenStop2Position=BetweenStop2Position)

    def createMpfbValueRamp4(self, x=0.0, y=0.0, name=None, label=None, Value=None, ZeroStopValue=None, BetweenStop1Value=None, BetweenStop2Value=None, BetweenStop3Value=None, OneStopValue=None, BetweenStop1Position=None, BetweenStop2Position=None, BetweenStop3Position=None):
        return self._molecule_singletons["MpfbValueRamp4"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, ZeroStopValue=ZeroStopValue, BetweenStop1Value=BetweenStop1Value, BetweenStop2Value=BetweenStop2Value, BetweenStop3Value=BetweenStop3Value, OneStopValue=OneStopValue, BetweenStop1Position=BetweenStop1Position, BetweenStop2Position=BetweenStop2Position, BetweenStop3Position=BetweenStop3Position)

    def createMpfbWithinDistance(self, x=0.0, y=0.0, name=None, label=None, Coordinate1=None, Coordinate2=None, MaxDist=None):
        return self._molecule_singletons["MpfbWithinDistance"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Coordinate1=Coordinate1, Coordinate2=Coordinate2, MaxDist=MaxDist)

    def createMpfbWithinDistanceOfEither(self, x=0.0, y=0.0, name=None, label=None, Position=None, Coordinate1=None, Coordinate2=None, MaxDist=None):
        return self._molecule_singletons["MpfbWithinDistanceOfEither"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Position=Position, Coordinate1=Coordinate1, Coordinate2=Coordinate2, MaxDist=MaxDist)
