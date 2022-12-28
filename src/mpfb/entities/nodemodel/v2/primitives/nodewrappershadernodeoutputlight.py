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
        "is_active_output": {
            "class": "bool",
            "name": "is_active_output",
            "value": true
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "target": {
            "class": "enum",
            "name": "target",
            "value": "ALL"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeOutputLight",
    "inputs": {
        "Surface": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Surface",
            "name": "Surface",
            "value_type": "SHADER"
        }
    },
    "outputs": {}
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeOutputLight(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snOutputLight = _NodeWrapperShaderNodeOutputLight()
