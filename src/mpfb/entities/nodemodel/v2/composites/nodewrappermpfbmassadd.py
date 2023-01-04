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
                -297.803,
                170.5456
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
    "class": "MpfbMassAdd",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_0",
            "name": "Value1",
            "value_type": "VALUE"
        },
        "Input_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_1",
            "name": "Value2",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_2",
            "name": "Value3",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_3",
            "name": "Value4",
            "value_type": "VALUE"
        },
        "Input_4": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_4",
            "name": "Value5",
            "value_type": "VALUE"
        },
        "Input_6": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_6",
            "name": "Value6",
            "value_type": "VALUE"
        },
        "Input_7": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_7",
            "name": "Value7",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_5",
            "name": "Sum",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Value1",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value2",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value3",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value4",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value5",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
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
            "from_node": "Math.006",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "Sum"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value6",
            "to_node": "Math.005",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value7",
            "to_node": "Math.006",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -551.3284,
                    251.326
                ]
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
                    -371.0575,
                    196.3447
                ]
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
                    -188.9339,
                    137.7794
                ]
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
                    -6.9791,
                    79.0685
                ]
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
                    177.5821,
                    20.3275
                ]
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
                    356.5507,
                    -44.9403
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
                    588.4963,
                    -45.0581
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
                    -795.1385,
                    119.0437
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

class _NodeWrapperMpfbMassAdd(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [588.4963, -45.0581]
        nodes["Group Input"].location = [-795.1385, 119.0437]

        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-551.3284, 251.326]})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-371.0575, 196.3447]})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [-188.9339, 137.7794]})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [-6.9791, 79.0685]})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [177.5821, 20.3275]})
        node("ShaderNodeMath", "Math.006", attribute_values={"location": [356.5507, -44.9403]})

        link("Group Input", "Value1", "Math.001", "Value")
        link("Group Input", "Value2", "Math.001", "Value_001")
        link("Group Input", "Value3", "Math.002", "Value_001")
        link("Group Input", "Value4", "Math.003", "Value_001")
        link("Group Input", "Value5", "Math.004", "Value_001")
        link("Group Input", "Value6", "Math.005", "Value_001")
        link("Group Input", "Value7", "Math.006", "Value_001")
        link("Math.001", "Value", "Math.002", "Value")
        link("Math.002", "Value", "Math.003", "Value")
        link("Math.003", "Value", "Math.004", "Value")
        link("Math.004", "Value", "Math.005", "Value")
        link("Math.005", "Value", "Math.006", "Value")
        link("Math.006", "Value", "Group Output", "Sum")

NodeWrapperMpfbMassAdd = _NodeWrapperMpfbMassAdd()
