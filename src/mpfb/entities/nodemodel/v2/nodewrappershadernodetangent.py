"""
{
    "attributes": {
        "axis": {
            "class": "enum",
            "name": "axis",
            "value": "Z"
        },
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.6079999804496765,
                0.6079999804496765,
                0.6079999804496765
            ]
        },
        "direction_type": {
            "class": "enum",
            "name": "direction_type",
            "value": "RADIAL"
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
        "uv_map": {
            "class": "str",
            "name": "uv_map",
            "value": ""
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeTangent",
    "inputs": {},
    "outputs": {
        "Tangent": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Tangent",
            "name": "Tangent",
            "value_type": "VECTOR"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeTangent:
    def __init__(self):
        pass
