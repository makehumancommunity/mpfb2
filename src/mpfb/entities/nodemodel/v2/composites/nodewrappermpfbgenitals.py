import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbGenitals",
    "inputs": {
        "Input_Socket_Color": {
            "name": "Color",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.4846,
                0.254,
                0.2188,
                1.0
            ]
        },
        "Input_Socket_Roughness": {
            "name": "Roughness",
            "identifier": "Socket_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_2",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_Socket_VariationColor": {
            "name": "VariationColor",
            "identifier": "Socket_3",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.3679,
                0.0,
                0.0004,
                1.0
            ]
        },
        "Input_Socket_ColorVariationFactor": {
            "name": "ColorVariationFactor",
            "identifier": "Socket_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationScale": {
            "name": "ColorVariationScale",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 400.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessScale": {
            "name": "UnevennessScale",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 200.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessStrength": {
            "name": "UnevennessStrength",
            "identifier": "Socket_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_Socket_SSSRadiusMultiplyer": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_Socket_BSDF": {
            "name": "BSDF",
            "identifier": "Socket_14",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        }
    },
    "attributes": {
        "color": {
            "name": "color",
            "class": "Color",
            "value": [
                0.4,
                0.4,
                0.5
            ]
        },
        "height": {
            "name": "height",
            "class": "float",
            "value": 100.0
        },
        "location": {
            "name": "location",
            "class": "Vector",
            "value": [
                707.9717,
                -1485.2301
            ]
        },
        "use_custom_color": {
            "name": "use_custom_color",
            "class": "bool",
            "value": true
        },
        "width": {
            "name": "width",
            "class": "float",
            "value": 310.2192
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Color",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VariationColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationFactor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScale",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScale",
            "to_node": "Noise Texture.001",
            "to_socket": "Scale"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSWeight",
            "to_node": "SSS",
            "to_socket": "SSSWeight"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "SSS",
            "to_socket": "SSSScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "SSS",
            "to_socket": "SSSRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "SSS",
            "to_socket": "SSSRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "SSS",
            "to_socket": "SSSRadiusZ"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "SSS",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Roughness",
            "to_node": "Principled BSDF.001",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Texture Coordinate.001",
            "from_socket": "Object",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate.001",
            "from_socket": "Object",
            "to_node": "Noise Texture.001",
            "to_socket": "Vector"
        },
        {
            "from_node": "Noise Texture.001",
            "from_socket": "Fac",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Principled BSDF.001",
            "to_socket": "Normal"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSRadius",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSWeight",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Weight"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSIor",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Principled BSDF.001",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Principled BSDF.001",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSScale",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Scale"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSAnisotropy",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Anisotropy"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSAnisotropy",
            "to_node": "SSS",
            "to_socket": "SSSAnisotropy"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    230.3597,
                    370.7975
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.7991,
                    0.3231,
                    0.3095,
                    1.0
                ],
                "A_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "B_Color": [
                    0.6618,
                    0.2422,
                    0.2108,
                    1.0
                ],
                "B_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {
                "Result_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            }
        },
        {
            "attribute_values": {
                "location": [
                    -58.5634,
                    416.1841
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -256.5074,
                    562.8046
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Scale": 120.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    374.1753,
                    -425.3056
                ]
            },
            "class": "ShaderNodeBump",
            "input_socket_values": {
                "Strength": 0.1
            },
            "label": "Bump",
            "name": "Bump",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -263.6289,
                    -349.6447
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Scale": 200.0
            },
            "label": "Noise Texture.001",
            "name": "Noise Texture.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -723.0281,
                    334.1442
                ]
            },
            "class": "ShaderNodeTexCoord",
            "input_socket_values": {},
            "label": "Texture Coordinate.001",
            "name": "Texture Coordinate.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1134.5013,
                    216.3279
                ]
            },
            "class": "NodeGroupOutput",
            "input_socket_values": {},
            "label": "Group Output",
            "name": "Group Output",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    793.9831,
                    283.0536
                ]
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {
                "Base Color": [
                    0.7991,
                    0.3231,
                    0.3095,
                    1.0
                ],
                "Roughness": 0.2
            },
            "label": "Principled BSDF.001",
            "name": "Principled BSDF.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    494.9734,
                    151.7243
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbSSSControl",
            "input_socket_values": {
                "SSSScaleMultiplier": 1.0
            },
            "label": "SSS",
            "name": "SSS",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -721.5581,
                    99.0309
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbGenitals(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1134.5013, 216.3279]
        nodes["Group Input"].location = [-721.5581, 99.0309]

        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [230.3597, 370.7975]}, input_socket_values={"A_Color": [0.7991, 0.3231, 0.3095, 1.0], "A_Rotation": [0.0, 0.0, 0.0], "B_Color": [0.6618, 0.2422, 0.2108, 1.0], "B_Rotation": [0.0, 0.0, 0.0]}, output_socket_values={"Result_Rotation": [0.0, 0.0, 0.0]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-58.5634, 416.1841], "operation": "MULTIPLY"})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-256.5074, 562.8046]}, input_socket_values={"Scale": 120.0})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [374.1753, -425.3056]}, input_socket_values={"Strength": 0.1})
        node("ShaderNodeTexNoise", "Noise Texture.001", attribute_values={"location": [-263.6289, -349.6447]}, input_socket_values={"Scale": 200.0})
        node("ShaderNodeTexCoord", "Texture Coordinate.001", attribute_values={"location": [-723.0281, 334.1442]})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF.001", attribute_values={"location": [793.9831, 283.0536]}, input_socket_values={"Base Color": [0.7991, 0.3231, 0.3095, 1.0], "Roughness": 0.2})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [494.9734, 151.7243], "use_custom_color": True, "width": 140.0}, input_socket_values={"SSSScaleMultiplier": 1.0})

        link("Group Input", "Color", "Mix", "A_Color")
        link("Group Input", "VariationColor", "Mix", "B_Color")
        link("Group Input", "ColorVariationFactor", "Math", "Value_001")
        link("Group Input", "ColorVariationScale", "Noise Texture", "Scale")
        link("Group Input", "UnevennessScale", "Noise Texture.001", "Scale")
        link("Group Input", "UnevennessStrength", "Bump", "Strength")
        link("Group Input", "SSSWeight", "SSS", "SSSWeight")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SSSScaleMultiplier")
        link("Group Input", "SSSRadiusX", "SSS", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SSSRadiusZ")
        link("Group Input", "SSSIor", "SSS", "SSSIor")
        link("Group Input", "Roughness", "Principled BSDF.001", "Roughness")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "SSSAnisotropy", "SSS", "SSSAnisotropy")
        link("Texture Coordinate.001", "Object", "Noise Texture", "Vector")
        link("Texture Coordinate.001", "Object", "Noise Texture.001", "Vector")
        link("Noise Texture.001", "Fac", "Bump", "Height")
        link("Bump", "Normal", "Principled BSDF.001", "Normal")
        link("SSS", "SSSRadius", "Principled BSDF.001", "Subsurface Radius")
        link("SSS", "SSSWeight", "Principled BSDF.001", "Subsurface Weight")
        link("SSS", "SSSIor", "Principled BSDF.001", "Subsurface IOR")
        link("Mix", "Result_Color", "Principled BSDF.001", "Base Color")
        link("Noise Texture", "Fac", "Math", "Value")
        link("Math", "Value", "Mix", "Factor_Float")
        link("SSS", "SSSScale", "Principled BSDF.001", "Subsurface Scale")
        link("SSS", "SSSAnisotropy", "Principled BSDF.001", "Subsurface Anisotropy")
        link("Principled BSDF.001", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbGenitals = _NodeWrapperMpfbGenitals()
