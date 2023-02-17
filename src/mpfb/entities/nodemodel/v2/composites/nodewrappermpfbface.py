import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbFace",
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
        "Input_9": {
            "name": "SpotColor",
            "identifier": "Input_9",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0762,
                0.0137,
                0.003,
                1.0
            ]
        },
        "Input_10": {
            "name": "VeinColor",
            "identifier": "Input_10",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
        },
        "Input_7": {
            "name": "EyelidColor",
            "identifier": "Input_7",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.2664,
                0.0802,
                0.0273,
                1.0
            ]
        },
        "Input_2": {
            "name": "Normal",
            "identifier": "Input_2",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_1": {
            "name": "Roughness",
            "identifier": "Input_1",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.35
        },
        "Input_4": {
            "name": "SSSStrength",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_5": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Input_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_6": {
            "name": "SSSIor",
            "identifier": "Input_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_18": {
            "name": "SSSRadiusX",
            "identifier": "Input_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_19": {
            "name": "SSSRadiusY",
            "identifier": "Input_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_20": {
            "name": "SSSRadiusZ",
            "identifier": "Input_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_11": {
            "name": "SpotStrength",
            "identifier": "Input_11",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.6
        },
        "Input_12": {
            "name": "SpotScaleMultiplier",
            "identifier": "Input_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 21.0,
            "min_value": 0.1,
            "max_value": 10000.0
        },
        "Input_13": {
            "name": "SpotDetail",
            "identifier": "Input_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_14": {
            "name": "SpotDistortion",
            "identifier": "Input_14",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_15": {
            "name": "SpotRoughness",
            "identifier": "Input_15",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Input_16": {
            "name": "SpotValley",
            "identifier": "Input_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_17": {
            "name": "SpotPeak",
            "identifier": "Input_17",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        },
        "Input_21": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Input_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 200.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_22": {
            "name": "UnevennessBumpStrength",
            "identifier": "Input_22",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1
        },
        "Input_23": {
            "name": "UnevennessDetail",
            "identifier": "Input_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_24": {
            "name": "UnevennessDistortion",
            "identifier": "Input_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_25": {
            "name": "UnevennessRoughness",
            "identifier": "Input_25",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0
        },
        "Input_26": {
            "name": "DermalScaleMultiplier",
            "identifier": "Input_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 120.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_27": {
            "name": "DermalBumpStrength",
            "identifier": "Input_27",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1
        },
        "Input_28": {
            "name": "SmallVeinScaleMultiplier",
            "identifier": "Input_28",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_29": {
            "name": "LargeVeinScaleMultiplier",
            "identifier": "Input_29",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_30": {
            "name": "VeinStrength",
            "identifier": "Input_30",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.08,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_31": {
            "name": "ColorVariationStrength",
            "identifier": "Input_31",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.15
        },
        "Input_32": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Input_32",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 30.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_33": {
            "name": "ColorVariationBrightness",
            "identifier": "Input_33",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_34": {
            "name": "ColorVariationDetail",
            "identifier": "Input_34",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_35": {
            "name": "ColorVariationDistortion",
            "identifier": "Input_35",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_36": {
            "name": "ColorVariationRoughness",
            "identifier": "Input_36",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0
        }
    },
    "outputs": {
        "Output_3": {
            "name": "BSDF",
            "identifier": "Output_3",
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
                709.2263,
                1507.9869
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
            "value": 331.479
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Principled BSDF.001",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group.001",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EyelidColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Skin",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Skin",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSStrength",
            "to_node": "Skin",
            "to_socket": "SSSStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMultiplyer",
            "to_node": "Skin",
            "to_socket": "SSSRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSIor",
            "to_node": "Skin",
            "to_socket": "SSSIor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotColor",
            "to_node": "Skin",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Skin",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotStrength",
            "to_node": "Skin",
            "to_socket": "SpotStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "SpotScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDetail",
            "to_node": "Skin",
            "to_socket": "SpotDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotDistortion",
            "to_node": "Skin",
            "to_socket": "SpotDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotRoughness",
            "to_node": "Skin",
            "to_socket": "SpotRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotValley",
            "to_node": "Skin",
            "to_socket": "SpotValley"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SpotPeak",
            "to_node": "Skin",
            "to_socket": "SpotPeak"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusX",
            "to_node": "Skin",
            "to_socket": "SSSRadiusX"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusY",
            "to_node": "Skin",
            "to_socket": "SSSRadiusY"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusZ",
            "to_node": "Skin",
            "to_socket": "SSSRadiusZ"
        },
        {
            "from_node": "Skin",
            "from_socket": "Normal",
            "to_node": "Principled BSDF.001",
            "to_socket": "Normal"
        },
        {
            "from_node": "Skin",
            "from_socket": "SubsurfaceColor",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Color"
        },
        {
            "from_node": "Skin",
            "from_socket": "Color",
            "to_node": "Principled BSDF.001",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Skin",
            "from_socket": "SSSRadius",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "Skin",
            "from_socket": "SSSStrength",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface"
        },
        {
            "from_node": "Skin",
            "from_socket": "SSSIor",
            "to_node": "Principled BSDF.001",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Roughness",
            "to_node": "Skin",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Skin",
            "from_socket": "Roughness",
            "to_node": "Principled BSDF.001",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "UnevennessScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessBumpStrength",
            "to_node": "Skin",
            "to_socket": "UnevennessBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "Skin",
            "to_socket": "UnevennessDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "Skin",
            "to_socket": "UnevennessDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "Skin",
            "to_socket": "UnevennessRoughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "DermalScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DermalBumpStrength",
            "to_node": "Skin",
            "to_socket": "DermalBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SmallVeinScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "SmallVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "LargeVeinScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "Skin",
            "to_socket": "VeinStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "Skin",
            "to_socket": "ColorVariationStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScaleMultiplier",
            "to_node": "Skin",
            "to_socket": "ColorVariationScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationBrightness",
            "to_node": "Skin",
            "to_socket": "ColorVariationBrightness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDetail",
            "to_node": "Skin",
            "to_socket": "ColorVariationDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationDistortion",
            "to_node": "Skin",
            "to_socket": "ColorVariationDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationRoughness",
            "to_node": "Skin",
            "to_socket": "ColorVariationRoughness"
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
                    -1468.9873,
                    748.6599
                ],
                "use_custom_color": false,
                "width": 297.9847
            },
            "class": "MpfbSystemValueTextureEyelids",
            "input_socket_values": {},
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    -1069.4127,
                    762.9279
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "B_Color": [
                    0.2655,
                    0.081,
                    0.0278,
                    1.0
                ]
            },
            "label": "Mix",
            "name": "Mix",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -144.3404,
                    677.2473
                ]
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {
                "Base Color": [
                    0.8,
                    0.6037,
                    0.5003,
                    1.0
                ],
                "Roughness": 0.35
            },
            "label": "Principled BSDF.001",
            "name": "Principled BSDF.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    233.8077,
                    683.8954
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
                    -747.6187,
                    798.8463
                ],
                "use_custom_color": false,
                "width": 400.0
            },
            "class": "MpfbSkin",
            "input_socket_values": {},
            "label": "Skin Settings",
            "name": "Skin",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1687.5262,
                    336.8824
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

class _NodeWrapperMpfbFace(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [233.8077, 683.8954]
        nodes["Group Input"].location = [-1687.5262, 336.8824]

        node("MpfbSystemValueTextureEyelids", "Group.001", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1468.9873, 748.6599], "use_custom_color": False, "width": 297.9847})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [-1069.4127, 762.9279]}, input_socket_values={"B_Color": [0.2655, 0.081, 0.0278, 1.0]})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF.001", attribute_values={"location": [-144.3404, 677.2473]}, input_socket_values={"Base Color": [0.8, 0.6037, 0.5003, 1.0], "Roughness": 0.35})
        node("MpfbSkin", "Skin", label="Skin Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-747.6187, 798.8463], "use_custom_color": False, "width": 400.0})

        link("Group Input", "SkinColor", "Mix", "A_Color")
        link("Group Input", "EyelidColor", "Mix", "B_Color")
        link("Group Input", "Normal", "Skin", "Normal")
        link("Group Input", "SSSStrength", "Skin", "SSSStrength")
        link("Group Input", "SSSRadiusMultiplyer", "Skin", "SSSRadiusMultiplyer")
        link("Group Input", "SSSIor", "Skin", "SSSIor")
        link("Group Input", "SpotColor", "Skin", "SpotColor")
        link("Group Input", "VeinColor", "Skin", "VeinColor")
        link("Group Input", "SpotStrength", "Skin", "SpotStrength")
        link("Group Input", "SpotScaleMultiplier", "Skin", "SpotScaleMultiplier")
        link("Group Input", "SpotDetail", "Skin", "SpotDetail")
        link("Group Input", "SpotDistortion", "Skin", "SpotDistortion")
        link("Group Input", "SpotRoughness", "Skin", "SpotRoughness")
        link("Group Input", "SpotValley", "Skin", "SpotValley")
        link("Group Input", "SpotPeak", "Skin", "SpotPeak")
        link("Group Input", "SSSRadiusX", "Skin", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "Skin", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "Skin", "SSSRadiusZ")
        link("Group Input", "Roughness", "Skin", "Roughness")
        link("Group Input", "UnevennessScaleMultiplier", "Skin", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "Skin", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "Skin", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "Skin", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "Skin", "UnevennessRoughness")
        link("Group Input", "DermalScaleMultiplier", "Skin", "DermalScaleMultiplier")
        link("Group Input", "DermalBumpStrength", "Skin", "DermalBumpStrength")
        link("Group Input", "SmallVeinScaleMultiplier", "Skin", "SmallVeinScaleMultiplier")
        link("Group Input", "LargeVeinScaleMultiplier", "Skin", "LargeVeinScaleMultiplier")
        link("Group Input", "VeinStrength", "Skin", "VeinStrength")
        link("Group Input", "ColorVariationStrength", "Skin", "ColorVariationStrength")
        link("Group Input", "ColorVariationScaleMultiplier", "Skin", "ColorVariationScaleMultiplier")
        link("Group Input", "ColorVariationBrightness", "Skin", "ColorVariationBrightness")
        link("Group Input", "ColorVariationDetail", "Skin", "ColorVariationDetail")
        link("Group Input", "ColorVariationDistortion", "Skin", "ColorVariationDistortion")
        link("Group Input", "ColorVariationRoughness", "Skin", "ColorVariationRoughness")
        link("Group.001", "Value", "Mix", "Factor_Float")
        link("Mix", "Result_Color", "Skin", "SkinColor")
        link("Skin", "Normal", "Principled BSDF.001", "Normal")
        link("Skin", "SubsurfaceColor", "Principled BSDF.001", "Subsurface Color")
        link("Skin", "Color", "Principled BSDF.001", "Base Color")
        link("Skin", "SSSRadius", "Principled BSDF.001", "Subsurface Radius")
        link("Skin", "SSSStrength", "Principled BSDF.001", "Subsurface")
        link("Skin", "SSSIor", "Principled BSDF.001", "Subsurface IOR")
        link("Skin", "Roughness", "Principled BSDF.001", "Roughness")
        link("Principled BSDF.001", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbFace = _NodeWrapperMpfbFace()
