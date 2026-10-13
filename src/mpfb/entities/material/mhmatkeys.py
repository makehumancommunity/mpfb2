"""The catalog of MHMAT keys, and the lookup tables MhMaterial parses against."""

from .mhmatkeytypes import *

MHMAT_KEY_GROUPS: list[str] = ["Metadata", "Color", "Texture", "Intensity", "SSS", "Various"]
"""The group names as_mhmat() writes, in the order it writes them.

Every key in MHMAT_KEYS carries one of these as its key_group. The two groups the shader classes
default to, "Shader" and the "Shaders" MHMAT_SHADER_KEYS passes, are deliberately not here: no key
in MHMAT_KEYS uses either, so as_mhmat() never reaches a section for them."""

MHMAT_KEYS: list[MhMatKey] = []
"""Every MHMAT key, in the order the groups below declare them."""

### METADATA ###

MHMAT_KEYS.append(MhMatStringKey("tag", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("name", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("description", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("uuid", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("license", 'CC0', 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("homepage", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringKey("author", None, 'Metadata'))
MHMAT_KEYS.append(MhMatStringShaderKey("shaderParam", None, 'Metadata'))

### COLORS ###

MHMAT_KEYS.append(MhMatColorKey("diffuseColor", [0.5, 0.5, 0.5], 'Color'))
MHMAT_KEYS.append(MhMatColorKey("specularColor", [0.5, 0.5, 0.5], 'Color'))
MHMAT_KEYS.append(MhMatColorKey("emissiveColor", None, 'Color'))
MHMAT_KEYS.append(MhMatColorKey("ambientColor", None, 'Color'))
MHMAT_KEYS.append(MhMatColorKey("viewPortColor", None, 'Color'))

### TEXTURES ###

MHMAT_KEYS.append(MhMatFileKey("diffuseTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("bumpmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("normalmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("displacementmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("specularmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("transmissionmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("opacitymapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("roughnessmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("metallicmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("aomapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("emissionColorMapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("emissionStrengthMapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("subsurfaceColorMapTexture", None, 'Texture'))
MHMAT_KEYS.append(MhMatFileKey("subsurfaceStrengthMapTexture", None, 'Texture'))


### INTENSITIES ###

MHMAT_KEYS.append(MhMatFloatKey("diffuseIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("bumpmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("normalmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("displacementMapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("specularmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("opacitymapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("aomapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("emissionIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MhMatFloatKey("subsurfaceIntensity", None, 'Intensity'))

### SSS ###

MHMAT_KEYS.append(MhMatBooleanKey("sssEnabled", None, 'SSS'))
MHMAT_KEYS.append(MhMatFloatKey("sssRScale", None, 'SSS'))
MHMAT_KEYS.append(MhMatFloatKey("sssGScale", None, 'SSS'))
MHMAT_KEYS.append(MhMatFloatKey("sssBScale", None, 'SSS'))

### VARIOUS ###

MHMAT_KEYS.append(MhMatFileKey("litsphereTexture", "lit_leather", 'Various'))
MHMAT_KEYS.append(MhMatFileKey("blendMaterial", None, 'Various', blendMaterial=True))
MHMAT_KEYS.append(MhMatFloatKey("metallic", None, 'Various'))
MHMAT_KEYS.append(MhMatFloatKey("ior", None, 'Various'))
MHMAT_KEYS.append(MhMatFloatKey("roughness", 0.7, 'Various'))
MHMAT_KEYS.append(MhMatFloatKey("shininess", 0.3, 'Various'))
MHMAT_KEYS.append(MhMatFloatKey("opacity", 1.0, 'Various'))
MHMAT_KEYS.append(MhMatFloatKey("translucency", None, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("shadeless", False, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("wireframe", False, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("transparent", False, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("alphaToCoverage", True, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("backfaceCull", True, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("depthless", False, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("castShadows", True, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("receiveShadows", True, 'Various'))
MHMAT_KEYS.append(MhMatBooleanKey("autoBlendSkin", None, 'Various'))

# ALIASES

MHMAT_ALIAS: dict[str, str] = {}
"""Legacy or alternative key name to the canonical name parse_alias() rewrites it to."""
MHMAT_ALIAS["diffusemapTexture"] = "diffuseTexture"
MHMAT_ALIAS["bumpTexture"] = "bumpmapTexture"
MHMAT_ALIAS["albedoTexture"] = "diffuseTexture"
MHMAT_ALIAS["albedoMapTexture"] = "diffuseTexture"
MHMAT_ALIAS["basecolorTexture"] = "diffuseTexture"
MHMAT_ALIAS["basecolorMapTexture"] = "diffuseTexture"
MHMAT_ALIAS["opacityTexture"] = "opacitymapTexture"
MHMAT_ALIAS["opacityMapTexture"] = "opacitymapTexture"
MHMAT_ALIAS["emissiveTexture"] = "emissionColorMapTexture"
MHMAT_ALIAS["emissionTexture"] = "emissionColorMapTexture"
MHMAT_ALIAS["sssTexture"] = "subsurfaceColorMapTexture"
MHMAT_ALIAS["sssMapTexture"] = "subsurfaceColorMapTexture"

def parse_alias(texture_name: str) -> str:
    """Return the canonical name for a key name, or the name unchanged if it is not an alias."""
    for key in MHMAT_ALIAS.keys():
        name = str(key).lower()
        if str(texture_name).lower() == name:
            return str(MHMAT_ALIAS[key])
    return texture_name

MHMAT_NAME_TO_KEY: dict[str, MhMatKey] = {}
"""Lowercased key name to the key object, for the O(1) dispatch MhMaterial parses with."""

for keyObj in MHMAT_KEYS:
    keyname = keyObj.key_name_lower
    MHMAT_NAME_TO_KEY[keyname] = keyObj

# SHADERS

MHMAT_SHADER_KEYS: list[MhMatKey] = []
"""The shader lines of the format, declared but not read anywhere in MPFB.

MhMaterial parses "shader" and "shaderConfig" lines nowhere and "shaderParam" through MHMAT_KEYS
instead, so nothing imports this list. It is kept as the format's own record of which shader lines
exist."""

MHMAT_SHADER_KEYS.append(MhMatStringKey("shader", None, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatStringShaderKey("shaderParam litsphereTexture", None, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig ambientOcclusion", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig normal", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig bump", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig displacement", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig vertexColors", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig spec", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig transparency", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MhMatBooleanShaderKey("shaderConfig diffuse", True, 'Shaders'))
