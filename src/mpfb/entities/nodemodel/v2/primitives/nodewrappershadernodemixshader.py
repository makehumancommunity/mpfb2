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
            "value": 140.0
        }
    },
    "class": "ShaderNodeMixShader",
    "inputs": {
        "Fac": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.5,
            "identifier": "Fac",
            "name": "Fac",
            "value_type": "VALUE"
        },
        "Shader": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Shader",
            "name": "Shader",
            "value_type": "SHADER"
        },
        "Shader_001": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Shader_001",
            "name": "Shader",
            "value_type": "SHADER"
        }
    },
    "outputs": {
        "Shader": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Shader",
            "name": "Shader",
            "value_type": "SHADER"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeMixShader(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snMixShader = _NodeWrapperShaderNodeMixShader()
