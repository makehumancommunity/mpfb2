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
        "convert_from": {
            "class": "enum",
            "name": "convert_from",
            "value": "WORLD"
        },
        "convert_to": {
            "class": "enum",
            "name": "convert_to",
            "value": "OBJECT"
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
        "vector_type": {
            "class": "enum",
            "name": "vector_type",
            "value": "VECTOR"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeVectorTransform",
    "inputs": {
        "Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.5,
                0.5,
                0.5
            ],
            "identifier": "Vector",
            "name": "Vector",
            "value_type": "VECTOR"
        }
    },
    "outputs": {
        "Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Vector",
            "name": "Vector",
            "value_type": "VECTOR"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeVectorTransform(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snVectorTransform = _NodeWrapperShaderNodeVectorTransform()
