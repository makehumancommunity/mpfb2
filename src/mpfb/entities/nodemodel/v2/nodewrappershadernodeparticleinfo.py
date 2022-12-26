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
    "class": "ShaderNodeParticleInfo",
    "inputs": {},
    "outputs": {
        "Age": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Age",
            "name": "Age",
            "value_type": "VALUE"
        },
        "Angular Velocity": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Angular Velocity",
            "name": "Angular Velocity",
            "value_type": "VECTOR"
        },
        "Index": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Index",
            "name": "Index",
            "value_type": "VALUE"
        },
        "Lifetime": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Lifetime",
            "name": "Lifetime",
            "value_type": "VALUE"
        },
        "Location": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Location",
            "name": "Location",
            "value_type": "VECTOR"
        },
        "Random": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Random",
            "name": "Random",
            "value_type": "VALUE"
        },
        "Size": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Size",
            "name": "Size",
            "value_type": "VALUE"
        },
        "Velocity": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Velocity",
            "name": "Velocity",
            "value_type": "VECTOR"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeParticleInfo:
    def __init__(self):
        pass
