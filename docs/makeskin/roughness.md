# roughness

* __Data type:__ float
* __What is it for:__ specifying the roughness of a material
* __Use when:__ the shininess setting doesn't work as expected
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes 
* __Makes visible difference in makehuman:__ no (makehuman will use shininess instead)

The traditional MHMAT setting closest to roughness is [shininess](shininess.md). However, 
the meaning of this is somewhat different between makehuman and blender. 

The roughness key is intended as something between an alias and an alternative to shininess.
It will follow the same logic as the roughness setting on the principled node. 

If the roughness key is not available on import, the roughness value on the principled node
will be set to 1.0 - shininess. If it is available, it will be used instead of the inversion
of shininess. 

When exported by makeskin, both shininess and roughness will be written to the MHMAT file,
both based on the principled node's roughness socket.

The roughness key will be completely ignored by makehuman.

## Example

To specify a rather rough material: 

    roughness 0.7

