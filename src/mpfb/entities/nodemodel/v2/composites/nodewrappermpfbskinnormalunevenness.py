import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinNormalUnevenness",
    "inputs": {
        "Input_0": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Input_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 150.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_2": {
            "name": "UnevennessBumpStrength",
            "identifier": "Input_2",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "UnevennessDetail",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_5": {
            "name": "UnevennessDistortion",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_6": {
            "name": "UnevennessRoughness",
            "identifier": "Input_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_3": {
            "name": "Normal",
            "identifier": "Input_3",
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
        "Output_1": {
            "name": "Normal",
            "identifier": "Output_1",
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
                -249.8333,
                -266.7137
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
            "value": 289.2502
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
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
            "from_socket": "UnevennessBumpStrength",
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
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "Noise Texture",
            "to_socket": "Detail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "Noise Texture",
            "to_socket": "Distortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "Noise Texture",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
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
                "color": [
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -597.7336,
                    345.4013
                ],
                "use_custom_color": false,
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
                    -48.6558,
                    160.4243
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Detail": 4.0,
                "Distortion": 2.0,
                "Roughness": 0.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -571.3127,
                    4.7156
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

class _NodeWrapperMpfbSkinNormalUnevenness(AbstractGroupWrapper):
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
        node("MpfbCharacterInfo", "Group", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-597.7336, 345.4013], "use_custom_color": False, "width": 140.0})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [678.1032, -18.3332]}, input_socket_values={"Strength": 0.3})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-48.6558, 160.4243]}, input_socket_values={"Detail": 4.0, "Distortion": 2.0, "Roughness": 0.0})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-571.3127, 4.7156]})

        link("Group Input", "UnevennessScaleMultiplier", "Math", "Value")
        link("Group Input", "UnevennessBumpStrength", "Bump", "Strength")
        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "UnevennessDetail", "Noise Texture", "Detail")
        link("Group Input", "UnevennessDistortion", "Noise Texture", "Distortion")
        link("Group Input", "UnevennessRoughness", "Noise Texture", "Roughness")
        link("Group", "scale_factor", "Math", "Value_001")
        link("Math", "Value", "Noise Texture", "Scale")
        link("Noise Texture", "Fac", "Bump", "Height")
        link("Texture Coordinate", "Object", "Noise Texture", "Vector")
        link("Bump", "Normal", "Group Output", "Normal")

NodeWrapperMpfbSkinNormalUnevenness = _NodeWrapperMpfbSkinNormalUnevenness()
