import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
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
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeEeveeSpecular",
    "inputs": {
        "Ambient Occlusion": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Ambient Occlusion",
            "name": "Ambient Occlusion",
            "value_type": "VALUE"
        },
        "Base Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.8,
                0.8,
                0.8,
                1.0
            ],
            "identifier": "Base Color",
            "name": "Base Color",
            "value_type": "RGBA"
        },
        "Clear Coat": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Clear Coat",
            "name": "Clear Coat",
            "value_type": "VALUE"
        },
        "Clear Coat Normal": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Clear Coat Normal",
            "name": "Clear Coat Normal",
            "value_type": "VECTOR"
        },
        "Clear Coat Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Clear Coat Roughness",
            "name": "Clear Coat Roughness",
            "value_type": "VALUE"
        },
        "Emissive Color": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ],
            "identifier": "Emissive Color",
            "name": "Emissive Color",
            "value_type": "RGBA"
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
        "Roughness": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.2,
            "identifier": "Roughness",
            "name": "Roughness",
            "value_type": "VALUE"
        },
        "Specular": {
            "class": "NodeSocketColor",
            "default_value": [
                0.03,
                0.03,
                0.03,
                1.0
            ],
            "identifier": "Specular",
            "name": "Specular",
            "value_type": "RGBA"
        },
        "Transparency": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Transparency",
            "name": "Transparency",
            "value_type": "VALUE"
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
        "BSDF": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "BSDF",
            "name": "BSDF",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeEeveeSpecular(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snEeveeSpecular = _NodeWrapperShaderNodeEeveeSpecular()
