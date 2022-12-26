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
            "value": 140.0
        }
    },
    "class": "ShaderNodeHairInfo",
    "inputs": {},
    "outputs": {
        "Intercept": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Intercept",
            "name": "Intercept",
            "value_type": "VALUE"
        },
        "Is Strand": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Strand",
            "name": "Is Strand",
            "value_type": "VALUE"
        },
        "Length": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Length",
            "name": "Length",
            "value_type": "VALUE"
        },
        "Random": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Random",
            "name": "Random",
            "value_type": "VALUE"
        },
        "Tangent Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Tangent Normal",
            "name": "Tangent Normal",
            "value_type": "VECTOR"
        },
        "Thickness": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Thickness",
            "name": "Thickness",
            "value_type": "VALUE"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeHairInfo:
    def __init__(self):
        pass
