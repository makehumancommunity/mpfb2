import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbValueRamp2",
    "inputs": {
        "Input_0": {
            "name": "Value",
            "identifier": "Input_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_1": {
            "name": "ZeroStopValue",
            "identifier": "Input_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_2": {
            "name": "BetweenStop1Value",
            "identifier": "Input_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.999,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_3": {
            "name": "OneStopValue",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_4": {
            "name": "BetweenStop1Position",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_5": {
            "name": "Value",
            "identifier": "Output_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
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
                17.6894,
                -687.0515
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
            "value": 201.5218
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Map Range.001",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ZeroStopValue",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Value",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "Math.005",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.005",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Math.005",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.006",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Math.007",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.007",
            "from_socket": "Value",
            "to_node": "Math.008",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Value",
            "to_node": "Math.008",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Math.009",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OneStopValue",
            "to_node": "Math.009",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop1Position",
            "to_node": "Math.010",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.010",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.008",
            "from_socket": "Value",
            "to_node": "Math.011",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.009",
            "from_socket": "Value",
            "to_node": "Math.011",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.010",
            "from_socket": "Value",
            "to_node": "Math.012",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.011",
            "from_socket": "Value",
            "to_node": "Math.012",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.012",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -872.1455,
                    16.1281
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    800.6749,
                    71.5684
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
                    -597.99,
                    521.639
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range",
            "name": "Map Range",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    115.164,
                    88.762
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.003",
            "name": "Math.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    575.236,
                    44.747
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.0
            },
            "label": "Math.006",
            "name": "Math.006",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -272.821,
                    570.429
                ],
                "operation": "SUBTRACT"
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
                "location": [
                    -85.848,
                    390.524
                ],
                "operation": "MULTIPLY"
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
                    -87.016,
                    215.58
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -619.152,
                    -525.678
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.001",
            "name": "Map Range.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    116.636,
                    -121.42
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.010",
            "name": "Math.010",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -359.484,
                    -647.242
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math.007",
            "name": "Math.007",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    113.845,
                    291.209
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.004",
            "name": "Math.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -75.77,
                    -290.888
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.008",
            "name": "Math.008",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -81.978,
                    -471.88
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.009",
            "name": "Math.009",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    116.868,
                    -333.754
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.011",
            "name": "Math.011",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    365.217,
                    193.257
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.005",
            "name": "Math.005",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    350.101,
                    -224.057
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.012",
            "name": "Math.012",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbValueRamp2(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-872.1455, 16.1281]
        nodes["Group Output"].location = [800.6749, 71.5684]

        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-597.99, 521.639]})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [115.164, 88.762], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.006", attribute_values={"location": [575.236, 44.747], "use_clamp": True}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-272.821, 570.429], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-85.848, 390.524], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-87.016, 215.58], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-619.152, -525.678]})
        node("ShaderNodeMath", "Math.010", attribute_values={"location": [116.636, -121.42], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.007", attribute_values={"location": [-359.484, -647.242], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [113.845, 291.209], "use_clamp": True})
        node("ShaderNodeMath", "Math.008", attribute_values={"location": [-75.77, -290.888], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.009", attribute_values={"location": [-81.978, -471.88], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.011", attribute_values={"location": [116.868, -333.754], "use_clamp": True})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [365.217, 193.257], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.012", attribute_values={"location": [350.101, -224.057], "operation": "MULTIPLY"})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "BetweenStop1Position", "Map Range", "From Max")
        link("Group Input", "BetweenStop1Position", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Group Input", "ZeroStopValue", "Math.001", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.002", "Value_001")
        link("Group Input", "Value", "Math.003", "Value")
        link("Group Input", "BetweenStop1Position", "Math.003", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.008", "Value_001")
        link("Group Input", "OneStopValue", "Math.009", "Value")
        link("Group Input", "BetweenStop1Position", "Math.010", "Value_001")
        link("Group Input", "Value", "Math.010", "Value")
        link("Map Range", "Result", "Math", "Value_001")
        link("Math", "Value", "Math.001", "Value")
        link("Map Range", "Result", "Math.002", "Value")
        link("Math.001", "Value", "Math.004", "Value")
        link("Math.002", "Value", "Math.004", "Value_001")
        link("Math.004", "Value", "Math.005", "Value")
        link("Math.005", "Value", "Math.006", "Value")
        link("Math.003", "Value", "Math.005", "Value_001")
        link("Map Range.001", "Result", "Math.007", "Value_001")
        link("Math.007", "Value", "Math.008", "Value")
        link("Map Range.001", "Result", "Math.009", "Value_001")
        link("Math.008", "Value", "Math.011", "Value")
        link("Math.009", "Value", "Math.011", "Value_001")
        link("Math.010", "Value", "Math.012", "Value")
        link("Math.011", "Value", "Math.012", "Value_001")
        link("Math.012", "Value", "Math.006", "Value_001")
        link("Math.006", "Value", "Group Output", "Value")

NodeWrapperMpfbValueRamp2 = _NodeWrapperMpfbValueRamp2()
