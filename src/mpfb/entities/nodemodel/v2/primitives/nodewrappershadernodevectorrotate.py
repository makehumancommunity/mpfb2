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
        "invert": {
            "class": "bool",
            "name": "invert",
            "value": false
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "rotation_type": {
            "class": "enum",
            "name": "rotation_type",
            "value": "AXIS_ANGLE"
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
    "class": "ShaderNodeVectorRotate",
    "inputs": {
        "Angle": {
            "class": "NodeSocketFloatAngle",
            "default_value": 0.0,
            "identifier": "Angle",
            "name": "Angle",
            "value_type": "VALUE"
        },
        "Axis": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Axis",
            "name": "Axis",
            "value_type": "VECTOR"
        },
        "Center": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Center",
            "name": "Center",
            "value_type": "VECTOR"
        },
        "Rotation": {
            "class": "NodeSocketVectorEuler",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Rotation",
            "name": "Rotation",
            "value_type": "VECTOR"
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

class _NodeWrapperShaderNodeVectorRotate(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snVectorRotate = _NodeWrapperShaderNodeVectorRotate()
