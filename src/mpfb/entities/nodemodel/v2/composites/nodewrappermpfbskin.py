import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkin",
    "inputs": {
        "Input_Socket_SkinColor": {
            "name": "SkinColor",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.807,
                0.565,
                0.4356,
                1.0
            ]
        },
        "Input_Socket_SpotColor": {
            "name": "SpotColor",
            "identifier": "Socket_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_Socket_VeinColor": {
            "name": "VeinColor",
            "identifier": "Socket_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
        },
        "Input_Socket_Roughness": {
            "name": "Roughness",
            "identifier": "Socket_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_4",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_Socket_SSSRadiusMultiplyer": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_43",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotStrength": {
            "name": "SpotStrength",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotScaleMultiplier": {
            "name": "SpotScaleMultiplier",
            "identifier": "Socket_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 20.0,
            "min_value": 0.1,
            "max_value": 10000.0
        },
        "Input_Socket_SpotDetail": {
            "name": "SpotDetail",
            "identifier": "Socket_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_SpotDistortion": {
            "name": "SpotDistortion",
            "identifier": "Socket_14",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_SpotRoughness": {
            "name": "SpotRoughness",
            "identifier": "Socket_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotValley": {
            "name": "SpotValley",
            "identifier": "Socket_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_Socket_SpotPeak": {
            "name": "SpotPeak",
            "identifier": "Socket_17",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessScaleMultiplier": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Socket_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 150.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_UnevennessBumpStrength": {
            "name": "UnevennessBumpStrength",
            "identifier": "Socket_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessDetail": {
            "name": "UnevennessDetail",
            "identifier": "Socket_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_UnevennessDistortion": {
            "name": "UnevennessDistortion",
            "identifier": "Socket_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessRoughness": {
            "name": "UnevennessRoughness",
            "identifier": "Socket_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_DermalScaleMultiplier": {
            "name": "DermalScaleMultiplier",
            "identifier": "Socket_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_DermalBumpStrength": {
            "name": "DermalBumpStrength",
            "identifier": "Socket_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SmallVeinScaleMultiplier": {
            "name": "SmallVeinScaleMultiplier",
            "identifier": "Socket_25",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_LargeVeinScaleMultiplier": {
            "name": "LargeVeinScaleMultiplier",
            "identifier": "Socket_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_VeinStrength": {
            "name": "VeinStrength",
            "identifier": "Socket_27",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.08,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationStrength": {
            "name": "ColorVariationStrength",
            "identifier": "Socket_28",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationScaleMultiplier": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Socket_29",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 30.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_Socket_ColorVariationBrightness": {
            "name": "ColorVariationBrightness",
            "identifier": "Socket_30",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationDetail": {
            "name": "ColorVariationDetail",
            "identifier": "Socket_31",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_ColorVariationDistortion": {
            "name": "ColorVariationDistortion",
            "identifier": "Socket_32",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_ColorVariationRoughness": {
            "name": "ColorVariationRoughness",
            "identifier": "Socket_33",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_Socket_Color": {
            "name": "Color",
            "identifier": "Socket_34",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_Socket_Roughness": {
            "name": "Roughness",
            "identifier": "Socket_36",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_38",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_SSSRadius": {
            "name": "SSSRadius",
            "identifier": "Socket_37",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_Socket_SSSScale": {
            "name": "SSSScale",
            "identifier": "Socket_41",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_39",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4
        },
        "Output_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_42",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_40",
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
                0.35,
                0.0,
                0.35
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
                -1208.3087,
                -5.6504
            ]
        },
        "use_custom_color": {
            "name": "use_custom_color",
            "class": "bool",
            "value": true
        },
        "width": {
            "name": "width",
            "class": "float",
            "value": 354.5488
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "ColorVarian",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Unevenness",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSWeight",
            "to_node": "SSS",
            "to_socket": "SSSWeight"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "SSS",
            "to_socket": "SSSScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "SSS",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "Spots",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Veins",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotStrength",
            "to_node": "Spots",
            "to_socket": "SpotStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotScaleMultiplier",
            "to_node": "Spots",
            "to_socket": "SpotScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDetail",
            "to_node": "Spots",
            "to_socket": "SpotDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDistortion",
            "to_node": "Spots",
            "to_socket": "SpotDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotRoughness",
            "to_node": "Spots",
            "to_socket": "SpotRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotValley",
            "to_node": "Spots",
            "to_socket": "SpotValley"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotPeak",
            "to_node": "Spots",
            "to_socket": "SpotPeak"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "SSS",
            "to_socket": "SSSRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "SSS",
            "to_socket": "SSSRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "SSS",
            "to_socket": "SSSRadiusZ"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
            "to_node": "Unevenness",
            "to_socket": "UnevennessScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessBumpStrength",
            "to_node": "Unevenness",
            "to_socket": "UnevennessBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "Unevenness",
            "to_socket": "UnevennessDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "Unevenness",
            "to_socket": "UnevennessDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "Unevenness",
            "to_socket": "UnevennessRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "Dermal",
            "to_socket": "DermalScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "Dermal",
            "to_socket": "DermalBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SmallVeinScaleMultiplier",
            "to_node": "Veins",
            "to_socket": "SmallVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScaleMultiplier",
            "to_node": "Veins",
            "to_socket": "LargeVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "Veins",
            "to_socket": "VeinStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScaleMultiplier",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationBrightness",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationBrightness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDetail",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDistortion",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationRoughness",
            "to_node": "ColorVarian",
            "to_socket": "ColorVariationRoughness"
        },
        {
            "from_node": "Unevenness",
            "from_socket": "Normal",
            "to_node": "Dermal",
            "to_socket": "Normal"
        },
        {
            "from_node": "ColorVarian",
            "from_socket": "Color",
            "to_node": "Veins",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Veins",
            "from_socket": "Color",
            "to_node": "Spots",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Dermal",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "Spots",
            "from_socket": "Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Roughness",
            "to_node": "Group Output",
            "to_socket": "Roughness"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSWeight",
            "to_node": "Group Output",
            "to_socket": "SSSWeight"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSRadius",
            "to_node": "Group Output",
            "to_socket": "SSSRadius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSScale",
            "to_node": "Group Output",
            "to_socket": "SSSScale"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSIor",
            "to_node": "Group Output",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSAnisotropy",
            "to_node": "Group Output",
            "to_socket": "SSSAnisotropy"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSAnisotropy",
            "to_node": "SSS",
            "to_socket": "SSSAnisotropy"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    -960.8616,
                    733.6772
                ],
                "use_custom_color": true,
                "width": 245.2778
            },
            "class": "MpfbSkinColorVariation",
            "input_socket_values": {},
            "label": "Skin color variation",
            "name": "ColorVarian",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    -458.1821,
                    638.4954
                ],
                "use_custom_color": true,
                "width": 210.2823
            },
            "class": "MpfbSkinVeins",
            "input_socket_values": {},
            "label": "Veins",
            "name": "Veins",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    -32.5884,
                    543.9255
                ],
                "use_custom_color": true,
                "width": 190.1191
            },
            "class": "MpfbSkinSpot",
            "input_socket_values": {},
            "label": "Spots",
            "name": "Spots",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    -249.8333,
                    -266.7137
                ],
                "use_custom_color": true,
                "width": 289.2502
            },
            "class": "MpfbSkinNormalUnevenness",
            "input_socket_values": {},
            "label": "Unevenness",
            "name": "Unevenness",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    175.0831,
                    -339.0752
                ],
                "use_custom_color": true,
                "width": 320.8665
            },
            "class": "MpfbSkinNormalDermal",
            "input_socket_values": {},
            "label": "Dermal",
            "name": "Dermal",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    972.3653,
                    122.3487
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
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    330.434,
                    97.355
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbSSSControl",
            "input_socket_values": {},
            "label": "SSS",
            "name": "SSS",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1462.442,
                    434.9085
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

class _NodeWrapperMpfbSkin(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [972.3653, 122.3487]
        nodes["Group Input"].location = [-1462.442, 434.9085]

        node("MpfbSkinColorVariation", "ColorVarian", label="Skin color variation", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-960.8616, 733.6772], "use_custom_color": True, "width": 245.2778})
        node("MpfbSkinVeins", "Veins", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-458.1821, 638.4954], "use_custom_color": True, "width": 210.2823})
        node("MpfbSkinSpot", "Spots", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-32.5884, 543.9255], "use_custom_color": True, "width": 190.1191})
        node("MpfbSkinNormalUnevenness", "Unevenness", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-249.8333, -266.7137], "use_custom_color": True, "width": 289.2502})
        node("MpfbSkinNormalDermal", "Dermal", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [175.0831, -339.0752], "use_custom_color": True, "width": 320.8665})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [330.434, 97.355], "use_custom_color": True, "width": 140.0})

        link("Group Input", "SkinColor", "ColorVarian", "Color")
        link("Group Input", "Normal", "Unevenness", "Normal")
        link("Group Input", "SSSWeight", "SSS", "SSSWeight")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SSSScaleMultiplier")
        link("Group Input", "SSSIor", "SSS", "SSSIor")
        link("Group Input", "SpotColor", "Spots", "SpotColor")
        link("Group Input", "VeinColor", "Veins", "VeinColor")
        link("Group Input", "SpotStrength", "Spots", "SpotStrength")
        link("Group Input", "SpotScaleMultiplier", "Spots", "SpotScaleMultiplier")
        link("Group Input", "SpotDetail", "Spots", "SpotDetail")
        link("Group Input", "SpotDistortion", "Spots", "SpotDistortion")
        link("Group Input", "SpotRoughness", "Spots", "SpotRoughness")
        link("Group Input", "SpotValley", "Spots", "SpotValley")
        link("Group Input", "SpotPeak", "Spots", "SpotPeak")
        link("Group Input", "SSSRadiusX", "SSS", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SSSRadiusZ")
        link("Group Input", "UnevennessScaleMultiplier", "Unevenness", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "Unevenness", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "Unevenness", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "Unevenness", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "Unevenness", "UnevennessRoughness")
        link("Group Input", "DermalScaleMultiplier", "Dermal", "DermalScaleMultiplier")
        link("Group Input", "DermalBumpStrength", "Dermal", "DermalBumpStrength")
        link("Group Input", "SmallVeinScaleMultiplier", "Veins", "SmallVeinScaleMultiplier")
        link("Group Input", "LargeVeinScaleMultiplier", "Veins", "LargeVeinScaleMultiplier")
        link("Group Input", "VeinStrength", "Veins", "VeinStrength")
        link("Group Input", "ColorVariationStrength", "ColorVarian", "ColorVariationStrength")
        link("Group Input", "ColorVariationScaleMultiplier", "ColorVarian", "ColorVariationScaleMultiplier")
        link("Group Input", "ColorVariationBrightness", "ColorVarian", "ColorVariationBrightness")
        link("Group Input", "ColorVariationDetail", "ColorVarian", "ColorVariationDetail")
        link("Group Input", "ColorVariationDistortion", "ColorVarian", "ColorVariationDistortion")
        link("Group Input", "ColorVariationRoughness", "ColorVarian", "ColorVariationRoughness")
        link("Group Input", "Roughness", "Group Output", "Roughness")
        link("Group Input", "SSSAnisotropy", "SSS", "SSSAnisotropy")
        link("Unevenness", "Normal", "Dermal", "Normal")
        link("ColorVarian", "Color", "Veins", "SkinColor")
        link("Veins", "Color", "Spots", "SkinColor")
        link("Dermal", "Normal", "Group Output", "Normal")
        link("Spots", "Color", "Group Output", "Color")
        link("Group Input", "Roughness", "Group Output", "Roughness")
        link("SSS", "SSSWeight", "Group Output", "SSSWeight")
        link("SSS", "SSSRadius", "Group Output", "SSSRadius")
        link("SSS", "SSSScale", "Group Output", "SSSScale")
        link("SSS", "SSSIor", "Group Output", "SSSIor")
        link("SSS", "SSSAnisotropy", "Group Output", "SSSAnisotropy")

NodeWrapperMpfbSkin = _NodeWrapperMpfbSkin()
