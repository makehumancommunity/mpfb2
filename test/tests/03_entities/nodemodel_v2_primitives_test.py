import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.systemservice import SystemService

from mpfb.entities.nodemodel.v2 import *

def test_primitives_are_available():
    assert snAddShader
    assert snAmbientOcclusion
    assert snAttribute
    assert snBackground
    assert snBevel
    assert snBlackbody
    assert snBrightContrast
    assert snBsdfAnisotropic
    assert snBsdfDiffuse
    assert snBsdfGlass
    assert snBsdfHair
    assert snBsdfHairPrincipled
    assert snBsdfPrincipled
    assert snBsdfRefraction
    assert snBsdfSheen
    assert snBsdfToon
    assert snBsdfTranslucent
    assert snBsdfTransparent
    assert snBump
    assert snCameraData
    assert snClamp
    assert snCombineColor
    assert snCombineHSV
    assert snCombineRGB
    assert snCombineXYZ
    assert snDisplacement
    assert snEeveeSpecular
    assert snEmission
    assert snFloatCurve
    assert snFresnel
    assert snGamma
    assert snGroup
    assert snHairInfo
    assert snHoldout
    assert snHueSaturation
    assert snInvert
    assert snLayerWeight
    assert snLightFalloff
    assert snLightPath
    assert snMapRange
    assert snMapping
    assert snMath
    assert snMix
    assert snMixRGB
    assert snMixShader
    assert snNewGeometry
    assert snNormal
    assert snNormalMap
    assert snObjectInfo
    assert snOutputAOV
    assert snOutputLight
    assert snOutputLineStyle
    assert snOutputMaterial
    assert snOutputWorld
    assert snParticleInfo
    assert snPointInfo
    assert snRGB
    assert snRGBCurve
    assert snRGBToBW
    assert snScript
    assert snSeparateColor
    assert snSeparateHSV
    assert snSeparateRGB
    assert snSeparateXYZ
    assert snShaderToRGB
    assert snSqueeze
    assert snSubsurfaceScattering
    assert snTangent
    assert snTexBrick
    assert snTexChecker
    assert snTexCoord
    assert snTexEnvironment
    assert snTexGradient
    assert snTexIES
    assert snTexImage
    assert snTexMagic
    if not SystemService.is_blender_version_at_least(version=[4,1,0]):
        assert snTexMusgrave
    assert snTexNoise
    assert snTexPointDensity
    assert snTexSky
    assert snTexVoronoi
    assert snTexWave
    assert snTexWhiteNoise
    assert snUVAlongStroke
    assert snUVMap
    assert snValToRGB
    assert snValue
    assert snVectorCurve
    assert snVectorDisplacement
    assert snVectorMath
    assert snVectorRotate
    assert snVectorTransform
    assert snVertexColor
    assert snVolumeAbsorption
    assert snVolumeInfo
    assert snVolumePrincipled
    assert snVolumeScatter
    assert snWavelength
    assert snWireframe

def test_can_create_snaddshader():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snAddShader.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeAddShader"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snambientocclusion():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snAmbientOcclusion.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeAmbientOcclusion"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snattribute():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snAttribute.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeAttribute"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbackground():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBackground.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBackground"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbevel():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBevel.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBevel"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snblackbody():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBlackbody.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBlackbody"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbrightcontrast():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBrightContrast.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBrightContrast"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfanisotropic():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfAnisotropic.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfAnisotropic"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfdiffuse():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfDiffuse.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfDiffuse"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfglass():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfGlass.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfGlass"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfhair():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfHair.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfHair"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfhairprincipled():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfHairPrincipled.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfHairPrincipled"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfprincipled():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfPrincipled.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfPrincipled"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfrefraction():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfRefraction.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfRefraction"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdfsheen():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfSheen.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfSheen"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdftoon():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfToon.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfToon"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdftranslucent():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfTranslucent.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfTranslucent"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbsdftransparent():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBsdfTransparent.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBsdfTransparent"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snbump():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snBump.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeBump"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sncameradata():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snCameraData.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeCameraData"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snclamp():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snClamp.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeClamp"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sncombinecolor():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snCombineColor.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeCombineColor"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sncombinehsv():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snCombineHSV.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeCombineHSV"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sncombinergb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snCombineRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeCombineRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sncombinexyz():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snCombineXYZ.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeCombineXYZ"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sndisplacement():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snDisplacement.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeDisplacement"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sneeveespecular():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snEeveeSpecular.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeEeveeSpecular"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snemission():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snEmission.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeEmission"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snfloatcurve():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snFloatCurve.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeFloatCurve"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snfresnel():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snFresnel.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeFresnel"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sngamma():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snGamma.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeGamma"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sngroup():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snGroup.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeGroup"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snhairinfo():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snHairInfo.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeHairInfo"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snholdout():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snHoldout.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeHoldout"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snhuesaturation():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snHueSaturation.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeHueSaturation"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sninvert():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snInvert.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeInvert"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snlayerweight():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snLayerWeight.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeLayerWeight"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snlightfalloff():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snLightFalloff.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeLightFalloff"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snlightpath():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snLightPath.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeLightPath"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmaprange():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMapRange.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMapRange"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmapping():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMapping.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMapping"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmath():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMath.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMath"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmix():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMix.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMix"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmixrgb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMixRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMixRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snmixshader():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snMixShader.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeMixShader"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snnewgeometry():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snNewGeometry.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeNewGeometry"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snnormal():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snNormal.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeNormal"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snnormalmap():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snNormalMap.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeNormalMap"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snobjectinfo():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snObjectInfo.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeObjectInfo"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snoutputaov():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snOutputAOV.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeOutputAOV"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snoutputlight():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snOutputLight.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeOutputLight"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snoutputlinestyle():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snOutputLineStyle.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeOutputLineStyle"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snoutputmaterial():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snOutputMaterial.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeOutputMaterial"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snoutputworld():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snOutputWorld.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeOutputWorld"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snparticleinfo():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snParticleInfo.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeParticleInfo"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snpointinfo():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snPointInfo.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodePointInfo"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snrgb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snrgbcurve():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snRGBCurve.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeRGBCurve"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snrgbtobw():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snRGBToBW.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeRGBToBW"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snscript():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snScript.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeScript"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snseparatecolor():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSeparateColor.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSeparateColor"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snseparatehsv():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSeparateHSV.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSeparateHSV"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snseparatergb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSeparateRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSeparateRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snseparatexyz():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSeparateXYZ.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSeparateXYZ"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snshadertorgb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snShaderToRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeShaderToRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snsqueeze():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSqueeze.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSqueeze"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snsubsurfacescattering():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snSubsurfaceScattering.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeSubsurfaceScattering"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntangent():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTangent.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTangent"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexbrick():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexBrick.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexBrick"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexchecker():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexChecker.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexChecker"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexcoord():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexCoord.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexCoord"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexenvironment():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexEnvironment.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexEnvironment"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexgradient():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexGradient.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexGradient"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexies():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexIES.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexIES"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snteximage():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexImage.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexImage"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexmagic():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexMagic.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexMagic"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexmusgrave():
    if SystemService.is_blender_version_at_least(version=[4,1,0]):
        return
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexMusgrave.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexMusgrave"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexnoise():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexNoise.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexNoise"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexpointdensity():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexPointDensity.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexPointDensity"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexsky():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexSky.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexSky"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexvoronoi():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexVoronoi.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexVoronoi"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexwave():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexWave.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexWave"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_sntexwhitenoise():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snTexWhiteNoise.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeTexWhiteNoise"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snuvalongstroke():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snUVAlongStroke.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeUVAlongStroke"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snuvmap():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snUVMap.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeUVMap"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvaltorgb():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snValToRGB.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeValToRGB"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvalue():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snValue.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeValue"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvectorcurve():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVectorCurve.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVectorCurve"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvectordisplacement():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVectorDisplacement.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVectorDisplacement"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvectormath():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVectorMath.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVectorMath"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvectorrotate():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVectorRotate.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVectorRotate"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvectortransform():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVectorTransform.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVectorTransform"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvertexcolor():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVertexColor.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVertexColor"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvolumeabsorption():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVolumeAbsorption.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVolumeAbsorption"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvolumeinfo():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVolumeInfo.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVolumeInfo"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvolumeprincipled():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVolumePrincipled.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVolumePrincipled"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snvolumescatter():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snVolumeScatter.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeVolumeScatter"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snwavelength():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snWavelength.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeWavelength"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_can_create_snwireframe():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = snWireframe.create_instance(node_tree)
    assert node
    assert node.__class__.__name__ == "ShaderNodeWireframe"
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
