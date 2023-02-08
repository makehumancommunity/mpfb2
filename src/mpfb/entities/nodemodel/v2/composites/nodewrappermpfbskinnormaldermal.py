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
                175.0831,
                -339.0752
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
            "value": 320.8665
        }
    },
    "class": "MpfbSkinNormalDermal",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 70.0,
            "identifier": "Input_0",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "DermalScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.15,
            "identifier": "Input_2",
            "name": "DermalBumpStrength",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_3",
            "name": "Normal",
            "value_type": "VECTOR"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Normal",
            "value_type": "VECTOR"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Voronoi Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Voronoi Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Voronoi Texture",
            "from_socket": "Distance",
            "to_node": "Group.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.001",
            "from_socket": "Value",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -314.7333,
                    246.1363
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "feature": "DISTANCE_TO_EDGE",
                "location": [
                    -27.5202,
                    196.071
                ]
            },
            "class": "ShaderNodeTexVoronoi",
            "input_socket_values": {},
            "label": "Voronoi Texture",
            "name": "Voronoi Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    248.2872,
                    182.0687
                ],
                "width": 248.8326
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "Input_6": 0.1
            },
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    972.6872,
                    46.8686
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
                    -597.7336,
                    345.4013
                ]
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Group",
            "name": "Group",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -467.8459,
                    14.2048
                ]
            },
            "class": "ShaderNodeTexCoord",
            "input_socket_values": {},
            "label": "Texture Coordinate",
            "name": "Texture Coordinate",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    678.1032,
                    -18.3332
                ]
            },
            "class": "ShaderNodeBump",
            "input_socket_values": {
                "Strength": 0.3
            },
            "label": "Bump",
            "name": "Bump",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -977.2401,
                    -294.2911
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

class _NodeWrapperMpfbSkinNormalDermal(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [972.6872, 46.8686]
        nodes["Group Input"].location = [-977.2401, -294.2911]

        node("ShaderNodeMath", "Math", attribute_values={"location": [-314.7333, 246.1363], "operation": "DIVIDE"})
        node("ShaderNodeTexVoronoi", "Voronoi Texture", attribute_values={"feature": "DISTANCE_TO_EDGE", "location": [-27.5202, 196.071]})
        node("MpfbValueRamp3", "Group.001", attribute_values={"location": [248.2872, 182.0687], "width": 248.8326}, input_socket_values={"Input_6": 0.1})
        node("MpfbCharacterInfo", "Group", attribute_values={"location": [-597.7336, 345.4013]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-467.8459, 14.2048]})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [678.1032, -18.3332]}, input_socket_values={"Strength": 0.3})

        link("Group Input", "DermalScaleMultiplier", "Math", "Value")
        link("Group Input", "DermalBumpStrength", "Bump", "Strength")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Group", "scale_factor", "Math", "Value_001")
        link("Math", "Value", "Voronoi Texture", "Scale")
        link("Texture Coordinate", "Object", "Voronoi Texture", "Vector")
        link("Voronoi Texture", "Distance", "Group.001", "Value")
        link("Group.001", "Value", "Bump", "Height")
        link("Bump", "Normal", "Group Output", "Normal")

NodeWrapperMpfbSkinNormalDermal = _NodeWrapperMpfbSkinNormalDermal()
