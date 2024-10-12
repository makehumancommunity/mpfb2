import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbAlphaMixer",
    "inputs": {
        "Input_Socket_BackgroundColor": {
            "name": "BackgroundColor",
            "identifier": "Socket_7",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ]
        },
        "Input_Socket_UpperLayerColor": {
            "name": "UpperLayerColor",
            "identifier": "Socket_3",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_Socket_UpperLayerAlpha": {
            "name": "UpperLayerAlpha",
            "identifier": "Socket_5",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_LowerLayerColor": {
            "name": "LowerLayerColor",
            "identifier": "Socket_4",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_Socket_LowerLayerAlpha": {
            "name": "LowerLayerAlpha",
            "identifier": "Socket_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_Socket_ResultingColor": {
            "name": "ResultingColor",
            "identifier": "Socket_8",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ]
        },
        "Output_Socket_ResultingAlpha": {
            "name": "ResultingAlpha",
            "identifier": "Socket_9",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0
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
                -470.1089,
                830.6763
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
            "value": 359.7994
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "ResultingAlpha"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LowerLayerAlpha",
            "to_node": "LowerLayerBackground",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BackgroundColor",
            "to_node": "LowerLayerBackground",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LowerLayerColor",
            "to_node": "LowerLayerBackground",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UpperLayerColor",
            "to_node": "UpperLayerAlpha",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UpperLayerAlpha",
            "to_node": "UpperLayerAlpha",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UpperLayerAlpha",
            "to_node": "UpperLowerLayer",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "UpperLowerLayer",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "ResultingColor"
        },
        {
            "from_node": "LowerLayerBackground",
            "from_socket": "Result_Color",
            "to_node": "UpperLowerLayer",
            "to_socket": "A_Color"
        },
        {
            "from_node": "UpperLayerAlpha",
            "from_socket": "Result_Color",
            "to_node": "UpperLowerLayer",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UpperLayerAlpha",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LowerLayerAlpha",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "BackgroundColor",
            "to_node": "UpperLayerBackground",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LowerLayerColor",
            "to_node": "UpperLayerBackground",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LowerLayerAlpha",
            "to_node": "UpperLayerBackground",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "UpperLayerBackground",
            "from_socket": "Result_Color",
            "to_node": "UpperLayerAlpha",
            "to_socket": "A_Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    541.6492,
                    60.4625
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
                    -758.4173,
                    111.93
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -213.2941,
                    32.4271
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "B_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            },
            "label": "Lower layer background",
            "name": "LowerLayerBackground",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    240.4412,
                    29.344
                ],
                "use_clamp": true
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
                    239.0526,
                    324.0063
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "B_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            },
            "label": "Upper vs lower layer",
            "name": "UpperLowerLayer",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -114.4676,
                    379.7975
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "B_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            },
            "label": "Upper layer alpha",
            "name": "UpperLayerAlpha",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -455.638,
                    395.9911
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "B_Rotation": [
                    0.0,
                    0.0,
                    0.0
                ]
            },
            "label": "Upper layer background",
            "name": "UpperLayerBackground",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbAlphaMixer(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [541.6492, 60.4625]
        nodes["Group Input"].location = [-758.4173, 111.93]

        node("ShaderNodeMix", "LowerLayerBackground", label="Lower layer background", attribute_values={"data_type": "RGBA", "location": [-213.2941, 32.4271]}, input_socket_values={"A_Rotation": [0.0, 0.0, 0.0], "B_Rotation": [0.0, 0.0, 0.0]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [240.4412, 29.344], "use_clamp": True})
        node("ShaderNodeMix", "UpperLowerLayer", label="Upper vs lower layer", attribute_values={"data_type": "RGBA", "location": [239.0526, 324.0063]}, input_socket_values={"A_Rotation": [0.0, 0.0, 0.0], "B_Rotation": [0.0, 0.0, 0.0]})
        node("ShaderNodeMix", "UpperLayerAlpha", label="Upper layer alpha", attribute_values={"data_type": "RGBA", "location": [-114.4676, 379.7975]}, input_socket_values={"A_Rotation": [0.0, 0.0, 0.0], "B_Rotation": [0.0, 0.0, 0.0]})
        node("ShaderNodeMix", "UpperLayerBackground", label="Upper layer background", attribute_values={"data_type": "RGBA", "location": [-455.638, 395.9911]}, input_socket_values={"A_Rotation": [0.0, 0.0, 0.0], "B_Rotation": [0.0, 0.0, 0.0]})

        link("Group Input", "LowerLayerAlpha", "LowerLayerBackground", "Factor_Float")
        link("Group Input", "BackgroundColor", "LowerLayerBackground", "A_Color")
        link("Group Input", "LowerLayerColor", "LowerLayerBackground", "B_Color")
        link("Group Input", "UpperLayerColor", "UpperLayerAlpha", "B_Color")
        link("Group Input", "UpperLayerAlpha", "UpperLayerAlpha", "Factor_Float")
        link("Group Input", "UpperLayerAlpha", "UpperLowerLayer", "Factor_Float")
        link("Group Input", "UpperLayerAlpha", "Math", "Value")
        link("Group Input", "LowerLayerAlpha", "Math", "Value_001")
        link("Group Input", "BackgroundColor", "UpperLayerBackground", "A_Color")
        link("Group Input", "LowerLayerColor", "UpperLayerBackground", "B_Color")
        link("Group Input", "LowerLayerAlpha", "UpperLayerBackground", "Factor_Float")
        link("LowerLayerBackground", "Result_Color", "UpperLowerLayer", "A_Color")
        link("UpperLayerAlpha", "Result_Color", "UpperLowerLayer", "B_Color")
        link("UpperLayerBackground", "Result_Color", "UpperLayerAlpha", "A_Color")
        link("Math", "Value", "Group Output", "ResultingAlpha")
        link("UpperLowerLayer", "Result_Color", "Group Output", "ResultingColor")

NodeWrapperMpfbAlphaMixer = _NodeWrapperMpfbAlphaMixer()
