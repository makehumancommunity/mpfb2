
from mpfb.services.logservice import LogService
from mpfb.entities.nodemodel._internalnodemanager import InternalNodeManager
_LOG = LogService.get_logger("nodemodel.atoms")
_LOG.trace("initializing nodemodel atoms module")

class AtomNodeManager(InternalNodeManager):
    def __init__(self, node_tree):
        _LOG.trace("Constructing AtomNodeManager with node_tree", node_tree)
        InternalNodeManager.__init__(self, node_tree)

from .shadernodetexcoord import createShaderNodeTexCoord
from .shadernodeattribute import createShaderNodeAttribute
from .shadernodelightpath import createShaderNodeLightPath
from .shadernodefresnel import createShaderNodeFresnel
from .shadernodelayerweight import createShaderNodeLayerWeight
from .shadernodergb import createShaderNodeRGB
from .shadernodevalue import createShaderNodeValue
from .shadernodetangent import createShaderNodeTangent
from .shadernodenewgeometry import createShaderNodeNewGeometry
from .shadernodewireframe import createShaderNodeWireframe
from .shadernodebevel import createShaderNodeBevel
from .shadernodeambientocclusion import createShaderNodeAmbientOcclusion
from .shadernodeobjectinfo import createShaderNodeObjectInfo
from .shadernodehairinfo import createShaderNodeHairInfo
from .shadernodepointinfo import createShaderNodePointInfo
from .shadernodevolumeinfo import createShaderNodeVolumeInfo
from .shadernodeparticleinfo import createShaderNodeParticleInfo
from .shadernodecameradata import createShaderNodeCameraData
from .shadernodeuvmap import createShaderNodeUVMap
from .shadernodevertexcolor import createShaderNodeVertexColor
from .shadernodeuvalongstroke import createShaderNodeUVAlongStroke
from .shadernodeoutputmaterial import createShaderNodeOutputMaterial
from .shadernodeoutputlight import createShaderNodeOutputLight
from .shadernodeoutputaov import createShaderNodeOutputAOV
from .shadernodeoutputworld import createShaderNodeOutputWorld
from .shadernodeoutputlinestyle import createShaderNodeOutputLineStyle
from .shadernodemixshader import createShaderNodeMixShader
from .shadernodeaddshader import createShaderNodeAddShader
from .shadernodebsdfdiffuse import createShaderNodeBsdfDiffuse
from .shadernodebsdfprincipled import createShaderNodeBsdfPrincipled
from .shadernodebsdfglossy import createShaderNodeBsdfGlossy
from .shadernodebsdftransparent import createShaderNodeBsdfTransparent
from .shadernodebsdfrefraction import createShaderNodeBsdfRefraction
from .shadernodebsdfglass import createShaderNodeBsdfGlass
from .shadernodebsdftranslucent import createShaderNodeBsdfTranslucent
from .shadernodebsdfanisotropic import createShaderNodeBsdfAnisotropic
from .shadernodebsdfvelvet import createShaderNodeBsdfVelvet
from .shadernodebsdftoon import createShaderNodeBsdfToon
from .shadernodesubsurfacescattering import createShaderNodeSubsurfaceScattering
from .shadernodeemission import createShaderNodeEmission
from .shadernodebsdfhair import createShaderNodeBsdfHair
from .shadernodebackground import createShaderNodeBackground
from .shadernodeholdout import createShaderNodeHoldout
from .shadernodevolumeabsorption import createShaderNodeVolumeAbsorption
from .shadernodevolumescatter import createShaderNodeVolumeScatter
from .shadernodevolumeprincipled import createShaderNodeVolumePrincipled
from .shadernodeeeveespecular import createShaderNodeEeveeSpecular
from .shadernodebsdfhairprincipled import createShaderNodeBsdfHairPrincipled
from .shadernodeteximage import createShaderNodeTexImage
from .shadernodetexenvironment import createShaderNodeTexEnvironment
from .shadernodetexsky import createShaderNodeTexSky
from .shadernodetexnoise import createShaderNodeTexNoise
from .shadernodetexwave import createShaderNodeTexWave
from .shadernodetexvoronoi import createShaderNodeTexVoronoi
from .shadernodetexmusgrave import createShaderNodeTexMusgrave
from .shadernodetexgradient import createShaderNodeTexGradient
from .shadernodetexmagic import createShaderNodeTexMagic
from .shadernodetexchecker import createShaderNodeTexChecker
from .shadernodetexbrick import createShaderNodeTexBrick
from .shadernodetexpointdensity import createShaderNodeTexPointDensity
from .shadernodetexies import createShaderNodeTexIES
from .shadernodetexwhitenoise import createShaderNodeTexWhiteNoise
from .shadernodemixrgb import createShaderNodeMixRGB
from .shadernodergbcurve import createShaderNodeRGBCurve
from .shadernodeinvert import createShaderNodeInvert
from .shadernodelightfalloff import createShaderNodeLightFalloff
from .shadernodehuesaturation import createShaderNodeHueSaturation
from .shadernodegamma import createShaderNodeGamma
from .shadernodebrightcontrast import createShaderNodeBrightContrast
from .shadernodemapping import createShaderNodeMapping
from .shadernodebump import createShaderNodeBump
from .shadernodedisplacement import createShaderNodeDisplacement
from .shadernodevectordisplacement import createShaderNodeVectorDisplacement
from .shadernodenormalmap import createShaderNodeNormalMap
from .shadernodenormal import createShaderNodeNormal
from .shadernodevectorcurve import createShaderNodeVectorCurve
from .shadernodevectorrotate import createShaderNodeVectorRotate
from .shadernodevectortransform import createShaderNodeVectorTransform
from .shadernodemaprange import createShaderNodeMapRange
from .shadernodefloatcurve import createShaderNodeFloatCurve
from .shadernodeclamp import createShaderNodeClamp
from .shadernodemath import createShaderNodeMath
from .shadernodevaltorgb import createShaderNodeValToRGB
from .shadernodergbtobw import createShaderNodeRGBToBW
from .shadernodeshadertorgb import createShaderNodeShaderToRGB
from .shadernodevectormath import createShaderNodeVectorMath
from .shadernodeseparatecolor import createShaderNodeSeparateColor
from .shadernodecombinecolor import createShaderNodeCombineColor
from .shadernodeseparatexyz import createShaderNodeSeparateXYZ
from .shadernodecombinexyz import createShaderNodeCombineXYZ
from .shadernodewavelength import createShaderNodeWavelength
from .shadernodeblackbody import createShaderNodeBlackbody
from .shadernodescript import createShaderNodeScript
from .shadernodegroup import createShaderNodeGroup

setattr(AtomNodeManager, "createShaderNodeTexCoord", createShaderNodeTexCoord)
setattr(AtomNodeManager, "createShaderNodeAttribute", createShaderNodeAttribute)
setattr(AtomNodeManager, "createShaderNodeLightPath", createShaderNodeLightPath)
setattr(AtomNodeManager, "createShaderNodeFresnel", createShaderNodeFresnel)
setattr(AtomNodeManager, "createShaderNodeLayerWeight", createShaderNodeLayerWeight)
setattr(AtomNodeManager, "createShaderNodeRGB", createShaderNodeRGB)
setattr(AtomNodeManager, "createShaderNodeValue", createShaderNodeValue)
setattr(AtomNodeManager, "createShaderNodeTangent", createShaderNodeTangent)
setattr(AtomNodeManager, "createShaderNodeNewGeometry", createShaderNodeNewGeometry)
setattr(AtomNodeManager, "createShaderNodeWireframe", createShaderNodeWireframe)
setattr(AtomNodeManager, "createShaderNodeBevel", createShaderNodeBevel)
setattr(AtomNodeManager, "createShaderNodeAmbientOcclusion", createShaderNodeAmbientOcclusion)
setattr(AtomNodeManager, "createShaderNodeObjectInfo", createShaderNodeObjectInfo)
setattr(AtomNodeManager, "createShaderNodeHairInfo", createShaderNodeHairInfo)
setattr(AtomNodeManager, "createShaderNodePointInfo", createShaderNodePointInfo)
setattr(AtomNodeManager, "createShaderNodeVolumeInfo", createShaderNodeVolumeInfo)
setattr(AtomNodeManager, "createShaderNodeParticleInfo", createShaderNodeParticleInfo)
setattr(AtomNodeManager, "createShaderNodeCameraData", createShaderNodeCameraData)
setattr(AtomNodeManager, "createShaderNodeUVMap", createShaderNodeUVMap)
setattr(AtomNodeManager, "createShaderNodeVertexColor", createShaderNodeVertexColor)
setattr(AtomNodeManager, "createShaderNodeUVAlongStroke", createShaderNodeUVAlongStroke)
setattr(AtomNodeManager, "createShaderNodeOutputMaterial", createShaderNodeOutputMaterial)
setattr(AtomNodeManager, "createShaderNodeOutputLight", createShaderNodeOutputLight)
setattr(AtomNodeManager, "createShaderNodeOutputAOV", createShaderNodeOutputAOV)
setattr(AtomNodeManager, "createShaderNodeOutputWorld", createShaderNodeOutputWorld)
setattr(AtomNodeManager, "createShaderNodeOutputLineStyle", createShaderNodeOutputLineStyle)
setattr(AtomNodeManager, "createShaderNodeMixShader", createShaderNodeMixShader)
setattr(AtomNodeManager, "createShaderNodeAddShader", createShaderNodeAddShader)
setattr(AtomNodeManager, "createShaderNodeBsdfDiffuse", createShaderNodeBsdfDiffuse)
setattr(AtomNodeManager, "createShaderNodeBsdfPrincipled", createShaderNodeBsdfPrincipled)
setattr(AtomNodeManager, "createShaderNodeBsdfGlossy", createShaderNodeBsdfGlossy)
setattr(AtomNodeManager, "createShaderNodeBsdfTransparent", createShaderNodeBsdfTransparent)
setattr(AtomNodeManager, "createShaderNodeBsdfRefraction", createShaderNodeBsdfRefraction)
setattr(AtomNodeManager, "createShaderNodeBsdfGlass", createShaderNodeBsdfGlass)
setattr(AtomNodeManager, "createShaderNodeBsdfTranslucent", createShaderNodeBsdfTranslucent)
setattr(AtomNodeManager, "createShaderNodeBsdfAnisotropic", createShaderNodeBsdfAnisotropic)
setattr(AtomNodeManager, "createShaderNodeBsdfVelvet", createShaderNodeBsdfVelvet)
setattr(AtomNodeManager, "createShaderNodeBsdfToon", createShaderNodeBsdfToon)
setattr(AtomNodeManager, "createShaderNodeSubsurfaceScattering", createShaderNodeSubsurfaceScattering)
setattr(AtomNodeManager, "createShaderNodeEmission", createShaderNodeEmission)
setattr(AtomNodeManager, "createShaderNodeBsdfHair", createShaderNodeBsdfHair)
setattr(AtomNodeManager, "createShaderNodeBackground", createShaderNodeBackground)
setattr(AtomNodeManager, "createShaderNodeHoldout", createShaderNodeHoldout)
setattr(AtomNodeManager, "createShaderNodeVolumeAbsorption", createShaderNodeVolumeAbsorption)
setattr(AtomNodeManager, "createShaderNodeVolumeScatter", createShaderNodeVolumeScatter)
setattr(AtomNodeManager, "createShaderNodeVolumePrincipled", createShaderNodeVolumePrincipled)
setattr(AtomNodeManager, "createShaderNodeEeveeSpecular", createShaderNodeEeveeSpecular)
setattr(AtomNodeManager, "createShaderNodeBsdfHairPrincipled", createShaderNodeBsdfHairPrincipled)
setattr(AtomNodeManager, "createShaderNodeTexImage", createShaderNodeTexImage)
setattr(AtomNodeManager, "createShaderNodeTexEnvironment", createShaderNodeTexEnvironment)
setattr(AtomNodeManager, "createShaderNodeTexSky", createShaderNodeTexSky)
setattr(AtomNodeManager, "createShaderNodeTexNoise", createShaderNodeTexNoise)
setattr(AtomNodeManager, "createShaderNodeTexWave", createShaderNodeTexWave)
setattr(AtomNodeManager, "createShaderNodeTexVoronoi", createShaderNodeTexVoronoi)
setattr(AtomNodeManager, "createShaderNodeTexMusgrave", createShaderNodeTexMusgrave)
setattr(AtomNodeManager, "createShaderNodeTexGradient", createShaderNodeTexGradient)
setattr(AtomNodeManager, "createShaderNodeTexMagic", createShaderNodeTexMagic)
setattr(AtomNodeManager, "createShaderNodeTexChecker", createShaderNodeTexChecker)
setattr(AtomNodeManager, "createShaderNodeTexBrick", createShaderNodeTexBrick)
setattr(AtomNodeManager, "createShaderNodeTexPointDensity", createShaderNodeTexPointDensity)
setattr(AtomNodeManager, "createShaderNodeTexIES", createShaderNodeTexIES)
setattr(AtomNodeManager, "createShaderNodeTexWhiteNoise", createShaderNodeTexWhiteNoise)
setattr(AtomNodeManager, "createShaderNodeMixRGB", createShaderNodeMixRGB)
setattr(AtomNodeManager, "createShaderNodeRGBCurve", createShaderNodeRGBCurve)
setattr(AtomNodeManager, "createShaderNodeInvert", createShaderNodeInvert)
setattr(AtomNodeManager, "createShaderNodeLightFalloff", createShaderNodeLightFalloff)
setattr(AtomNodeManager, "createShaderNodeHueSaturation", createShaderNodeHueSaturation)
setattr(AtomNodeManager, "createShaderNodeGamma", createShaderNodeGamma)
setattr(AtomNodeManager, "createShaderNodeBrightContrast", createShaderNodeBrightContrast)
setattr(AtomNodeManager, "createShaderNodeMapping", createShaderNodeMapping)
setattr(AtomNodeManager, "createShaderNodeBump", createShaderNodeBump)
setattr(AtomNodeManager, "createShaderNodeDisplacement", createShaderNodeDisplacement)
setattr(AtomNodeManager, "createShaderNodeVectorDisplacement", createShaderNodeVectorDisplacement)
setattr(AtomNodeManager, "createShaderNodeNormalMap", createShaderNodeNormalMap)
setattr(AtomNodeManager, "createShaderNodeNormal", createShaderNodeNormal)
setattr(AtomNodeManager, "createShaderNodeVectorCurve", createShaderNodeVectorCurve)
setattr(AtomNodeManager, "createShaderNodeVectorRotate", createShaderNodeVectorRotate)
setattr(AtomNodeManager, "createShaderNodeVectorTransform", createShaderNodeVectorTransform)
setattr(AtomNodeManager, "createShaderNodeMapRange", createShaderNodeMapRange)
setattr(AtomNodeManager, "createShaderNodeFloatCurve", createShaderNodeFloatCurve)
setattr(AtomNodeManager, "createShaderNodeClamp", createShaderNodeClamp)
setattr(AtomNodeManager, "createShaderNodeMath", createShaderNodeMath)
setattr(AtomNodeManager, "createShaderNodeValToRGB", createShaderNodeValToRGB)
setattr(AtomNodeManager, "createShaderNodeRGBToBW", createShaderNodeRGBToBW)
setattr(AtomNodeManager, "createShaderNodeShaderToRGB", createShaderNodeShaderToRGB)
setattr(AtomNodeManager, "createShaderNodeVectorMath", createShaderNodeVectorMath)
setattr(AtomNodeManager, "createShaderNodeSeparateColor", createShaderNodeSeparateColor)
setattr(AtomNodeManager, "createShaderNodeCombineColor", createShaderNodeCombineColor)
setattr(AtomNodeManager, "createShaderNodeSeparateXYZ", createShaderNodeSeparateXYZ)
setattr(AtomNodeManager, "createShaderNodeCombineXYZ", createShaderNodeCombineXYZ)
setattr(AtomNodeManager, "createShaderNodeWavelength", createShaderNodeWavelength)
setattr(AtomNodeManager, "createShaderNodeBlackbody", createShaderNodeBlackbody)
setattr(AtomNodeManager, "createShaderNodeScript", createShaderNodeScript)
setattr(AtomNodeManager, "createShaderNodeGroup", createShaderNodeGroup)
