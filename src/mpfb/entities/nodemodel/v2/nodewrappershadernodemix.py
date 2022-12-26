"""
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
                0.6079999804496765,
                0.6079999804496765,
                0.6079999804496765
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
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeMix:
    def __init__(self):
        pass
