import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbColorRamp3",
    "inputs": {
        "Input_0": {
            "name": "Value",
            "identifier": "Input_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_9": {
            "name": "ZeroStopColor",
            "identifier": "Input_9",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.0003,
                0.0,
                1.0
            ]
        },
        "Input_10": {
            "name": "BetweenStep1Color",
            "identifier": "Input_10",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0016,
                1.0,
                0.0,
                1.0
            ]
        },
        "Input_14": {
            "name": "BetweenStep2Color",
            "identifier": "Input_14",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.0,
                1.0,
                1.0
            ]
        },
        "Input_11": {
            "name": "OneStopColor",
            "identifier": "Input_11",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0041,
                0.0,
                1.0,
                1.0
            ]
        },
        "Input_12": {
            "name": "BetweenStep1Pos",
            "identifier": "Input_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.33,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_13": {
            "name": "BetweenStep2Pos",
            "identifier": "Input_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.66,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_8": {
            "name": "Color",
            "identifier": "Output_8",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
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
                -336.9789,
                585.7422
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
            "value": 400.0
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
            "from_socket": "OneStopColor",
            "to_node": "Mix.002",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix.002",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
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
                "location": [
                    -499.518,
                    -234.0972
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
                    557.3922,
                    58.9916
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

class _NodeWrapperMpfbColorRamp3(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [557.3922, 58.9916]
        nodes["Group Input"].location = [-910.8173, 26.4824]

        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-497.6537, 420.4658]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-177.6934, 331.2724]}, input_socket_values={"A_Color": [0.0, 0.0, 0.0, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-498.5858, 46.5631]})
        node("ShaderNodeMapRange", "Map Range.002", attribute_values={"location": [-499.518, -234.0972]})
        node("ShaderNodeMix", "Mix.001", attribute_values={"data_type": "RGBA", "location": [54.5713, 78.1749]}, input_socket_values={"A_Color": [1.0, 1.0, 1.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0]})
        node("ShaderNodeMix", "Mix.002", attribute_values={"data_type": "RGBA", "location": [288.5428, -127.8912]}, input_socket_values={"A_Color": [1.0, 1.0, 1.0, 1.0], "B_Color": [0.0, 0.0, 0.0, 1.0]})

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
        link("Group Input", "OneStopColor", "Mix.002", "B_Color")
        link("Map Range", "Result", "Mix", "Factor_Float")
        link("Map Range.001", "Result", "Mix.001", "Factor_Float")
        link("Mix", "Result_Color", "Mix.001", "A_Color")
        link("Mix.001", "Result_Color", "Mix.002", "A_Color")
        link("Map Range.002", "Result", "Mix.002", "Factor_Float")
        link("Mix.002", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbColorRamp3 = _NodeWrapperMpfbColorRamp3()
