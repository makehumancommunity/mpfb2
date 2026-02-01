# MHMAT

This file explains the MHMAT file format.

## Purpose

An MHMAT file defines a material for use with MakeHuman or MPFB meshes. It describes surface properties such as
colors, textures, transparency, sub-surface scattering, and shader parameters. MHMAT files are referenced from
MHCLO files via the `material` key.

## Structure

An MHMAT file is a text-based format. Each line contains a key-value pair in the form:

```
key value
```

Lines starting with `#` or `//` are comments and are ignored. Keys are organized into logical groups described below.
Only keys with values need to be present; absent keys use their defaults.

### Metadata

- name `<material_name>` - Display name of the material
- description `<text>` - Human-readable description
- uuid `<unique_id>` - Unique identifier for this material
- license `<license_type>` - License (e.g., CC0, CC-BY). Defaults to CC0
- author `<author_name>` - Creator name
- homepage `<url>` - URL for the material's homepage
- tag `<tag_text>` - Categorization tag. Can appear multiple times for multiple tags

### Colors

RGB values in the range 0.0-1.0, specified as three floats:

- diffuseColor `<r>` `<g>` `<b>` - Base color / albedo. Default: 0.5 0.5 0.5
- specularColor `<r>` `<g>` `<b>` - Specular highlight color. Default: 0.5 0.5 0.5
- emissiveColor `<r>` `<g>` `<b>` - Self-emitted light color
- ambientColor `<r>` `<g>` `<b>` - Ambient lighting color
- viewPortColor `<r>` `<g>` `<b>` - Viewport display color

### Textures

File paths to texture images. Paths are relative to the MHMAT file. 
Backslashes are normalized to forward slashes during parsing.

- diffuseTexture `<filename>` - Base color / albedo map
- bumpmapTexture `<filename>` - Bump map
- normalmapTexture `<filename>` - Normal map
- displacementmapTexture `<filename>` - Displacement map
- specularmapTexture `<filename>` - Specular intensity map
- transmissionmapTexture `<filename>` - Transmission / refraction map
- opacitymapTexture `<filename>` - Opacity / alpha map
- roughnessmapTexture `<filename>` - Roughness map
- metallicmapTexture `<filename>` - Metallic map
- aomapTexture `<filename>` - Ambient occlusion map
- emissionColorMapTexture `<filename>` - Emission color map
- emissionStrengthMapTexture `<filename>` - Emission strength map
- subsurfaceColorMapTexture `<filename>` - Sub-surface scattering color map
- subsurfaceStrengthMapTexture `<filename>` - Sub-surface scattering strength map

#### Texture Key Aliases

Several alternative key names are accepted and mapped to canonical names:

| Alias | Canonical Key |
|-------|---------------|
| diffusemapTexture | diffuseTexture |
| albedoTexture | diffuseTexture |
| albedoMapTexture | diffuseTexture |
| basecolorTexture | diffuseTexture |
| basecolorMapTexture | diffuseTexture |
| bumpTexture | bumpmapTexture |
| opacityTexture | opacitymapTexture |
| opacityMapTexture | opacitymapTexture |
| emissiveTexture | emissionColorMapTexture |
| emissionTexture | emissionColorMapTexture |
| sssTexture | subsurfaceColorMapTexture |
| sssMapTexture | subsurfaceColorMapTexture |

### Intensities

Float values controlling texture and effect strengths:

- diffuseIntensity `<float>` - Base color texture influence
- bumpmapIntensity `<float>` - Bump map strength
- normalmapIntensity `<float>` - Normal map strength
- displacementmapIntensity `<float>` - Displacement map strength
- specularmapIntensity `<float>` - Specular map influence
- opacitymapIntensity `<float>` - Opacity texture influence
- aomapIntensity `<float>` - Ambient occlusion map strength
- emissionIntensity `<float>` - Emission / glow strength
- subsurfaceIntensity `<float>` - Sub-surface scattering strength

### Sub-Surface Scattering (SSS)

Controls for skin-like light translucency:

- sssEnabled `<boolean>` - Enable SSS
- sssRScale `<float>` - Red channel SSS radius scale
- sssGScale `<float>` - Green channel SSS radius scale
- sssBScale `<float>` - Blue channel SSS radius scale

### Material Properties

- metallic `<float>` - Metallic value (0.0-1.0)
- roughness `<float>` - Surface roughness (0.0-1.0). Default: 0.7
- shininess `<float>` - Specular shininess. Default: 0.3
- opacity `<float>` - Opacity (0.0-1.0, where 1.0 is fully opaque). Default: 1.0
- ior `<float>` - Index of refraction
- translucency `<float>` - How much light passes through the surface
- litsphereTexture `<name>` - Lit sphere texture for special shading. Default: lit_leather
- blendMaterial `<filename>` - Another material to blend with

### Boolean Flags

Boolean values accept `true`, `t`, or `1` (case-insensitive) for true; anything else is false.

- shadeless `<boolean>` - Render without shading. Default: false
- wireframe `<boolean>` - Show as wireframe. Default: false
- transparent `<boolean>` - Material uses transparency. Default: false
- alphaToCoverage `<boolean>` - Use alpha-to-coverage. Default: true
- backfaceCull `<boolean>` - Cull back-facing polygons. Default: true
- depthless `<boolean>` - Ignore depth testing. Default: false
- castShadows `<boolean>` - Object casts shadows. Default: true
- receiveShadows `<boolean>` - Object receives shadows. Default: true
- autoBlendSkin `<boolean>` - Auto-blend with skin material

### Shader Properties

These keys control how the material appears in MakeHuman's viewport and are not used by MPFB's Blender rendering:

- shader `<shader_path>` - Shader program path (e.g., `shaders/glsl/litsphere`)
- shaderParam `<key>` `<value>` - Shader parameter
- shader_config `<key>` `<value>` - Shader configuration flag

## Example content

```
# This is a material for MakeHuman or MPFB

// Metadata

name My Skin Material
description A realistic skin material
uuid 59985471-ab08-479f-a32d-2d88411714ef
license CC0
author John Doe
tag skin
tag realistic

// Color

diffuseColor 0.7210 0.5680 0.4310
specularColor 0.5000 0.5000 0.5000

// Texture

diffuseTexture diffuse_skin.png
normalmapTexture normalmap_skin.png
roughnessmapTexture roughness_skin.png

// Intensity

diffuseIntensity 1.0000
normalmapIntensity 0.8000

// SSS

sssEnabled true
sssRScale 0.1000
sssGScale 0.1000
sssBScale 0.1000

// Various

metallic 0.0000
roughness 0.5000
shininess 0.3000
opacity 1.0000
ior 1.4500
transparent false
backfaceCull true
castShadows true
receiveShadows true

// Shader (MakeHuman viewport only)

shader shaders/glsl/litsphere
shaderParam litsphereTexture litspheres/lit_leather.png
```
