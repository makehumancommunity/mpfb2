import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "bytecode": {
            "class": "str",
            "name": "bytecode",
            "value": ""
        },
        "bytecode_hash": {
            "class": "str",
            "name": "bytecode_hash",
            "value": ""
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
        "filepath": {
            "class": "str",
            "name": "filepath",
            "value": ""
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
            "value": "INTERNAL"
        },
        "script": {
            "class": "NoneType",
            "name": "script",
            "value": null
        },
        "use_auto_update": {
            "class": "bool",
            "name": "use_auto_update",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeScript",
    "inputs": {},
    "outputs": {}
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeScript(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snScript = _NodeWrapperShaderNodeScript()
