import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbBody",
    "inputs": {
        "Input_0": {
            "name": "SkinColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_8": {
            "name": "SpotColor",
            "identifier": "Input_8",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_1": {
            "name": "NavelCenterColor",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_9": {
            "name": "VeinColor",
            "identifier": "Input_9",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
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
        },
        "Input_2": {
            "name": "Roughness",
            "identifier": "Input_2",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.35,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_5": {
            "name": "SSSStrength",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_6": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Input_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_7": {
            "name": "SSSIor",
            "identifier": "Input_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_21": {
            "name": "SSSRadiusX",
            "identifier": "Input_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_22": {
            "name": "SSSRadiusY",
            "identifier": "Input_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_23": {
            "name": "SSSRadiusZ",
            "identifier": "Input_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_42": {
            "name": "NavelColorStrength",
            "identifier": "Input_42",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_40": {
            "name": "NavelWidthMultiplier",
            "identifier": "Input_40",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 11.0,
            "min_value": 0.001,
            "max_value": 0.2
        },
        "Input_41": {
            "name": "NavelBumpStrength",
            "identifier": "Input_41",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_14": {
            "name": "SpotStrength",
            "identifier": "Input_14",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_15": {
            "name": "SpotScaleMultiplier",
            "identifier": "Input_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 20.0,
            "min_value": 0.0001,
            "max_value": 1000.0
        },
        "Input_16": {
            "name": "SpotDetail",
            "identifier": "Input_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_17": {
            "name": "SpotDistortion",
            "identifier": "Input_17",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_18": {
            "name": "SpotRoughness",
            "identifier": "Input_18",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_19": {
            "name": "SpotValley",
            "identifier": "Input_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_20": {
            "name": "SpotPeak",
            "identifier": "Input_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        },
        "Input_24": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Input_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 150.0,
            "min_value": 0.0001,
            "max_value": 1000.0
        },
        "Input_25": {
            "name": "UnevennessBumpStrength",
            "identifier": "Input_25",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_26": {
            "name": "UnevennessDetail",
            "identifier": "Input_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_27": {
            "name": "UnevennessDistortion",
            "identifier": "Input_27",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_28": {
            "name": "UnevennessRoughness",
            "identifier": "Input_28",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_29": {
            "name": "DermalScaleMultiplier",
            "identifier": "Input_29",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_30": {
            "name": "DermalBumpStrength",
            "identifier": "Input_30",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_31": {
            "name": "SmallVeinScaleMultiplier",
            "identifier": "Input_31",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_32": {
            "name": "LargeVeinScaleMultiplier",
            "identifier": "Input_32",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_33": {
            "name": "VeinStrength",
            "identifier": "Input_33",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.08,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_34": {
            "name": "ColorVariationStrength",
            "identifier": "Input_34",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.25,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_35": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Input_35",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 35.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_36": {
            "name": "ColorVariationBrightness",
            "identifier": "Input_36",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_37": {
            "name": "ColorVariationDetail",
            "identifier": "Input_37",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_38": {
            "name": "ColorVariationDistortion",
            "identifier": "Input_38",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_39": {
            "name": "ColorVariationRoughness",
            "identifier": "Input_39",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_4": {
            "name": "BSDF",
            "identifier": "Output_4",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
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
                711.826,
                2404.9126
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
            "value": 315.4109
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "NavelSettings",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelCenterColor",
            "to_node": "NavelSettings",
            "to_socket": "NavelCenterColor"
        },
        {
            "from_node": "NavelSettings",
            "from_socket": "Normal",
            "to_node": "bodyskingroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "NavelSettings",
            "to_socket": "Normal"
        },
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SubsurfaceColor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Color"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSRadius",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSStrength",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSIor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSStrength",
            "to_node": "bodyskingroup",
            "to_socket": "SSSStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "bodyskingroup",
            "to_socket": "SSSRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "bodyskingroup",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "bodyskingroup",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "Color",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "bodyskingroup",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotStrength",
            "to_node": "bodyskingroup",
            "to_socket": "SpotStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "SpotScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDetail",
            "to_node": "bodyskingroup",
            "to_socket": "SpotDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDistortion",
            "to_node": "bodyskingroup",
            "to_socket": "SpotDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotRoughness",
            "to_node": "bodyskingroup",
            "to_socket": "SpotRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotValley",
            "to_node": "bodyskingroup",
            "to_socket": "SpotValley"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotPeak",
            "to_node": "bodyskingroup",
            "to_socket": "SpotPeak"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "bodyskingroup",
            "to_socket": "SSSRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "bodyskingroup",
            "to_socket": "SSSRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "bodyskingroup",
            "to_socket": "SSSRadiusZ"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Roughness",
            "to_node": "bodyskingroup",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "UnevennessScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessBumpStrength",
            "to_node": "bodyskingroup",
            "to_socket": "UnevennessBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "bodyskingroup",
            "to_socket": "UnevennessDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "bodyskingroup",
            "to_socket": "UnevennessDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "bodyskingroup",
            "to_socket": "UnevennessRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "DermalScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "bodyskingroup",
            "to_socket": "DermalBumpStrength"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "Roughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SmallVeinScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "SmallVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "LargeVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "bodyskingroup",
            "to_socket": "VeinStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScaleMultiplier",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationBrightness",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationBrightness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDetail",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDistortion",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationRoughness",
            "to_node": "bodyskingroup",
            "to_socket": "ColorVariationRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelWidthMultiplier",
            "to_node": "NavelSettings",
            "to_socket": "NavelWidthMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelBumpStrength",
            "to_node": "NavelSettings",
            "to_socket": "NavelBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelColorStrength",
            "to_node": "NavelSettings",
            "to_socket": "NavelColorStrength"
        },
        {
            "from_node": "NavelSettings",
            "from_socket": "SkinColor",
            "to_node": "bodyskingroup",
            "to_socket": "SkinColor"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -583.7446,
                    130.6071
                ]
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {},
            "label": "Principled BSDF",
            "name": "Principled BSDF",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -273.2507,
                    132.5241
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
                    -1208.3087,
                    -5.6504
                ],
                "use_custom_color": false,
                "width": 354.5488
            },
            "class": "MpfbSkin",
            "input_socket_values": {},
            "label": "Skin Settings",
            "name": "bodyskingroup",
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
                    -1609.5137,
                    126.2919
                ],
                "use_custom_color": false,
                "width": 272.0078
            },
            "class": "MpfbSkinNavel",
            "input_socket_values": {},
            "label": "Navel Settings",
            "name": "NavelSettings",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1994.3385,
                    -73.7013
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

class _NodeWrapperMpfbBody(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [-273.2507, 132.5241]
        nodes["Group Input"].location = [-1994.3385, -73.7013]

        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [-583.7446, 130.6071]})
        node("MpfbSkin", "bodyskingroup", label="Skin Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1208.3087, -5.6504], "use_custom_color": False, "width": 354.5488})
        node("MpfbSkinNavel", "NavelSettings", label="Navel Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1609.5137, 126.2919], "use_custom_color": False, "width": 272.0078})

        link("Group Input", "SkinColor", "NavelSettings", "SkinColor")
        link("Group Input", "NavelCenterColor", "NavelSettings", "NavelCenterColor")
        link("Group Input", "Normal", "NavelSettings", "Normal")
        link("Group Input", "SSSStrength", "bodyskingroup", "SSSStrength")
        link("Group Input", "SSSRadiusMultiplyer", "bodyskingroup", "SSSRadiusMultiplyer")
        link("Group Input", "SSSIor", "bodyskingroup", "SSSIor")
        link("Group Input", "SpotColor", "bodyskingroup", "SpotColor")
        link("Group Input", "VeinColor", "bodyskingroup", "VeinColor")
        link("Group Input", "SpotStrength", "bodyskingroup", "SpotStrength")
        link("Group Input", "SpotScaleMultiplier", "bodyskingroup", "SpotScaleMultiplier")
        link("Group Input", "SpotDetail", "bodyskingroup", "SpotDetail")
        link("Group Input", "SpotDistortion", "bodyskingroup", "SpotDistortion")
        link("Group Input", "SpotRoughness", "bodyskingroup", "SpotRoughness")
        link("Group Input", "SpotValley", "bodyskingroup", "SpotValley")
        link("Group Input", "SpotPeak", "bodyskingroup", "SpotPeak")
        link("Group Input", "SSSRadiusX", "bodyskingroup", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "bodyskingroup", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "bodyskingroup", "SSSRadiusZ")
        link("Group Input", "Roughness", "bodyskingroup", "Roughness")
        link("Group Input", "UnevennessScaleMultiplier", "bodyskingroup", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "bodyskingroup", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "bodyskingroup", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "bodyskingroup", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "bodyskingroup", "UnevennessRoughness")
        link("Group Input", "DermalScaleMultiplier", "bodyskingroup", "DermalScaleMultiplier")
        link("Group Input", "DermalBumpStrength", "bodyskingroup", "DermalBumpStrength")
        link("Group Input", "SmallVeinScaleMultiplier", "bodyskingroup", "SmallVeinScaleMultiplier")
        link("Group Input", "LargeVeinScaleMultiplier", "bodyskingroup", "LargeVeinScaleMultiplier")
        link("Group Input", "VeinStrength", "bodyskingroup", "VeinStrength")
        link("Group Input", "ColorVariationStrength", "bodyskingroup", "ColorVariationStrength")
        link("Group Input", "ColorVariationScaleMultiplier", "bodyskingroup", "ColorVariationScaleMultiplier")
        link("Group Input", "ColorVariationBrightness", "bodyskingroup", "ColorVariationBrightness")
        link("Group Input", "ColorVariationDetail", "bodyskingroup", "ColorVariationDetail")
        link("Group Input", "ColorVariationDistortion", "bodyskingroup", "ColorVariationDistortion")
        link("Group Input", "ColorVariationRoughness", "bodyskingroup", "ColorVariationRoughness")
        link("Group Input", "NavelWidthMultiplier", "NavelSettings", "NavelWidthMultiplier")
        link("Group Input", "NavelBumpStrength", "NavelSettings", "NavelBumpStrength")
        link("Group Input", "NavelColorStrength", "NavelSettings", "NavelColorStrength")
        link("NavelSettings", "Normal", "bodyskingroup", "Normal")
        link("bodyskingroup", "Normal", "Principled BSDF", "Normal")
        #link("bodyskingroup", "SubsurfaceColor", "Principled BSDF", "Subsurface Color")
        link("bodyskingroup", "SSSRadius", "Principled BSDF", "Subsurface Radius")
        link("bodyskingroup", "SSSStrength", "Principled BSDF", "Subsurface Weight")
        link("bodyskingroup", "SSSIor", "Principled BSDF", "Subsurface IOR")
        link("bodyskingroup", "Color", "Principled BSDF", "Base Color")
        link("bodyskingroup", "Roughness", "Principled BSDF", "Roughness")
        link("NavelSettings", "SkinColor", "bodyskingroup", "SkinColor")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbBody = _NodeWrapperMpfbBody()
