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
                -142.4896,
                867.0698
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
            "value": 294.3394
        }
    },
    "class": "MpfbSkinMasterColor",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Input_0",
            "name": "DiffuseTextureStrength",
            "value_type": "VALUE"
        },
        "Input_1": {
            "class": "NodeSocketColor",
            "default_value": [
                0.6795,
                0.4678,
                0.3763,
                1.0
            ],
            "identifier": "Input_1",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Input_11": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.7206,
                0.6135,
                1.0
            ],
            "identifier": "Input_11",
            "name": "FingernailsColor",
            "value_type": "RGBA"
        },
        "Input_12": {
            "class": "NodeSocketColor",
            "default_value": [
                1.0,
                0.7231,
                0.6105,
                1.0
            ],
            "identifier": "Input_12",
            "name": "ToenailsColor",
            "value_type": "RGBA"
        },
        "Input_14": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ],
            "identifier": "Input_14",
            "name": "SpotColor",
            "value_type": "RGBA"
        },
        "Input_16": {
            "class": "NodeSocketColor",
            "default_value": [
                0.3467,
                0.1912,
                0.1356,
                1.0
            ],
            "identifier": "Input_16",
            "name": "EyelidColor",
            "value_type": "RGBA"
        },
        "Input_18": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_18",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "SkinOverride",
            "value_type": "VALUE"
        },
        "Input_19": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_19",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "AurolaeOverride",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketColor",
            "default_value": [
                0.807,
                0.5647,
                0.4342,
                1.0
            ],
            "identifier": "Input_2",
            "name": "DiffuseTexture",
            "value_type": "RGBA"
        },
        "Input_20": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_20",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "NavelCenterOverride",
            "value_type": "VALUE"
        },
        "Input_21": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_21",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "LipsOverride",
            "value_type": "VALUE"
        },
        "Input_22": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_22",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "FingernailsOverride",
            "value_type": "VALUE"
        },
        "Input_23": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_23",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "ToenailsOverride",
            "value_type": "VALUE"
        },
        "Input_24": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_24",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "SpotOverride",
            "value_type": "VALUE"
        },
        "Input_25": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_25",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "EyelidOverride",
            "value_type": "VALUE"
        },
        "Input_26": {
            "class": "NodeSocketColor",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ],
            "identifier": "Input_26",
            "name": "VeinColor",
            "value_type": "RGBA"
        },
        "Input_28": {
            "class": "NodeSocketColor",
            "default_value": [
                0.6795,
                0.3608,
                0.3062,
                1.0
            ],
            "identifier": "Input_28",
            "name": "GenitalsColor",
            "value_type": "RGBA"
        },
        "Input_29": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_29",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "GenitalsOverride",
            "value_type": "VALUE"
        },
        "Input_4": {
            "class": "NodeSocketColor",
            "default_value": [
                0.633,
                0.4019,
                0.3516,
                1.0
            ],
            "identifier": "Input_4",
            "name": "AureolaeColor",
            "value_type": "RGBA"
        },
        "Input_6": {
            "class": "NodeSocketColor",
            "default_value": [
                0.3467,
                0.1912,
                0.1356,
                1.0
            ],
            "identifier": "Input_6",
            "name": "NavelCenterColor",
            "value_type": "RGBA"
        },
        "Input_8": {
            "class": "NodeSocketColor",
            "default_value": [
                0.6795,
                0.3622,
                0.3348,
                1.0
            ],
            "identifier": "Input_8",
            "name": "LipsColor",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Output_10": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_10",
            "name": "FingernailsColor",
            "value_type": "RGBA"
        },
        "Output_13": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_13",
            "name": "ToenailsColor",
            "value_type": "RGBA"
        },
        "Output_15": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_15",
            "name": "SpotColor",
            "value_type": "RGBA"
        },
        "Output_17": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_17",
            "name": "EyelidColor",
            "value_type": "RGBA"
        },
        "Output_27": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_27",
            "name": "VeinColor",
            "value_type": "RGBA"
        },
        "Output_3": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_3",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Output_30": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_30",
            "name": "GenitalsColor",
            "value_type": "RGBA"
        },
        "Output_5": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_5",
            "name": "AureolaeColor",
            "value_type": "RGBA"
        },
        "Output_7": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_7",
            "name": "NavelCenterColor",
            "value_type": "RGBA"
        },
        "Output_9": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_9",
            "name": "LipsColor",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "SkinMainOverride",
            "from_socket": "Value",
            "to_node": "SkinMainMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "SkinMainMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "SkinMainMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "SkinMainMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "AurolaeOverride",
            "from_socket": "Value",
            "to_node": "AureolaeMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "AureolaeMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AureolaeColor",
            "to_node": "AureolaeMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "AureolaeMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "AureolaeColor"
        },
        {
            "from_node": "NavelCenterOverride",
            "from_socket": "Value",
            "to_node": "NavelCenterMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "NavelCenterMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterColor",
            "to_node": "NavelCenterMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "NavelCenterMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "NavelCenterColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "LipsMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsColor",
            "to_node": "LipsMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "LipsMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "LipsColor"
        },
        {
            "from_node": "LipsOverride",
            "from_socket": "Value",
            "to_node": "LipsMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "FingernailsMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "FingernailsColor"
        },
        {
            "from_node": "FingernailsOverride",
            "from_socket": "Value",
            "to_node": "FingernailsMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FingernailsColor",
            "to_node": "FingernailsMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "ToenailsOverride",
            "from_socket": "Value",
            "to_node": "ToenailsMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ToenailsMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "FingernailsMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ToenailsColor",
            "to_node": "ToenailsMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "ToenailsMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "ToenailsColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "SpotMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "SpotMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "SpotOverride",
            "from_socket": "Value",
            "to_node": "SpotMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "SpotMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EyelidColor",
            "to_node": "EyelidMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "EyelidMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "EyelidColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "EyelidMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "EyelidOverride",
            "from_socket": "Value",
            "to_node": "EyelidMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "SkinMainOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinOverride",
            "to_node": "SkinMainOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "AurolaeOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AurolaeOverride",
            "to_node": "AurolaeOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "NavelCenterOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterOverride",
            "to_node": "NavelCenterOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "LipsOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsOverride",
            "to_node": "LipsOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "FingernailsOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FingernailsOverride",
            "to_node": "FingernailsOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ToenailsOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ToenailsOverride",
            "to_node": "ToenailsOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "SpotOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotOverride",
            "to_node": "SpotOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "EyelidOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EyelidOverride",
            "to_node": "EyelidOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "GenitalsOverride",
            "from_socket": "Value",
            "to_node": "GenitalsMix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "GenitalsMix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "GenitalsColor",
            "to_node": "GenitalsMix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "GenitalsOverride",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "GenitalsOverride",
            "to_node": "GenitalsOverride",
            "to_socket": "Value_001"
        },
        {
            "from_node": "GenitalsMix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "GenitalsColor"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    392.2274,
                    -444.5667
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
                "data_type": "RGBA",
                "location": [
                    -143.8119,
                    554.3099
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Skin Main Mix",
            "name": "SkinMainMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -146.9567,
                    289.8055
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Aureolae Mix",
            "name": "AureolaeMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -146.6655,
                    36.6086
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Navel Center Mix",
            "name": "NavelCenterMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -145.7235,
                    -206.1388
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Lips Mix",
            "name": "LipsMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -142.7661,
                    -701.5549
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Toenails Mix",
            "name": "ToenailsMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -144.2362,
                    -942.5393
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Spot Mix",
            "name": "SpotMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -395.0411,
                    519.9173
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Skin Main Override",
            "name": "SkinMainOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -392.8619,
                    262.7036
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Aurolae Override",
            "name": "AurolaeOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -389.5932,
                    -7.5887
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Navel Center Override",
            "name": "NavelCenterOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -390.6827,
                    -259.3529
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Lips Override",
            "name": "LipsOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -145.9052,
                    -460.5084
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Fingernails Mix",
            "name": "FingernailsMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -383.0556,
                    -492.5891
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Fingernails Override",
            "name": "FingernailsOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -380.8764,
                    -737.8142
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Toenails Override",
            "name": "ToenailsOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -384.7022,
                    -953.6123
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Spot Override",
            "name": "SpotOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -382.523,
                    -1185.7588
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Eyelid Override",
            "name": "EyelidOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -143.9895,
                    -1203.0403
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Eyelid Mix",
            "name": "EyelidMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -129.8082,
                    -1707.5752
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "Factor_Float": 0.0
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -141.951,
                    -1436.5038
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Genitals Mix",
            "name": "GenitalsMix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -376.4073,
                    -1406.9883
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Genitals Override",
            "name": "GenitalsOverride",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1113.7202,
                    -454.5674
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

class _NodeWrapperMpfbSkinMasterColor(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [392.2274, -444.5667]
        nodes["Group Input"].location = [-1113.7202, -454.5674]

        node("ShaderNodeMix", "SkinMainMix", label="Skin Main Mix", attribute_values={"data_type": "RGBA", "location": [-143.8119, 554.3099]})
        node("ShaderNodeMix", "AureolaeMix", label="Aureolae Mix", attribute_values={"data_type": "RGBA", "location": [-146.9567, 289.8055]})
        node("ShaderNodeMix", "NavelCenterMix", label="Navel Center Mix", attribute_values={"data_type": "RGBA", "location": [-146.6655, 36.6086]})
        node("ShaderNodeMix", "LipsMix", label="Lips Mix", attribute_values={"data_type": "RGBA", "location": [-145.7235, -206.1388]})
        node("ShaderNodeMix", "ToenailsMix", label="Toenails Mix", attribute_values={"data_type": "RGBA", "location": [-142.7661, -701.5549]})
        node("ShaderNodeMix", "SpotMix", label="Spot Mix", attribute_values={"data_type": "RGBA", "location": [-144.2362, -942.5393]})
        node("ShaderNodeMath", "SkinMainOverride", label="Skin Main Override", attribute_values={"location": [-395.0411, 519.9173], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "AurolaeOverride", label="Aurolae Override", attribute_values={"location": [-392.8619, 262.7036], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "NavelCenterOverride", label="Navel Center Override", attribute_values={"location": [-389.5932, -7.5887], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "LipsOverride", label="Lips Override", attribute_values={"location": [-390.6827, -259.3529], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMix", "FingernailsMix", label="Fingernails Mix", attribute_values={"data_type": "RGBA", "location": [-145.9052, -460.5084]})
        node("ShaderNodeMath", "FingernailsOverride", label="Fingernails Override", attribute_values={"location": [-383.0556, -492.5891], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "ToenailsOverride", label="Toenails Override", attribute_values={"location": [-380.8764, -737.8142], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "SpotOverride", label="Spot Override", attribute_values={"location": [-384.7022, -953.6123], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMath", "EyelidOverride", label="Eyelid Override", attribute_values={"location": [-382.523, -1185.7588], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMix", "EyelidMix", label="Eyelid Mix", attribute_values={"data_type": "RGBA", "location": [-143.9895, -1203.0403]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-129.8082, -1707.5752]}, input_socket_values={"Factor_Float": 0.0})
        node("ShaderNodeMix", "GenitalsMix", label="Genitals Mix", attribute_values={"data_type": "RGBA", "location": [-141.951, -1436.5038]})
        node("ShaderNodeMath", "GenitalsOverride", label="Genitals Override", attribute_values={"location": [-376.4073, -1406.9883], "operation": "SUBTRACT", "use_clamp": True})

        link("Group Input", "SkinColor", "SkinMainMix", "A_Color")
        link("Group Input", "DiffuseTexture", "SkinMainMix", "B_Color")
        link("Group Input", "DiffuseTexture", "AureolaeMix", "B_Color")
        link("Group Input", "AureolaeColor", "AureolaeMix", "A_Color")
        link("Group Input", "DiffuseTexture", "NavelCenterMix", "B_Color")
        link("Group Input", "NavelCenterColor", "NavelCenterMix", "A_Color")
        link("Group Input", "DiffuseTexture", "LipsMix", "B_Color")
        link("Group Input", "LipsColor", "LipsMix", "A_Color")
        link("Group Input", "FingernailsColor", "FingernailsMix", "A_Color")
        link("Group Input", "DiffuseTexture", "ToenailsMix", "B_Color")
        link("Group Input", "DiffuseTexture", "FingernailsMix", "B_Color")
        link("Group Input", "ToenailsColor", "ToenailsMix", "A_Color")
        link("Group Input", "SpotColor", "SpotMix", "A_Color")
        link("Group Input", "DiffuseTexture", "SpotMix", "B_Color")
        link("Group Input", "EyelidColor", "EyelidMix", "A_Color")
        link("Group Input", "DiffuseTexture", "EyelidMix", "B_Color")
        link("Group Input", "DiffuseTextureStrength", "SkinMainOverride", "Value")
        link("Group Input", "SkinOverride", "SkinMainOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "AurolaeOverride", "Value")
        link("Group Input", "AurolaeOverride", "AurolaeOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "NavelCenterOverride", "Value")
        link("Group Input", "NavelCenterOverride", "NavelCenterOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "LipsOverride", "Value")
        link("Group Input", "LipsOverride", "LipsOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "FingernailsOverride", "Value")
        link("Group Input", "FingernailsOverride", "FingernailsOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "ToenailsOverride", "Value")
        link("Group Input", "ToenailsOverride", "ToenailsOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "SpotOverride", "Value")
        link("Group Input", "SpotOverride", "SpotOverride", "Value_001")
        link("Group Input", "DiffuseTextureStrength", "EyelidOverride", "Value")
        link("Group Input", "EyelidOverride", "EyelidOverride", "Value_001")
        link("Group Input", "VeinColor", "Mix", "A_Color")
        link("Group Input", "DiffuseTexture", "GenitalsMix", "B_Color")
        link("Group Input", "GenitalsColor", "GenitalsMix", "A_Color")
        link("Group Input", "DiffuseTextureStrength", "GenitalsOverride", "Value")
        link("Group Input", "GenitalsOverride", "GenitalsOverride", "Value_001")
        link("SkinMainOverride", "Value", "SkinMainMix", "Factor_Float")
        link("AurolaeOverride", "Value", "AureolaeMix", "Factor_Float")
        link("NavelCenterOverride", "Value", "NavelCenterMix", "Factor_Float")
        link("LipsOverride", "Value", "LipsMix", "Factor_Float")
        link("FingernailsOverride", "Value", "FingernailsMix", "Factor_Float")
        link("ToenailsOverride", "Value", "ToenailsMix", "Factor_Float")
        link("SpotOverride", "Value", "SpotMix", "Factor_Float")
        link("EyelidOverride", "Value", "EyelidMix", "Factor_Float")
        link("GenitalsOverride", "Value", "GenitalsMix", "Factor_Float")
        link("SkinMainMix", "Result_Color", "Group Output", "SkinColor")
        link("AureolaeMix", "Result_Color", "Group Output", "AureolaeColor")
        link("NavelCenterMix", "Result_Color", "Group Output", "NavelCenterColor")
        link("LipsMix", "Result_Color", "Group Output", "LipsColor")
        link("FingernailsMix", "Result_Color", "Group Output", "FingernailsColor")
        link("ToenailsMix", "Result_Color", "Group Output", "ToenailsColor")
        link("SpotMix", "Result_Color", "Group Output", "SpotColor")
        link("EyelidMix", "Result_Color", "Group Output", "EyelidColor")
        link("Mix", "Result_Color", "Group Output", "VeinColor")
        link("GenitalsMix", "Result_Color", "Group Output", "GenitalsColor")

NodeWrapperMpfbSkinMasterColor = _NodeWrapperMpfbSkinMasterColor()
