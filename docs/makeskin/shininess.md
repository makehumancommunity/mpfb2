# roughness

* __Data type:__ float
* __What is it for:__ specifying the roughness of a material
* __Use when:__ you want a specific roughness
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes (but see also [roughness](roughness.md))
* __Makes visible difference in makehuman:__ yes

The traditional MHMAT setting closest to roughness is shininess. However, the meaning of 
this is somewhat different between makehuman and blender. 

On import and export in makeskin, shininess will be treated as the inverse of roughness. 
That is, 0.0 is a very rough material and 1.0 is a very smooth material. 

If the roughness key is not available on import, the roughness value on the principled node
will be set to 1.0 - shininess. If it is available, it will be used instead of shininess.

When exported by makeskin, both shininess and roughness will be written to the MHMAT file,
both based on the principled node's roughness socket.

## Example

To specify a rather smooth material: 

    shininess 0.7

