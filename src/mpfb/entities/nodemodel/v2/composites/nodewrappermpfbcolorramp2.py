import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbColorRamp2",
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
            "default_value": 0.5,
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
            "from_node": "Mix.001",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Mix.001",
            "to_socket": "A_Color"
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
            "from_socket": "OneStopColor",
            "to_node": "Mix.001",
            "to_socket": "B_Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -171.1683,
                    303.2997
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
                "data_type": "RGBA",
                "location": [
                    123.5509,
                    267.4574
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
                "location": [
                    -494.8572,
                    44.6982
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

class _NodeWrapperMpfbColorRamp2(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [353.2497, 140.1127]
        nodes["Group Input"].location = [-878.1918, 154.2248]

        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-171.1683, 303.2997]})
        node("ShaderNodeMix", "Mix.001", attribute_values={"data_type": "RGBA", "location": [123.5509, 267.4574]})
        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-497.6537, 420.4658]})
        node("ShaderNodeMapRange", "Map Range.001", attribute_values={"location": [-494.8572, 44.6982]})

        link("Group Input", "Value", "Map Range", "Value")
        link("Group Input", "BetweenStep1Pos", "Map Range", "From Max")
        link("Group Input", "ZeroStopColor", "Mix", "A_Color")
        link("Group Input", "BetweenStep1Color", "Mix", "B_Color")
        link("Group Input", "BetweenStep1Pos", "Map Range.001", "From Min")
        link("Group Input", "Value", "Map Range.001", "Value")
        link("Group Input", "OneStopColor", "Mix.001", "B_Color")
        link("Map Range", "Result", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Mix.001", "A_Color")
        link("Map Range.001", "Result", "Mix.001", "Factor_Float")
        link("Mix.001", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbColorRamp2 = _NodeWrapperMpfbColorRamp2()
