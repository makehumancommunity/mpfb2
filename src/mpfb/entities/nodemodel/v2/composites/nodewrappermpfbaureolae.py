import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbAureolae",
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
        "Input_19": {
            "name": "Normal",
            "identifier": "Input_19",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Input_20": {
            "name": "Roughness",
            "identifier": "Input_20",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.45,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_21": {
            "name": "SSSStrength",
            "identifier": "Input_21",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_22": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Input_22",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_23": {
            "name": "SSSIor",
            "identifier": "Input_23",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_24": {
            "name": "SSSRadiusX",
            "identifier": "Input_24",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_25": {
            "name": "SSSRadiusY",
            "identifier": "Input_25",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_26": {
            "name": "SSSRadiusZ",
            "identifier": "Input_26",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_13": {
            "name": "AureolaeRadius",
            "identifier": "Input_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.25,
            "min_value": 0.001,
            "max_value": 0.3
        },
        "Input_15": {
            "name": "UnevennessScale",
            "identifier": "Input_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 120.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_16": {
            "name": "WartScale",
            "identifier": "Input_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 40.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_17": {
            "name": "ColorVariationStrength",
            "identifier": "Input_17",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.3,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_18": {
            "name": "ColorVariationScale",
            "identifier": "Input_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        }
    },
    "outputs": {
        "Output_12": {
            "name": "BSDF",
            "identifier": "Output_12",
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
                706.7771,
                -442.8696
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
            "value": 323.4169
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "UV",
            "to_node": "InRange",
            "to_socket": "Position"
        },
        {
            "from_node": "BodyConstants",
            "from_socket": "RightNippleCoordinate",
            "to_node": "InRange",
            "to_socket": "Coordinate1"
        },
        {
            "from_node": "BodyConstants",
            "from_socket": "LeftNippleCoordinate",
            "to_node": "InRange",
            "to_socket": "Coordinate2"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AureolaeRadius",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "InRange",
            "to_socket": "MaxDist"
        },
        {
            "from_node": "InRange",
            "from_socket": "ActualLeastDistance",
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "CharacterInfo",
            "from_socket": "scale_factor",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Group.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.003",
            "from_socket": "Value",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "ColorVariation",
            "from_socket": "Color",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Voronoi Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "CharacterInfo",
            "from_socket": "scale_factor",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Voronoi Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "Group.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.004",
            "from_socket": "Value",
            "to_node": "Bump.001",
            "to_socket": "Height"
        },
        {
            "from_node": "Voronoi Texture",
            "from_socket": "Distance",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Bump.001",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScale",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "WartScale",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Color",
            "to_node": "ColorVariation",
            "to_socket": "Color"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationStrength",
            "to_node": "ColorVariation",
            "to_socket": "ColorVariationStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ColorVariationScale",
            "to_node": "ColorVariation",
            "to_socket": "ColorVariationScaleMultiplier"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Group.006",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.006",
            "from_socket": "Value",
            "to_node": "Bump.001",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump.001",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Roughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
        },
        {
            "from_node": "ColorVariation",
            "from_socket": "Color",
            "to_node": "SSS",
            "to_socket": "SubsurfaceColor"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceColor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Color"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceRadius",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceStrength",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface"
        },
        {
            "from_node": "SSS",
            "from_socket": "SubsurfaceIor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface IOR"
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
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    2152.1079,
                    273.0883
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
                    788.281,
                    -13.9948
                ],
                "use_custom_color": false,
                "width": 268.4089
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.5,
                "BetweenStop1Value": 1.0,
                "BetweenStop2Value": -0.6
            },
            "label": "Group.004",
            "name": "Group.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    571.2413,
                    -321.8509
                ]
            },
            "class": "ShaderNodeMapRange",
            "input_socket_values": {},
            "label": "Map Range",
            "name": "Map Range",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1796.3329,
                    153.0367
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
                    -1025.0469,
                    479.591
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
                "color": [
                    0.608,
                    0.608,
                    0.608
                ],
                "height": 100.0,
                "location": [
                    -1024.2196,
                    224.0364
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbBodyConstants",
            "input_socket_values": {},
            "label": "Body Constants",
            "name": "BodyConstants",
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
                    789.1182,
                    -293.4978
                ],
                "use_custom_color": false,
                "width": 260.2514
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Value": 0.0,
                "BetweenStop2Position": 0.6,
                "BetweenStop2Value": 0.3,
                "OneStopValue": 0.3
            },
            "label": "Group.006",
            "name": "Group.006",
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
                    269.8811,
                    376.1695
                ],
                "use_custom_color": false,
                "width": 236.5711
            },
            "class": "MpfbSkinColorVariation",
            "input_socket_values": {
                "Color": [
                    1.0,
                    0.6899,
                    0.4647,
                    1.0
                ],
                "ColorVariationScaleMultiplier": 70.0,
                "ColorVariationStrength": 0.3
            },
            "label": "Color Variation",
            "name": "ColorVariation",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -461.2459,
                    297.1048
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.02
            },
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    14.5556,
                    -408.4892
                ]
            },
            "class": "ShaderNodeTexVoronoi",
            "input_socket_values": {
                "Randomness": 0.4
            },
            "label": "Voronoi Texture",
            "name": "Voronoi Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -707.8688,
                    -646.6351
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 40.0
            },
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -695.9287,
                    -436.6577
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 100.0
            },
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -474.7035,
                    -384.9797
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {},
            "label": "Noise Texture",
            "name": "Noise Texture",
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
                    17.6894,
                    -687.0515
                ],
                "use_custom_color": false,
                "width": 201.5218
            },
            "class": "MpfbValueRamp2",
            "input_socket_values": {},
            "label": "Group.003",
            "name": "Group.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    382.3456,
                    -60.4096
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.003",
            "name": "Math.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    582.977,
                    -61.1753
                ]
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.004",
            "name": "Math.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1196.2094,
                    -124.2676
                ]
            },
            "class": "ShaderNodeBump",
            "input_socket_values": {
                "Strength": 0.3
            },
            "label": "Bump.001",
            "name": "Bump.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "invert": true,
                "location": [
                    1533.3766,
                    -362.5945
                ]
            },
            "class": "ShaderNodeBump",
            "input_socket_values": {
                "Strength": 0.3
            },
            "label": "Bump",
            "name": "Bump",
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
                    -242.8965,
                    530.403
                ],
                "use_custom_color": false,
                "width": 248.0564
            },
            "class": "MpfbWithinDistanceOfEither",
            "input_socket_values": {},
            "label": "Inside relevant range",
            "name": "InRange",
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
                    784.6497,
                    323.3286
                ],
                "use_custom_color": false,
                "width": 271.502
            },
            "class": "MpfbSSSControl",
            "input_socket_values": {
                "SubsurfaceRadiusMultiplyer": 1.0
            },
            "label": "SSS",
            "name": "SSS",
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
                    -1020.6154,
                    -340.0347
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Character Info",
            "name": "CharacterInfo",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1024.4425,
                    18.8993
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

class _NodeWrapperMpfbAureolae(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [2152.1079, 273.0883]
        nodes["Group Input"].location = [-1024.4425, 18.8993]

        node("MpfbValueRamp3", "Group.004", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [788.281, -13.9948], "use_custom_color": False, "width": 268.4089}, input_socket_values={"BetweenStop1Value": 1.0, "BetweenStop2Value": -0.6, "BetweenStop1Position": 0.5})
        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [571.2413, -321.8509]})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [1796.3329, 153.0367]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-1025.0469, 479.591]})
        node("MpfbBodyConstants", "BodyConstants", label="Body Constants", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1024.2196, 224.0364], "use_custom_color": False, "width": 140.0})
        node("MpfbValueRamp3", "Group.006", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [789.1182, -293.4978], "use_custom_color": False, "width": 260.2514}, input_socket_values={"BetweenStop1Value": 0.0, "BetweenStop2Value": 0.3, "OneStopValue": 0.3, "BetweenStop2Position": 0.6})
        node("MpfbSkinColorVariation", "ColorVariation", label="Color Variation", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [269.8811, 376.1695], "use_custom_color": False, "width": 236.5711}, input_socket_values={"Color": [1.0, 0.6899, 0.4647, 1.0], "ColorVariationStrength": 0.3, "ColorVariationScaleMultiplier": 70.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-461.2459, 297.1048], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.02})
        node("ShaderNodeTexVoronoi", "Voronoi Texture", attribute_values={"location": [14.5556, -408.4892]}, input_socket_values={"Randomness": 0.4})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-707.8688, -646.6351], "operation": "DIVIDE"}, input_socket_values={"Value": 40.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-695.9287, -436.6577], "operation": "DIVIDE"}, input_socket_values={"Value": 100.0})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-474.7035, -384.9797]})
        node("MpfbValueRamp2", "Group.003", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [17.6894, -687.0515], "use_custom_color": False, "width": 201.5218})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [382.3456, -60.4096], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [582.977, -61.1753]})
        node("ShaderNodeBump", "Bump.001", attribute_values={"location": [1196.2094, -124.2676]}, input_socket_values={"Strength": 0.3})
        node("ShaderNodeBump", "Bump", attribute_values={"invert": True, "location": [1533.3766, -362.5945]}, input_socket_values={"Strength": 0.3})
        node("MpfbWithinDistanceOfEither", "InRange", label="Inside relevant range", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-242.8965, 530.403], "use_custom_color": False, "width": 248.0564})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [784.6497, 323.3286], "use_custom_color": False, "width": 271.502}, input_socket_values={"SubsurfaceRadiusMultiplyer": 1.0})
        node("MpfbCharacterInfo", "CharacterInfo", label="Character Info", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-1020.6154, -340.0347], "use_custom_color": False, "width": 140.0})

        link("Group Input", "AureolaeRadius", "Math", "Value")
        link("Group Input", "UnevennessScale", "Math.001", "Value")
        link("Group Input", "WartScale", "Math.002", "Value")
        link("Group Input", "Color", "ColorVariation", "Color")
        link("Group Input", "ColorVariationStrength", "ColorVariation", "ColorVariationStrength")
        link("Group Input", "ColorVariationScale", "ColorVariation", "ColorVariationScaleMultiplier")
        link("Group Input", "Normal", "Bump.001", "Normal")
        link("Group Input", "Roughness", "Principled BSDF", "Roughness")
        link("Group Input", "SSSStrength", "SSS", "SubsurfaceStrength")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "SSSIor", "SSS", "SubsurfaceIor")
        link("Group Input", "SSSRadiusX", "SSS", "SubSurfaceRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SubSurfaceRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SubSurfaceRadiusZ")
        link("Texture Coordinate", "UV", "InRange", "Position")
        link("BodyConstants", "RightNippleCoordinate", "InRange", "Coordinate1")
        link("BodyConstants", "LeftNippleCoordinate", "InRange", "Coordinate2")
        link("Math", "Value", "InRange", "MaxDist")
        link("InRange", "ActualLeastDistance", "Map Range", "Value")
        link("Math", "Value", "Map Range", "From Max")
        link("Texture Coordinate", "Object", "Noise Texture", "Vector")
        link("CharacterInfo", "scale_factor", "Math.001", "Value_001")
        link("Math.001", "Value", "Noise Texture", "Scale")
        link("Noise Texture", "Fac", "Group.003", "Value")
        link("Group.003", "Value", "Bump", "Height")
        link("ColorVariation", "Color", "Principled BSDF", "Base Color")
        link("Texture Coordinate", "Object", "Voronoi Texture", "Vector")
        link("CharacterInfo", "scale_factor", "Math.002", "Value_001")
        link("Math.002", "Value", "Voronoi Texture", "Scale")
        link("Math.004", "Value", "Group.004", "Value")
        link("Group.004", "Value", "Bump.001", "Height")
        link("Voronoi Texture", "Distance", "Math.003", "Value")
        link("Math.003", "Value", "Math.004", "Value")
        link("Bump.001", "Normal", "Bump", "Normal")
        link("Bump", "Normal", "Principled BSDF", "Normal")
        link("Map Range", "Result", "Group.006", "Value")
        link("Group.006", "Value", "Bump.001", "Strength")
        link("ColorVariation", "Color", "SSS", "SubsurfaceColor")
        #link("SSS", "SubsurfaceColor", "Principled BSDF", "Subsurface Color")
        link("SSS", "SubsurfaceRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SubsurfaceStrength", "Principled BSDF", "Subsurface Weight")
        link("SSS", "SubsurfaceIor", "Principled BSDF", "Subsurface IOR")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbAureolae = _NodeWrapperMpfbAureolae()
