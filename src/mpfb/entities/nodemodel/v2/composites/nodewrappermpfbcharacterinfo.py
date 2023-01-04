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
                -843.0322,
                412.9678
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
    "class": "MpfbCharacterInfo",
    "inputs": {},
    "outputs": {
        "Output_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_0",
            "name": "scale_factor",
            "value_type": "VALUE"
        },
        "Output_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_1",
            "name": "gender",
            "value_type": "VALUE"
        },
        "Output_2": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_2",
            "name": "age",
            "value_type": "VALUE"
        },
        "Output_3": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_3",
            "name": "height",
            "value_type": "VALUE"
        },
        "Output_4": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_4",
            "name": "weight",
            "value_type": "VALUE"
        },
        "Output_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_5",
            "name": "muscle",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "scale_factor",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "scale_factor"
        },
        {
            "from_node": "gender",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "gender"
        },
        {
            "from_node": "age",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "age"
        },
        {
            "from_node": "height",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "height"
        },
        {
            "from_node": "weight",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "weight"
        },
        {
            "from_node": "muscle",
            "from_socket": "Fac",
            "to_node": "Group Output",
            "to_socket": "muscle"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "attribute_name": "MPFB_GEN_scale_factor",
                "attribute_type": "OBJECT",
                "location": [
                    -144.1031,
                    537.2661
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "scale_factor",
            "name": "scale_factor",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_HUM_gender",
                "attribute_type": "OBJECT",
                "location": [
                    -144.1031,
                    352.8013
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "gender",
            "name": "gender",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_HUM_weight",
                "attribute_type": "OBJECT",
                "location": [
                    -144.103,
                    -200.5927
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "weight",
            "name": "weight",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -344.1031,
                    73.5843
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
                "attribute_name": "MPFB_HUM_muscle",
                "attribute_type": "OBJECT",
                "location": [
                    -142.0875,
                    -390.0974
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "muscle",
            "name": "muscle",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_HUM_age",
                "attribute_type": "OBJECT",
                "location": [
                    -143.0953,
                    169.3447
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "age",
            "name": "age",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_HUM_height",
                "attribute_type": "OBJECT",
                "location": [
                    -140.0721,
                    -15.12
                ],
                "width": 294.1801
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "height",
            "name": "height",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    380.4579,
                    83.6644
                ]
            },
            "class": "NodeGroupOutput",
            "input_socket_values": {},
            "label": "Group Output",
            "name": "Group Output",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbCharacterInfo(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-344.1031, 73.5843]
        nodes["Group Output"].location = [380.4579, 83.6644]

        node("ShaderNodeAttribute", "scale_factor", attribute_values={"attribute_name": "MPFB_GEN_scale_factor", "attribute_type": "OBJECT", "location": [-144.1031, 537.2661], "width": 294.1801})
        node("ShaderNodeAttribute", "gender", attribute_values={"attribute_name": "MPFB_HUM_gender", "attribute_type": "OBJECT", "location": [-144.1031, 352.8013], "width": 294.1801})
        node("ShaderNodeAttribute", "weight", attribute_values={"attribute_name": "MPFB_HUM_weight", "attribute_type": "OBJECT", "location": [-144.103, -200.5927], "width": 294.1801})
        node("ShaderNodeAttribute", "muscle", attribute_values={"attribute_name": "MPFB_HUM_muscle", "attribute_type": "OBJECT", "location": [-142.0875, -390.0974], "width": 294.1801})
        node("ShaderNodeAttribute", "age", attribute_values={"attribute_name": "MPFB_HUM_age", "attribute_type": "OBJECT", "location": [-143.0953, 169.3447], "width": 294.1801})
        node("ShaderNodeAttribute", "height", attribute_values={"attribute_name": "MPFB_HUM_height", "attribute_type": "OBJECT", "location": [-140.0721, -15.12], "width": 294.1801})

        link("scale_factor", "Fac", "Group Output", "scale_factor")
        link("gender", "Fac", "Group Output", "gender")
        link("age", "Fac", "Group Output", "age")
        link("height", "Fac", "Group Output", "height")
        link("weight", "Fac", "Group Output", "weight")
        link("muscle", "Fac", "Group Output", "muscle")

NodeWrapperMpfbCharacterInfo = _NodeWrapperMpfbCharacterInfo()
