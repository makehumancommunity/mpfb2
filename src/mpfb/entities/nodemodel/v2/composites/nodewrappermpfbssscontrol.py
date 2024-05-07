import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSSSControl",
    "inputs": {
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSScaleMultiplier": {
            "name": "SSSScaleMultiplier",
            "identifier": "Socket_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.001,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_SSSRadius": {
            "name": "SSSRadius",
            "identifier": "Socket_8",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_Socket_SSSScale": {
            "name": "SSSScale",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4
        },
        "Output_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_14",
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
                0.4,
                0.4,
                0.5
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
                330.434,
                97.355
            ]
        },
        "use_custom_color": {
            "name": "use_custom_color",
            "class": "bool",
            "value": true
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
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "Combine XYZ.001",
            "to_socket": "X"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "Combine XYZ.001",
            "to_socket": "Y"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "Combine XYZ.001",
            "to_socket": "Z"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSWeight",
            "to_node": "Group Output",
            "to_socket": "SSSWeight"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "Group Output",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Combine XYZ.001",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "SSSRadius"
        },
        {
            "from_node": "Group.003",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSScaleMultiplier",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Group Output",
            "to_socket": "SSSScale"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSAnisotropy",
            "to_node": "Group Output",
            "to_socket": "SSSAnisotropy"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -794.27,
                    296.3641
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Group.003",
            "name": "Group.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -282.2525,
                    248.0846
                ],
                "operation": "MULTIPLY"
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
                    -283.4263,
                    -287.7945
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 1.0,
                "Y": 0.2,
                "Z": 0.1
            },
            "label": "Combine XYZ.001",
            "name": "Combine XYZ.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    299.8103,
                    14.135
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
                    -821.2342,
                    -3.7404
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

class _NodeWrapperMpfbSSSControl(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [299.8103, 14.135]
        nodes["Group Input"].location = [-821.2342, -3.7404]

        node("MpfbCharacterInfo", "Group.003", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-794.27, 296.3641], "use_custom_color": True, "width": 140.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-282.2525, 248.0846], "operation": "MULTIPLY"})
        node("ShaderNodeCombineXYZ", "Combine XYZ.001", attribute_values={"location": [-283.4263, -287.7945]}, input_socket_values={"X": 1.0, "Y": 0.2, "Z": 0.1})

        link("Group Input", "SSSRadiusX", "Combine XYZ.001", "X")
        link("Group Input", "SSSRadiusY", "Combine XYZ.001", "Y")
        link("Group Input", "SSSRadiusZ", "Combine XYZ.001", "Z")
        link("Group Input", "SSSWeight", "Group Output", "SSSWeight")
        link("Group Input", "SSSIor", "Group Output", "SSSIor")
        link("Group Input", "SSSScaleMultiplier", "Math", "Value_001")
        link("Group Input", "SSSAnisotropy", "Group Output", "SSSAnisotropy")
        link("Group.003", "scale_factor", "Math", "Value")
        link("Group Input", "SSSWeight", "Group Output", "SSSWeight")
        link("Group Input", "SSSIor", "Group Output", "SSSIor")
        link("Combine XYZ.001", "Vector", "Group Output", "SSSRadius")
        link("Math", "Value", "Group Output", "SSSScale")
        link("Group Input", "SSSAnisotropy", "Group Output", "SSSAnisotropy")

NodeWrapperMpfbSSSControl = _NodeWrapperMpfbSSSControl()
