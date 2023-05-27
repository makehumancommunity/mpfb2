import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinNavel",
    "inputs": {
        "Input_0": {
            "name": "SkinColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_1": {
            "name": "NavelCenterColor",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_2": {
            "name": "Normal",
            "identifier": "Input_2",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_3": {
            "name": "NavelColorStrength",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "NavelWidthMultiplier",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.01,
            "min_value": 0.001,
            "max_value": 0.2
        },
        "Input_5": {
            "name": "NavelBumpStrength",
            "identifier": "Input_5",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_6": {
            "name": "SkinColor",
            "identifier": "Output_6",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_7": {
            "name": "Normal",
            "identifier": "Output_7",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
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
                0.35,
                0.0,
                0.35
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
                -1609.5137,
                126.2919
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
            "value": 272.0078
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
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "ColorMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelBumpStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelWidthMultiplier",
            "to_node": "WidthMultiplier",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelColorStrength",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
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
            "from_node": "MapNavelRange",
            "from_socket": "Result",
            "to_node": "ValueRamp",
            "to_socket": "Value"
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
            "from_node": "WidthMultiplier",
            "from_socket": "Value",
            "to_node": "MapNavelRange",
            "to_socket": "From Max"
        },
        {
            "from_node": "AsValue",
            "from_socket": "Val",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "ColorMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "ColorMix",
            "to_socket": "A_Color"
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
            "from_node": "InsideDistance",
            "from_socket": "WithinDistance",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "ValueRamp",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    1434.42,
                    -310.9015
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
                    -570.997,
                    9.5032
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
                    -110.1569,
                    196.2622
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
                    387.7695,
                    358.6567
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
                "data_type": "RGBA",
                "location": [
                    618.1644,
                    332.8789
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
                    830.3863,
                    171.6911
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
                "color": [
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -758.4177,
                    358.8649
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbBodyConstants",
            "input_socket_values": {},
            "label": "Body coordinates",
            "name": "Coordinates",
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
                    96.0727,
                    227.7157
                ],
                "use_custom_color": true,
                "width": 208.9785
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.2,
                "BetweenStop1Value": 0.0,
                "BetweenStop2Position": 0.8,
                "BetweenStop2Value": 0.8,
                "OneStopValue": 1.0,
                "ZeroStopValue": 0.0
            },
            "label": "Value ramp",
            "name": "ValueRamp",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1160.9521,
                    -348.1321
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
                "data_type": "RGBA",
                "location": [
                    755.8022,
                    -102.8571
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
                "data_type": "RGBA",
                "location": [
                    156.7835,
                    -15.1607
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "Factor_Float": 1.0
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -130.8755,
                    430.1924
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math",
            "name": "Math",
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
                    -378.4563,
                    213.7805
                ],
                "use_custom_color": true,
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
                    399.6143,
                    136.9439
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -757.0346,
                    144.964
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
                    -756.8537,
                    -158.8215
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

        nodes["Group Output"].location = [1434.42, -310.9015]
        nodes["Group Input"].location = [-756.8537, -158.8215]

        node("ShaderNodeMath", "WidthMultiplier", label="Width multiplier", attribute_values={"location": [-570.997, 9.5032], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.001})
        node("ShaderNodeMapRange", "MapNavelRange", label="Map Range", attribute_values={"location": [-110.1569, 196.2622]})
        node("ShaderNodeMath", "AdjustBump", label="Adjust bump value", attribute_values={"location": [387.7695, 358.6567], "use_clamp": True}, input_socket_values={"Value_001": 0.3})
        node("ShaderNodeMix", "HeightMix", label="Height Mix", attribute_values={"data_type": "RGBA", "location": [618.1644, 332.8789]}, input_socket_values={"A_Color": [0.0, 0.0, 0.0, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeRGBToBW", "AsValue", label="As value", attribute_values={"location": [830.3863, 171.6911]})
        node("MpfbBodyConstants", "Coordinates", label="Body coordinates", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-758.4177, 358.8649], "use_custom_color": True, "width": 140.0})
        node("MpfbValueRamp3", "ValueRamp", label="Value ramp", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [96.0727, 227.7157], "use_custom_color": True, "width": 208.9785}, input_socket_values={"ZeroStopValue": 0.0, "BetweenStop1Value": 0.0, "BetweenStop2Value": 0.8, "OneStopValue": 1.0, "BetweenStop1Position": 0.2, "BetweenStop2Position": 0.8})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [1160.9521, -348.1321]}, input_socket_values={"Strength": 0.3})
        node("ShaderNodeMix", "ColorMix", label="Color Mix", attribute_values={"data_type": "RGBA", "location": [755.8022, -102.8571]}, input_socket_values={"A_Color": [0.5138, 0.2284, 0.0983, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [156.7835, -15.1607]}, input_socket_values={"Factor_Float": 1.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-130.8755, 430.1924], "operation": "SUBTRACT", "use_clamp": True}, input_socket_values={"Value": 1.0})
        node("MpfbWithinDistance", "InsideDistance", label="Within relevant distance", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [-378.4563, 213.7805], "use_custom_color": True, "width": 200.3467})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [399.6143, 136.9439], "use_clamp": True})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-757.0346, 144.964]})

        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "SkinColor", "ColorMix", "B_Color")
        link("Group Input", "NavelBumpStrength", "Bump", "Strength")
        link("Group Input", "NavelWidthMultiplier", "WidthMultiplier", "Value")
        link("Group Input", "NavelCenterColor", "Mix", "B_Color")
        link("Group Input", "SkinColor", "Mix", "A_Color")
        link("Group Input", "NavelColorStrength", "Mix", "Factor_Float")
        link("Coordinates", "NavelCoordinate", "InsideDistance", "Coordinate1")
        link("Texture Coordinate", "UV", "InsideDistance", "Coordinate2")
        link("WidthMultiplier", "Value", "InsideDistance", "MaxDist")
        link("HeightMix", "Result_Color", "AsValue", "Color")
        link("InsideDistance", "ActualDistance", "MapNavelRange", "Value")
        link("MapNavelRange", "Result", "ValueRamp", "Value")
        link("AdjustBump", "Value", "HeightMix", "Factor_Float")
        link("ValueRamp", "Value", "AdjustBump", "Value")
        link("WidthMultiplier", "Value", "MapNavelRange", "From Max")
        link("AsValue", "Val", "Bump", "Height")
        link("Math.001", "Value", "ColorMix", "Factor_Float")
        link("Mix", "Result_Color", "ColorMix", "A_Color")
        link("InsideDistance", "WithinDistance", "Math", "Value_001")
        link("ValueRamp", "Value", "Math.001", "Value")
        link("Math", "Value", "Math.001", "Value_001")
        link("Bump", "Normal", "Group Output", "Normal")
        link("ColorMix", "Result_Color", "Group Output", "SkinColor")

NodeWrapperMpfbSkinNavel = _NodeWrapperMpfbSkinNavel()
