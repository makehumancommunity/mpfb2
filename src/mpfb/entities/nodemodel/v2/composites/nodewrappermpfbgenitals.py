import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbGenitals",
    "inputs": {
        "Input_1": {
            "name": "Color",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.4846,
                0.254,
                0.2188,
                1.0
            ]
        },
        "Input_13": {
            "name": "Roughness",
            "identifier": "Input_13",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_14": {
            "name": "Normal",
            "identifier": "Input_14",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_2": {
            "name": "VariationColor",
            "identifier": "Input_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.3679,
                0.0,
                0.0004,
                1.0
            ]
        },
        "Input_3": {
            "name": "ColorVariationFactor",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "ColorVariationScale",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 400.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_5": {
            "name": "UnevennessScale",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 200.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_6": {
            "name": "UnevennessStrength",
            "identifier": "Input_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_7": {
            "name": "SubsurfaceStrength",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_8": {
            "name": "SubsurfaceRadiusMultiplyer",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_9": {
            "name": "SubSurfaceRadiusX",
            "identifier": "Input_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_10": {
            "name": "SubSurfaceRadiusY",
            "identifier": "Input_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_11": {
            "name": "SubSurfaceRadiusZ",
            "identifier": "Input_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_12": {
            "name": "SubsurfaceIor",
            "identifier": "Input_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_0": {
            "name": "BSDF",
            "identifier": "Output_0",
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
                0.608,
                0.608,
                0.608
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
                710.5547,
                -1317.3098
            ]
        },
        "use_custom_color": {
            "name": "use_custom_color",
            "class": "bool",
            "value": false
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
            "from_node": "Principled BSDF.001",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceColor",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Color"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceRadius",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceIor",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface IOR"
        },
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
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "SSS",
            "to_socket": "SubsurfaceColor"
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
            "from_socket": "SubsurfaceStrength",
            "to_node": "SSS",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceRadiusMultiplyer",
            "to_node": "SSS",
            "to_socket": "SubsurfaceRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusX",
            "to_node": "SSS",
            "to_socket": "SubSurfaceRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusY",
            "to_node": "SSS",
            "to_socket": "SubSurfaceRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusZ",
            "to_node": "SSS",
            "to_socket": "SubSurfaceRadiusZ"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceIor",
            "to_node": "SSS",
            "to_socket": "SubsurfaceIor"
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
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -506.0604,
                    320.366
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
                    1081.9813,
                    110.4079
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
                "data_type": "RGBA",
                "location": [
                    278.5748,
                    164.1244
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
                "B_Color": [
                    0.6618,
                    0.2422,
                    0.2108,
                    1.0
                ]
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    5.1494,
                    182.8157
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
                    -185.0458,
                    -77.8821
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
                    -164.6158,
                    -320.366
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
                    757.8218,
                    184.8839
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
                "location": [
                    329.4041,
                    -247.05
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
                "color": [
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    510.471,
                    52.6934
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSSSControl",
            "input_socket_values": {
                "SubsurfaceRadiusMultiplyer": 1.0
            },
            "label": "SSS",
            "name": "SSS",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -706.0604,
                    -0.0
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

        nodes["Group Output"].location = [1081.9813, 110.4079]
        nodes["Group Input"].location = [-706.0604, -0.0]

        node("ShaderNodeTexCoord", "Texture Coordinate.001", attribute_values={"location": [-506.0604, 320.366]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [278.5748, 164.1244]}, input_socket_values={"A_Color": [0.7991, 0.3231, 0.3095, 1.0], "B_Color": [0.6618, 0.2422, 0.2108, 1.0]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [5.1494, 182.8157], "operation": "MULTIPLY"})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-185.0458, -77.8821]}, input_socket_values={"Scale": 120.0})
        node("ShaderNodeTexNoise", "Noise Texture.001", attribute_values={"location": [-164.6158, -320.366]}, input_socket_values={"Scale": 200.0})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF.001", attribute_values={"location": [757.8218, 184.8839]}, input_socket_values={"Base Color": [0.7991, 0.3231, 0.3095, 1.0], "Roughness": 0.2})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [329.4041, -247.05]}, input_socket_values={"Strength": 0.1})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [510.471, 52.6934], "use_custom_color": False, "width": 140.0}, input_socket_values={"SubsurfaceRadiusMultiplyer": 1.0})

        link("Group Input", "Color", "Mix", "A_Color")
        link("Group Input", "VariationColor", "Mix", "B_Color")
        link("Group Input", "ColorVariationFactor", "Math", "Value_001")
        link("Group Input", "ColorVariationScale", "Noise Texture", "Scale")
        link("Group Input", "UnevennessScale", "Noise Texture.001", "Scale")
        link("Group Input", "UnevennessStrength", "Bump", "Strength")
        link("Group Input", "SubsurfaceStrength", "SSS", "SubsurfaceStrength")
        link("Group Input", "SubsurfaceRadiusMultiplyer", "SSS", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "SubSurfaceRadiusX", "SSS", "SubSurfaceRadiusX")
        link("Group Input", "SubSurfaceRadiusY", "SSS", "SubSurfaceRadiusY")
        link("Group Input", "SubSurfaceRadiusZ", "SSS", "SubSurfaceRadiusZ")
        link("Group Input", "SubsurfaceIor", "SSS", "SubsurfaceIor")
        link("Group Input", "Roughness", "Principled BSDF.001", "Roughness")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Texture Coordinate.001", "Object", "Noise Texture", "Vector")
        link("Texture Coordinate.001", "Object", "Noise Texture.001", "Vector")
        link("Noise Texture.001", "Fac", "Bump", "Height")
        link("Bump", "Normal", "Principled BSDF.001", "Normal")
        #link("SSS", "SubsurfaceColor", "Principled BSDF.001", "Subsurface Color")
        link("SSS", "SubsurfaceRadius", "Principled BSDF.001", "Subsurface Radius")
        link("SSS", "SubsurfaceStrength", "Principled BSDF.001", "Subsurface Weight")
        link("SSS", "SubsurfaceIor", "Principled BSDF.001", "Subsurface IOR")
        link("Mix", "Result_Color", "SSS", "SubsurfaceColor")
        link("Mix", "Result_Color", "Principled BSDF.001", "Base Color")
        link("Noise Texture", "Fac", "Math", "Value")
        link("Math", "Value", "Mix", "Factor_Float")
        link("Principled BSDF.001", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbGenitals = _NodeWrapperMpfbGenitals()
