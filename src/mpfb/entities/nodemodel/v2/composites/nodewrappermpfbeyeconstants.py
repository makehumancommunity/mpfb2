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
                -665.9365,
                -167.7792
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
    "class": "MpfbEyeConstants",
    "inputs": {},
    "outputs": {
        "Output_0": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_0",
            "name": "Left eye coord",
            "value_type": "VECTOR"
        },
        "Output_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Right eye coord",
            "value_type": "VECTOR"
        },
        "Output_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_2",
            "name": "Eyeball size",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "LeftEye",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "Left eye coord"
        },
        {
            "from_node": "RightEye",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "Right eye coord"
        },
        {
            "from_node": "EyeballSize",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "Eyeball size"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -529.988,
                    78.6233
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
                "location": [
                    146.07,
                    110.879
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
                    -238.2518,
                    108.771
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.705,
                "Y": 0.7
            },
            "label": "RightEye",
            "name": "RightEye",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -238.9953,
                    244.33
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.295,
                "Y": 0.3
            },
            "label": "LeftEye",
            "name": "LeftEye",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -239.6429,
                    -26.8051
                ]
            },
            "class": "ShaderNodeValue",
            "input_socket_values": {},
            "label": "EyeballSize",
            "name": "EyeballSize",
            "output_socket_values": {
                "Value": 0.285
            }
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbEyeConstants(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-529.988, 78.6233]
        nodes["Group Output"].location = [146.07, 110.879]

        node("ShaderNodeCombineXYZ", "RightEye", attribute_values={"location": [-238.2518, 108.771]}, input_socket_values={"X": 0.705, "Y": 0.7})
        node("ShaderNodeCombineXYZ", "LeftEye", attribute_values={"location": [-238.9953, 244.33]}, input_socket_values={"X": 0.295, "Y": 0.3})
        node("ShaderNodeValue", "EyeballSize", attribute_values={"location": [-239.6429, -26.8051]}, output_socket_values={"Value": 0.285})

        link("LeftEye", "Vector", "Group Output", "Left eye coord")
        link("RightEye", "Vector", "Group Output", "Right eye coord")
        link("EyeballSize", "Value", "Group Output", "Eyeball size")

NodeWrapperMpfbEyeConstants = _NodeWrapperMpfbEyeConstants()
