# diffuseColor

* __Data type:__ RGB floats
* __What is it for:__ controlling the color of the object
* __Use when:__ you want to set a color but don't want to use a texture
* __Implemented in MakeSkin:__ yes 
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ yes (unless there is a diffuse texture)

For simple materials which have no image texture, you can provide a solid color. This setting
will also have an influence on the final color if you have specified a [diffuseTexture](diffuseTexture.md)
and a [diffuseIntensity](diffuseIntensity.md) lower than 1.0.

## Example

A yellow solid color:

    diffuseColor 1.0 1.0 0.5

## In blender

If there is a diffuseTexture, the value of diffuseColor will be read from the diffuseIntensity
MixRGB node between the texture node and the principled node.

If there is not a diffuseTexture, the value of diffuseColor will be read from the principled
node's "Base Color" socket.
