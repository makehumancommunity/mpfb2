# MakeSkin

MakeSkin is available on the "materials" tab in MPFB.

MakeSkin is a tool for working with MakeHuman materials. It is intended for uses where more advanced settings are needed,
as opposed to (for example) the rather primitive materials written by MakeClothes. MakeSkin can be used by the
Makehuman Plugin For Blender to get support for the full material model, although this feature is currently experimental
and only exists in a feature branch of MPFB.

It is also intended to cater for production of skin materials, something which was never supported by MakeClothes. 

In the longer run, it is intended that the full MHMAT model should be supported, with both import and export to/from
blender node setups. However, at this point, there are areas which do not map. See "compatibility matrix" below.
 
## Current status

The tool works mostly as intended, although parts of the MHMAT model is yet unimplemented. You should be able to use
it to produce more competent materials for MakeHuman. 

Note though that the asset repos do not yet support all texture files. It will thus be difficult to share materials
using all features. Work is in progress to remedy this.  
 
## Installation and usage

A zip with the plugin is available from [the plugins page](http://www.makehumancommunity.org/content/plugins.html)
at the community homepage. This can be installed as an addon in Blender. 

## Compatibility matrix

The following is an overview of how the MakeSkin material model fits into MHMAT, Blender and MakeHuman.

"Visible in blender" means that the material feature can be represented in such a way that it would make a visible difference 
in Blender (even if this has not been implemented by MakeSkin yet). "Visible in MH" means that the feature will make a visible 
difference in MakeHuman, under the right conditions (not all shaders in MH support all material features). 

It should be especially noted that the MHMAT model is wider than what is actually implemented in MakeHuman, so there are 
several keys that are supported by MHMAT, but which makes no visible difference at all in MakeHuman.

On the opposite end it should be noted that a few keys have been added to make the handling in blender more smooth. These
keys are outside the MHMAT spec and will not make a visible difference in MakeHuman. They will, however, survive the roundtrip
to blender: If you use makeskin (or MPFB with makeskin enabled) when importing, you will get the settings set in blender.

For more details, see the respective key's documentation.

| MHMAT key                                                           | Implemented in MakeSkin | Visible in Blender | Visible in MH  | Description |  
| :------------------------------------------------------------------ | :---------------------: | :----------------: | :------------: | :---------- |
| [tag](tag.md)                                             | PARTIAL                 | -                  | YES            | Tags are used for filtering in MakeHuman. Materials support multiple tags, but MakeSkin currently only has support for one   |
| [name](name.md)                                           | YES                     | AFTER MHX2 EXPORT  | MATERIAL EDITOR | Name is a simple metadata string in MHMAT files. Used for creation of material name in blender when exported via mhx2.             |
| [description](description.md)                             | YES                     | -                  | -              | Description is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| [uuid](uuid.md)                                           | YES                     | -                  | ?              | UUID is used for telling materials apart. It is unclear if this is ever used though.            |
| [license](license.md)                                     | YES                     | -                  | -              | License is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| [homepage](homepage.md)                                   | YES                     | -                  | -              | Homepage is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| [author](author.md)                                       | YES                     | -                  | -              | Author is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| [diffuseColor](diffuseColor.md)                           | YES                     | YES                | YES            | This is the color of the material. It is usually overwritten by the diffuseTexture.            |
| [specularColor](specularColor.md)                         | PARTIAL                 | -                  | YES            | The color of specular highlights. This is not supported by nodes materials.            |
| [emissiveColor](emissiveColor.md)                         | YES                     | YES                | -              | What light (if any) is emitted by the material.            |
| [ambientColor](ambientColor.md)                           | -                       | -                  | ?              | Color used for simulating ambient light. This is not supported by nodes materials            |
| [viewPortColor](viewPortColor.md)                         | YES                     | YES                | -              | What color to use for material when displaying object in viewport            |
| [diffuseTexture](diffuseTexture.md)                       | YES                     | YES                | YES            | The image file used for diffuse color texturing. This also uses the texture's alpha channel to map for transparency.            |
| [bumpmapTexture](bumpmapTexture.md)                       | YES                     | YES                | -              | The image file used for bump mapping. No shaders in MH are able to represent this visually.            |
| [normalmapTexture](normalmapTexture.md)                   | YES                     | YES                | YES            | The image file used for normal mapping.            |
| [displacementmapTexture](displacementmapTexture.md)       | YES                     | YES                | -              | The image file used for displacement mapping.             |
| [specularmapTexture](specularmapTexture.md)               | -                       | -                  | ?              | Normally used for glossiness of a material. Does not work in Makehuman. Can be used as a map for the Specular socket of the principled shader (sometimes it is also used for roughness variation!)            |
| [transmissionmapTexture](transmissionmapTexture.md)       | YES                     | YES                | -              | The image file used for transmission type transparency mapping. This maps onto the principled's "Transmission" socket, whereas the diffuseTexture alpha channel maps on the "Alpha". The transmission map is ignored in MakeHuman (whereas the alpha channel works) |
| [transparencymapTexture](transparencymapTexture.md)       | -                       | -                  | -              | The image file used for transparency mapping, as an alternative to using the diffuse alpha channel. This is not supported anywhere atm. |
| [aomapTexture](aomapTexture.md)                           | -                       | -                  | ?              | The image file used for ambient occlusion mapping. This is not supported by node materials.            |
| [blendMaterial](blendMaterial.md)                         | YES                     | YES                | -              | A file name pointing at a .blend file with a complete blender material. This is supported by MakeSkin, but not actually a part of the MHMAT spec.            |
| [diffuseIntensity](diffuseIntensity.md)                   | YES                     | YES                | FRINGE CASES   | How much weight should be assigned to the diffuse texture (vs the diffuseColor key). Default is 1.0.            |
| [bumpmapIntensity](bumpmapIntensity.md)                   | YES                     | YES                | -              | How strong is the bump map? Default is 1.0           |
| [normalmapIntensity](normalmapIntensity.md)               | YES                     | YES                | YES            | How strong is the normal map? Default is 1.0            |
| [displacementMapIntensity](displacementmapIntensity.md)   | -                       | YES                | -              | How strong is the displacement map? Default is 1.0            |
| transparencymapIntensity    | -                       | -                  | -              | How strong is the transparency map? Since transparencymapTexture isn't used anywhere, this key is redundant. |
| specularmapIntensity        | -                       | -                  | ?              | How strong is the specular map? Default is 1.0            |
| aomapIntensity              | -                       | -                  | ?              | How strong is the ao map? Default is 1.0            |
| sssEnabled                  | -                       | YES                | ?              | Should we use SSS at all?            |
| sssRScale                   | -                       | YES                | ?              | Scale of red SSS channel            |
| sssGScale                   | -                       | YES                | ?              | Scale of green SSS channel            |
| sssBScale                   | -                       | YES                | ?              | Scale of blue SSS channel            |
| [shininess](shininess.md)                                  | YES                     | YES                | YES            | How shiny is the material. This has been implemented in reverse as roughness in blender.            |
| [roughness](roughness.md)                                  | YES                     | YES                | -              | This is an alias of shininess, specifically for blender            |
| [metallic](metallic.md)                                    | YES                     | YES                | -              | If the material is to be considered metallic            |
| [ior](ior.md)                                              | YES                     | YES                | -              | Index of refraction            |
| opacity                     | -                       | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| translucency                | -                       | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| shadeless                   | YES                     | -                  | YES            | The material is display without shades in MakeHuman (if this is selected, the asset appears with same illuminance and the 3D effect disappears)            |
| wireframe                   | YES                     | -                  | YES            | Whether to render the material as a wireframe in MH. Doesn't have any correspondence in blender.            |
| transparent                 | YES                     | -                  | YES            | If a transparent asset is in front of another asset or even another transparent layer of the same asset, transparent should be switched on. Together with backface culling switched off, it is a standard when e.g. transparency is used for hair. MakeHuman uses dithering techniques to create the assets instead of using a transparent shading itself.             |
| alphaToCoverage             | YES                     | -                  | -              | Use A2C rendering if supported by graphics card (this is a hardware optimization and makes no visible difference)            |
| backfaceCull                | YES                     | -                  | YES            | Should we render both sides of a face or remove ("cull") the back side when rendering? This is not a material property in blender.           |
| depthless                   | YES                     | -                  | ?              | ?            |
| castShadows                 | YES                     | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| receiveShadows              | YES                     | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| autoBlendSkin               | YES                     | -                  | ?              | When using a litsphere, autoadjust diffuse and litsphere texture for skin tone            |
| litsphere (shader)          | YES                     | -                  | YES            | Use the "litsphere" shader when rendering in MakeHuman            |
| litsphere texture (param)   | YES                     | -                  | YES            | When using litsphere, use this texture to emulate reflections            |
| normalmap (shader)          | -                       | -                  | YES            | Use the "normalmap" shader when rendering in MakeHuman            |
| phong (shader)              | -                       | -                  | YES            | Use the "phong" shader when rendering in MakeHuman            |
| skin (shader)               | -                       | -                  | YES            | Use the "skin" shader when rendering in MakeHuman            |
| toon (shader)               | -                       | -                  | YES            | Use the "toon" shader when rendering in MakeHuman            |
| xray (shader)               | -                       | -                  | YES            | Use the "xray" shader when rendering in MakeHuman            |

There are also a bunch of other shaderParam settings which are not listed here. They are usually consequences of the above, such as "normal" 
for saying whether we should take the normal map into account. MakeSkin will infer this from whether the texture is set or not.
