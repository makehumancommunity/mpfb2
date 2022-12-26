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
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeLightFalloff",
    "inputs": {
        "Smooth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Smooth",
            "name": "Smooth",
            "value_type": "VALUE"
        },
        "Strength": {
            "class": "NodeSocketFloat",
            "default_value": 100.0,
            "identifier": "Strength",
            "name": "Strength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Constant": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Constant",
            "name": "Constant",
            "value_type": "VALUE"
        },
        "Linear": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Linear",
            "name": "Linear",
            "value_type": "VALUE"
        },
        "Quadratic": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Quadratic",
            "name": "Quadratic",
            "value_type": "VALUE"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeLightFalloff:
    def __init__(self):
        pass
