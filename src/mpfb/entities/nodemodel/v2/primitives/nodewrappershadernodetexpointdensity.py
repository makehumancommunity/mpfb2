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
        "interpolation": {
            "class": "str",
            "name": "interpolation",
            "value": "Linear"
        },
        "location": {
            "class": "Vector",
            "name": "location",
            "value": [
                0.0,
                0.0
            ]
        },
        "object": {
            "class": "NoneType",
            "name": "object",
            "value": null
        },
        "particle_color_source": {
            "class": "enum",
            "name": "particle_color_source",
            "value": "PARTICLE_AGE"
        },
        "particle_system": {
            "class": "NoneType",
            "name": "particle_system",
            "value": null
        },
        "point_source": {
            "class": "enum",
            "name": "point_source",
            "value": "PARTICLE_SYSTEM"
        },
        "radius": {
            "class": "float",
            "name": "radius",
            "value": 0.3
        },
        "resolution": {
            "class": "int",
            "name": "resolution",
            "value": 100
        },
        "space": {
            "class": "enum",
            "name": "space",
            "value": "OBJECT"
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "vertex_attribute_name": {
            "class": "str",
            "name": "vertex_attribute_name",
            "value": ""
        },
        "vertex_color_source": {
            "class": "enum",
            "name": "vertex_color_source",
            "value": "VERTEX_COLOR"
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 140.0
        }
    },
    "class": "ShaderNodeTexPointDensity",
    "inputs": {
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
        "Density": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Density",
            "name": "Density",
            "value_type": "VALUE"
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeTexPointDensity(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexPointDensity = _NodeWrapperShaderNodeTexPointDensity()
