import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkinMasterColor",
    "inputs": {
        "Input_2": {
            "name": "DiffuseTexture",
            "identifier": "Input_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.807,
                0.5647,
                0.4342,
                1.0
            ]
        },
        "Input_0": {
            "name": "DiffuseTextureStrength",
            "identifier": "Input_0",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_31": {
            "name": "InkLayerColor",
            "identifier": "Input_31",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0119,
                0.0,
                1.0,
                1.0
            ]
        },
        "Input_32": {
            "name": "InkLayerStrength",
            "identifier": "Input_32",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_1": {
            "name": "SkinColor",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.71,
                0.45,
                0.32,
                1.0
            ]
        },
        "Input_18": {
            "name": "SkinOverride",
            "identifier": "Input_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_4": {
            "name": "AureolaeColor",
            "identifier": "Input_4",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.6975,
                0.3997,
                0.3149,
                1.0
            ]
        },
        "Input_19": {
            "name": "AurolaeOverride",
            "identifier": "Input_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_6": {
            "name": "NavelCenterColor",
            "identifier": "Input_6",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.3467,
                0.1912,
                0.1356,
                1.0
            ]
        },
        "Input_20": {
            "name": "NavelCenterOverride",
            "identifier": "Input_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_8": {
            "name": "LipsColor",
            "identifier": "Input_8",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.8,
                0.3834,
                0.3199,
                1.0
            ]
        },
        "Input_21": {
            "name": "LipsOverride",
            "identifier": "Input_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_11": {
            "name": "FingernailsColor",
            "identifier": "Input_11",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.7206,
                0.6135,
                1.0
            ]
        },
        "Input_22": {
            "name": "FingernailsOverride",
            "identifier": "Input_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_12": {
            "name": "ToenailsColor",
            "identifier": "Input_12",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.7231,
                0.6105,
                1.0
            ]
        },
        "Input_23": {
            "name": "ToenailsOverride",
            "identifier": "Input_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_14": {
            "name": "SpotColor",
            "identifier": "Input_14",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_24": {
            "name": "SpotOverride",
            "identifier": "Input_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_16": {
            "name": "EyelidColor",
            "identifier": "Input_16",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.3467,
                0.1912,
                0.1356,
                1.0
            ]
        },
        "Input_25": {
            "name": "EyelidOverride",
            "identifier": "Input_25",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_28": {
            "name": "GenitalsColor",
            "identifier": "Input_28",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.6795,
                0.3608,
                0.3062,
                1.0
            ]
        },
        "Input_29": {
            "name": "GenitalsOverride",
            "identifier": "Input_29",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_26": {
            "name": "VeinColor",
            "identifier": "Input_26",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
        }
    },
    "outputs": {
        "Output_3": {
            "name": "SkinColor",
            "identifier": "Output_3",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_5": {
            "name": "AureolaeColor",
            "identifier": "Output_5",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_7": {
            "name": "NavelCenterColor",
            "identifier": "Output_7",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_9": {
            "name": "LipsColor",
            "identifier": "Output_9",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_10": {
            "name": "FingernailsColor",
            "identifier": "Output_10",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_13": {
            "name": "ToenailsColor",
            "identifier": "Output_13",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_15": {
            "name": "SpotColor",
            "identifier": "Output_15",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_17": {
            "name": "EyelidColor",
            "identifier": "Output_17",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_30": {
            "name": "GenitalsColor",
            "identifier": "Output_30",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_27": {
            "name": "VeinColor",
            "identifier": "Output_27",
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
                -141.6174,
                910.6931
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
            "value": 294.3394
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "ColorLayersSkin",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersSkin",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersSkin",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "ColorLayersSkin",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinOverride",
            "to_node": "ColorLayersSkin",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AureolaeColor",
            "to_node": "ColorLayersAurolae",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersAurolae",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersAurolae",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AurolaeOverride",
            "to_node": "ColorLayersAurolae",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersAurolae",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "AureolaeColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersNavel",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterColor",
            "to_node": "ColorLayersNavel",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersNavel",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterOverride",
            "to_node": "ColorLayersNavel",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersNavel",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "NavelCenterColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersLips",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersLips",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsColor",
            "to_node": "ColorLayersLips",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsOverride",
            "to_node": "ColorLayersLips",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersLips",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "LipsColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersFingernails",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersFingernails",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FingernailsColor",
            "to_node": "ColorLayersFingernails",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FingernailsOverride",
            "to_node": "ColorLayersFingernails",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersFingernails",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "FingernailsColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersToenails",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersToenails",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ToenailsColor",
            "to_node": "ColorLayersToenails",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ToenailsOverride",
            "to_node": "ColorLayersToenails",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersSpots",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersSpots",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "ColorLayersSpots",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotOverride",
            "to_node": "ColorLayersSpots",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersToenails",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "ToenailsColor"
        },
        {
            "from_node": "ColorLayersSpots",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersEyelids",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersEyelids",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EyelidColor",
            "to_node": "ColorLayersEyelids",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EyelidOverride",
            "to_node": "ColorLayersEyelids",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersEyelids",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "EyelidColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTextureStrength",
            "to_node": "ColorLayersGenitals",
            "to_socket": "DefaultColorStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DiffuseTexture",
            "to_node": "ColorLayersGenitals",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "GenitalsColor",
            "to_node": "ColorLayersGenitals",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "GenitalsOverride",
            "to_node": "ColorLayersGenitals",
            "to_socket": "MixinOverrideStrength"
        },
        {
            "from_node": "ColorLayersGenitals",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "GenitalsColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "ColorLayersVeins",
            "to_socket": "DefaultColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "ColorLayersVeins",
            "to_socket": "MixinColor"
        },
        {
            "from_node": "ColorLayersVeins",
            "from_socket": "Result",
            "to_node": "Group Output",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersSkin",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersSkin",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersAurolae",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersAurolae",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersNavel",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersNavel",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersLips",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersLips",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersEyelids",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersEyelids",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersFingernails",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersFingernails",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersToenails",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersToenails",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersSpots",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersSpots",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersGenitals",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersGenitals",
            "to_socket": "OverlayStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerColor",
            "to_node": "ColorLayersVeins",
            "to_socket": "OverlayColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "InkLayerStrength",
            "to_node": "ColorLayersVeins",
            "to_socket": "OverlayStrength"
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
                    -389.7957,
                    632.5613
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Aurolae",
            "name": "ColorLayersAurolae",
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
                    -390.6679,
                    404.847
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Navel",
            "name": "ColorLayersNavel",
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
                    -392.4124,
                    182.3674
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Lips",
            "name": "ColorLayersLips",
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
                    -393.2846,
                    -45.3471
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Fingernails",
            "name": "ColorLayersFingernails",
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
                    -392.4124,
                    -270.4442
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Toenails",
            "name": "ColorLayersToenails",
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
                    -390.6679,
                    -499.0314
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Spots",
            "name": "ColorLayersSpots",
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
                    -391.5401,
                    -727.619
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Eyelids",
            "name": "ColorLayersEyelids",
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
                    -393.2846,
                    -948.3545
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Genitals",
            "name": "ColorLayersGenitals",
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
                    -395.0291,
                    -1176.0699
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Veins",
            "name": "ColorLayersVeins",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    244.2672,
                    30.335
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
                    -391.5401,
                    855.0407
                ],
                "use_custom_color": false,
                "width": 273.9324
            },
            "class": "MpfbColorLayerMixer",
            "input_socket_values": {},
            "label": "Main skin",
            "name": "ColorLayersSkin",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -995.7593,
                    137.6411
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

        nodes["Group Output"].location = [244.2672, 30.335]
        nodes["Group Input"].location = [-995.7593, 137.6411]

        node("MpfbColorLayerMixer", "ColorLayersAurolae", label="Aurolae", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-389.7957, 632.5613], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersNavel", label="Navel", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-390.6679, 404.847], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersLips", label="Lips", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-392.4124, 182.3674], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersFingernails", label="Fingernails", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-393.2846, -45.3471], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersToenails", label="Toenails", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-392.4124, -270.4442], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersSpots", label="Spots", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-390.6679, -499.0314], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersEyelids", label="Eyelids", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-391.5401, -727.619], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersGenitals", label="Genitals", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-393.2846, -948.3545], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersVeins", label="Veins", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-395.0291, -1176.0699], "use_custom_color": False, "width": 273.9324})
        node("MpfbColorLayerMixer", "ColorLayersSkin", label="Main skin", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-391.5401, 855.0407], "use_custom_color": False, "width": 273.9324})

        link("Group Input", "DiffuseTextureStrength", "ColorLayersSkin", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersSkin", "DefaultColor")
        link("Group Input", "SkinColor", "ColorLayersSkin", "MixinColor")
        link("Group Input", "SkinOverride", "ColorLayersSkin", "MixinOverrideStrength")
        link("Group Input", "AureolaeColor", "ColorLayersAurolae", "MixinColor")
        link("Group Input", "DiffuseTexture", "ColorLayersAurolae", "DefaultColor")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersAurolae", "DefaultColorStrength")
        link("Group Input", "AurolaeOverride", "ColorLayersAurolae", "MixinOverrideStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersNavel", "DefaultColor")
        link("Group Input", "NavelCenterColor", "ColorLayersNavel", "MixinColor")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersNavel", "DefaultColorStrength")
        link("Group Input", "NavelCenterOverride", "ColorLayersNavel", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersLips", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersLips", "DefaultColor")
        link("Group Input", "LipsColor", "ColorLayersLips", "MixinColor")
        link("Group Input", "LipsOverride", "ColorLayersLips", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersFingernails", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersFingernails", "DefaultColor")
        link("Group Input", "FingernailsColor", "ColorLayersFingernails", "MixinColor")
        link("Group Input", "FingernailsOverride", "ColorLayersFingernails", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersToenails", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersToenails", "DefaultColor")
        link("Group Input", "ToenailsColor", "ColorLayersToenails", "MixinColor")
        link("Group Input", "ToenailsOverride", "ColorLayersToenails", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersSpots", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersSpots", "DefaultColor")
        link("Group Input", "SpotColor", "ColorLayersSpots", "MixinColor")
        link("Group Input", "SpotOverride", "ColorLayersSpots", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersEyelids", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersEyelids", "DefaultColor")
        link("Group Input", "EyelidColor", "ColorLayersEyelids", "MixinColor")
        link("Group Input", "EyelidOverride", "ColorLayersEyelids", "MixinOverrideStrength")
        link("Group Input", "DiffuseTextureStrength", "ColorLayersGenitals", "DefaultColorStrength")
        link("Group Input", "DiffuseTexture", "ColorLayersGenitals", "DefaultColor")
        link("Group Input", "GenitalsColor", "ColorLayersGenitals", "MixinColor")
        link("Group Input", "GenitalsOverride", "ColorLayersGenitals", "MixinOverrideStrength")
        link("Group Input", "VeinColor", "ColorLayersVeins", "DefaultColor")
        link("Group Input", "VeinColor", "ColorLayersVeins", "MixinColor")
        link("Group Input", "InkLayerColor", "ColorLayersSkin", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersSkin", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersAurolae", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersAurolae", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersNavel", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersNavel", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersLips", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersLips", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersEyelids", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersEyelids", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersFingernails", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersFingernails", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersToenails", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersToenails", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersSpots", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersSpots", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersGenitals", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersGenitals", "OverlayStrength")
        link("Group Input", "InkLayerColor", "ColorLayersVeins", "OverlayColor")
        link("Group Input", "InkLayerStrength", "ColorLayersVeins", "OverlayStrength")
        link("ColorLayersSkin", "Result", "Group Output", "SkinColor")
        link("ColorLayersAurolae", "Result", "Group Output", "AureolaeColor")
        link("ColorLayersNavel", "Result", "Group Output", "NavelCenterColor")
        link("ColorLayersLips", "Result", "Group Output", "LipsColor")
        link("ColorLayersFingernails", "Result", "Group Output", "FingernailsColor")
        link("ColorLayersToenails", "Result", "Group Output", "ToenailsColor")
        link("ColorLayersSpots", "Result", "Group Output", "SpotColor")
        link("ColorLayersEyelids", "Result", "Group Output", "EyelidColor")
        link("ColorLayersGenitals", "Result", "Group Output", "GenitalsColor")
        link("ColorLayersVeins", "Result", "Group Output", "VeinColor")

NodeWrapperMpfbSkinMasterColor = _NodeWrapperMpfbSkinMasterColor()
