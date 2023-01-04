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
                -464.7218,
                539.9684
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
            "value": 140.0
        }
    },
    "class": "MpfbAdditiveRange2",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_0",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Input_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_1",
            "name": "Section1Size",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_2",
            "name": "Section2Size",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_4": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_4",
            "name": "NormalizedSectionValue",
            "value_type": "VALUE"
        },
        "Output_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_5",
            "name": "WithinSection1",
            "value_type": "VALUE"
        },
        "Output_6": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_6",
            "name": "WithinSection2",
            "value_type": "VALUE"
        },
        "Output_7": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_7",
            "name": "TotalSectionSize",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Section1Size",
            "to_node": "TotalSectionSize",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section2Size",
            "to_node": "TotalSectionSize",
            "to_socket": "Value_001"
        },
        {
            "from_node": "TotalSectionSize",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "TotalSectionSize"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Size",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "WithinSection1",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "WithinSection1",
            "to_socket": "Value"
        },
        {
            "from_node": "WithinSection1",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "WithinSection1"
        },
        {
            "from_node": "TotalSectionSize",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Size",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "WithinSection2",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "WithinSection2",
            "to_socket": "Value_001"
        },
        {
            "from_node": "WithinSection2",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "WithinSection2"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Size",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "TotalSectionSize",
            "from_socket": "Value",
            "to_node": "Map Range.001",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Size",
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
            "from_node": "WithinSection2",
            "from_socket": "Value",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "WithinSection1",
            "from_socket": "Value",
            "to_node": "Math.005",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
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
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.006",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.006",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "NormalizedSectionValue"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -281.4596,
                    279.4569
                ],
                "operation": "LESS_THAN"
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
                    -284.3259,
                    111.5318
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.0
            },
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -289.7557,
                    -465.763
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.0
            },
            "label": "Math.004",
            "name": "Math.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -285.9573,
                    -284.085
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
                    -37.6297,
                    -356.3592
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "WithinSection2",
            "name": "WithinSection2",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -539.6771,
                    -237.1958
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "TotalSectionSize",
            "name": "TotalSectionSize",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    188.0531,
                    -458.819
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
                    422.4159,
                    -315.3939
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
                    407.5018,
                    328.8941
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
                    -33.6075,
                    193.1193
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "WithinSection1",
            "name": "WithinSection1",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    174.0712,
                    470.7832
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
                    627.0646,
                    184.216
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.006",
            "name": "Math.006",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    850.4581,
                    -57.8787
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
                    -924.0525,
                    31.5151
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

class _NodeWrapperMpfbAdditiveRange2(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [850.4581, -57.8787]
        nodes["Group Input"].location = [-924.0525, 31.5151]

        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-281.4596, 279.4569], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-284.3259, 111.5318], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [-289.7557, -465.763], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.0})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [-285.9573, -284.085], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "WithinSection2", attribute_values={"location": [-37.6297, -356.3592], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "TotalSectionSize", attribute_values={"location": [-539.6771, -237.1958]})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [188.0531, -458.819]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [422.4159, -315.3939], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [407.5018, 328.8941], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "WithinSection1", attribute_values={"location": [-33.6075, 193.1193], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [174.0712, 470.7832]})
        node("ShaderNodeMath", "Math.006", attribute_values={"location": [627.0646, 184.216]})

        link("Group Input", "Section1Size", "TotalSectionSize", "Value")
        link("Group Input", "Section2Size", "TotalSectionSize", "Value_001")
        link("Group Input", "Value", "Math.002", "Value")
        link("Group Input", "Value", "Math.001", "Value")
        link("Group Input", "Section1Size", "Math.001", "Value_001")
        link("Group Input", "Value", "Math.003", "Value")
        link("Group Input", "Section1Size", "Math.004", "Value_001")
        link("Group Input", "Value", "Math.004", "Value")
        link("Group Input", "Section1Size", "Map Range", "From Max")
        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "Section1Size", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Math.002", "Value", "WithinSection1", "Value_001")
        link("Math.001", "Value", "WithinSection1", "Value")
        link("TotalSectionSize", "Value", "Math.003", "Value_001")
        link("Math.003", "Value", "WithinSection2", "Value")
        link("Math.004", "Value", "WithinSection2", "Value_001")
        link("TotalSectionSize", "Value", "Map Range.001", "From Max")
        link("WithinSection2", "Value", "Math", "Value")
        link("Map Range.001", "Result", "Math", "Value_001")
        link("WithinSection1", "Value", "Math.005", "Value_001")
        link("Map Range", "Result", "Math.005", "Value")
        link("Math.005", "Value", "Math.006", "Value")
        link("Math", "Value", "Math.006", "Value_001")
        link("TotalSectionSize", "Value", "Group Output", "TotalSectionSize")
        link("WithinSection1", "Value", "Group Output", "WithinSection1")
        link("WithinSection2", "Value", "Group Output", "WithinSection2")
        link("Math.006", "Value", "Group Output", "NormalizedSectionValue")

NodeWrapperMpfbAdditiveRange2 = _NodeWrapperMpfbAdditiveRange2()
