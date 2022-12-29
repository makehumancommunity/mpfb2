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
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "musgrave_dimensions": {
            "class": "enum",
            "name": "musgrave_dimensions",
            "value": "3D"
        },
        "musgrave_type": {
            "class": "enum",
            "name": "musgrave_type",
            "value": "FBM"
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeTexMusgrave",
    "inputs": {
        "Detail": {
            "class": "NodeSocketFloat",
            "default_value": 2.0,
            "identifier": "Detail",
            "name": "Detail",
            "value_type": "VALUE"
        },
        "Dimension": {
            "class": "NodeSocketFloat",
            "default_value": 2.0,
            "identifier": "Dimension",
            "name": "Dimension",
            "value_type": "VALUE"
        },
        "Gain": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Gain",
            "name": "Gain",
            "value_type": "VALUE"
        },
        "Lacunarity": {
            "class": "NodeSocketFloat",
            "default_value": 2.0,
            "identifier": "Lacunarity",
            "name": "Lacunarity",
            "value_type": "VALUE"
        },
        "Offset": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Offset",
            "name": "Offset",
            "value_type": "VALUE"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 5.0,
            "identifier": "Scale",
            "name": "Scale",
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
        },
        "W": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "W",
            "name": "W",
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

class _NodeWrapperShaderNodeTexMusgrave(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexMusgrave = _NodeWrapperShaderNodeTexMusgrave()
