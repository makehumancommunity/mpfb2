# normalmapTexture

* __Data type:__ filename
* __What is it for:__ emulating structural changes on a surface 
* __Use when:__ you want detailed structure, such as wrinkles or pores
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ yes

A normalmap is the standard approach for adding fine detail structure to a surface. A normalmap
emulates changes in structure by adding shadows as if the structure had bent in certain ways. 

This is used where the mesh would become too dense if you tried to model the same structure by 
using vertices. 

In blender you can "bake" normalmaps from sculpting, but it outside the scope of this documentation
to describe this process.

## Example

    normalmapTexture mycharacter_normal.png

