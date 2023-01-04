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
                -211.1376,
                586.6746
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
    "class": "MpfbValueRamp1",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_0",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Input_6": {
            "class": "NodeSocketFloat",
            "default_value": 0.9,
            "identifier": "Input_6",
            "name": "ZeroStopValue",
            "value_type": "VALUE"
        },
        "Input_7": {
            "class": "NodeSocketFloat",
            "default_value": 0.1,
            "identifier": "Input_7",
            "name": "OneStopValue",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_1",
            "name": "Value",
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
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ZeroStopValue",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OneStopValue",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -529.7517,
                    349.4768
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
                "location": [
                    -253.6853,
                    115.5385
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
                    -254.693,
                    294.9634
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
                    38.8086,
                    206.8738
                ],
                "use_clamp": true
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
                    353.2497,
                    140.1127
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
                    -878.1918,
                    154.2248
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

class _NodeWrapperMpfbValueRamp1(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [353.2497, 140.1127]
        nodes["Group Input"].location = [-878.1918, 154.2248]

        node("ShaderNodeMath", "Math", attribute_values={"location": [-529.7517, 349.4768], "operation": "SUBTRACT", "use_clamp": True}, input_socket_values={"Value": 1.0})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-253.6853, 115.5385], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-254.693, 294.9634], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [38.8086, 206.8738], "use_clamp": True})

        link("Group Input", "Value", "Math", "Value_001")
        link("Group Input", "ZeroStopValue", "Math.001", "Value_001")
        link("Group Input", "OneStopValue", "Math.002", "Value_001")
        link("Group Input", "Value", "Math.002", "Value")
        link("Math", "Value", "Math.001", "Value")
        link("Math.001", "Value", "Math.003", "Value")
        link("Math.002", "Value", "Math.003", "Value_001")
        link("Math.003", "Value", "Group Output", "Value")

NodeWrapperMpfbValueRamp1 = _NodeWrapperMpfbValueRamp1()
