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
                -458.1821,
                638.4954
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
            "value": 210.2823
        }
    },
    "class": "MpfbSkinVeins",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketColor",
            "default_value": [
                0.2414,
                0.2432,
                0.5,
                1.0
            ],
            "identifier": "Input_0",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 1.1,
            "identifier": "Input_2",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SmallVeinScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketFloat",
            "default_value": 0.6,
            "identifier": "Input_3",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "LargeVeinScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_4": {
            "class": "NodeSocketColor",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ],
            "identifier": "Input_4",
            "name": "VeinColor",
            "value_type": "RGBA"
        },
        "Input_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.08,
            "identifier": "Input_5",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "VeinStrength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Color",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SmallVeinScaleMultiplier",
            "to_node": "SmallVeinScale",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScaleMultiplier",
            "to_node": "LargeVeinScale",
            "to_socket": "Value"
        },
        {
            "from_node": "Mapping",
            "from_socket": "Vector",
            "to_node": "SmallVeinWaveTexture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Mapping",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "LargeVeinWaveTexture",
            "to_socket": "Vector"
        },
        {
            "from_node": "SmallVeinCropPeak",
            "from_socket": "Value",
            "to_node": "SelectPeak",
            "to_socket": "Value"
        },
        {
            "from_node": "LargeVeinCropPeak",
            "from_socket": "Value",
            "to_node": "SelectPeak",
            "to_socket": "Value_001"
        },
        {
            "from_node": "LargeVeinWaveTexture",
            "from_socket": "Fac",
            "to_node": "LargeVeinCropPeak",
            "to_socket": "Value"
        },
        {
            "from_node": "SmallVeinWaveTexture",
            "from_socket": "Fac",
            "to_node": "SmallVeinCropPeak",
            "to_socket": "Value"
        },
        {
            "from_node": "SelectPeak",
            "from_socket": "Value",
            "to_node": "StrengthMultiplier",
            "to_socket": "Value"
        },
        {
            "from_node": "StrengthMultiplier",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "SmallVeinScale",
            "from_socket": "Value",
            "to_node": "SmallVeinWaveTexture",
            "to_socket": "Scale"
        },
        {
            "from_node": "LargeVeinScale",
            "from_socket": "Value",
            "to_node": "LargeVeinWaveTexture",
            "to_socket": "Scale"
        },
        {
            "from_node": "CharacterInfo",
            "from_socket": "scale_factor",
            "to_node": "SmallVeinScale",
            "to_socket": "Value_001"
        },
        {
            "from_node": "CharacterInfo",
            "from_socket": "scale_factor",
            "to_node": "LargeVeinScale",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "StrengthMultiplier",
            "to_socket": "Value_001"
        },
        {
            "from_node": "TextureRotation",
            "from_socket": "Vector",
            "to_node": "Mapping",
            "to_socket": "Rotation"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    1215.6146,
                    30.6328
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
                    -276.5124,
                    435.6444
                ]
            },
            "class": "ShaderNodeMapping",
            "input_socket_values": {},
            "label": "Mapping",
            "name": "Mapping",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -30.5671,
                    96.3246
                ]
            },
            "class": "ShaderNodeTexWave",
            "input_socket_values": {
                "Detail": 3.0,
                "Detail Scale": 4.0,
                "Distortion": 20.0,
                "Scale": 15.0
            },
            "label": "Small vein texture",
            "name": "SmallVeinWaveTexture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -540.1043,
                    89.0243
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Calculate small vein scale",
            "name": "SmallVeinScale",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -479.6731,
                    224.3652
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "Z": 90.0
            },
            "label": "Texture rotation",
            "name": "TextureRotation",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -551.7733,
                    -163.1668
                ],
                "operation": "DIVIDE",
                "width": 207.1555
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Calculate large vein scale",
            "name": "LargeVeinScale",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    427.4991,
                    -13.7494
                ],
                "operation": "MAXIMUM"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.98
            },
            "label": "Pick highest peak",
            "name": "SelectPeak",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    708.0868,
                    167.1202
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.05
            },
            "label": "Strength multiplier",
            "name": "StrengthMultiplier",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    983.21,
                    29.0103
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.2414,
                    0.2432,
                    0.5,
                    1.0
                ],
                "B_Color": [
                    0.0015,
                    0.0,
                    0.5,
                    1.0
                ]
            },
            "label": "Skin color vs vein color",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1218.6906,
                    179.3788
                ]
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Character info",
            "name": "CharacterInfo",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1216.33,
                    -241.5409
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
                    -30.6633,
                    -214.2721
                ]
            },
            "class": "ShaderNodeTexWave",
            "input_socket_values": {
                "Detail Roughness": 0.4,
                "Detail Scale": 4.0,
                "Distortion": 15.0,
                "Phase Offset": 0.5,
                "Scale": 9.0
            },
            "label": "Large vein texture",
            "name": "LargeVeinWaveTexture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    177.5623,
                    152.2363
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.99
            },
            "label": "Use only peaks",
            "name": "SmallVeinCropPeak",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    189.4745,
                    -157.6698
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.995
            },
            "label": "Use only peak",
            "name": "LargeVeinCropPeak",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1220.417,
                    -43.8082
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

class _NodeWrapperMpfbSkinVeins(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1215.6146, 30.6328]
        nodes["Group Input"].location = [-1220.417, -43.8082]

        node("ShaderNodeMapping", "Mapping", attribute_values={"location": [-276.5124, 435.6444]})
        node("ShaderNodeTexWave", "SmallVeinWaveTexture", label="Small vein texture", attribute_values={"location": [-30.5671, 96.3246]}, input_socket_values={"Detail": 3.0, "Detail Scale": 4.0, "Distortion": 20.0, "Scale": 15.0})
        node("ShaderNodeMath", "SmallVeinScale", label="Calculate small vein scale", attribute_values={"location": [-540.1043, 89.0243], "operation": "DIVIDE"})
        node("ShaderNodeCombineXYZ", "TextureRotation", label="Texture rotation", attribute_values={"location": [-479.6731, 224.3652]}, input_socket_values={"Z": 90.0})
        node("ShaderNodeMath", "LargeVeinScale", label="Calculate large vein scale", attribute_values={"location": [-551.7733, -163.1668], "operation": "DIVIDE", "width": 207.1555})
        node("ShaderNodeMath", "SelectPeak", label="Pick highest peak", attribute_values={"location": [427.4991, -13.7494], "operation": "MAXIMUM"}, input_socket_values={"Value_001": 0.98})
        node("ShaderNodeMath", "StrengthMultiplier", label="Strength multiplier", attribute_values={"location": [708.0868, 167.1202], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.05})
        node("ShaderNodeMix", "Mix", label="Skin color vs vein color", attribute_values={"data_type": "RGBA", "location": [983.21, 29.0103]}, input_socket_values={"A_Color": [0.2414, 0.2432, 0.5, 1.0], "B_Color": [0.0015, 0.0, 0.5, 1.0]})
        node("MpfbCharacterInfo", "CharacterInfo", label="Character info", attribute_values={"location": [-1218.6906, 179.3788]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-1216.33, -241.5409]})
        node("ShaderNodeTexWave", "LargeVeinWaveTexture", label="Large vein texture", attribute_values={"location": [-30.6633, -214.2721]}, input_socket_values={"Detail Roughness": 0.4, "Detail Scale": 4.0, "Distortion": 15.0, "Phase Offset": 0.5, "Scale": 9.0})
        node("ShaderNodeMath", "SmallVeinCropPeak", label="Use only peaks", attribute_values={"location": [177.5623, 152.2363], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.99})
        node("ShaderNodeMath", "LargeVeinCropPeak", label="Use only peak", attribute_values={"location": [189.4745, -157.6698], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.995})

        link("Group Input", "SkinColor", "Mix", "A_Color")
        link("Group Input", "SmallVeinScaleMultiplier", "SmallVeinScale", "Value")
        link("Group Input", "LargeVeinScaleMultiplier", "LargeVeinScale", "Value")
        link("Group Input", "VeinColor", "Mix", "B_Color")
        link("Group Input", "VeinStrength", "StrengthMultiplier", "Value_001")
        link("Mapping", "Vector", "SmallVeinWaveTexture", "Vector")
        link("Texture Coordinate", "Object", "Mapping", "Vector")
        link("Texture Coordinate", "Object", "LargeVeinWaveTexture", "Vector")
        link("SmallVeinCropPeak", "Value", "SelectPeak", "Value")
        link("LargeVeinCropPeak", "Value", "SelectPeak", "Value_001")
        link("LargeVeinWaveTexture", "Fac", "LargeVeinCropPeak", "Value")
        link("SmallVeinWaveTexture", "Fac", "SmallVeinCropPeak", "Value")
        link("SelectPeak", "Value", "StrengthMultiplier", "Value")
        link("StrengthMultiplier", "Value", "Mix", "Factor_Float")
        link("SmallVeinScale", "Value", "SmallVeinWaveTexture", "Scale")
        link("LargeVeinScale", "Value", "LargeVeinWaveTexture", "Scale")
        link("CharacterInfo", "scale_factor", "SmallVeinScale", "Value_001")
        link("CharacterInfo", "scale_factor", "LargeVeinScale", "Value_001")
        link("TextureRotation", "Vector", "Mapping", "Rotation")
        link("Mix", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbSkinVeins = _NodeWrapperMpfbSkinVeins()
