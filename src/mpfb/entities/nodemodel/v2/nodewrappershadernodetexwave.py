"""
{
    "attributes": {
        "bands_direction": {
            "class": "enum",
            "name": "bands_direction",
            "value": "X"
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
        "rings_direction": {
            "class": "enum",
            "name": "rings_direction",
            "value": "X"
        },
        "wave_profile": {
            "class": "enum",
            "name": "wave_profile",
            "value": "SIN"
        },
        "wave_type": {
            "class": "enum",
            "name": "wave_type",
            "value": "BANDS"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeTexWave",
    "inputs": {
        "Detail": {
            "class": "NodeSocketFloat",
            "default_value": 2.0,
            "identifier": "Detail",
            "name": "Detail",
            "value_type": "VALUE"
        },
        "Detail Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Detail Roughness",
            "name": "Detail Roughness",
            "value_type": "VALUE"
        },
        "Detail Scale": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Detail Scale",
            "name": "Detail Scale",
            "value_type": "VALUE"
        },
        "Distortion": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Distortion",
            "name": "Distortion",
            "value_type": "VALUE"
        },
        "Phase Offset": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Phase Offset",
            "name": "Phase Offset",
            "value_type": "VALUE"
        },
        "Scale": {
            "class": "NodeSocketFloat",
            "default_value": 5.0,
            "identifier": "Scale",
            "name": "Scale",
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
        "Fac": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Fac",
            "name": "Fac",
            "value_type": "VALUE"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeTexWave:
    def __init__(self):
        pass
