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
        "is_active_output": {
            "class": "bool",
            "name": "is_active_output",
            "value": true
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "target": {
            "class": "enum",
            "name": "target",
            "value": "ALL"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeOutputMaterial",
    "inputs": {
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
        },
        "Surface": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Surface",
            "name": "Surface",
            "value_type": "SHADER"
        },
        "Thickness": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Thickness",
            "name": "Thickness",
            "value_type": "VALUE"
        },
        "Volume": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Volume",
            "name": "Volume",
            "value_type": "SHADER"
        }
    },
    "outputs": {}
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeOutputMaterial:
    def __init__(self):
        pass
