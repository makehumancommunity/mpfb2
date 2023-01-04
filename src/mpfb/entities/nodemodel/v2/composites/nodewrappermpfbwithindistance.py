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
                -478.512,
                346.8373
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
    "class": "MpfbWithinDistance",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_0",
            "name": "Coordinate1",
            "value_type": "VECTOR"
        },
        "Input_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_1",
            "name": "Coordinate2",
            "value_type": "VECTOR"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_2",
            "name": "MaxDist",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_3": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_3",
            "name": "WithinDistance",
            "value_type": "VALUE"
        },
        "Output_4": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_4",
            "name": "ActualDistance",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Coordinate1",
            "to_node": "Vector Math",
            "to_socket": "Vector"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Coordinate2",
            "to_node": "Vector Math",
            "to_socket": "Vector_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "MaxDist",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "WithinDistance"
        },
        {
            "from_node": "Vector Math",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "ActualDistance"
        },
        {
            "from_node": "Vector Math",
            "from_socket": "Value",
            "to_node": "Math",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    392.9464,
                    41.3276
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
                    -157.7106,
                    193.546
                ],
                "operation": "DISTANCE"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {},
            "label": "Vector Math",
            "name": "Vector Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    64.9711,
                    30.6791
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
                    -397.9847,
                    96.7671
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

class _NodeWrapperMpfbWithinDistance(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [392.9464, 41.3276]
        nodes["Group Input"].location = [-397.9847, 96.7671]

        node("ShaderNodeVectorMath", "Vector Math", attribute_values={"location": [-157.7106, 193.546], "operation": "DISTANCE"})
        node("ShaderNodeMath", "Math", attribute_values={"location": [64.9711, 30.6791], "operation": "LESS_THAN"})

        link("Group Input", "Coordinate1", "Vector Math", "Vector")
        link("Group Input", "Coordinate2", "Vector Math", "Vector_001")
        link("Group Input", "MaxDist", "Math", "Value_001")
        link("Vector Math", "Value", "Math", "Value")
        link("Math", "Value", "Group Output", "WithinDistance")
        link("Vector Math", "Value", "Group Output", "ActualDistance")

NodeWrapperMpfbWithinDistance = _NodeWrapperMpfbWithinDistance()
