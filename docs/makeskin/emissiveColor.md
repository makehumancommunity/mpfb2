# emissiveColor

* __Data type:__ RGB floats
* __What is it for:__ controlling the color of emitted light
* __Use when:__ you want the material to emit light 
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__  yes
* __Makes visible difference in makehuman:__ no

The purpose of emissiveColor is to allow materials to emit light. The range is from 0, 0, 0 (black) which is no
emission to 1.0, 1.0, 1.0 (white) which is emission of light with strength 1.0. 

The default is 0, 0, 0 (black), which means emit no light.

The value is read from the principled node's "Emission" socket.

## Example

This will emit bright white light in blender:

    emissiveColor 1.0 1.0 1.0

