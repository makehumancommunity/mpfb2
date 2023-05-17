import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbLips",
    "inputs": {
        "Input_4": {
            "name": "LipsColor",
            "identifier": "Input_4",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.0,
                0.0022,
                1.0
            ]
        },
        "Input_9": {
            "name": "LipsCreaseScale",
            "identifier": "Input_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 9.5,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_8": {
            "name": "LipsCreaseStretch",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 7.0,
            "min_value": 0.1,
            "max_value": 20.0
        },
        "Input_10": {
            "name": "LipsCreaseStrength",
            "identifier": "Input_10",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.3,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_12": {
            "name": "LipsRoughness",
            "identifier": "Input_12",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.4,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_13": {
            "name": "LipsSSSStrength",
            "identifier": "Input_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_14": {
            "name": "LipsSSSRadiusMultiplyer",
            "identifier": "Input_14",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_15": {
            "name": "LipsSSSIor",
            "identifier": "Input_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_11": {
            "name": "Normal",
            "identifier": "Input_11",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        }
    },
    "outputs": {
        "Output_7": {
            "name": "BSDF",
            "identifier": "Output_7",
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
                708.2214,
                -157.2171
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
            "value": 323.4168
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Vector Math",
            "from_socket": "Vector",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Vector Math",
            "to_socket": "Vector"
        },
        {
            "from_node": "characterinfo",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "Combine XYZ",
            "from_socket": "Vector",
            "to_node": "Vector Math",
            "to_socket": "Vector_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseStretch",
            "to_node": "Combine XYZ",
            "to_socket": "X"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseScale",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsRoughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsColor",
            "to_node": "SSS",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceColor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Color"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceRadius",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceIor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsSSSStrength",
            "to_node": "SSS",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsSSSRadiusMultiplyer",
            "to_node": "SSS",
            "to_socket": "SubsurfaceRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsSSSIor",
            "to_node": "SSS",
            "to_socket": "SubsurfaceIor"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Group.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsColor",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Group.002",
            "from_socket": "Value",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    1027.3911,
                    150.8435
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
                    -636.2607,
                    -330.3268
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 20.0
            },
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    599.8683,
                    26.5137
                ]
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {
                "Roughness": 0.2
            },
            "label": "Principled BSDF",
            "name": "Principled BSDF",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -748.2275,
                    -528.289
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 8.0,
                "Y": 1.0,
                "Z": 1.0
            },
            "label": "Combine XYZ",
            "name": "Combine XYZ",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -495.3525,
                    -611.6572
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {
                "Vector_001": [
                    8.0,
                    1.0,
                    1.0
                ]
            },
            "label": "Vector Math",
            "name": "Vector Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1016.369,
                    -543.5457
                ]
            },
            "class": "ShaderNodeTexCoord",
            "input_socket_values": {},
            "label": "Texture Coordinate",
            "name": "Texture Coordinate",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    329.0903,
                    -352.9689
                ]
            },
            "class": "ShaderNodeBump",
            "input_socket_values": {
                "Strength": 0.3
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
                    -20.4761,
                    -534.9553
                ],
                "use_custom_color": false,
                "width": 247.2069
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.45,
                "BetweenStop1Value": 1.0,
                "BetweenStop2Position": 0.7,
                "BetweenStop2Value": 0.4,
                "OneStopValue": 0.0,
                "ZeroStopValue": 1.0
            },
            "label": "Group.002",
            "name": "Group.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -254.1799,
                    -522.9743
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Detail": 4.0,
                "Distortion": 2.0,
                "Scale": 50.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
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
                    -1017.6295,
                    -344.016
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Character Info",
            "name": "characterinfo",
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
                    137.0951,
                    254.0526
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
                    -1017.7735,
                    -93.5589
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

class _NodeWrapperMpfbLips(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1027.3911, 150.8435]
        nodes["Group Input"].location = [-1017.7735, -93.5589]

        node("ShaderNodeMath", "Math", attribute_values={"location": [-636.2607, -330.3268], "operation": "DIVIDE"}, input_socket_values={"Value": 20.0})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [599.8683, 26.5137]}, input_socket_values={"Roughness": 0.2})
        node("ShaderNodeCombineXYZ", "Combine XYZ", attribute_values={"location": [-748.2275, -528.289]}, input_socket_values={"X": 8.0, "Y": 1.0, "Z": 1.0})
        node("ShaderNodeVectorMath", "Vector Math", attribute_values={"location": [-495.3525, -611.6572], "operation": "MULTIPLY"}, input_socket_values={"Vector_001": [8.0, 1.0, 1.0]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-1016.369, -543.5457]})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [329.0903, -352.9689]}, input_socket_values={"Strength": 0.3})
        node("MpfbValueRamp3", "Group.002", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-20.4761, -534.9553], "use_custom_color": False, "width": 247.2069}, input_socket_values={"ZeroStopValue": 1.0, "BetweenStop1Value": 1.0, "BetweenStop2Value": 0.4, "OneStopValue": 0.0, "BetweenStop1Position": 0.45, "BetweenStop2Position": 0.7})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-254.1799, -522.9743]}, input_socket_values={"Detail": 4.0, "Distortion": 2.0, "Scale": 50.0})
        node("MpfbCharacterInfo", "characterinfo", label="Character Info", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1017.6295, -344.016], "use_custom_color": False, "width": 140.0})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [137.0951, 254.0526], "use_custom_color": False, "width": 140.0}, input_socket_values={"SubsurfaceRadiusMultiplyer": 1.0})

        link("Group Input", "LipsCreaseStretch", "Combine XYZ", "X")
        link("Group Input", "LipsCreaseScale", "Math", "Value")
        link("Group Input", "LipsCreaseStrength", "Bump", "Strength")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "LipsRoughness", "Principled BSDF", "Roughness")
        link("Group Input", "LipsColor", "SSS", "SubsurfaceColor")
        link("Group Input", "LipsSSSStrength", "SSS", "SubsurfaceStrength")
        link("Group Input", "LipsSSSRadiusMultiplyer", "SSS", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "LipsSSSIor", "SSS", "SubsurfaceIor")
        link("Group Input", "LipsColor", "Principled BSDF", "Base Color")
        link("Vector Math", "Vector", "Noise Texture", "Vector")
        link("Texture Coordinate", "Object", "Vector Math", "Vector")
        link("characterinfo", "scale_factor", "Math", "Value_001")
        link("Math", "Value", "Noise Texture", "Scale")
        link("Combine XYZ", "Vector", "Vector Math", "Vector_001")
        link("SSS", "SubsurfaceColor", "Principled BSDF", "Subsurface Color")
        link("SSS", "SubsurfaceRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SubsurfaceStrength", "Principled BSDF", "Subsurface")
        link("SSS", "SubsurfaceIor", "Principled BSDF", "Subsurface IOR")
        link("Noise Texture", "Fac", "Group.002", "Value")
        link("Group.002", "Value", "Bump", "Height")
        link("Bump", "Normal", "Principled BSDF", "Normal")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbLips = _NodeWrapperMpfbLips()
