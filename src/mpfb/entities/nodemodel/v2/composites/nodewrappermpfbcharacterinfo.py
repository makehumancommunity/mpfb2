import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbCharacterInfo",
    "inputs": {},
    "outputs": {
        "Output_0": {
            "name": "scale_factor",
            "identifier": "Output_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_1": {
            "name": "gender",
            "identifier": "Output_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_2": {
            "name": "age",
            "identifier": "Output_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_3": {
            "name": "height",
            "identifier": "Output_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_4": {
            "name": "weight",
            "identifier": "Output_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_5": {
            "name": "muscle",
            "identifier": "Output_5",
            "class": "NodeSocketFloat",
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
                -805.7254,
                212.348
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
            "value": 140.0
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
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_GEN_scale_factor",
                "attribute_type": "OBJECT",
                "location": [
                    -144.103,
                    537.266
                ]
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
                    -144.103,
                    352.801
                ]
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
                    -200.593
                ]
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "weight",
            "name": "weight",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "attribute_name": "MPFB_HUM_muscle",
                "attribute_type": "OBJECT",
                "location": [
                    -142.088,
                    -390.097
                ]
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
                    -143.095,
                    169.345
                ]
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
                    -140.072,
                    -15.12
                ]
            },
            "class": "ShaderNodeAttribute",
            "input_socket_values": {},
            "label": "height",
            "name": "height",
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

        node("ShaderNodeAttribute", "scale_factor", attribute_values={"attribute_name": "MPFB_GEN_scale_factor", "attribute_type": "OBJECT", "location": [-144.103, 537.266]})
        node("ShaderNodeAttribute", "gender", attribute_values={"attribute_name": "MPFB_HUM_gender", "attribute_type": "OBJECT", "location": [-144.103, 352.801]})
        node("ShaderNodeAttribute", "weight", attribute_values={"attribute_name": "MPFB_HUM_weight", "attribute_type": "OBJECT", "location": [-144.103, -200.593]})
        node("ShaderNodeAttribute", "muscle", attribute_values={"attribute_name": "MPFB_HUM_muscle", "attribute_type": "OBJECT", "location": [-142.088, -390.097]})
        node("ShaderNodeAttribute", "age", attribute_values={"attribute_name": "MPFB_HUM_age", "attribute_type": "OBJECT", "location": [-143.095, 169.345]})
        node("ShaderNodeAttribute", "height", attribute_values={"attribute_name": "MPFB_HUM_height", "attribute_type": "OBJECT", "location": [-140.072, -15.12]})

        link("scale_factor", "Fac", "Group Output", "scale_factor")
        link("gender", "Fac", "Group Output", "gender")
        link("age", "Fac", "Group Output", "age")
        link("height", "Fac", "Group Output", "height")
        link("weight", "Fac", "Group Output", "weight")
        link("muscle", "Fac", "Group Output", "muscle")

NodeWrapperMpfbCharacterInfo = _NodeWrapperMpfbCharacterInfo()
