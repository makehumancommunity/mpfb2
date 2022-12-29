import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "clamp": {
            "class": "bool",
            "name": "clamp",
            "value": true
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
        "height": {
            "class": "float",
            "name": "height",
            "value": 100.0
        },
        "interpolation_type": {
            "class": "enum",
            "name": "interpolation_type",
            "value": "LINEAR"
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
    "class": "ShaderNodeMapRange",
    "inputs": {
        "From Max": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "From Max",
            "name": "From Max",
            "value_type": "VALUE"
        },
        "From Min": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "From Min",
            "name": "From Min",
            "value_type": "VALUE"
        },
        "From_Max_FLOAT3": {
            "class": "NodeSocketVector",
            "default_value": [
                1.0,
                1.0,
                1.0
            ],
            "identifier": "From_Max_FLOAT3",
            "name": "From Max",
            "value_type": "VECTOR"
        },
        "From_Min_FLOAT3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "From_Min_FLOAT3",
            "name": "From Min",
            "value_type": "VECTOR"
        },
        "Steps": {
            "class": "NodeSocketFloat",
            "default_value": 4.0,
            "identifier": "Steps",
            "name": "Steps",
            "value_type": "VALUE"
        },
        "Steps_FLOAT3": {
            "class": "NodeSocketVector",
            "default_value": [
                4.0,
                4.0,
                4.0
            ],
            "identifier": "Steps_FLOAT3",
            "name": "Steps",
            "value_type": "VECTOR"
        },
        "To Max": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "To Max",
            "name": "To Max",
            "value_type": "VALUE"
        },
        "To Min": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "To Min",
            "name": "To Min",
            "value_type": "VALUE"
        },
        "To_Max_FLOAT3": {
            "class": "NodeSocketVector",
            "default_value": [
                1.0,
                1.0,
                1.0
            ],
            "identifier": "To_Max_FLOAT3",
            "name": "To Max",
            "value_type": "VECTOR"
        },
        "To_Min_FLOAT3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "To_Min_FLOAT3",
            "name": "To Min",
            "value_type": "VECTOR"
        },
        "Value": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Value",
            "name": "Value",
            "value_type": "VALUE"
        },
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
    },
    "outputs": {
        "Result": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Result",
            "name": "Result",
            "value_type": "VALUE"
        },
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

class _NodeWrapperShaderNodeMapRange(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snMapRange = _NodeWrapperShaderNodeMapRange()
