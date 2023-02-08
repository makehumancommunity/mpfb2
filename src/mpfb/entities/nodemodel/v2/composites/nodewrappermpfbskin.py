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
                -1208.3087,
                -5.6504
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
            "value": 354.5488
        }
    },
    "class": "MpfbSkin",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketColor",
            "default_value": [
                0.807,
                0.565,
                0.4356,
                1.0
            ],
            "identifier": "Input_0",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Input_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_1",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Input_10": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ],
            "identifier": "Input_10",
            "name": "SpotColor",
            "value_type": "RGBA"
        },
        "Input_12": {
            "class": "NodeSocketColor",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ],
            "identifier": "Input_12",
            "name": "VeinColor",
            "value_type": "RGBA"
        },
        "Input_13": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.6,
            "identifier": "Input_13",
            "name": "SpotStrength",
            "value_type": "VALUE"
        },
        "Input_14": {
            "class": "NodeSocketFloat",
            "default_value": 20.0,
            "identifier": "Input_14",
            "max_value": 10000.0,
            "min_value": 0.1,
            "name": "SpotScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_15": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_15",
            "max_value": 15.0,
            "min_value": 0.0,
            "name": "SpotDetail",
            "value_type": "VALUE"
        },
        "Input_16": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_16",
            "max_value": 1000.0,
            "min_value": -1000.0,
            "name": "SpotDistortion",
            "value_type": "VALUE"
        },
        "Input_17": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Input_17",
            "name": "SpotRoughness",
            "value_type": "VALUE"
        },
        "Input_18": {
            "class": "NodeSocketFloat",
            "default_value": 0.848,
            "identifier": "Input_18",
            "max_value": 0.99,
            "min_value": 0.0,
            "name": "SpotValley",
            "value_type": "VALUE"
        },
        "Input_19": {
            "class": "NodeSocketFloat",
            "default_value": 0.916,
            "identifier": "Input_19",
            "max_value": 1.0,
            "min_value": 0.01,
            "name": "SpotPeak",
            "value_type": "VALUE"
        },
        "Input_20": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_20",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SSSRadiusX",
            "value_type": "VALUE"
        },
        "Input_21": {
            "class": "NodeSocketFloat",
            "default_value": 0.2,
            "identifier": "Input_21",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SSSRadiusY",
            "value_type": "VALUE"
        },
        "Input_22": {
            "class": "NodeSocketFloat",
            "default_value": 0.1,
            "identifier": "Input_22",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SSSRadiusZ",
            "value_type": "VALUE"
        },
        "Input_23": {
            "class": "NodeSocketFloat",
            "default_value": 150.0,
            "identifier": "Input_23",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "UnevennessScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_24": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.1,
            "identifier": "Input_24",
            "name": "UnevennessBumpStrength",
            "value_type": "VALUE"
        },
        "Input_25": {
            "class": "NodeSocketFloat",
            "default_value": 3.0,
            "identifier": "Input_25",
            "max_value": 15.0,
            "min_value": 0.0,
            "name": "UnevennessDetail",
            "value_type": "VALUE"
        },
        "Input_26": {
            "class": "NodeSocketFloat",
            "default_value": 1.5,
            "identifier": "Input_26",
            "max_value": 1000.0,
            "min_value": -1000.0,
            "name": "UnevennessDistortion",
            "value_type": "VALUE"
        },
        "Input_27": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Input_27",
            "name": "UnevennessRoughness",
            "value_type": "VALUE"
        },
        "Input_28": {
            "class": "NodeSocketFloat",
            "default_value": 70.0,
            "identifier": "Input_28",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "DermalScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_29": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.15,
            "identifier": "Input_29",
            "name": "DermalBumpStrength",
            "value_type": "VALUE"
        },
        "Input_30": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_30",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "Roughness",
            "value_type": "VALUE"
        },
        "Input_32": {
            "class": "NodeSocketFloat",
            "default_value": 1.1,
            "identifier": "Input_32",
            "max_value": 100.0,
            "min_value": 0.0,
            "name": "SmallVeinScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_33": {
            "class": "NodeSocketFloat",
            "default_value": 0.6,
            "identifier": "Input_33",
            "max_value": 100.0,
            "min_value": 0.0,
            "name": "LargeVeinScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_34": {
            "class": "NodeSocketFloat",
            "default_value": 0.08,
            "identifier": "Input_34",
            "max_value": 1.0,
            "min_value": 0.0,
            "name": "VeinStrength",
            "value_type": "VALUE"
        },
        "Input_35": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.15,
            "identifier": "Input_35",
            "name": "ColorVariationStrength",
            "value_type": "VALUE"
        },
        "Input_36": {
            "class": "NodeSocketFloat",
            "default_value": 30.0,
            "identifier": "Input_36",
            "max_value": 1000.0,
            "min_value": 0.0,
            "name": "ColorVariationScaleMultiplier",
            "value_type": "VALUE"
        },
        "Input_37": {
            "class": "NodeSocketFloat",
            "default_value": -0.5,
            "identifier": "Input_37",
            "max_value": 1.0,
            "min_value": -1.0,
            "name": "ColorVariationBrightness",
            "value_type": "VALUE"
        },
        "Input_38": {
            "class": "NodeSocketFloat",
            "default_value": 1.0,
            "identifier": "Input_38",
            "max_value": 15.0,
            "min_value": 0.0,
            "name": "ColorVariationDetail",
            "value_type": "VALUE"
        },
        "Input_39": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_39",
            "max_value": 1000.0,
            "min_value": -1000.0,
            "name": "ColorVariationDistortion",
            "value_type": "VALUE"
        },
        "Input_40": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.0,
            "identifier": "Input_40",
            "name": "ColorVariationRoughness",
            "value_type": "VALUE"
        },
        "Input_7": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Input_7",
            "max_value": 3.4028234663852886e+38,
            "min_value": -3.4028234663852886e+38,
            "name": "SSSStrength",
            "value_type": "VALUE"
        },
        "Input_8": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_8",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SSSRadiusMultiplyer",
            "value_type": "VALUE"
        },
        "Input_9": {
            "class": "NodeSocketFloat",
            "default_value": 1.4,
            "identifier": "Input_9",
            "max_value": 3.4028234663852886e+38,
            "min_value": -3.4028234663852886e+38,
            "name": "SSSIor",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_11": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_11",
            "name": "Color",
            "value_type": "RGBA"
        },
        "Output_2": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_2",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Output_3": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Output_3",
            "name": "SubsurfaceColor",
            "value_type": "RGBA"
        },
        "Output_31": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_31",
            "name": "Roughness",
            "value_type": "VALUE"
        },
        "Output_4": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_4",
            "name": "SSSRadius",
            "value_type": "VECTOR"
        },
        "Output_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_5",
            "name": "SSSStrength",
            "value_type": "VALUE"
        },
        "Output_6": {
            "class": "NodeSocketFloat",
            "default_value": 1.4,
            "identifier": "Output_6",
            "name": "SSSIor",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Group.001",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Group.002",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group.004",
            "from_socket": "SubsurfaceColor",
            "to_node": "Group Output",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "Group.004",
            "from_socket": "SubsurfaceRadius",
            "to_node": "Group Output",
            "to_socket": "SSSRadius"
        },
        {
            "from_node": "Group.004",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Group Output",
            "to_socket": "SSSStrength"
        },
        {
            "from_node": "Group.004",
            "from_socket": "SubsurfaceIor",
            "to_node": "Group Output",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSStrength",
            "to_node": "Group.004",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "Group.004",
            "to_socket": "SubsurfaceRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "Group.004",
            "to_socket": "SubsurfaceIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "Group.003",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "Group.003",
            "from_socket": "Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Group.005",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotStrength",
            "to_node": "Group.003",
            "to_socket": "SpotStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotScaleMultiplier",
            "to_node": "Group.003",
            "to_socket": "SpotScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDetail",
            "to_node": "Group.003",
            "to_socket": "SpotDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDistortion",
            "to_node": "Group.003",
            "to_socket": "SpotDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotRoughness",
            "to_node": "Group.003",
            "to_socket": "SpotRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotValley",
            "to_node": "Group.003",
            "to_socket": "SpotValley"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotPeak",
            "to_node": "Group.003",
            "to_socket": "SpotPeak"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "Group.004",
            "to_socket": "SubSurfaceRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "Group.004",
            "to_socket": "SubSurfaceRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "Group.004",
            "to_socket": "SubSurfaceRadiusZ"
        },
        {
            "from_node": "Group.002",
            "from_socket": "Normal",
            "to_node": "Group",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group.003",
            "from_socket": "Color",
            "to_node": "Group.004",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "Group.001",
            "from_socket": "Color",
            "to_node": "Group.005",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Group.005",
            "from_socket": "Color",
            "to_node": "Group.003",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
            "to_node": "Group.002",
            "to_socket": "UnevennessScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessBumpStrength",
            "to_node": "Group.002",
            "to_socket": "UnevennessBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "Group.002",
            "to_socket": "UnevennessDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "Group.002",
            "to_socket": "UnevennessDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "Group.002",
            "to_socket": "UnevennessRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "Group",
            "to_socket": "DermalScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "Group",
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
            "to_node": "Group.005",
            "to_socket": "SmallVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScaleMultiplier",
            "to_node": "Group.005",
            "to_socket": "LargeVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "Group.005",
            "to_socket": "VeinStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "Group.001",
            "to_socket": "ColorVariationStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScaleMultiplier",
            "to_node": "Group.001",
            "to_socket": "ColorVariationScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationBrightness",
            "to_node": "Group.001",
            "to_socket": "ColorVariationBrightness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDetail",
            "to_node": "Group.001",
            "to_socket": "ColorVariationDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDistortion",
            "to_node": "Group.001",
            "to_socket": "ColorVariationDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationRoughness",
            "to_node": "Group.001",
            "to_socket": "ColorVariationRoughness"
        }
    ],
    "nodes": [
        {
            "attribute_values": {},
            "class": "MpfbSkinSpot",
            "input_socket_values": {},
            "label": "Group.003",
            "name": "Group.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {},
            "class": "MpfbSkinNormalUnevenness",
            "input_socket_values": {},
            "label": "Group.002",
            "name": "Group.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {},
            "class": "MpfbSkinNormalDermal",
            "input_socket_values": {},
            "label": "Group",
            "name": "Group",
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
            "attribute_values": {},
            "class": "MpfbSkinColorVariation",
            "input_socket_values": {},
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {},
            "class": "MpfbSSSControl",
            "input_socket_values": {},
            "label": "Group.004",
            "name": "Group.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {},
            "class": "MpfbSkinVeins",
            "input_socket_values": {},
            "label": "Group.005",
            "name": "Group.005",
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

        node("MpfbSkinSpot", "Group.003")
        node("MpfbSkinNormalUnevenness", "Group.002")
        node("MpfbSkinNormalDermal", "Group")
        node("MpfbSkinColorVariation", "Group.001")
        node("MpfbSSSControl", "Group.004")
        node("MpfbSkinVeins", "Group.005")

        link("Group Input", "SkinColor", "Group.001", "Color")
        link("Group Input", "Normal", "Group.002", "Normal")
        link("Group Input", "SSSStrength", "Group.004", "SubsurfaceStrength")
        link("Group Input", "SSSRadiusMultiplyer", "Group.004", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "SSSIor", "Group.004", "SubsurfaceIor")
        link("Group Input", "SpotColor", "Group.003", "SpotColor")
        link("Group Input", "VeinColor", "Group.005", "VeinColor")
        link("Group Input", "SpotStrength", "Group.003", "SpotStrength")
        link("Group Input", "SpotScaleMultiplier", "Group.003", "SpotScaleMultiplier")
        link("Group Input", "SpotDetail", "Group.003", "SpotDetail")
        link("Group Input", "SpotDistortion", "Group.003", "SpotDistortion")
        link("Group Input", "SpotRoughness", "Group.003", "SpotRoughness")
        link("Group Input", "SpotValley", "Group.003", "SpotValley")
        link("Group Input", "SpotPeak", "Group.003", "SpotPeak")
        link("Group Input", "SSSRadiusX", "Group.004", "SubSurfaceRadiusX")
        link("Group Input", "SSSRadiusY", "Group.004", "SubSurfaceRadiusY")
        link("Group Input", "SSSRadiusZ", "Group.004", "SubSurfaceRadiusZ")
        link("Group Input", "UnevennessScaleMultiplier", "Group.002", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "Group.002", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "Group.002", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "Group.002", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "Group.002", "UnevennessRoughness")
        link("Group Input", "DermalScaleMultiplier", "Group", "DermalScaleMultiplier")
        link("Group Input", "DermalBumpStrength", "Group", "DermalBumpStrength")
        link("Group Input", "Roughness", "Group Output", "Roughness")
        link("Group Input", "SmallVeinScaleMultiplier", "Group.005", "SmallVeinScaleMultiplier")
        link("Group Input", "LargeVeinScaleMultiplier", "Group.005", "LargeVeinScaleMultiplier")
        link("Group Input", "VeinStrength", "Group.005", "VeinStrength")
        link("Group Input", "ColorVariationStrength", "Group.001", "ColorVariationStrength")
        link("Group Input", "ColorVariationScaleMultiplier", "Group.001", "ColorVariationScaleMultiplier")
        link("Group Input", "ColorVariationBrightness", "Group.001", "ColorVariationBrightness")
        link("Group Input", "ColorVariationDetail", "Group.001", "ColorVariationDetail")
        link("Group Input", "ColorVariationDistortion", "Group.001", "ColorVariationDistortion")
        link("Group Input", "ColorVariationRoughness", "Group.001", "ColorVariationRoughness")
        link("Group.002", "Normal", "Group", "Normal")
        link("Group.003", "Color", "Group.004", "SubsurfaceColor")
        link("Group.001", "Color", "Group.005", "SkinColor")
        link("Group.005", "Color", "Group.003", "SkinColor")
        link("Group", "Normal", "Group Output", "Normal")
        link("Group.004", "SubsurfaceColor", "Group Output", "SubsurfaceColor")
        link("Group.004", "SubsurfaceRadius", "Group Output", "SSSRadius")
        link("Group.004", "SubsurfaceStrength", "Group Output", "SSSStrength")
        link("Group.004", "SubsurfaceIor", "Group Output", "SSSIor")
        link("Group.003", "Color", "Group Output", "Color")
        link("Group Input", "Roughness", "Group Output", "Roughness")

NodeWrapperMpfbSkin = _NodeWrapperMpfbSkin()
