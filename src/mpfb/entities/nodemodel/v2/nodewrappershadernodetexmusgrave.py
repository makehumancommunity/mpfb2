"""
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
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeTexMusgrave:
    def __init__(self):
        pass
