import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSSSControl",
    "inputs": {
        "Input_6": {
            "name": "SubsurfaceColor",
            "identifier": "Input_6",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_5": {
            "name": "SubsurfaceStrength",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_4": {
            "name": "SubsurfaceRadiusMultiplyer",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_8": {
            "name": "SubSurfaceRadiusX",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_9": {
            "name": "SubSurfaceRadiusY",
            "identifier": "Input_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_10": {
            "name": "SubSurfaceRadiusZ",
            "identifier": "Input_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_7": {
            "name": "SubsurfaceIor",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        }
    },
    "outputs": {
        "Output_2": {
            "name": "SubsurfaceColor",
            "identifier": "Output_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Output_0": {
            "name": "SubsurfaceRadius",
            "identifier": "Output_0",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_1": {
            "name": "SubsurfaceStrength",
            "identifier": "Output_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_3": {
            "name": "SubsurfaceIor",
            "identifier": "Output_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4
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
                348.2335,
                172.3807
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
            "from_node": "Vector Math",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceRadius"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Combine XYZ",
            "to_socket": "X"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Combine XYZ",
            "to_socket": "Y"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Combine XYZ",
            "to_socket": "Z"
        },
        {
            "from_node": "Combine XYZ",
            "from_socket": "Vector",
            "to_node": "Vector Math",
            "to_socket": "Vector_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceRadiusMultiplyer",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceColor",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubsurfaceIor",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceIor"
        },
        {
            "from_node": "Group.003",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Combine XYZ.001",
            "from_socket": "Vector",
            "to_node": "Vector Math",
            "to_socket": "Vector"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusX",
            "to_node": "Combine XYZ.001",
            "to_socket": "X"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusY",
            "to_node": "Combine XYZ.001",
            "to_socket": "Y"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SubSurfaceRadiusZ",
            "to_node": "Combine XYZ.001",
            "to_socket": "Z"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "color": [
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -794.27,
                    296.3641
                ],
                "use_custom_color": false,
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
                    -265.9958,
                    338.3492
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {},
            "label": "Combine XYZ",
            "name": "Combine XYZ",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -525.0374,
                    296.8846
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
                    -264.3076,
                    164.0919
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
                    11.9186,
                    222.8446
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {
                "Vector": [
                    1.0,
                    0.2,
                    0.1
                ]
            },
            "label": "Vector Math",
            "name": "Vector Math",
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

        node("MpfbCharacterInfo", "Group.003", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-794.27, 296.3641], "use_custom_color": False, "width": 140.0})
        node("ShaderNodeCombineXYZ", "Combine XYZ", attribute_values={"location": [-265.9958, 338.3492]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-525.0374, 296.8846], "operation": "MULTIPLY"})
        node("ShaderNodeCombineXYZ", "Combine XYZ.001", attribute_values={"location": [-264.3076, 164.0919]}, input_socket_values={"X": 1.0, "Y": 0.2, "Z": 0.1})
        node("ShaderNodeVectorMath", "Vector Math", attribute_values={"location": [11.9186, 222.8446], "operation": "MULTIPLY"}, input_socket_values={"Vector": [1.0, 0.2, 0.1]})

        link("Group Input", "SubsurfaceRadiusMultiplyer", "Math", "Value_001")
        link("Group Input", "SubsurfaceStrength", "Group Output", "SubsurfaceStrength")
        link("Group Input", "SubsurfaceColor", "Group Output", "SubsurfaceColor")
        link("Group Input", "SubsurfaceIor", "Group Output", "SubsurfaceIor")
        link("Group Input", "SubSurfaceRadiusX", "Combine XYZ.001", "X")
        link("Group Input", "SubSurfaceRadiusY", "Combine XYZ.001", "Y")
        link("Group Input", "SubSurfaceRadiusZ", "Combine XYZ.001", "Z")
        link("Math", "Value", "Combine XYZ", "X")
        link("Math", "Value", "Combine XYZ", "Y")
        link("Math", "Value", "Combine XYZ", "Z")
        link("Combine XYZ", "Vector", "Vector Math", "Vector_001")
        link("Group.003", "scale_factor", "Math", "Value")
        link("Combine XYZ.001", "Vector", "Vector Math", "Vector")
        link("Vector Math", "Vector", "Group Output", "SubsurfaceRadius")
        link("Group Input", "SubsurfaceStrength", "Group Output", "SubsurfaceStrength")
        link("Group Input", "SubsurfaceColor", "Group Output", "SubsurfaceColor")
        link("Group Input", "SubsurfaceIor", "Group Output", "SubsurfaceIor")

NodeWrapperMpfbSSSControl = _NodeWrapperMpfbSSSControl()
