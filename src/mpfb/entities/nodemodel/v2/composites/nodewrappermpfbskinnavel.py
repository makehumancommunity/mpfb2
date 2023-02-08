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
                -1609.5137,
                126.2919
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
            "value": 272.0078
        }
    },
    "class": "MpfbSkinNavel",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.01,
            "identifier": "Input_0",
            "max_value": 0.2,
            "min_value": 0.001,
            "name": "NavelWidthMultiplier",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.1,
            "identifier": "Input_2",
            "name": "NavelBumpStrength",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_3",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Input_4": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_4",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Input_5": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_5",
            "name": "NavelCenterColor",
            "value_type": "RGBA"
        },
        "Input_7": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_7",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "NavelColorStrength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Output_6": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_6",
            "name": "SkinColor",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Coordinates",
            "from_socket": "NavelCoordinate",
            "to_node": "InsideDistance",
            "to_socket": "Coordinate1"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "UV",
            "to_node": "InsideDistance",
            "to_socket": "Coordinate2"
        },
        {
            "from_node": "WidthMultiplier",
            "from_socket": "Value",
            "to_node": "InsideDistance",
            "to_socket": "MaxDist"
        },
        {
            "from_node": "HeightMix",
            "from_socket": "Result_Color",
            "to_node": "AsValue",
            "to_socket": "Color"
        },
        {
            "from_node": "InsideDistance",
            "from_socket": "ActualDistance",
            "to_node": "MapNavelRange",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "ColorMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "MapNavelRange",
            "from_socket": "Result",
            "to_node": "ValueRamp",
            "to_socket": "Value"
        },
        {
            "from_node": "ColorStrength",
            "from_socket": "Value",
            "to_node": "ColorMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelBumpStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterColor",
            "to_node": "ColorMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "AdjustBump",
            "from_socket": "Value",
            "to_node": "HeightMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "ValueRamp",
            "from_socket": "Value",
            "to_node": "AdjustBump",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelWidthMultiplier",
            "to_node": "WidthMultiplier",
            "to_socket": "Value"
        },
        {
            "from_node": "WidthMultiplier",
            "from_socket": "Value",
            "to_node": "MapNavelRange",
            "to_socket": "From Max"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "ColorMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "ValueRamp",
            "from_socket": "Value",
            "to_node": "ColorStrength",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelColorStrength",
            "to_node": "ColorStrength",
            "to_socket": "Value_001"
        },
        {
            "from_node": "AsValue",
            "from_socket": "Val",
            "to_node": "Bump",
            "to_socket": "Height"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -895.7065,
                    152.4116
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
                    1170.8096,
                    95.9387
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
                    -709.6689,
                    16.9508
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.001
            },
            "label": "Width multiplier",
            "name": "WidthMultiplier",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -517.1282,
                    221.2281
                ],
                "width": 200.3467
            },
            "class": "MpfbWithinDistance",
            "input_socket_values": {},
            "label": "Within relevant distance",
            "name": "InsideDistance",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -248.8288,
                    203.7098
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range",
            "name": "MapNavelRange",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -42.5992,
                    235.1633
                ],
                "width": 208.9785
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "Input_6": 0.8
            },
            "label": "Value ramp",
            "name": "ValueRamp",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    249.0976,
                    366.1043
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.3
            },
            "label": "Adjust bump value",
            "name": "AdjustBump",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    250.2501,
                    108.7121
                ],
                "operation": "MULTIPLY",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0,
                "Value_001": 1.0
            },
            "label": "Color strength",
            "name": "ColorStrength",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    479.4925,
                    340.3265
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ],
                "B_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "label": "Height Mix",
            "name": "HeightMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    691.7144,
                    179.1387
                ]
            },
            "class": "ShaderNodeRGBToBW",
            "input_socket_values": {},
            "label": "As value",
            "name": "AsValue",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    474.1593,
                    68.2127
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.5138,
                    0.2284,
                    0.0983,
                    1.0
                ],
                "B_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "label": "Color Mix",
            "name": "ColorMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    917.9501,
                    -53.3795
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
                "location": [
                    -897.0895,
                    366.3125
                ]
            },
            "class": "MpfbBodyConstants",
            "input_socket_values": {},
            "label": "Body coordinates",
            "name": "Coordinates",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -895.5255,
                    -151.3739
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

class _NodeWrapperMpfbSkinNavel(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1170.8096, 95.9387]
        nodes["Group Input"].location = [-895.5255, -151.3739]

        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-895.7065, 152.4116]})
        node("ShaderNodeMath", "WidthMultiplier", label="Width multiplier", attribute_values={"location": [-709.6689, 16.9508], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.001})
        node("MpfbWithinDistance", "InsideDistance", label="Within relevant distance", attribute_values={"location": [-517.1282, 221.2281], "width": 200.3467})
        node("ShaderNodeMapRange", "MapNavelRange", label="Map Range", attribute_values={"location": [-248.8288, 203.7098]})
        node("MpfbValueRamp3", "ValueRamp", label="Value ramp", attribute_values={"location": [-42.5992, 235.1633], "width": 208.9785}, input_socket_values={"Input_6": 0.8})
        node("ShaderNodeMath", "AdjustBump", label="Adjust bump value", attribute_values={"location": [249.0976, 366.1043], "use_clamp": True}, input_socket_values={"Value_001": 0.3})
        node("ShaderNodeMath", "ColorStrength", label="Color strength", attribute_values={"location": [250.2501, 108.7121], "operation": "MULTIPLY", "use_clamp": True}, input_socket_values={"Value": 1.0, "Value_001": 1.0})
        node("ShaderNodeMix", "HeightMix", label="Height Mix", attribute_values={"data_type": "RGBA", "location": [479.4925, 340.3265]}, input_socket_values={"A_Color": [0.0, 0.0, 0.0, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeRGBToBW", "AsValue", label="As value", attribute_values={"location": [691.7144, 179.1387]})
        node("ShaderNodeMix", "ColorMix", label="Color Mix", attribute_values={"data_type": "RGBA", "location": [474.1593, 68.2127]}, input_socket_values={"A_Color": [0.5138, 0.2284, 0.0983, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [917.9501, -53.3795]}, input_socket_values={"Strength": 0.3})
        node("MpfbBodyConstants", "Coordinates", label="Body coordinates", attribute_values={"location": [-897.0895, 366.3125]})

        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "SkinColor", "ColorMix", "B_Color")
        link("Group Input", "NavelBumpStrength", "Bump", "Strength")
        link("Group Input", "NavelCenterColor", "ColorMix", "A_Color")
        link("Group Input", "NavelWidthMultiplier", "WidthMultiplier", "Value")
        link("Group Input", "NavelColorStrength", "ColorStrength", "Value_001")
        link("Coordinates", "NavelCoordinate", "InsideDistance", "Coordinate1")
        link("Texture Coordinate", "UV", "InsideDistance", "Coordinate2")
        link("WidthMultiplier", "Value", "InsideDistance", "MaxDist")
        link("HeightMix", "Result_Color", "AsValue", "Color")
        link("InsideDistance", "ActualDistance", "MapNavelRange", "Value")
        link("MapNavelRange", "Result", "ValueRamp", "Value")
        link("ColorStrength", "Value", "ColorMix", "Factor_Float")
        link("AdjustBump", "Value", "HeightMix", "Factor_Float")
        link("ValueRamp", "Value", "AdjustBump", "Value")
        link("WidthMultiplier", "Value", "MapNavelRange", "From Max")
        link("ValueRamp", "Value", "ColorStrength", "Value")
        link("AsValue", "Val", "Bump", "Height")
        link("Bump", "Normal", "Group Output", "Normal")
        link("ColorMix", "Result_Color", "Group Output", "SkinColor")

NodeWrapperMpfbSkinNavel = _NodeWrapperMpfbSkinNavel()
