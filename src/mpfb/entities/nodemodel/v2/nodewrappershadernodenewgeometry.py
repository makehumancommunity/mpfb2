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
    "class": "ShaderNodeNewGeometry",
    "inputs": {},
    "outputs": {
        "Backfacing": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Backfacing",
            "name": "Backfacing",
            "value_type": "VALUE"
        },
        "Incoming": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Incoming",
            "name": "Incoming",
            "value_type": "VECTOR"
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
        "Parametric": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Parametric",
            "name": "Parametric",
            "value_type": "VECTOR"
        },
        "Pointiness": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Pointiness",
            "name": "Pointiness",
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
        "Random Per Island": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Random Per Island",
            "name": "Random Per Island",
            "value_type": "VALUE"
        },
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
        },
        "True Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "True Normal",
            "name": "True Normal",
            "value_type": "VECTOR"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeNewGeometry:
    def __init__(self):
        pass
