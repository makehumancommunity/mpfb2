import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbValueRamp3",
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
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_2": {
            "name": "BetweenStop1Value",
            "identifier": "Input_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_3": {
            "name": "BetweenStop2Value",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_4": {
            "name": "OneStopValue",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_5": {
            "name": "BetweenStop1Position",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.45,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_6": {
            "name": "BetweenStop2Position",
            "identifier": "Input_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_7": {
            "name": "Value",
            "identifier": "Output_7",
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
                -20.4761,
                -534.9553
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
            "value": 247.2069
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
            "from_node": "Math.021",
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
            "from_node": "Map Range.002",
            "from_socket": "Result",
            "to_node": "Math.014",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.014",
            "from_socket": "Value",
            "to_node": "Math.015",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range.002",
            "from_socket": "Result",
            "to_node": "Math.016",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.015",
            "from_socket": "Value",
            "to_node": "Math.017",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.016",
            "from_socket": "Value",
            "to_node": "Math.017",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.013",
            "from_socket": "Value",
            "to_node": "Math.018",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.017",
            "from_socket": "Value",
            "to_node": "Math.018",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Map Range.001",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Value",
            "to_node": "Math.009",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Map Range.002",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Value",
            "to_node": "Math.015",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OneStopValue",
            "to_node": "Math.016",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Math.013",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.013",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStop2Position",
            "to_node": "Math.019",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.019",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.019",
            "from_socket": "Value",
            "to_node": "Math.020",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.012",
            "from_socket": "Value",
            "to_node": "Math.020",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.020",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.006",
            "from_socket": "Value",
            "to_node": "Math.021",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.018",
            "from_socket": "Value",
            "to_node": "Math.021",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -1205.736,
                    -213.1223
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
                    1078.6742,
                    88.3517
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
                    -599.264,
                    747.069
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
                    113.891,
                    314.191
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
                    -274.094,
                    795.858
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
                    -87.121,
                    615.953
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
                    -88.29,
                    441.009
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
                    112.572,
                    516.639
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
                    363.944,
                    418.687
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
                    -616.414,
                    -824.414
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.002",
            "name": "Map Range.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    119.374,
                    -420.156
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.013",
            "name": "Math.013",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -356.746,
                    -945.977
                ],
                "operation": "SUBTRACT"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 1.0
            },
            "label": "Math.014",
            "name": "Math.014",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -73.032,
                    -589.624
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.015",
            "name": "Math.015",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -79.24,
                    -770.616
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.016",
            "name": "Math.016",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    119.606,
                    -632.49
                ],
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.017",
            "name": "Math.017",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -754.61,
                    -371.864
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
                    -498.67,
                    -439.349
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
                    -214.639,
                    -345.106
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
                    -269.02,
                    -124.953
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
                    -267.701,
                    70.622
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
                    -40.028,
                    -206.981
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
                    346.075,
                    41.645
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.020",
            "name": "Math.020",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    145.825,
                    111.387
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.019",
            "name": "Math.019",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    159.648,
                    -64.649
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.012",
            "name": "Math.012",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    636.757,
                    96.029
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
                    858.464,
                    94.332
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.021",
            "name": "Math.021",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    352.839,
                    -522.793
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.018",
            "name": "Math.018",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbValueRamp3(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-1205.736, -213.1223]
        nodes["Group Output"].location = [1078.6742, 88.3517]

        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-599.264, 747.069]})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [113.891, 314.191], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-274.094, 795.858], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-87.121, 615.953], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-88.29, 441.009], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [112.572, 516.639], "use_clamp": True})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [363.944, 418.687], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range.002", attribute_values={"location": [-616.414, -824.414]})
        node("ShaderNodeMath", "Math.013", attribute_values={"location": [119.374, -420.156], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.014", attribute_values={"location": [-356.746, -945.977], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.015", attribute_values={"location": [-73.032, -589.624], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.016", attribute_values={"location": [-79.24, -770.616], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.017", attribute_values={"location": [119.606, -632.49], "use_clamp": True})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-754.61, -371.864]})
        node("ShaderNodeMath", "Math.007", attribute_values={"location": [-498.67, -439.349], "operation": "SUBTRACT"}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.009", attribute_values={"location": [-214.639, -345.106], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.008", attribute_values={"location": [-269.02, -124.953], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.010", attribute_values={"location": [-267.701, 70.622], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.011", attribute_values={"location": [-40.028, -206.981], "use_clamp": True})
        node("ShaderNodeMath", "Math.020", attribute_values={"location": [346.075, 41.645], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.019", attribute_values={"location": [145.825, 111.387], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.012", attribute_values={"location": [159.648, -64.649], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.006", attribute_values={"location": [636.757, 96.029], "use_clamp": True}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math.021", attribute_values={"location": [858.464, 94.332]})
        node("ShaderNodeMath", "Math.018", attribute_values={"location": [352.839, -522.793], "operation": "MULTIPLY"})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "BetweenStop1Position", "Map Range", "From Max")
        link("Group Input", "BetweenStop1Position", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Group Input", "ZeroStopValue", "Math.001", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.002", "Value_001")
        link("Group Input", "Value", "Math.003", "Value")
        link("Group Input", "BetweenStop1Position", "Math.003", "Value_001")
        link("Group Input", "BetweenStop1Value", "Math.008", "Value_001")
        link("Group Input", "BetweenStop1Position", "Math.010", "Value_001")
        link("Group Input", "Value", "Math.010", "Value")
        link("Group Input", "BetweenStop2Position", "Map Range.001", "From Max")
        link("Group Input", "BetweenStop2Value", "Math.009", "Value")
        link("Group Input", "BetweenStop2Position", "Map Range.002", "From Min")
        link("Group Input", "Value", "Map Range.002", "Value")
        link("Group Input", "BetweenStop2Value", "Math.015", "Value_001")
        link("Group Input", "OneStopValue", "Math.016", "Value")
        link("Group Input", "BetweenStop2Position", "Math.013", "Value_001")
        link("Group Input", "Value", "Math.013", "Value")
        link("Group Input", "BetweenStop2Position", "Math.019", "Value_001")
        link("Group Input", "Value", "Math.019", "Value")
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
        link("Map Range.002", "Result", "Math.014", "Value_001")
        link("Math.014", "Value", "Math.015", "Value")
        link("Map Range.002", "Result", "Math.016", "Value_001")
        link("Math.015", "Value", "Math.017", "Value")
        link("Math.016", "Value", "Math.017", "Value_001")
        link("Math.013", "Value", "Math.018", "Value")
        link("Math.017", "Value", "Math.018", "Value_001")
        link("Math.019", "Value", "Math.020", "Value")
        link("Math.012", "Value", "Math.020", "Value_001")
        link("Math.020", "Value", "Math.006", "Value_001")
        link("Math.006", "Value", "Math.021", "Value")
        link("Math.018", "Value", "Math.021", "Value_001")
        link("Math.021", "Value", "Group Output", "Value")

NodeWrapperMpfbValueRamp3 = _NodeWrapperMpfbValueRamp3()
