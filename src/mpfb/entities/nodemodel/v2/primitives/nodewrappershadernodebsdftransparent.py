import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.6079999804496765,
                0.6079999804496765,
                0.6079999804496765
            ]
        },
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeBsdfTransparent",
    "inputs": {
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Weight": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Weight",
            "name": "Weight",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "BSDF": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "BSDF",
            "name": "BSDF",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeBsdfTransparent(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snBsdfTransparent = _NodeWrapperShaderNodeBsdfTransparent()
