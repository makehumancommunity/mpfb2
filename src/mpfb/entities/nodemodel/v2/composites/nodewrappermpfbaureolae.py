import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbAureolae",
    "inputs": {
        "Input_Socket_Color": {
            "name": "Color",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                0.6899,
                0.4647,
                1.0
            ]
        },
        "Input_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_1",
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
            "identifier": "Socket_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.45,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSStrength": {
            "name": "SSSStrength",
            "identifier": "Socket_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_Socket_SSSRadiusMultiplyer": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Socket_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.6,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_7",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 100.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 0.0,
            "max_value": 10.0
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessScale": {
            "name": "UnevennessScale",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 120.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_WartScale": {
            "name": "WartScale",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 40.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_WartStrength": {
            "name": "WartStrength",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.25,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationStrength": {
            "name": "ColorVariationStrength",
            "identifier": "Socket_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.3,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_ColorVariationScale": {
            "name": "ColorVariationScale",
            "identifier": "Socket_13",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 70.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        }
    },
    "outputs": {
        "Output_Socket_BSDF": {
            "name": "BSDF",
            "identifier": "Socket_14",
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
                700.8848,
                -624.3138
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
            "value": 323.4169
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
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
            "from_node": "Group Input",
            "from_socket": "SSSStrength",
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
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSRadius",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Radius"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSWeight",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Weight"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSIor",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface IOR"
        },
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSAnisotropy",
            "to_node": "SSS",
            "to_socket": "SSSAnisotropy"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSScale",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Scale"
        },
        {
            "from_node": "SSS",
            "from_socket": "SSSAnisotropy",
            "to_node": "Principled BSDF",
            "to_socket": "Subsurface Anisotropy"
        },
        {
            "from_node": "Bump.001",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "WartStrength",
            "to_node": "Bump.001",
            "to_socket": "Strength"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    2309.6929,
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
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    788.281,
                    -13.9948
                ],
                "use_custom_color": true,
                "width": 268.4089
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "BetweenStop1Position": 0.5,
                "BetweenStop2Value": -0.6
            },
            "label": "Group.004",
            "name": "Group.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1953.9177,
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
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -1024.2196,
                    224.0364
                ],
                "use_custom_color": true,
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
                    0.35,
                    0.0,
                    0.35
                ],
                "height": 100.0,
                "location": [
                    269.8811,
                    376.1695
                ],
                "use_custom_color": true,
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
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    17.6894,
                    -687.0515
                ],
                "use_custom_color": true,
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
                "color": [
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    784.6497,
                    323.3286
                ],
                "use_custom_color": true,
                "width": 271.502
            },
            "class": "MpfbSSSControl",
            "input_socket_values": {
                "SSSScaleMultiplier": 1.0
            },
            "label": "SSS",
            "name": "SSS",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "color": [
                    0.35,
                    0.35,
                    0.0
                ],
                "height": 100.0,
                "location": [
                    -1024.0593,
                    -357.2574
                ],
                "use_custom_color": true,
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
                    -17.301,
                    -246.5739
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
                "invert": true,
                "location": [
                    1690.9614,
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
                "location": [
                    1353.7942,
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

        nodes["Group Output"].location = [2309.6929, 273.0883]
        nodes["Group Input"].location = [-1024.4425, 18.8993]

        node("MpfbValueRamp3", "Group.004", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [788.281, -13.9948], "use_custom_color": True, "width": 268.4089}, input_socket_values={"BetweenStop2Value": -0.6, "BetweenStop1Position": 0.5})
        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [1953.9177, 153.0367]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-1025.0469, 479.591]})
        node("MpfbBodyConstants", "BodyConstants", label="Body Constants", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-1024.2196, 224.0364], "use_custom_color": True, "width": 140.0})
        node("MpfbSkinColorVariation", "ColorVariation", label="Color Variation", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [269.8811, 376.1695], "use_custom_color": True, "width": 236.5711}, input_socket_values={"Color": [1.0, 0.6899, 0.4647, 1.0], "ColorVariationStrength": 0.3, "ColorVariationScaleMultiplier": 70.0})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-707.8688, -646.6351], "operation": "DIVIDE"}, input_socket_values={"Value": 40.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-695.9287, -436.6577], "operation": "DIVIDE"}, input_socket_values={"Value": 100.0})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-474.7035, -384.9797]})
        node("MpfbValueRamp2", "Group.003", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [17.6894, -687.0515], "use_custom_color": True, "width": 201.5218})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [382.3456, -60.4096], "operation": "MULTIPLY"})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [582.977, -61.1753]})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [784.6497, 323.3286], "use_custom_color": True, "width": 271.502}, input_socket_values={"SSSScaleMultiplier": 1.0})
        node("MpfbCharacterInfo", "CharacterInfo", label="Character Info", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-1024.0593, -357.2574], "use_custom_color": True, "width": 140.0})
        node("ShaderNodeTexVoronoi", "Voronoi Texture", attribute_values={"location": [-17.301, -246.5739]}, input_socket_values={"Randomness": 0.4})
        node("ShaderNodeBump", "Bump", attribute_values={"invert": True, "location": [1690.9614, -362.5945]}, input_socket_values={"Strength": 0.3})
        node("ShaderNodeBump", "Bump.001", attribute_values={"location": [1353.7942, -124.2676]}, input_socket_values={"Strength": 0.3})

        link("Group Input", "UnevennessScale", "Math.001", "Value")
        link("Group Input", "WartScale", "Math.002", "Value")
        link("Group Input", "Color", "ColorVariation", "Color")
        link("Group Input", "ColorVariationStrength", "ColorVariation", "ColorVariationStrength")
        link("Group Input", "ColorVariationScale", "ColorVariation", "ColorVariationScaleMultiplier")
        link("Group Input", "Normal", "Bump.001", "Normal")
        link("Group Input", "Roughness", "Principled BSDF", "Roughness")
        link("Group Input", "SSSStrength", "SSS", "SSSWeight")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SSSScaleMultiplier")
        link("Group Input", "SSSIor", "SSS", "SSSIor")
        link("Group Input", "SSSRadiusX", "SSS", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SSSRadiusZ")
        link("Group Input", "SSSAnisotropy", "SSS", "SSSAnisotropy")
        link("Group Input", "WartStrength", "Bump.001", "Strength")
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
        link("Bump", "Normal", "Principled BSDF", "Normal")
        link("SSS", "SSSRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SSSWeight", "Principled BSDF", "Subsurface Weight")
        link("SSS", "SSSIor", "Principled BSDF", "Subsurface IOR")
        link("SSS", "SSSScale", "Principled BSDF", "Subsurface Scale")
        link("SSS", "SSSAnisotropy", "Principled BSDF", "Subsurface Anisotropy")
        link("Bump.001", "Normal", "Bump", "Normal")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbAureolae = _NodeWrapperMpfbAureolae()
