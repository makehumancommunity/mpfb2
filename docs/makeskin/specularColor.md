# specularColor

* __Data type:__ RGB floats 
* __What is it for:__ Controling the color of specular highligts in MakeHuman
* __Use when:__ You want other other highlights than the default white
* __Implemented in MakeSkin:__ partially (as a secondary effect of roughness)
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ yes

In makehuman you can control the color of the specular highligts on objects. As this has no corresponding 
setting in Principled BSDF, it will not have any visible effect in Blender. 

MakeSkin will write this key automatically as the inverse of the roughness setting on the principled node.
For example, if you have 0.2 as roughness, the specular color will be set to "0.8 0.8 0.8" (for red, green
and blue).

## Example

This will cause specular highlights to be bright green in MakeHuman: 

    specularColor 0.5 1.0 0.5


