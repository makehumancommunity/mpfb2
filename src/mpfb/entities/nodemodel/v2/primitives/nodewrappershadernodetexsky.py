import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "attributes": {
        "air_density": {
            "class": "float",
            "name": "air_density",
            "value": 1.0
        },
        "altitude": {
            "class": "float",
            "name": "altitude",
            "value": 0.0
        },
        "color": {
            "class": "Color",
            "name": "color",
            "value": [
                0.608,
                0.608,
                0.608
            ]
        },
        "dust_density": {
            "class": "float",
            "name": "dust_density",
            "value": 1.0
        },
        "ground_albedo": {
            "class": "float",
            "name": "ground_albedo",
            "value": 0.3
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
        "ozone_density": {
            "class": "float",
            "name": "ozone_density",
            "value": 1.0
        },
        "sky_type": {
            "class": "enum",
            "name": "sky_type",
            "value": "NISHITA"
        },
        "sun_direction": {
            "class": "Vector",
            "name": "sun_direction",
            "value": [
                0.0,
                0.0,
                1.0
            ]
        },
        "sun_disc": {
            "class": "bool",
            "name": "sun_disc",
            "value": true
        },
        "sun_elevation": {
            "class": "float",
            "name": "sun_elevation",
            "value": 0.2618
        },
        "sun_intensity": {
            "class": "float",
            "name": "sun_intensity",
            "value": 1.0
        },
        "sun_rotation": {
            "class": "float",
            "name": "sun_rotation",
            "value": 0.0
        },
        "sun_size": {
            "class": "float",
            "name": "sun_size",
            "value": 0.00951
        },
        "turbidity": {
            "class": "float",
            "name": "turbidity",
            "value": 2.2
        },
        "use_custom_color": {
            "class": "bool",
            "name": "use_custom_color",
            "value": false
        },
        "width": {
            "class": "float",
            "name": "width",
            "value": 150.0
        }
    },
    "class": "ShaderNodeTexSky",
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
        }
    }
}""")

from .abstractnodewrapper import AbstractNodeWrapper

class _NodeWrapperShaderNodeTexSky(AbstractNodeWrapper):
    def __init__(self):
        AbstractNodeWrapper.__init__(self, _ORIGINAL_NODE_DEF)

snTexSky = _NodeWrapperShaderNodeTexSky()
