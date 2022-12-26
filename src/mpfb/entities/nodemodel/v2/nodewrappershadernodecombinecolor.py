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
        "mode": {
            "class": "enum",
            "name": "mode",
            "value": "RGB"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeCombineColor",
    "inputs": {
        "Blue": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Blue",
            "name": "Blue",
            "value_type": "VALUE"
        },
        "Green": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Green",
            "name": "Green",
            "value_type": "VALUE"
        },
        "Red": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Red",
            "name": "Red",
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
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeCombineColor:
    def __init__(self):
        pass
