import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinNormalDermal",
    "inputs": {
        "Input_0": {
            "name": "DermalScaleMultiplier",
            "identifier": "Input_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_1": {
            "name": "DermalBumpStrength",
            "identifier": "Input_1",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "DermalValley",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.05,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_5": {
            "name": "DermalPeak",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_2": {
            "name": "Normal",
            "identifier": "Input_2",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        }
    },
    "outputs": {
        "Output_3": {
            "name": "Normal",
            "identifier": "Output_3",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
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
                -439.0309,
                178.1685
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
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
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
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalValley",
            "to_node": "Group.001",
            "to_socket": "BetweenStop1Position"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalPeak",
            "to_node": "Group.001",
            "to_socket": "BetweenStop2Position"
        }
    ],
    "nodes": [
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
                "color": [
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    248.2872,
                    182.0687
                ],
                "use_custom_color": true,
                "width": 248.8326
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.05,
                "BetweenStop2Position": 0.1,
                "BetweenStop2Value": 0.0
            },
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -597.7336,
                    345.4013
                ],
                "use_custom_color": true,
                "width": 140.0
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
        node("MpfbValueRamp3", "Group.001", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [248.2872, 182.0687], "use_custom_color": True, "width": 248.8326}, input_socket_values={"BetweenStop2Value": 0.0, "BetweenStop1Position": 0.05, "BetweenStop2Position": 0.1})
        node("MpfbCharacterInfo", "Group", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-597.7336, 345.4013], "use_custom_color": True, "width": 140.0})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-467.8459, 14.2048]})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [678.1032, -18.3332]}, input_socket_values={"Strength": 0.3})

        link("Group Input", "DermalScaleMultiplier", "Math", "Value")
        link("Group Input", "DermalBumpStrength", "Bump", "Strength")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "DermalValley", "Group.001", "BetweenStop1Position")
        link("Group Input", "DermalPeak", "Group.001", "BetweenStop2Position")
        link("Group", "scale_factor", "Math", "Value_001")
        link("Math", "Value", "Voronoi Texture", "Scale")
        link("Texture Coordinate", "Object", "Voronoi Texture", "Vector")
        link("Voronoi Texture", "Distance", "Group.001", "Value")
        link("Group.001", "Value", "Bump", "Height")
        link("Bump", "Normal", "Group Output", "Normal")

NodeWrapperMpfbSkinNormalDermal = _NodeWrapperMpfbSkinNormalDermal()
