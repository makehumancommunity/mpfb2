from .abstractnodewrapper import AbstractNodeWrapper
from .nodewrappershadernodeaddshader import snAddShader
from .nodewrappershadernodeambientocclusion import snAmbientOcclusion
from .nodewrappershadernodeattribute import snAttribute
from .nodewrappershadernodebackground import snBackground
from .nodewrappershadernodebevel import snBevel
from .nodewrappershadernodeblackbody import snBlackbody
from .nodewrappershadernodebrightcontrast import snBrightContrast
from .nodewrappershadernodebsdfanisotropic import snBsdfAnisotropic
from .nodewrappershadernodebsdfdiffuse import snBsdfDiffuse
from .nodewrappershadernodebsdfglass import snBsdfGlass
from .nodewrappershadernodebsdfglossy import snBsdfGlossy
from .nodewrappershadernodebsdfhair import snBsdfHair
from .nodewrappershadernodebsdfhairprincipled import snBsdfHairPrincipled
from .nodewrappershadernodebsdfprincipled import snBsdfPrincipled
from .nodewrappershadernodebsdfrefraction import snBsdfRefraction
from .nodewrappershadernodebsdftoon import snBsdfToon
from .nodewrappershadernodebsdftranslucent import snBsdfTranslucent
from .nodewrappershadernodebsdftransparent import snBsdfTransparent
from .nodewrappershadernodebsdfvelvet import snBsdfVelvet
from .nodewrappershadernodebump import snBump
from .nodewrappershadernodecameradata import snCameraData
from .nodewrappershadernodeclamp import snClamp
from .nodewrappershadernodecombinecolor import snCombineColor
from .nodewrappershadernodecombinexyz import snCombineXYZ
from .nodewrappershadernodedisplacement import snDisplacement
from .nodewrappershadernodeeeveespecular import snEeveeSpecular
from .nodewrappershadernodeemission import snEmission
from .nodewrappershadernodefloatcurve import snFloatCurve
from .nodewrappershadernodefresnel import snFresnel
from .nodewrappershadernodegamma import snGamma
from .nodewrappershadernodegroup import snGroup
from .nodewrappershadernodehairinfo import snHairInfo
from .nodewrappershadernodeholdout import snHoldout
from .nodewrappershadernodehuesaturation import snHueSaturation
from .nodewrappershadernodeinvert import snInvert
from .nodewrappershadernodelayerweight import snLayerWeight
from .nodewrappershadernodelightfalloff import snLightFalloff
from .nodewrappershadernodelightpath import snLightPath
from .nodewrappershadernodemaprange import snMapRange
from .nodewrappershadernodemapping import snMapping
from .nodewrappershadernodemath import snMath
from .nodewrappershadernodemix import snMix
from .nodewrappershadernodemixshader import snMixShader
from .nodewrappershadernodenewgeometry import snNewGeometry
from .nodewrappershadernodenormal import snNormal
from .nodewrappershadernodenormalmap import snNormalMap
from .nodewrappershadernodeobjectinfo import snObjectInfo
from .nodewrappershadernodeoutputaov import snOutputAOV
from .nodewrappershadernodeoutputlight import snOutputLight
from .nodewrappershadernodeoutputlinestyle import snOutputLineStyle
from .nodewrappershadernodeoutputmaterial import snOutputMaterial
from .nodewrappershadernodeoutputworld import snOutputWorld
from .nodewrappershadernodeparticleinfo import snParticleInfo
from .nodewrappershadernodepointinfo import snPointInfo
from .nodewrappershadernodergb import snRGB
from .nodewrappershadernodergbcurve import snRGBCurve
from .nodewrappershadernodergbtobw import snRGBToBW
from .nodewrappershadernodescript import snScript
from .nodewrappershadernodeseparatecolor import snSeparateColor
from .nodewrappershadernodeseparatexyz import snSeparateXYZ
from .nodewrappershadernodeshadertorgb import snShaderToRGB
from .nodewrappershadernodesubsurfacescattering import snSubsurfaceScattering
from .nodewrappershadernodetangent import snTangent
from .nodewrappershadernodetexbrick import snTexBrick
from .nodewrappershadernodetexchecker import snTexChecker
from .nodewrappershadernodetexcoord import snTexCoord
from .nodewrappershadernodetexenvironment import snTexEnvironment
from .nodewrappershadernodetexgradient import snTexGradient
from .nodewrappershadernodetexies import snTexIES
from .nodewrappershadernodeteximage import snTexImage
from .nodewrappershadernodetexmagic import snTexMagic
from .nodewrappershadernodetexmusgrave import snTexMusgrave
from .nodewrappershadernodetexnoise import snTexNoise
from .nodewrappershadernodetexpointdensity import snTexPointDensity
from .nodewrappershadernodetexsky import snTexSky
from .nodewrappershadernodetexvoronoi import snTexVoronoi
from .nodewrappershadernodetexwave import snTexWave
from .nodewrappershadernodetexwhitenoise import snTexWhiteNoise
from .nodewrappershadernodeuvalongstroke import snUVAlongStroke
from .nodewrappershadernodeuvmap import snUVMap
from .nodewrappershadernodevaltorgb import snValToRGB
from .nodewrappershadernodevalue import snValue
from .nodewrappershadernodevectorcurve import snVectorCurve
from .nodewrappershadernodevectordisplacement import snVectorDisplacement
from .nodewrappershadernodevectormath import snVectorMath
from .nodewrappershadernodevectorrotate import snVectorRotate
from .nodewrappershadernodevectortransform import snVectorTransform
from .nodewrappershadernodevertexcolor import snVertexColor
from .nodewrappershadernodevolumeabsorption import snVolumeAbsorption
from .nodewrappershadernodevolumeinfo import snVolumeInfo
from .nodewrappershadernodevolumeprincipled import snVolumePrincipled
from .nodewrappershadernodevolumescatter import snVolumeScatter
from .nodewrappershadernodewavelength import snWavelength
from .nodewrappershadernodewireframe import snWireframe

PRIMITIVE_NODE_WRAPPERS = dict()
PRIMITIVE_NODE_WRAPPERS["ShaderNodeAddShader"] = snAddShader
PRIMITIVE_NODE_WRAPPERS["ShaderNodeAmbientOcclusion"] = snAmbientOcclusion
PRIMITIVE_NODE_WRAPPERS["ShaderNodeAttribute"] = snAttribute
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBackground"] = snBackground
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBevel"] = snBevel
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBlackbody"] = snBlackbody
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBrightContrast"] = snBrightContrast
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfAnisotropic"] = snBsdfAnisotropic
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfDiffuse"] = snBsdfDiffuse
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfGlass"] = snBsdfGlass
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfGlossy"] = snBsdfGlossy
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfHair"] = snBsdfHair
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfHairPrincipled"] = snBsdfHairPrincipled
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfPrincipled"] = snBsdfPrincipled
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfRefraction"] = snBsdfRefraction
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfToon"] = snBsdfToon
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfTranslucent"] = snBsdfTranslucent
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfTransparent"] = snBsdfTransparent
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBsdfVelvet"] = snBsdfVelvet
PRIMITIVE_NODE_WRAPPERS["ShaderNodeBump"] = snBump
PRIMITIVE_NODE_WRAPPERS["ShaderNodeCameraData"] = snCameraData
PRIMITIVE_NODE_WRAPPERS["ShaderNodeClamp"] = snClamp
PRIMITIVE_NODE_WRAPPERS["ShaderNodeCombineColor"] = snCombineColor
PRIMITIVE_NODE_WRAPPERS["ShaderNodeCombineXYZ"] = snCombineXYZ
PRIMITIVE_NODE_WRAPPERS["ShaderNodeDisplacement"] = snDisplacement
PRIMITIVE_NODE_WRAPPERS["ShaderNodeEeveeSpecular"] = snEeveeSpecular
PRIMITIVE_NODE_WRAPPERS["ShaderNodeEmission"] = snEmission
PRIMITIVE_NODE_WRAPPERS["ShaderNodeFloatCurve"] = snFloatCurve
PRIMITIVE_NODE_WRAPPERS["ShaderNodeFresnel"] = snFresnel
PRIMITIVE_NODE_WRAPPERS["ShaderNodeGamma"] = snGamma
PRIMITIVE_NODE_WRAPPERS["ShaderNodeGroup"] = snGroup
PRIMITIVE_NODE_WRAPPERS["ShaderNodeHairInfo"] = snHairInfo
PRIMITIVE_NODE_WRAPPERS["ShaderNodeHoldout"] = snHoldout
PRIMITIVE_NODE_WRAPPERS["ShaderNodeHueSaturation"] = snHueSaturation
PRIMITIVE_NODE_WRAPPERS["ShaderNodeInvert"] = snInvert
PRIMITIVE_NODE_WRAPPERS["ShaderNodeLayerWeight"] = snLayerWeight
PRIMITIVE_NODE_WRAPPERS["ShaderNodeLightFalloff"] = snLightFalloff
PRIMITIVE_NODE_WRAPPERS["ShaderNodeLightPath"] = snLightPath
PRIMITIVE_NODE_WRAPPERS["ShaderNodeMapRange"] = snMapRange
PRIMITIVE_NODE_WRAPPERS["ShaderNodeMapping"] = snMapping
PRIMITIVE_NODE_WRAPPERS["ShaderNodeMath"] = snMath
PRIMITIVE_NODE_WRAPPERS["ShaderNodeMix"] = snMix
PRIMITIVE_NODE_WRAPPERS["ShaderNodeMixShader"] = snMixShader
PRIMITIVE_NODE_WRAPPERS["ShaderNodeNewGeometry"] = snNewGeometry
PRIMITIVE_NODE_WRAPPERS["ShaderNodeNormal"] = snNormal
PRIMITIVE_NODE_WRAPPERS["ShaderNodeNormalMap"] = snNormalMap
PRIMITIVE_NODE_WRAPPERS["ShaderNodeObjectInfo"] = snObjectInfo
PRIMITIVE_NODE_WRAPPERS["ShaderNodeOutputAOV"] = snOutputAOV
PRIMITIVE_NODE_WRAPPERS["ShaderNodeOutputLight"] = snOutputLight
PRIMITIVE_NODE_WRAPPERS["ShaderNodeOutputLineStyle"] = snOutputLineStyle
PRIMITIVE_NODE_WRAPPERS["ShaderNodeOutputMaterial"] = snOutputMaterial
PRIMITIVE_NODE_WRAPPERS["ShaderNodeOutputWorld"] = snOutputWorld
PRIMITIVE_NODE_WRAPPERS["ShaderNodeParticleInfo"] = snParticleInfo
PRIMITIVE_NODE_WRAPPERS["ShaderNodePointInfo"] = snPointInfo
PRIMITIVE_NODE_WRAPPERS["ShaderNodeRGB"] = snRGB
PRIMITIVE_NODE_WRAPPERS["ShaderNodeRGBCurve"] = snRGBCurve
PRIMITIVE_NODE_WRAPPERS["ShaderNodeRGBToBW"] = snRGBToBW
PRIMITIVE_NODE_WRAPPERS["ShaderNodeScript"] = snScript
PRIMITIVE_NODE_WRAPPERS["ShaderNodeSeparateColor"] = snSeparateColor
PRIMITIVE_NODE_WRAPPERS["ShaderNodeSeparateXYZ"] = snSeparateXYZ
PRIMITIVE_NODE_WRAPPERS["ShaderNodeShaderToRGB"] = snShaderToRGB
PRIMITIVE_NODE_WRAPPERS["ShaderNodeSubsurfaceScattering"] = snSubsurfaceScattering
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTangent"] = snTangent
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexBrick"] = snTexBrick
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexChecker"] = snTexChecker
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexCoord"] = snTexCoord
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexEnvironment"] = snTexEnvironment
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexGradient"] = snTexGradient
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexIES"] = snTexIES
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexImage"] = snTexImage
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexMagic"] = snTexMagic
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexMusgrave"] = snTexMusgrave
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexNoise"] = snTexNoise
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexPointDensity"] = snTexPointDensity
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexSky"] = snTexSky
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexVoronoi"] = snTexVoronoi
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexWave"] = snTexWave
PRIMITIVE_NODE_WRAPPERS["ShaderNodeTexWhiteNoise"] = snTexWhiteNoise
PRIMITIVE_NODE_WRAPPERS["ShaderNodeUVAlongStroke"] = snUVAlongStroke
PRIMITIVE_NODE_WRAPPERS["ShaderNodeUVMap"] = snUVMap
PRIMITIVE_NODE_WRAPPERS["ShaderNodeValToRGB"] = snValToRGB
PRIMITIVE_NODE_WRAPPERS["ShaderNodeValue"] = snValue
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVectorCurve"] = snVectorCurve
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVectorDisplacement"] = snVectorDisplacement
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVectorMath"] = snVectorMath
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVectorRotate"] = snVectorRotate
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVectorTransform"] = snVectorTransform
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVertexColor"] = snVertexColor
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVolumeAbsorption"] = snVolumeAbsorption
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVolumeInfo"] = snVolumeInfo
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVolumePrincipled"] = snVolumePrincipled
PRIMITIVE_NODE_WRAPPERS["ShaderNodeVolumeScatter"] = snVolumeScatter
PRIMITIVE_NODE_WRAPPERS["ShaderNodeWavelength"] = snWavelength
PRIMITIVE_NODE_WRAPPERS["ShaderNodeWireframe"] = snWireframe

__all__ = [
    "AbstractNodeWrapper",
    "PRIMITIVE_NODE_WRAPPERS",
    "snAddShader",
    "snAmbientOcclusion",
    "snAttribute",
    "snBackground",
    "snBevel",
    "snBlackbody",
    "snBrightContrast",
    "snBsdfAnisotropic",
    "snBsdfDiffuse",
    "snBsdfGlass",
    "snBsdfGlossy",
    "snBsdfHair",
    "snBsdfHairPrincipled",
    "snBsdfPrincipled",
    "snBsdfRefraction",
    "snBsdfToon",
    "snBsdfTranslucent",
    "snBsdfTransparent",
    "snBsdfVelvet",
    "snBump",
    "snCameraData",
    "snClamp",
    "snCombineColor",
    "snCombineXYZ",
    "snDisplacement",
    "snEeveeSpecular",
    "snEmission",
    "snFloatCurve",
    "snFresnel",
    "snGamma",
    "snGroup",
    "snHairInfo",
    "snHoldout",
    "snHueSaturation",
    "snInvert",
    "snLayerWeight",
    "snLightFalloff",
    "snLightPath",
    "snMapRange",
    "snMapping",
    "snMath",
    "snMix",
    "snMixShader",
    "snNewGeometry",
    "snNormal",
    "snNormalMap",
    "snObjectInfo",
    "snOutputAOV",
    "snOutputLight",
    "snOutputLineStyle",
    "snOutputMaterial",
    "snOutputWorld",
    "snParticleInfo",
    "snPointInfo",
    "snRGB",
    "snRGBCurve",
    "snRGBToBW",
    "snScript",
    "snSeparateColor",
    "snSeparateXYZ",
    "snShaderToRGB",
    "snSubsurfaceScattering",
    "snTangent",
    "snTexBrick",
    "snTexChecker",
    "snTexCoord",
    "snTexEnvironment",
    "snTexGradient",
    "snTexIES",
    "snTexImage",
    "snTexMagic",
    "snTexMusgrave",
    "snTexNoise",
    "snTexPointDensity",
    "snTexSky",
    "snTexVoronoi",
    "snTexWave",
    "snTexWhiteNoise",
    "snUVAlongStroke",
    "snUVMap",
    "snValToRGB",
    "snValue",
    "snVectorCurve",
    "snVectorDisplacement",
    "snVectorMath",
    "snVectorRotate",
    "snVectorTransform",
    "snVertexColor",
    "snVolumeAbsorption",
    "snVolumeInfo",
    "snVolumePrincipled",
    "snVolumeScatter",
    "snWavelength",
    "snWireframe"
]
