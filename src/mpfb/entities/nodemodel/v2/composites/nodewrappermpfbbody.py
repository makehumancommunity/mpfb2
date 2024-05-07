import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbBody",
    "inputs": {
        "Input_Socket_SkinColor": {
            "name": "SkinColor",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
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
        "Input_Socket_NavelCenterColor": {
            "name": "NavelCenterColor",
            "identifier": "Socket_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ]
        },
        "Input_Socket_VeinColor": {
            "name": "VeinColor",
            "identifier": "Socket_3",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ]
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
        "Input_Socket_Roughness": {
            "name": "Roughness",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.35,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusMultiplyer": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Socket_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_39",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.8,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_NavelColorStrength": {
            "name": "NavelColorStrength",
            "identifier": "Socket_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_NavelWidthMultiplier": {
            "name": "NavelWidthMultiplier",
            "identifier": "Socket_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 11.0,
            "min_value": 0.001,
            "max_value": 0.2
        },
        "Input_Socket_NavelBumpStrength": {
            "name": "NavelBumpStrength",
            "identifier": "Socket_14",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotStrength": {
            "name": "SpotStrength",
            "identifier": "Socket_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotScaleMultiplier": {
            "name": "SpotScaleMultiplier",
            "identifier": "Socket_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 20.0,
            "min_value": 0.0001,
            "max_value": 1000.0
        },
        "Input_Socket_SpotDetail": {
            "name": "SpotDetail",
            "identifier": "Socket_17",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_SpotDistortion": {
            "name": "SpotDistortion",
            "identifier": "Socket_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_SpotRoughness": {
            "name": "SpotRoughness",
            "identifier": "Socket_19",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SpotValley": {
            "name": "SpotValley",
            "identifier": "Socket_20",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.848,
            "min_value": 0.0,
            "max_value": 0.99
        },
        "Input_Socket_SpotPeak": {
            "name": "SpotPeak",
            "identifier": "Socket_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.916,
            "min_value": 0.01,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessScaleMultiplier": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Socket_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 150.0,
            "min_value": 0.0001,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessBumpStrength": {
            "name": "UnevennessBumpStrength",
            "identifier": "Socket_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessDetail": {
            "name": "UnevennessDetail",
            "identifier": "Socket_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_UnevennessDistortion": {
            "name": "UnevennessDistortion",
            "identifier": "Socket_25",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessRoughness": {
            "name": "UnevennessRoughness",
            "identifier": "Socket_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_DermalScaleMultiplier": {
            "name": "DermalScaleMultiplier",
            "identifier": "Socket_27",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_Socket_DermalBumpStrength": {
            "name": "DermalBumpStrength",
            "identifier": "Socket_28",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SmallVeinScaleMultiplier": {
            "name": "SmallVeinScaleMultiplier",
            "identifier": "Socket_29",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_LargeVeinScaleMultiplier": {
            "name": "LargeVeinScaleMultiplier",
            "identifier": "Socket_30",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_VeinStrength": {
            "name": "VeinStrength",
            "identifier": "Socket_31",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.08,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationStrength": {
            "name": "ColorVariationStrength",
            "identifier": "Socket_32",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.25,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationScaleMultiplier": {
            "name": "ColorVariationScaleMultiplier",
            "identifier": "Socket_33",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 35.0,
            "min_value": 0.0,
            "max_value": 1000.0
        },
        "Input_Socket_ColorVariationBrightness": {
            "name": "ColorVariationBrightness",
            "identifier": "Socket_34",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": -0.5,
            "min_value": -1.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationDetail": {
            "name": "ColorVariationDetail",
            "identifier": "Socket_35",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_ColorVariationDistortion": {
            "name": "ColorVariationDistortion",
            "identifier": "Socket_36",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.5,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_ColorVariationRoughness": {
            "name": "ColorVariationRoughness",
            "identifier": "Socket_37",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_Socket_BSDF": {
            "name": "BSDF",
            "identifier": "Socket_38",
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
                0.4,
                0.4,
                0.5
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
            "value": true
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
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "NavelSettings",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSWeight",
            "to_node": "bodyskingroup",
            "to_socket": "SSSWeight"
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
            "from_node": "bodyskingroup",
            "from_socket": "SSSRadius",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSWeight",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Weight"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSIor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "Color",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "Roughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
        },
        {
            "from_node": "NavelSettings",
            "from_socket": "SkinColor",
            "to_node": "bodyskingroup",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSAnisotropy",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Anisotropy"
        },
        {
            "from_node": "bodyskingroup",
            "from_socket": "SSSScale",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Scale"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSAnisotropy",
            "to_node": "bodyskingroup",
            "to_socket": "SSSAnisotropy"
        }
    ],
    "nodes": [
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
                "location": [
                    -583.7446,
                    130.6071
                ],
                "subsurface_method": "RANDOM_WALK_SKIN"
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {},
            "label": "Principled BSDF",
            "name": "Principled BSDF",
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
                    -1609.5137,
                    126.2919
                ],
                "use_custom_color": true,
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
                "color": [
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    -1208.3087,
                    -5.6504
                ],
                "use_custom_color": true,
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

        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [-583.7446, 130.6071], "subsurface_method": "RANDOM_WALK_SKIN"})
        node("MpfbSkinNavel", "NavelSettings", label="Navel Settings", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-1609.5137, 126.2919], "use_custom_color": True, "width": 272.0078})
        node("MpfbSkin", "bodyskingroup", label="Skin Settings", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-1208.3087, -5.6504], "use_custom_color": True, "width": 354.5488})

        link("Group Input", "SkinColor", "NavelSettings", "SkinColor")
        link("Group Input", "NavelCenterColor", "NavelSettings", "NavelCenterColor")
        link("Group Input", "Normal", "NavelSettings", "Normal")
        link("Group Input", "SSSWeight", "bodyskingroup", "SSSWeight")
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
        link("Group Input", "SSSAnisotropy", "bodyskingroup", "SSSAnisotropy")
        link("NavelSettings", "Normal", "bodyskingroup", "Normal")
        link("bodyskingroup", "Normal", "Principled BSDF", "Normal")
        link("bodyskingroup", "SSSRadius", "Principled BSDF", "Subsurface Radius")
        link("bodyskingroup", "SSSWeight", "Principled BSDF", "Subsurface Weight")
        link("bodyskingroup", "SSSIor", "Principled BSDF", "Subsurface IOR")
        link("bodyskingroup", "Color", "Principled BSDF", "Base Color")
        link("bodyskingroup", "Roughness", "Principled BSDF", "Roughness")
        link("NavelSettings", "SkinColor", "bodyskingroup", "SkinColor")
        link("bodyskingroup", "SSSAnisotropy", "Principled BSDF", "Subsurface Anisotropy")
        link("bodyskingroup", "SSSScale", "Principled BSDF", "Subsurface Scale")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbBody = _NodeWrapperMpfbBody()
