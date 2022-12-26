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
    "class": "ShaderNodeLightPath",
    "inputs": {},
    "outputs": {
        "Diffuse Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Diffuse Depth",
            "name": "Diffuse Depth",
            "value_type": "VALUE"
        },
        "Glossy Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Glossy Depth",
            "name": "Glossy Depth",
            "value_type": "VALUE"
        },
        "Is Camera Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Camera Ray",
            "name": "Is Camera Ray",
            "value_type": "VALUE"
        },
        "Is Diffuse Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Diffuse Ray",
            "name": "Is Diffuse Ray",
            "value_type": "VALUE"
        },
        "Is Glossy Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Glossy Ray",
            "name": "Is Glossy Ray",
            "value_type": "VALUE"
        },
        "Is Reflection Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Reflection Ray",
            "name": "Is Reflection Ray",
            "value_type": "VALUE"
        },
        "Is Shadow Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Shadow Ray",
            "name": "Is Shadow Ray",
            "value_type": "VALUE"
        },
        "Is Singular Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Singular Ray",
            "name": "Is Singular Ray",
            "value_type": "VALUE"
        },
        "Is Transmission Ray": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Is Transmission Ray",
            "name": "Is Transmission Ray",
            "value_type": "VALUE"
        },
        "Ray Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Ray Depth",
            "name": "Ray Depth",
            "value_type": "VALUE"
        },
        "Ray Length": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Ray Length",
            "name": "Ray Length",
            "value_type": "VALUE"
        },
        "Transmission Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Transmission Depth",
            "name": "Transmission Depth",
            "value_type": "VALUE"
        },
        "Transparent Depth": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Transparent Depth",
            "name": "Transparent Depth",
            "value_type": "VALUE"
        }
    }
}"""

from .abstractnodewrapper import AbstractNodeWrapper

class NodeWrapperShaderNodeLightPath:
    def __init__(self):
        pass
