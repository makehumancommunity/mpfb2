# metallic

* __Data type:__ float
* __What is it for:__ Determining if the material is supposed to be metallic in nature
* __Use when:__ Creating metal materials, such as armor and tools
* __Implemented in MakeSkin:__ Yes
* __Makes visible difference in blender:__ Yes
* __Makes visible difference in makehuman:__ No

Metallic is a property of the principled node in blender. In most cases you will want to use
it as an either/or property where 1.0 is metal and 0.0 is non-metal, but there are also 
use cases when you want to mix these.

The metallic key is outside the MHMAT spec and is implemented solely for blender. It will
have no effect in makehuman.

## Example

To specify that a material is metallic in nature:

    metallic 1.0

