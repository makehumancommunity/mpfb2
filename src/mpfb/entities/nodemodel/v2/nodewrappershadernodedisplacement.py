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
        "space": {
            "class": "enum",
            "name": "space",
            "value": "OBJECT"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeDisplacement",
    "inputs": {
        "Height": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Height",
            "name": "Height",
            "value_type": "VALUE"
        },
        "Midlevel": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Midlevel",
            "name": "Midlevel",
            "value_type": "VALUE"
        },
        "Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Normal",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Scale",
            "name": "Scale",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Displacement": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Displacement",
            "name": "Displacement",
            "value_type": "VECTOR"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeDisplacement:
    def __init__(self):
        pass
