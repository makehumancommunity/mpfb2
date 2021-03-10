# diffuseTexture

* __Data type:__ filename
* __What is it for:__ adding different colors to different parts of the surface
* __Use when:__ you want detailed control over the colors of the surface
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ yes

The diffuseTexture controls the color of a surface. This is what you usually mean when 
saying "texture" or "image texture". You will probably want this in all cases but the 
most primitive ones. 

If you want a plain color covering the entire surface, you do not need a diffuseTexture. 
In those cases you can use the [diffuseColor](diffuseColor.md) setting instead.

The diffuseTexture can also cater for primitive transparency. The alpha channel is 
preserved in both blender and MakeHuman. If you want transparency which also takes
IOR etc into account, see [transparencymapTexture](transparencymapTexture.md). But only
the diffuseTexture alpha transparency is shown in MakeHuman.

## Example

    diffuseTexture mycharacter_diffuse.png

