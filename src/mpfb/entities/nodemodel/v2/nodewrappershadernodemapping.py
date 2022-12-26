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
        "vector_type": {
            "class": "enum",
            "name": "vector_type",
            "value": "POINT"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeMapping",
    "inputs": {
        "Location": {
            "class": "NodeSocketVectorTranslation",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Location",
            "name": "Location",
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
        "Scale": {
            "class": "NodeSocketVectorXYZ",
            "default_value": [
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Scale",
            "name": "Scale",
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
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeMapping:
    def __init__(self):
        pass
