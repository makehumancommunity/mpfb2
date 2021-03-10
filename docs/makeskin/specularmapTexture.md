# specularmapTexture

* __Data type:__ filename
* __What is it for:__ mapping color of specular highlights
* __Use when:__ when you want detailed control over specular highlights in makehuman
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ yes

In makehuman you can set the color of specular highlights by either using the [specularColor](specularColor.md) setting, 
which sets highlight color for the entire object, or by using a image texture for mapping the same. The 
specularmapTexture is for using an image texture. 

There is no corresponding setting for the principled node in blender, so this setting is not used there.

## Example

    specularmapTexture mycharacter_diffuse.png




