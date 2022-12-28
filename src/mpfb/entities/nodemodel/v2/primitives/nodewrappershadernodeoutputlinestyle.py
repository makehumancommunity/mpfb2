import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "blend_type": {
            "class": "enum",
            "name": "blend_type",
            "value": "MIX"
        },
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
        "use_alpha": {
            "class": "bool",
            "name": "use_alpha",
            "value": false
        },
        "use_clamp": {
            "class": "bool",
            "name": "use_clamp",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeOutputLineStyle",
    "inputs": {
        "Alpha": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Alpha",
            "name": "Alpha",
            "value_type": "VALUE"
        },
        "Alpha Fac": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Alpha Fac",
            "name": "Alpha Fac",
            "value_type": "VALUE"
        },
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.0,
                1.0,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Color Fac": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Color Fac",
            "name": "Color Fac",
            "value_type": "VALUE"
        }
    },
    "outputs": {}
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeOutputLineStyle(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snOutputLineStyle = _NodeWrapperShaderNodeOutputLineStyle()
