# ior

* __Data type:__ float (usually in the range 1.0 - 1.5)
* __What is it for:__ specifying the index of refraction for a material
* __Use when:__ creating semi-transparent materials 
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ no 

Ior is a property of the principled node in blender, used to specify the index of refraction
of a material. IOR is how much the light will bend when passing through the material, where
a setting of 1.4 (ish) is how glass works, and 1.0 is no light bending at all.

The ior setting will only be relevant if the material also specifies a 
[transparencymapTexture](transparencymapTexture.md), as opaque materials won't be influenced
by IOR. 

The ior key is outside the MHMAT spec and is implemented solely for blender. It will
have no effect in makehuman.

## Example

To specify that the material has a glass-like refraction:

    ior 1.4

