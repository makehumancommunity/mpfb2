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

PRIMITIVE_NODES = dict()
PRIMITIVE_NODES["ShaderNodeAddShader"] = snAddShader
PRIMITIVE_NODES["ShaderNodeAmbientOcclusion"] = snAmbientOcclusion
PRIMITIVE_NODES["ShaderNodeAttribute"] = snAttribute
PRIMITIVE_NODES["ShaderNodeBackground"] = snBackground
PRIMITIVE_NODES["ShaderNodeBevel"] = snBevel
PRIMITIVE_NODES["ShaderNodeBlackbody"] = snBlackbody
PRIMITIVE_NODES["ShaderNodeBrightContrast"] = snBrightContrast
PRIMITIVE_NODES["ShaderNodeBsdfAnisotropic"] = snBsdfAnisotropic
PRIMITIVE_NODES["ShaderNodeBsdfDiffuse"] = snBsdfDiffuse
PRIMITIVE_NODES["ShaderNodeBsdfGlass"] = snBsdfGlass
PRIMITIVE_NODES["ShaderNodeBsdfGlossy"] = snBsdfGlossy
PRIMITIVE_NODES["ShaderNodeBsdfHair"] = snBsdfHair
PRIMITIVE_NODES["ShaderNodeBsdfHairPrincipled"] = snBsdfHairPrincipled
PRIMITIVE_NODES["ShaderNodeBsdfPrincipled"] = snBsdfPrincipled
PRIMITIVE_NODES["ShaderNodeBsdfRefraction"] = snBsdfRefraction
PRIMITIVE_NODES["ShaderNodeBsdfToon"] = snBsdfToon
PRIMITIVE_NODES["ShaderNodeBsdfTranslucent"] = snBsdfTranslucent
PRIMITIVE_NODES["ShaderNodeBsdfTransparent"] = snBsdfTransparent
PRIMITIVE_NODES["ShaderNodeBsdfVelvet"] = snBsdfVelvet
PRIMITIVE_NODES["ShaderNodeBump"] = snBump
PRIMITIVE_NODES["ShaderNodeCameraData"] = snCameraData
PRIMITIVE_NODES["ShaderNodeClamp"] = snClamp
PRIMITIVE_NODES["ShaderNodeCombineColor"] = snCombineColor
PRIMITIVE_NODES["ShaderNodeCombineXYZ"] = snCombineXYZ
PRIMITIVE_NODES["ShaderNodeDisplacement"] = snDisplacement
PRIMITIVE_NODES["ShaderNodeEeveeSpecular"] = snEeveeSpecular
PRIMITIVE_NODES["ShaderNodeEmission"] = snEmission
PRIMITIVE_NODES["ShaderNodeFloatCurve"] = snFloatCurve
PRIMITIVE_NODES["ShaderNodeFresnel"] = snFresnel
PRIMITIVE_NODES["ShaderNodeGamma"] = snGamma
PRIMITIVE_NODES["ShaderNodeGroup"] = snGroup
PRIMITIVE_NODES["ShaderNodeHairInfo"] = snHairInfo
PRIMITIVE_NODES["ShaderNodeHoldout"] = snHoldout
PRIMITIVE_NODES["ShaderNodeHueSaturation"] = snHueSaturation
PRIMITIVE_NODES["ShaderNodeInvert"] = snInvert
PRIMITIVE_NODES["ShaderNodeLayerWeight"] = snLayerWeight
PRIMITIVE_NODES["ShaderNodeLightFalloff"] = snLightFalloff
PRIMITIVE_NODES["ShaderNodeLightPath"] = snLightPath
PRIMITIVE_NODES["ShaderNodeMapRange"] = snMapRange
PRIMITIVE_NODES["ShaderNodeMapping"] = snMapping
PRIMITIVE_NODES["ShaderNodeMath"] = snMath
PRIMITIVE_NODES["ShaderNodeMix"] = snMix
PRIMITIVE_NODES["ShaderNodeMixShader"] = snMixShader
PRIMITIVE_NODES["ShaderNodeNewGeometry"] = snNewGeometry
PRIMITIVE_NODES["ShaderNodeNormal"] = snNormal
PRIMITIVE_NODES["ShaderNodeNormalMap"] = snNormalMap
PRIMITIVE_NODES["ShaderNodeObjectInfo"] = snObjectInfo
PRIMITIVE_NODES["ShaderNodeOutputAOV"] = snOutputAOV
PRIMITIVE_NODES["ShaderNodeOutputLight"] = snOutputLight
PRIMITIVE_NODES["ShaderNodeOutputLineStyle"] = snOutputLineStyle
PRIMITIVE_NODES["ShaderNodeOutputMaterial"] = snOutputMaterial
PRIMITIVE_NODES["ShaderNodeOutputWorld"] = snOutputWorld
PRIMITIVE_NODES["ShaderNodeParticleInfo"] = snParticleInfo
PRIMITIVE_NODES["ShaderNodePointInfo"] = snPointInfo
PRIMITIVE_NODES["ShaderNodeRGB"] = snRGB
PRIMITIVE_NODES["ShaderNodeRGBCurve"] = snRGBCurve
PRIMITIVE_NODES["ShaderNodeRGBToBW"] = snRGBToBW
PRIMITIVE_NODES["ShaderNodeScript"] = snScript
PRIMITIVE_NODES["ShaderNodeSeparateColor"] = snSeparateColor
PRIMITIVE_NODES["ShaderNodeSeparateXYZ"] = snSeparateXYZ
PRIMITIVE_NODES["ShaderNodeShaderToRGB"] = snShaderToRGB
PRIMITIVE_NODES["ShaderNodeSubsurfaceScattering"] = snSubsurfaceScattering
PRIMITIVE_NODES["ShaderNodeTangent"] = snTangent
PRIMITIVE_NODES["ShaderNodeTexBrick"] = snTexBrick
PRIMITIVE_NODES["ShaderNodeTexChecker"] = snTexChecker
PRIMITIVE_NODES["ShaderNodeTexCoord"] = snTexCoord
PRIMITIVE_NODES["ShaderNodeTexEnvironment"] = snTexEnvironment
PRIMITIVE_NODES["ShaderNodeTexGradient"] = snTexGradient
PRIMITIVE_NODES["ShaderNodeTexIES"] = snTexIES
PRIMITIVE_NODES["ShaderNodeTexImage"] = snTexImage
PRIMITIVE_NODES["ShaderNodeTexMagic"] = snTexMagic
PRIMITIVE_NODES["ShaderNodeTexMusgrave"] = snTexMusgrave
PRIMITIVE_NODES["ShaderNodeTexNoise"] = snTexNoise
PRIMITIVE_NODES["ShaderNodeTexPointDensity"] = snTexPointDensity
PRIMITIVE_NODES["ShaderNodeTexSky"] = snTexSky
PRIMITIVE_NODES["ShaderNodeTexVoronoi"] = snTexVoronoi
PRIMITIVE_NODES["ShaderNodeTexWave"] = snTexWave
PRIMITIVE_NODES["ShaderNodeTexWhiteNoise"] = snTexWhiteNoise
PRIMITIVE_NODES["ShaderNodeUVAlongStroke"] = snUVAlongStroke
PRIMITIVE_NODES["ShaderNodeUVMap"] = snUVMap
PRIMITIVE_NODES["ShaderNodeValToRGB"] = snValToRGB
PRIMITIVE_NODES["ShaderNodeValue"] = snValue
PRIMITIVE_NODES["ShaderNodeVectorCurve"] = snVectorCurve
PRIMITIVE_NODES["ShaderNodeVectorDisplacement"] = snVectorDisplacement
PRIMITIVE_NODES["ShaderNodeVectorMath"] = snVectorMath
PRIMITIVE_NODES["ShaderNodeVectorRotate"] = snVectorRotate
PRIMITIVE_NODES["ShaderNodeVectorTransform"] = snVectorTransform
PRIMITIVE_NODES["ShaderNodeVertexColor"] = snVertexColor
PRIMITIVE_NODES["ShaderNodeVolumeAbsorption"] = snVolumeAbsorption
PRIMITIVE_NODES["ShaderNodeVolumeInfo"] = snVolumeInfo
PRIMITIVE_NODES["ShaderNodeVolumePrincipled"] = snVolumePrincipled
PRIMITIVE_NODES["ShaderNodeVolumeScatter"] = snVolumeScatter
PRIMITIVE_NODES["ShaderNodeWavelength"] = snWavelength
PRIMITIVE_NODES["ShaderNodeWireframe"] = snWireframe

__all__ = [
    "AbstractNodeWrapper",
    "PRIMITIVE_NODES",
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
