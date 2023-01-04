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
                -336.9789,
                585.7422
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
            "value": 400.0
        }
    },
    "class": "MpfbColorRamp4",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_0",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Input_10": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0016,
                1.0,
                0.0,
                1.0
            ],
            "identifier": "Input_10",
            "name": "BetweenStep1Color",
            "value_type": "RGBA"
        },
        "Input_11": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0041,
                0.0,
                1.0,
                1.0
            ],
            "identifier": "Input_11",
            "name": "OneStopColor",
            "value_type": "RGBA"
        },
        "Input_12": {
            "class": "NodeSocketFloat",
            "default_value": 0.25,
            "identifier": "Input_12",
            "name": "BetweenStep1Pos",
            "value_type": "VALUE"
        },
        "Input_13": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_13",
            "name": "BetweenStep2Pos",
            "value_type": "VALUE"
        },
        "Input_14": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.0,
                1.0,
                1.0
            ],
            "identifier": "Input_14",
            "name": "BetweenStep2Color",
            "value_type": "RGBA"
        },
        "Input_15": {
            "class": "NodeSocketFloat",
            "default_value": 0.75,
            "identifier": "Input_15",
            "name": "BetweenStep3Pos",
            "value_type": "VALUE"
        },
        "Input_16": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                1.0,
                1.0,
                1.0
            ],
            "identifier": "Input_16",
            "name": "BetweenStep3Color",
            "value_type": "RGBA"
        },
        "Input_9": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.0003,
                0.0,
                1.0
            ],
            "identifier": "Input_9",
            "name": "ZeroStopColor",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Output_8": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_8",
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
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep1Pos",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep1Pos",
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
            "from_node": "Map Range.001",
            "from_socket": "Result",
            "to_node": "Mix.001",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep2Pos",
            "to_node": "Map Range.001",
            "to_socket": "From Max"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Mix.001",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ZeroStopColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep1Color",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep2Color",
            "to_node": "Mix.001",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix.001",
            "from_socket": "Result_Color",
            "to_node": "Mix.002",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Map Range.002",
            "from_socket": "Result",
            "to_node": "Mix.002",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep2Pos",
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
            "from_socket": "BetweenStep3Pos",
            "to_node": "Map Range.002",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep3Pos",
            "to_node": "Map Range.003",
            "to_socket": "From Min"
        },
        {
            "from_node": "Mix.002",
            "from_socket": "Result_Color",
            "to_node": "Mix.003",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BetweenStep3Color",
            "to_node": "Mix.002",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OneStopColor",
            "to_node": "Mix.003",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Map Range.003",
            "from_socket": "Result",
            "to_node": "Mix.003",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Mix.003",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Map Range.003",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -497.6537,
                    420.4658
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
                "data_type": "RGBA",
                "location": [
                    -177.6934,
                    331.2724
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
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -498.5858,
                    46.5631
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
                "data_type": "RGBA",
                "location": [
                    54.5713,
                    78.1749
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ],
                "B_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            },
            "label": "Mix.001",
            "name": "Mix.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -498.5858,
                    -252.7457
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
                    -503.2466,
                    -534.3383
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range.003",
            "name": "Map Range.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    820.2605,
                    -59.4265
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
                "data_type": "RGBA",
                "location": [
                    288.5428,
                    -127.8912
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ],
                "B_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            },
            "label": "Mix.002",
            "name": "Mix.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    525.3107,
                    -305.9845
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ],
                "B_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ]
            },
            "label": "Mix.003",
            "name": "Mix.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -910.8173,
                    26.4824
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

class _NodeWrapperMpfbColorRamp4(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [820.2605, -59.4265]
        nodes["Group Input"].location = [-910.8173, 26.4824]

        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-497.6537, 420.4658]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-177.6934, 331.2724]}, input_socket_values={"A_Color": [0.0, 0.0, 0.0, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-498.5858, 46.5631]})
        node("ShaderNodeMix", "Mix.001", attribute_values={"data_type": "RGBA", "location": [54.5713, 78.1749]}, input_socket_values={"A_Color": [1.0, 1.0, 1.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0]})
        node("ShaderNodeMapRange", "Map Range.002", attribute_values={"location": [-498.5858, -252.7457]})
        node("ShaderNodeMapRange", "Map Range.003", attribute_values={"location": [-503.2466, -534.3383]})
        node("ShaderNodeMix", "Mix.002", attribute_values={"data_type": "RGBA", "location": [288.5428, -127.8912]}, input_socket_values={"A_Color": [1.0, 1.0, 1.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0]})
        node("ShaderNodeMix", "Mix.003", attribute_values={"data_type": "RGBA", "location": [525.3107, -305.9845]}, input_socket_values={"A_Color": [1.0, 1.0, 1.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0]})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "BetweenStep1Pos", "Map Range", "From Max")
        link("Group Input", "BetweenStep1Pos", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Group Input", "BetweenStep2Pos", "Map Range.001", "From Max")
        link("Group Input", "ZeroStopColor", "Mix", "A_Color")
        link("Group Input", "BetweenStep1Color", "Mix", "B_Color")
        link("Group Input", "BetweenStep2Color", "Mix.001", "B_Color")
        link("Group Input", "BetweenStep2Pos", "Map Range.002", "From Min")
        link("Group Input", "Value", "Map Range.002", "Value")
        link("Group Input", "BetweenStep3Pos", "Map Range.002", "From Max")
        link("Group Input", "BetweenStep3Pos", "Map Range.003", "From Min")
        link("Group Input", "BetweenStep3Color", "Mix.002", "B_Color")
        link("Group Input", "OneStopColor", "Mix.003", "B_Color")
        link("Group Input", "Value", "Map Range.003", "Value")
        link("Map Range", "Result", "Mix", "Factor_Float")
        link("Map Range.001", "Result", "Mix.001", "Factor_Float")
        link("Mix", "Result_Color", "Mix.001", "A_Color")
        link("Mix.001", "Result_Color", "Mix.002", "A_Color")
        link("Map Range.002", "Result", "Mix.002", "Factor_Float")
        link("Mix.002", "Result_Color", "Mix.003", "A_Color")
        link("Map Range.003", "Result", "Mix.003", "Factor_Float")
        link("Mix.003", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbColorRamp4 = _NodeWrapperMpfbColorRamp4()
