# bumpmapTexture

* __Data type:__ filename
* __What is it for:__ emulating surface structure 
* __Use when:__ you want detailed control over surface structure
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ no

A bumpmap is the older form of normal mapping. It is a more primitive approach where you have 
a greyscale image where white is up and black is down. It can also be combined with a 
normalmap (as specified with the [normalmapTexture](normalmapTexture.md) setting).

A bumpmap is usually used to emulate forms of surface roughness, such as skin pores or 
rough rocks.

Bumpmaps will not be visible in makehuman.

## Example

    bumpmapTexture mycharacter_bump.png

