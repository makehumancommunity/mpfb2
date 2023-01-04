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
    "class": "MpfbColorRouter5",
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
            "name": "Threshold1",
            "value_type": "VALUE"
        },
        "Input_10": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_10",
            "name": "Section4Color",
            "value_type": "RGBA"
        },
        "Input_11": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_11",
            "name": "Threshold3",
            "value_type": "VALUE"
        },
        "Input_12": {
            "class": "NodeSocketFloat",
            "default_value": 0.8,
            "identifier": "Input_12",
            "name": "Threshold4",
            "value_type": "VALUE"
        },
        "Input_13": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_13",
            "name": "Section5Color",
            "value_type": "RGBA"
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
        },
        "Input_8": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0007,
                1.0,
                1.0
            ],
            "identifier": "Input_8",
            "name": "Section3Color",
            "value_type": "RGBA"
        },
        "Input_9": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_9",
            "name": "Threshold2",
            "value_type": "VALUE"
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
            "from_socket": "Threshold1",
            "to_node": "Math",
            "to_socket": "Value_001"
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
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Mix.001",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Mix.001",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section3Color",
            "to_node": "Mix.001",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold2",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Mix.001",
            "from_socket": "Result_Color",
            "to_node": "Mix.002",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section4Color",
            "to_node": "Mix.002",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold3",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Mix.002",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Mix.002",
            "from_socket": "Result_Color",
            "to_node": "Mix.003",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Mix.003",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold4",
            "to_node": "Math.003",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section5Color",
            "to_node": "Mix.003",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix.003",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -175.9859,
                    62.7062
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
                    -371.9658,
                    119.5547
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
                "location": [
                    -171.5583,
                    -199.3249
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
                "data_type": "RGBA",
                "location": [
                    103.6562,
                    -19.3167
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Mix.001",
            "name": "Mix.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    112.6146,
                    -358.5883
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    331.3976,
                    -169.5081
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Mix.002",
            "name": "Mix.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    883.7009,
                    -306.3297
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
                    329.2714,
                    -568.2515
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.003",
            "name": "Math.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    570.2239,
                    -399.3313
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Mix.003",
            "name": "Mix.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -664.0698,
                    -246.0766
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

class _NodeWrapperMpfbColorRouter5(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [883.7009, -306.3297]
        nodes["Group Input"].location = [-664.0698, -246.0766]

        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-175.9859, 62.7062]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-371.9658, 119.5547], "operation": "GREATER_THAN"})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-171.5583, -199.3249], "operation": "GREATER_THAN"})
        node("ShaderNodeMix", "Mix.001", attribute_values={"data_type": "RGBA", "location": [103.6562, -19.3167]})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [112.6146, -358.5883], "operation": "GREATER_THAN"})
        node("ShaderNodeMix", "Mix.002", attribute_values={"data_type": "RGBA", "location": [331.3976, -169.5081]})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [329.2714, -568.2515], "operation": "GREATER_THAN"})
        node("ShaderNodeMix", "Mix.003", attribute_values={"data_type": "RGBA", "location": [570.2239, -399.3313]})

        link("Group Input", "Value", "Math", "Value")
        link("Group Input", "Threshold1", "Math", "Value_001")
        link("Group Input", "Section1Color", "Mix", "A_Color")
        link("Group Input", "Section2Color", "Mix", "B_Color")
        link("Group Input", "Section3Color", "Mix.001", "B_Color")
        link("Group Input", "Value", "Math.001", "Value")
        link("Group Input", "Threshold2", "Math.001", "Value_001")
        link("Group Input", "Section4Color", "Mix.002", "B_Color")
        link("Group Input", "Value", "Math.002", "Value")
        link("Group Input", "Threshold3", "Math.002", "Value_001")
        link("Group Input", "Value", "Math.003", "Value")
        link("Group Input", "Threshold4", "Math.003", "Value_001")
        link("Group Input", "Section5Color", "Mix.003", "B_Color")
        link("Math", "Value", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Mix.001", "A_Color")
        link("Math.001", "Value", "Mix.001", "Factor_Float")
        link("Mix.001", "Result_Color", "Mix.002", "A_Color")
        link("Math.002", "Value", "Mix.002", "Factor_Float")
        link("Mix.002", "Result_Color", "Mix.003", "A_Color")
        link("Math.003", "Value", "Mix.003", "Factor_Float")
        link("Mix.003", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbColorRouter5 = _NodeWrapperMpfbColorRouter5()
