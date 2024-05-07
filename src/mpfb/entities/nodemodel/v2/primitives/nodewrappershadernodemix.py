import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "blend_type": {
            "class": "enum",
            "name": "blend_type",
            "value": "MIX"
        },
        "clamp_factor": {
            "class": "bool",
            "name": "clamp_factor",
            "value": true
        },
        "clamp_result": {
            "class": "bool",
            "name": "clamp_result",
            "value": false
        },
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
            ]
        },
        "data_type": {
            "class": "enum",
            "name": "data_type",
            "value": "FLOAT"
        },
        "factor_mode": {
            "class": "enum",
            "name": "factor_mode",
            "value": "UNIFORM"
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
    "class": "ShaderNodeMix",
    "inputs": {
        "A_Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "A_Color",
            "name": "A",
            "value_type": "RGBA"
        },
        "A_Float": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "A_Float",
            "name": "A",
            "value_type": "VALUE"
        },
        "A_Rotation": {
            "class": "NodeSocketRotation",
            "default_value": null,
            "identifier": "A_Rotation",
            "name": "A",
            "value_type": "ROTATION"
        },
        "A_Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "A_Vector",
            "name": "A",
            "value_type": "VECTOR"
        },
        "B_Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "B_Color",
            "name": "B",
            "value_type": "RGBA"
        },
        "B_Float": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "B_Float",
            "name": "B",
            "value_type": "VALUE"
        },
        "B_Rotation": {
            "class": "NodeSocketRotation",
            "default_value": null,
            "identifier": "B_Rotation",
            "name": "B",
            "value_type": "ROTATION"
        },
        "B_Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "B_Vector",
            "name": "B",
            "value_type": "VECTOR"
        },
        "Factor_Float": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Factor_Float",
            "name": "Factor",
            "value_type": "VALUE"
        },
        "Factor_Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.5,
                0.5,
                0.5
            ],
            "identifier": "Factor_Vector",
            "name": "Factor",
            "value_type": "VECTOR"
        }
    },
    "outputs": {
        "Result_Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Result_Color",
            "name": "Result",
            "value_type": "RGBA"
        },
        "Result_Float": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Result_Float",
            "name": "Result",
            "value_type": "VALUE"
        },
        "Result_Rotation": {
            "class": "NodeSocketRotation",
            "default_value": null,
            "identifier": "Result_Rotation",
            "name": "Result",
            "value_type": "ROTATION"
        },
        "Result_Vector": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Result_Vector",
            "name": "Result",
            "value_type": "VECTOR"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeMix(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snMix = _NodeWrapperShaderNodeMix()
