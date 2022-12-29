import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
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
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeOutputMaterial",
    "inputs": {
        "Displacement": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Displacement",
            "name": "Displacement",
            "value_type": "VECTOR"
        },
        "Surface": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Surface",
            "name": "Surface",
            "value_type": "SHADER"
        },
        "Thickness": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Thickness",
            "name": "Thickness",
            "value_type": "VALUE"
        },
        "Volume": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Volume",
            "name": "Volume",
            "value_type": "SHADER"
        }
    },
    "outputs": {}
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeOutputMaterial(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snOutputMaterial = _NodeWrapperShaderNodeOutputMaterial()
