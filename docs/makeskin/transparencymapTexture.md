# transparencymapTexture

* __Data type:__ filename
* __What is it for:__ mapping alpha type transparency of an object
* __Use when:__ never, since it's not implemented. Use the alpha channel of the diffuseTexture instead.
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ no

Normally, you would implement transparency by using the alpha channel of the [diffuseTexture](diffuseTexture.md).
At the dawn of time, it was intended that transparencymapTexture would provide an alternative mapping for when 
you couldn't use a file format capable of handling an alpha channel.

As this is not implemented in MakeHuman (although the key is defined), and all current assets use the 
diffuseTexture alpha channel approach, this key is not used anywhere.

## Example

    transparencymapTexture mycharacter_transparency.png

