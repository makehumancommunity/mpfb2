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
                -32.0294,
                393.0536
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
            "value": 265.8835
        }
    },
    "class": "MpfbColorRouter2",
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
            "name": "Threshold",
            "value_type": "VALUE"
        },
        "Input_6": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.0,
                0.0011,
                1.0
            ],
            "identifier": "Input_6",
            "name": "Section1Color",
            "value_type": "RGBA"
        },
        "Input_7": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                1.0,
                0.0012,
                1.0
            ],
            "identifier": "Input_7",
            "name": "Section2Color",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Output_5": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_5",
            "name": "Color",
            "value_type": "RGBA"
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
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Color",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section2Color",
            "to_node": "Mix",
            "to_socket": "B_Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    345.2334,
                    -122.9751
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
                    -111.9022,
                    18.8559
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    109.2451,
                    -89.2745
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -383.4491,
                    -122.9751
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

class _NodeWrapperMpfbColorRouter2(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [345.2334, -122.9751]
        nodes["Group Input"].location = [-383.4491, -122.9751]

        node("ShaderNodeMath", "Math", attribute_values={"location": [-111.9022, 18.8559], "operation": "GREATER_THAN"})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [109.2451, -89.2745]})

        link("Group Input", "Value", "Math", "Value")
        link("Group Input", "Threshold", "Math", "Value_001")
        link("Group Input", "Section1Color", "Mix", "A_Color")
        link("Group Input", "Section2Color", "Mix", "B_Color")
        link("Math", "Value", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbColorRouter2 = _NodeWrapperMpfbColorRouter2()
