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
        "distance": {
            "class": "enum",
            "name": "distance",
            "value": "EUCLIDEAN"
        },
        "feature": {
            "class": "enum",
            "name": "feature",
            "value": "F1"
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
        "voronoi_dimensions": {
            "class": "enum",
            "name": "voronoi_dimensions",
            "value": "3D"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeTexVoronoi",
    "inputs": {
        "Exponent": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Exponent",
            "name": "Exponent",
            "value_type": "VALUE"
        },
        "Randomness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Randomness",
            "name": "Randomness",
            "value_type": "VALUE"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 5.0,
            "identifier": "Scale",
            "name": "Scale",
            "value_type": "VALUE"
        },
        "Smoothness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 1.0,
            "identifier": "Smoothness",
            "name": "Smoothness",
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
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Distance": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Distance",
            "name": "Distance",
            "value_type": "VALUE"
        },
        "Position": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Position",
            "name": "Position",
            "value_type": "VECTOR"
        },
        "Radius": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Radius",
            "name": "Radius",
            "value_type": "VALUE"
        },
        "W": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "W",
            "name": "W",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeTexVoronoi(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexVoronoi = _NodeWrapperShaderNodeTexVoronoi()
