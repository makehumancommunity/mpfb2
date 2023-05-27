import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinSpot",
    "inputs": {
        "Input_0": {
            "name": "SkinColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.9963,
                0.936,
                1.0,
                1.0
            ]
        },
        "Input_1": {
            "name": "SpotColor",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_2": {
            "name": "SpotStrength",
            "identifier": "Input_2",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_3": {
            "name": "SpotScaleMultiplier",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 20.0,
            "min_value": 0.1,
            "max_value": 10000.0
        },
        "Input_4": {
            "name": "SpotDetail",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_5": {
            "name": "SpotDistortion",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_6": {
            "name": "SpotRoughness",
            "identifier": "Input_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_7": {
            "name": "SpotValley",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_8": {
            "name": "SpotPeak",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_9": {
            "name": "Color",
            "identifier": "Output_9",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
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
                -437.9299,
                347.867
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
            "value": 140.0
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SpotScaleMultiplier",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotStrength",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDetail",
            "to_node": "Noise Texture",
            "to_socket": "Detail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDistortion",
            "to_node": "Noise Texture",
            "to_socket": "Distortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotRoughness",
            "to_node": "Noise Texture",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Group.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.001",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotValley",
            "to_node": "Group.001",
            "to_socket": "BetweenStop1Position"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotPeak",
            "to_node": "Group.001",
            "to_socket": "BetweenStop2Position"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -444.5622,
                    608.2729
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
                    50.5701,
                    299.0699
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Detail": 1.0,
                "Roughness": 0.0,
                "Scale": 200.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -429.549,
                    158.7146
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 40.0
            },
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -805.7254,
                    212.348
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Group",
            "name": "Group",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1366.6917,
                    21.0829
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
                    1070.9824,
                    -65.9174
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.5,
                    0.0051,
                    0.0,
                    1.0
                ],
                "B_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ],
                "Factor_Float": 0.1
            },
            "label": "Mix",
            "name": "Mix",
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
                    464.3445,
                    359.8197
                ],
                "use_custom_color": true,
                "width": 242.6163
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.848,
                "BetweenStop1Value": 0.0,
                "BetweenStop2Position": 0.916,
                "BetweenStop2Value": 1.0,
                "OneStopValue": 1.0,
                "ZeroStopValue": 0.0
            },
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    814.5854,
                    63.3332
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 1.0
            },
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -989.225,
                    -200.5338
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

class _NodeWrapperMpfbSkinSpot(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1366.6917, 21.0829]
        nodes["Group Input"].location = [-989.225, -200.5338]

        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-444.5622, 608.2729]})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [50.5701, 299.0699]}, input_socket_values={"Detail": 1.0, "Roughness": 0.0, "Scale": 200.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-429.549, 158.7146], "operation": "DIVIDE"}, input_socket_values={"Value": 40.0})
        node("MpfbCharacterInfo", "Group", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-805.7254, 212.348], "use_custom_color": True, "width": 140.0})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [1070.9824, -65.9174]}, input_socket_values={"A_Color": [0.5, 0.0051, 0.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0], "Factor_Float": 0.1})
        node("MpfbValueRamp3", "Group.001", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [464.3445, 359.8197], "use_custom_color": True, "width": 242.6163}, input_socket_values={"ZeroStopValue": 0.0, "BetweenStop1Value": 0.0, "BetweenStop2Value": 1.0, "OneStopValue": 1.0, "BetweenStop1Position": 0.848, "BetweenStop2Position": 0.916})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [814.5854, 63.3332], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 1.0})

        link("Group Input", "SpotScaleMultiplier", "Math", "Value")
        link("Group Input", "SpotStrength", "Math.001", "Value_001")
        link("Group Input", "SpotDetail", "Noise Texture", "Detail")
        link("Group Input", "SpotDistortion", "Noise Texture", "Distortion")
        link("Group Input", "SpotRoughness", "Noise Texture", "Roughness")
        link("Group Input", "SpotValley", "Group.001", "BetweenStop1Position")
        link("Group Input", "SpotPeak", "Group.001", "BetweenStop2Position")
        link("Group Input", "SkinColor", "Mix", "A_Color")
        link("Group Input", "SpotColor", "Mix", "B_Color")
        link("Group", "scale_factor", "Math", "Value_001")
        link("Texture Coordinate", "Object", "Noise Texture", "Vector")
        link("Noise Texture", "Fac", "Group.001", "Value")
        link("Group.001", "Value", "Math.001", "Value")
        link("Math", "Value", "Noise Texture", "Scale")
        link("Math.001", "Value", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbSkinSpot = _NodeWrapperMpfbSkinSpot()
