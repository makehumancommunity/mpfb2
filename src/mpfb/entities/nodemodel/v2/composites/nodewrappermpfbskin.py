import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSkin",
    "inputs": {
        "Input_0": {
            "name": "SkinColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.807,
                0.565,
                0.4356,
                1.0
            ]
        },
        "Input_10": {
            "name": "SpotColor",
            "identifier": "Input_10",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_12": {
            "name": "VeinColor",
            "identifier": "Input_12",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
        },
        "Input_30": {
            "name": "Roughness",
            "identifier": "Input_30",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_1": {
            "name": "Normal",
            "identifier": "Input_1",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_7": {
            "name": "SSSStrength",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_8": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Input_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_9": {
            "name": "SSSIor",
            "identifier": "Input_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_20": {
            "name": "SSSRadiusX",
            "identifier": "Input_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_21": {
            "name": "SSSRadiusY",
            "identifier": "Input_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_22": {
            "name": "SSSRadiusZ",
            "identifier": "Input_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_13": {
            "name": "SpotStrength",
            "identifier": "Input_13",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_14": {
            "name": "SpotScaleMultiplier",
            "identifier": "Input_14",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 20.0,
            "min_value": 0.1,
            "max_value": 10000.0
        },
        "Input_15": {
            "name": "SpotDetail",
            "identifier": "Input_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_16": {
            "name": "SpotDistortion",
            "identifier": "Input_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_17": {
            "name": "SpotRoughness",
            "identifier": "Input_17",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_18": {
            "name": "SpotValley",
            "identifier": "Input_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_19": {
            "name": "SpotPeak",
            "identifier": "Input_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        },
        "Input_23": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Input_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 150.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_24": {
            "name": "UnevennessBumpStrength",
            "identifier": "Input_24",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_25": {
            "name": "UnevennessDetail",
            "identifier": "Input_25",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_26": {
            "name": "UnevennessDistortion",
            "identifier": "Input_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_27": {
            "name": "UnevennessRoughness",
            "identifier": "Input_27",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_28": {
            "name": "DermalScaleMultiplier",
            "identifier": "Input_28",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_29": {
            "name": "DermalBumpStrength",
            "identifier": "Input_29",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_32": {
            "name": "SmallVeinScaleMultiplier",
            "identifier": "Input_32",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_33": {
            "name": "LargeVeinScaleMultiplier",
            "identifier": "Input_33",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_34": {
            "name": "VeinStrength",
            "identifier": "Input_34",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.08,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_35": {
            "name": "ColorVariationStrength",
            "identifier": "Input_35",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_36": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Input_36",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 30.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_37": {
            "name": "ColorVariationBrightness",
            "identifier": "Input_37",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_38": {
            "name": "ColorVariationDetail",
            "identifier": "Input_38",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_39": {
            "name": "ColorVariationDistortion",
            "identifier": "Input_39",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_40": {
            "name": "ColorVariationRoughness",
            "identifier": "Input_40",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_11": {
            "name": "Color",
            "identifier": "Output_11",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_3": {
            "name": "SubsurfaceColor",
            "identifier": "Output_3",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Output_31": {
            "name": "Roughness",
            "identifier": "Output_31",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_4": {
            "name": "SSSRadius",
            "identifier": "Output_4",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Output_5": {
            "name": "SSSStrength",
            "identifier": "Output_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Output_6": {
            "name": "SSSIor",
            "identifier": "Output_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4
        },
        "Output_2": {
            "name": "Normal",
            "identifier": "Output_2",
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
                -1208.3087,
                -5.6504
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
            "from_node": "Dermal",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceColor",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceRadius",
            "to_node": "Group Output",
            "to_socket": "SSSRadius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Group Output",
            "to_socket": "SSSStrength"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceIor",
            "to_node": "Group Output",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSStrength",
            "to_node": "SSS",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "SSS",
            "to_socket": "SubsurfaceRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "SSS",
            "to_socket": "SubsurfaceIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "Spots",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "Spots",
            "from_socket": "Color",
            "to_node": "Group Output",
            "to_socket": "Color"
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
            "to_socket": "SubSurfaceRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "SSS",
            "to_socket": "SubSurfaceRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "SSS",
            "to_socket": "SubSurfaceRadiusZ"
        },
        {
            "from_node": "Unevenness",
            "from_socket": "Normal",
            "to_node": "Dermal",
            "to_socket": "Normal"
        },
        {
            "from_node": "Spots",
            "from_socket": "Color",
            "to_node": "SSS",
            "to_socket": "SubsurfaceColor"
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
            "from_socket": "Roughness",
            "to_node": "Group Output",
            "to_socket": "Roughness"
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
        }
    ],
    "nodes": [
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
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -960.8616,
                    733.6772
                ],
                "use_custom_color": false,
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
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -458.1821,
                    638.4954
                ],
                "use_custom_color": false,
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
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -32.5884,
                    543.9255
                ],
                "use_custom_color": false,
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
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -249.8333,
                    -266.7137
                ],
                "use_custom_color": false,
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
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    175.0831,
                    -339.0752
                ],
                "use_custom_color": false,
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
                "color": [
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    348.2335,
                    172.3807
                ],
                "use_custom_color": false,
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

        node("MpfbSkinColorVariation", "ColorVarian", label="Skin color variation", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-960.8616, 733.6772], "use_custom_color": False, "width": 245.2778})
        node("MpfbSkinVeins", "Veins", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-458.1821, 638.4954], "use_custom_color": False, "width": 210.2823})
        node("MpfbSkinSpot", "Spots", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-32.5884, 543.9255], "use_custom_color": False, "width": 190.1191})
        node("MpfbSkinNormalUnevenness", "Unevenness", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-249.8333, -266.7137], "use_custom_color": False, "width": 289.2502})
        node("MpfbSkinNormalDermal", "Dermal", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [175.0831, -339.0752], "use_custom_color": False, "width": 320.8665})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [348.2335, 172.3807], "use_custom_color": False, "width": 140.0})

        link("Group Input", "SkinColor", "ColorVarian", "Color")
        link("Group Input", "Normal", "Unevenness", "Normal")
        link("Group Input", "SSSStrength", "SSS", "SubsurfaceStrength")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "SSSIor", "SSS", "SubsurfaceIor")
        link("Group Input", "SpotColor", "Spots", "SpotColor")
        link("Group Input", "VeinColor", "Veins", "VeinColor")
        link("Group Input", "SpotStrength", "Spots", "SpotStrength")
        link("Group Input", "SpotScaleMultiplier", "Spots", "SpotScaleMultiplier")
        link("Group Input", "SpotDetail", "Spots", "SpotDetail")
        link("Group Input", "SpotDistortion", "Spots", "SpotDistortion")
        link("Group Input", "SpotRoughness", "Spots", "SpotRoughness")
        link("Group Input", "SpotValley", "Spots", "SpotValley")
        link("Group Input", "SpotPeak", "Spots", "SpotPeak")
        link("Group Input", "SSSRadiusX", "SSS", "SubSurfaceRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SubSurfaceRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SubSurfaceRadiusZ")
        link("Group Input", "UnevennessScaleMultiplier", "Unevenness", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "Unevenness", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "Unevenness", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "Unevenness", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "Unevenness", "UnevennessRoughness")
        link("Group Input", "DermalScaleMultiplier", "Dermal", "DermalScaleMultiplier")
        link("Group Input", "DermalBumpStrength", "Dermal", "DermalBumpStrength")
        link("Group Input", "Roughness", "Group Output", "Roughness")
        link("Group Input", "SmallVeinScaleMultiplier", "Veins", "SmallVeinScaleMultiplier")
        link("Group Input", "LargeVeinScaleMultiplier", "Veins", "LargeVeinScaleMultiplier")
        link("Group Input", "VeinStrength", "Veins", "VeinStrength")
        link("Group Input", "ColorVariationStrength", "ColorVarian", "ColorVariationStrength")
        link("Group Input", "ColorVariationScaleMultiplier", "ColorVarian", "ColorVariationScaleMultiplier")
        link("Group Input", "ColorVariationBrightness", "ColorVarian", "ColorVariationBrightness")
        link("Group Input", "ColorVariationDetail", "ColorVarian", "ColorVariationDetail")
        link("Group Input", "ColorVariationDistortion", "ColorVarian", "ColorVariationDistortion")
        link("Group Input", "ColorVariationRoughness", "ColorVarian", "ColorVariationRoughness")
        link("Unevenness", "Normal", "Dermal", "Normal")
        link("Spots", "Color", "SSS", "SubsurfaceColor")
        link("ColorVarian", "Color", "Veins", "SkinColor")
        link("Veins", "Color", "Spots", "SkinColor")
        link("Dermal", "Normal", "Group Output", "Normal")
        link("SSS", "SubsurfaceColor", "Group Output", "SubsurfaceColor")
        link("SSS", "SubsurfaceRadius", "Group Output", "SSSRadius")
        link("SSS", "SubsurfaceStrength", "Group Output", "SSSStrength")
        link("SSS", "SubsurfaceIor", "Group Output", "SSSIor")
        link("Spots", "Color", "Group Output", "Color")
        link("Group Input", "Roughness", "Group Output", "Roughness")

NodeWrapperMpfbSkin = _NodeWrapperMpfbSkin()
