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
                -876.2673,
                -13.0458
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
    "class": "MpfbBodyConstants",
    "inputs": {},
    "outputs": {
        "Output_2": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_2",
            "name": "RightNippleCoordinate",
            "value_type": "VECTOR"
        },
        "Output_3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_3",
            "name": "LeftNippleCoordinate",
            "value_type": "VECTOR"
        },
        "Output_4": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_4",
            "name": "NavelCoordinate",
            "value_type": "VECTOR"
        },
        "Output_5": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_5",
            "name": "RightMouthCorner",
            "value_type": "VECTOR"
        },
        "Output_6": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_6",
            "name": "LeftMouthCorner",
            "value_type": "VECTOR"
        },
        "Output_7": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_7",
            "name": "MouthCenter",
            "value_type": "VECTOR"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "RightNipple",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "RightNippleCoordinate"
        },
        {
            "from_node": "LeftNipple",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "LeftNippleCoordinate"
        },
        {
            "from_node": "Navel",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "NavelCoordinate"
        },
        {
            "from_node": "RightMouthCorner",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "RightMouthCorner"
        },
        {
            "from_node": "LeftMouthCorner",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "LeftMouthCorner"
        },
        {
            "from_node": "RightMouthCorner",
            "from_socket": "Vector",
            "to_node": "Separate XYZ",
            "to_socket": "Vector"
        },
        {
            "from_node": "LeftMouthCorner",
            "from_socket": "Vector",
            "to_node": "Separate XYZ.001",
            "to_socket": "Vector"
        },
        {
            "from_node": "Separate XYZ.001",
            "from_socket": "Y",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Separate XYZ",
            "from_socket": "Y",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Separate XYZ",
            "from_socket": "X",
            "to_node": "Combine XYZ",
            "to_socket": "X"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Combine XYZ",
            "to_socket": "Y"
        },
        {
            "from_node": "Combine XYZ",
            "from_socket": "Vector",
            "to_node": "Group Output",
            "to_socket": "MouthCenter"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -854.189,
                    -67.3678
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
                    -677.574,
                    301.1666
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.3252,
                "Y": 0.699
            },
            "label": "RightNipple",
            "name": "RightNipple",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -678.5061,
                    167.5498
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.4358,
                "Y": 0.699
            },
            "label": "LeftNipple",
            "name": "LeftNipple",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -678.4309,
                    30.1713
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.3806,
                "Y": 0.5634
            },
            "label": "Navel",
            "name": "Navel",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -678.8247,
                    -101.1879
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.91,
                "Y": 0.465
            },
            "label": "RightMouthCorner",
            "name": "RightMouthCorner",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -686.282,
                    -230.7953
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 0.91,
                "Y": 0.502
            },
            "label": "LeftMouthCorner",
            "name": "LeftMouthCorner",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -302.9055,
                    -326.138
                ]
            },
            "class": "ShaderNodeSeparateXYZ",
            "input_socket_values": {},
            "label": "Separate XYZ.001",
            "name": "Separate XYZ.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -88.253,
                    -178.9764
                ]
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
                    305.1906,
                    -27.2413
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
                    -301.9734,
                    -180.6793
                ]
            },
            "class": "ShaderNodeSeparateXYZ",
            "input_socket_values": {},
            "label": "Separate XYZ",
            "name": "Separate XYZ",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    105.3512,
                    -169.8206
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 2.0
            },
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    541.3774,
                    219.5866
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

class _NodeWrapperMpfbBodyConstants(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-854.189, -67.3678]
        nodes["Group Output"].location = [541.3774, 219.5866]

        node("ShaderNodeCombineXYZ", "RightNipple", attribute_values={"location": [-677.574, 301.1666]}, input_socket_values={"X": 0.3252, "Y": 0.699})
        node("ShaderNodeCombineXYZ", "LeftNipple", attribute_values={"location": [-678.5061, 167.5498]}, input_socket_values={"X": 0.4358, "Y": 0.699})
        node("ShaderNodeCombineXYZ", "Navel", attribute_values={"location": [-678.4309, 30.1713]}, input_socket_values={"X": 0.3806, "Y": 0.5634})
        node("ShaderNodeCombineXYZ", "RightMouthCorner", attribute_values={"location": [-678.8247, -101.1879]}, input_socket_values={"X": 0.91, "Y": 0.465})
        node("ShaderNodeCombineXYZ", "LeftMouthCorner", attribute_values={"location": [-686.282, -230.7953]}, input_socket_values={"X": 0.91, "Y": 0.502})
        node("ShaderNodeSeparateXYZ", "Separate XYZ.001", attribute_values={"location": [-302.9055, -326.138]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-88.253, -178.9764]})
        node("ShaderNodeCombineXYZ", "Combine XYZ", attribute_values={"location": [305.1906, -27.2413]})
        node("ShaderNodeSeparateXYZ", "Separate XYZ", attribute_values={"location": [-301.9734, -180.6793]})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [105.3512, -169.8206], "operation": "DIVIDE"}, input_socket_values={"Value_001": 2.0})

        link("RightMouthCorner", "Vector", "Separate XYZ", "Vector")
        link("LeftMouthCorner", "Vector", "Separate XYZ.001", "Vector")
        link("Separate XYZ.001", "Y", "Math", "Value_001")
        link("Separate XYZ", "Y", "Math", "Value")
        link("Math", "Value", "Math.001", "Value")
        link("Separate XYZ", "X", "Combine XYZ", "X")
        link("Math.001", "Value", "Combine XYZ", "Y")
        link("RightNipple", "Vector", "Group Output", "RightNippleCoordinate")
        link("LeftNipple", "Vector", "Group Output", "LeftNippleCoordinate")
        link("Navel", "Vector", "Group Output", "NavelCoordinate")
        link("RightMouthCorner", "Vector", "Group Output", "RightMouthCorner")
        link("LeftMouthCorner", "Vector", "Group Output", "LeftMouthCorner")
        link("Combine XYZ", "Vector", "Group Output", "MouthCenter")

NodeWrapperMpfbBodyConstants = _NodeWrapperMpfbBodyConstants()
