import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinColorVariation",
    "inputs": {
        "Input_8": {
            "name": "Color",
            "identifier": "Input_8",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.6899,
                0.4647,
                1.0
            ]
        },
        "Input_9": {
            "name": "ColorVariationStrength",
            "identifier": "Input_9",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.3
        },
        "Input_10": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Input_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_11": {
            "name": "ColorVariationBrightness",
            "identifier": "Input_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "ColorVariationDetail",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_5": {
            "name": "ColorVariationDistortion",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_6": {
            "name": "ColorVariationRoughness",
            "identifier": "Input_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0
        }
    },
    "outputs": {
        "Output_7": {
            "name": "Color",
            "identifier": "Output_7",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
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
                90.467,
                101.8807
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
            "value": 236.5711
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

        node("MpfbCharacterInfo", "Group", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-597.7336, 345.4013], "use_custom_color": False, "width": 140.0})
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
