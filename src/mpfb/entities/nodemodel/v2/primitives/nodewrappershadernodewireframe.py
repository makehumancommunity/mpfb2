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
        "use_pixel_size": {
            "class": "bool",
            "name": "use_pixel_size",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeWireframe",
    "inputs": {
        "Size": {
            "class": "NodeSocketFloat",
            "default_value": 0.009999999776482582,
            "identifier": "Size",
            "name": "Size",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Fac": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Fac",
            "name": "Fac",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeWireframe(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snWireframe = _NodeWrapperShaderNodeWireframe()
