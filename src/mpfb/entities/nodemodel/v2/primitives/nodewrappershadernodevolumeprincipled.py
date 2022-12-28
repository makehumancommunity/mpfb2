import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
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
            "value": 240.0
        }
    },
    "class": "ShaderNodeVolumePrincipled",
    "inputs": {
        "Absorption Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Absorption Color",
            "name": "Absorption Color",
            "value_type": "RGBA"
        },
        "Anisotropy": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Anisotropy",
            "name": "Anisotropy",
            "value_type": "VALUE"
        },
        "Blackbody Intensity": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Blackbody Intensity",
            "name": "Blackbody Intensity",
            "value_type": "VALUE"
        },
        "Blackbody Tint": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Blackbody Tint",
            "name": "Blackbody Tint",
            "value_type": "RGBA"
        },
        "Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Color",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Color Attribute": {
            "class": "NodeSocketString",
            "default_value": "",
            "identifier": "Color Attribute",
            "name": "Color Attribute",
            "value_type": "STRING"
        },
        "Density": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Density",
            "name": "Density",
            "value_type": "VALUE"
        },
        "Density Attribute": {
            "class": "NodeSocketString",
            "default_value": "density",
            "identifier": "Density Attribute",
            "name": "Density Attribute",
            "value_type": "STRING"
        },
        "Emission Color": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Emission Color",
            "name": "Emission Color",
            "value_type": "RGBA"
        },
        "Emission Strength": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Emission Strength",
            "name": "Emission Strength",
            "value_type": "VALUE"
        },
        "Temperature": {
            "class": "NodeSocketFloat",
            "default_value": 1000.0,
            "identifier": "Temperature",
            "name": "Temperature",
            "value_type": "VALUE"
        },
        "Temperature Attribute": {
            "class": "NodeSocketString",
            "default_value": "temperature",
            "identifier": "Temperature Attribute",
            "name": "Temperature Attribute",
            "value_type": "STRING"
        },
        "Weight": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Weight",
            "name": "Weight",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Volume": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Volume",
            "name": "Volume",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeVolumePrincipled(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snVolumePrincipled = _NodeWrapperShaderNodeVolumePrincipled()
