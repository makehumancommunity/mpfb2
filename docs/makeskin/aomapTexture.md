# aomapTexture

* __Data type:__ filename
* __What is it for:__ mapping ambient occlusion 
* __Use when:__ you want to map ambient occlusion
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ yes

When emulating secondary light in MakeHuman, you can use map for ambient occlusion. This is treated 
on a per-world setting in blender though, so it will have no effect there. 

## Example

    aomapTexture mycharacter_ao.png

