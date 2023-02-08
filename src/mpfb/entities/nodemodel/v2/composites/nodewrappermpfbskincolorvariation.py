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
                -960.8616,
                733.6772
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
            "value": 245.2778
        }
    },
    "class": "MpfbSkinColorVariation",
    "inputs": {
        "Input_10": {
            "class": "NodeSocketFloat",
            "default_value": 30.0,
            "identifier": "Input_10",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "ColorVariationScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_11": {
            "class": "NodeSocketFloat",
            "default_value": -0.5,
            "identifier": "Input_11",
            "max_value": 1.0,
            "min_value": -1.0,
            "name": "ColorVariationBrightness",
            "value_type": "VALUE"
        },
        "Input_4": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_4",
            "max_value": 15.0,
            "min_value": 0.0,
            "name": "ColorVariationDetail",
            "value_type": "VALUE"
        },
        "Input_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_5",
            "max_value": 1000.0,
            "min_value": -1000.0,
            "name": "ColorVariationDistortion",
            "value_type": "VALUE"
        },
        "Input_6": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Input_6",
            "name": "ColorVariationRoughness",
            "value_type": "VALUE"
        },
        "Input_8": {
            "class": "NodeSocketColor",
            "default_value": [
                0.807,
                0.565,
                0.4356,
                1.0
            ],
            "identifier": "Input_8",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Input_9": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.15,
            "identifier": "Input_9",
            "name": "ColorVariationStrength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_7": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_7",
            "name": "Color",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDetail",
            "to_node": "Noise Texture",
            "to_socket": "Detail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDistortion",
            "to_node": "Noise Texture",
            "to_socket": "Distortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationRoughness",
            "to_node": "Noise Texture",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Color",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Color",
            "to_node": "Bright/Contrast",
            "to_socket": "Color"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Bright/Contrast",
            "from_socket": "Color",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScaleMultiplier",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationBrightness",
            "to_node": "Bright/Contrast",
            "to_socket": "Bright"
        }
    ],
    "nodes": [
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
                    -416.1124,
                    52.1619
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
                    911.4695,
                    -0.5778
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
                    103.9577,
                    143.1711
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Detail": 4.0,
                "Distortion": 2.0,
                "Roughness": 0.0,
                "Scale": 400.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    604.6409,
                    -110.2636
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "Factor_Float": 0.1
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    326.351,
                    -21.1942
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.15
            },
            "label": "Math.001",
            "name": "Math.001",
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
            "input_socket_values": {
                "Value": 40.0
            },
            "label": "Math",
            "name": "Math",
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
        },
        {
            "attribute_values": {
                "location": [
                    120.8774,
                    -436.067
                ]
            },
            "class": "ShaderNodeBrightContrast",
            "input_socket_values": {
                "Bright": -0.5
            },
            "label": "Bright/Contrast",
            "name": "Bright/Contrast",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbSkinColorVariation(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [911.4695, -0.5778]
        nodes["Group Input"].location = [-977.2401, -294.2911]

        node("MpfbCharacterInfo", "Group", attribute_values={"location": [-597.7336, 345.4013]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-416.1124, 52.1619]})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [103.9577, 143.1711]}, input_socket_values={"Detail": 4.0, "Distortion": 2.0, "Roughness": 0.0, "Scale": 400.0})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [604.6409, -110.2636]}, input_socket_values={"Factor_Float": 0.1})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [326.351, -21.1942], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.15})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-314.7333, 246.1363], "operation": "DIVIDE"}, input_socket_values={"Value": 40.0})
        node("ShaderNodeBrightContrast", "Bright/Contrast", attribute_values={"location": [120.8774, -436.067]}, input_socket_values={"Bright": -0.5})

        link("Group Input", "ColorVariationDetail", "Noise Texture", "Detail")
        link("Group Input", "ColorVariationDistortion", "Noise Texture", "Distortion")
        link("Group Input", "ColorVariationRoughness", "Noise Texture", "Roughness")
        link("Group Input", "Color", "Mix", "A_Color")
        link("Group Input", "Color", "Bright/Contrast", "Color")
        link("Group Input", "ColorVariationScaleMultiplier", "Math", "Value")
        link("Group Input", "ColorVariationStrength", "Math.001", "Value_001")
        link("Group Input", "ColorVariationBrightness", "Bright/Contrast", "Bright")
        link("Group", "scale_factor", "Math", "Value_001")
        link("Texture Coordinate", "Object", "Noise Texture", "Vector")
        link("Noise Texture", "Fac", "Math.001", "Value")
        link("Bright/Contrast", "Color", "Mix", "B_Color")
        link("Math", "Value", "Noise Texture", "Scale")
        link("Math.001", "Value", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbSkinColorVariation = _NodeWrapperMpfbSkinColorVariation()
