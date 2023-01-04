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
                31.3492,
                395.6969
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
    "class": "MpfbNormalizeValue",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_0",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Input_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_1",
            "name": "IncomingMax",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_2",
            "name": "IncomingMin",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_5",
            "name": "IsWithinRange",
            "value_type": "VALUE"
        },
        "Output_6": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_6",
            "name": "NormalizedValue",
            "value_type": "VALUE"
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
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "IsWithinRange"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "NormalizedValue"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math",
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
            "from_socket": "IncomingMin",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "IncomingMax",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "IncomingMin",
            "to_node": "Map Range",
            "to_socket": "From Min"
        },
        {
            "from_node": "Group Input",
            "from_socket": "IncomingMax",
            "to_node": "Map Range",
            "to_socket": "From Max"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -320.6336,
                    -213.4447
                ],
                "operation": "GREATER_THAN"
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
                    -319.0385,
                    -49.8992
                ],
                "operation": "LESS_THAN"
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
                    -101.2581,
                    -120.8263
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
                    78.1912,
                    240.5693
                ],
                "operation": "MULTIPLY"
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
                    -323.8376,
                    218.613
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
                    398.9899,
                    39.8891
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
                    -689.7286,
                    39.0914
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

class _NodeWrapperMpfbNormalizeValue(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [398.9899, 39.8891]
        nodes["Group Input"].location = [-689.7286, 39.0914]

        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-320.6336, -213.4447], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-319.0385, -49.8992], "operation": "LESS_THAN"})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-101.2581, -120.8263], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [78.1912, 240.5693], "operation": "MULTIPLY"})
        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-323.8376, 218.613]})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "Value", "Math", "Value")
        link("Group Input", "Value", "Math.001", "Value")
        link("Group Input", "IncomingMin", "Math.001", "Value_001")
        link("Group Input", "IncomingMax", "Math", "Value_001")
        link("Group Input", "IncomingMin", "Map Range", "From Min")
        link("Group Input", "IncomingMax", "Map Range", "From Max")
        link("Math.001", "Value", "Math.002", "Value_001")
        link("Math", "Value", "Math.002", "Value")
        link("Math.002", "Value", "Math.004", "Value_001")
        link("Map Range", "Result", "Math.004", "Value")
        link("Math.002", "Value", "Group Output", "IsWithinRange")
        link("Math.004", "Value", "Group Output", "NormalizedValue")

NodeWrapperMpfbNormalizeValue = _NodeWrapperMpfbNormalizeValue()
