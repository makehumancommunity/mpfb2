# ambientColor

* __Data type:__ RGB floats
* __What is it for:__ Controlling the color of emulated ambient light 
* __Use when:__ You want to emulate ambient color other than white in MakeHuman
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ yes (in some specific shaders)

In MakeHuman, different forms of light sources are emulated by specifying a color to add to 
drawn objects. For general ambient light, you can specify a color by using ambientColor.

As this is only for emulating light in MakeHuman, it has no effect on exported objects. 

## Example

This will set a red ambient color:

    ambientColor 1.0 0.0 0.0

