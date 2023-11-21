import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbLips",
    "inputs": {
        "Input_Socket_LipsColor": {
            "name": "LipsColor",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.5,
                0.0,
                0.0022,
                1.0
            ]
        },
        "Input_Socket_LipsCreaseScale": {
            "name": "LipsCreaseScale",
            "identifier": "Socket_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 9.5,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_LipsCreaseStretch": {
            "name": "LipsCreaseStretch",
            "identifier": "Socket_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 7.0,
            "min_value": 0.1,
            "max_value": 20.0
        },
        "Input_Socket_LipsCreaseStrength": {
            "name": "LipsCreaseStrength",
            "identifier": "Socket_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.35,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_LipsRoughness": {
            "name": "LipsRoughness",
            "identifier": "Socket_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.4,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -3.4028234663852886e+38,
            "max_value": 3.4028234663852886e+38
        },
        "Input_Socket_SSSRadiusMultiplyer": {
            "name": "SSSRadiusMultiplyer",
            "identifier": "Socket_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_15",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_16",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_17",
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
            "identifier": "Socket_18",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessScaleMultiplier": {
            "name": "UnevennessScaleMultiplier",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 100.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_UnevennessBumpStrength": {
            "name": "UnevennessBumpStrength",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.15,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_UnevennessDetail": {
            "name": "UnevennessDetail",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 3.0,
            "min_value": 0.0,
            "max_value": 15.0
        },
        "Input_Socket_UnevennessDistortion": {
            "name": "UnevennessDistortion",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.5,
            "min_value": -1000.0,
            "max_value": 1000.0
        },
        "Input_Socket_UnevennessRoughness": {
            "name": "UnevennessRoughness",
            "identifier": "Socket_12",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_13",
            "class": "NodeSocketVector",
            "value_type": "VECTOR",
            "default_value": [
                0.0,
                0.0,
                0.0
            ]
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
                699.1651,
                -168.2879
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
            "value": 323.4168
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseStretch",
            "to_node": "Combine XYZ",
            "to_socket": "X"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseScale",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsCreaseStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsRoughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
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
            "from_socket": "LipsColor",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Group",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessScaleMultiplier",
            "to_node": "Group",
            "to_socket": "UnevennessScaleMultiplier"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessBumpStrength",
            "to_node": "Group",
            "to_socket": "UnevennessBumpStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDetail",
            "to_node": "Group",
            "to_socket": "UnevennessDetail"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessDistortion",
            "to_node": "Group",
            "to_socket": "UnevennessDistortion"
        },
        {
            "from_node": "Group Input",
            "from_socket": "UnevennessRoughness",
            "to_node": "Group",
            "to_socket": "UnevennessRoughness"
        },
        {
            "from_node": "Group",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Vector Math",
            "from_socket": "Vector",
            "to_node": "Noise Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Vector Math",
            "to_socket": "Vector"
        },
        {
            "from_node": "characterinfo",
            "from_socket": "scale_factor",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Noise Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Combine XYZ",
            "from_socket": "Vector",
            "to_node": "Vector Math",
            "to_socket": "Vector_001"
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
            "from_node": "Noise Texture",
            "from_socket": "Fac",
            "to_node": "Group.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.002",
            "from_socket": "Value",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        },
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
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
            "from_socket": "SSSAnisotropy",
            "to_node": "SSS",
            "to_socket": "SSSAnisotropy"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    1027.3911,
                    150.8435
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
                    599.8683,
                    26.5137
                ]
            },
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {
                "Roughness": 0.2
            },
            "label": "Principled BSDF",
            "name": "Principled BSDF",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    329.0903,
                    -352.9689
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
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    77.2454,
                    -830.0649
                ],
                "use_custom_color": true,
                "width": 247.2069
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {},
            "label": "Group.002",
            "name": "Group.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -156.4584,
                    -818.0838
                ]
            },
            "class": "ShaderNodeTexNoise",
            "input_socket_values": {
                "Detail": 4.0,
                "Distortion": 2.0,
                "Scale": 50.0
            },
            "label": "Noise Texture",
            "name": "Noise Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -397.631,
                    -906.7668
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeVectorMath",
            "input_socket_values": {
                "Vector_001": [
                    8.0,
                    1.0,
                    1.0
                ]
            },
            "label": "Vector Math",
            "name": "Vector Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -669.1196,
                    -961.1784
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "X": 8.0,
                "Y": 1.0,
                "Z": 1.0
            },
            "label": "Combine XYZ",
            "name": "Combine XYZ",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -518.0641,
                    -698.05
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value": 20.0
            },
            "label": "Math",
            "name": "Math",
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
                    -338.2765,
                    -408.3474
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbSkinNormalUnevenness",
            "input_socket_values": {},
            "label": "Group",
            "name": "Group",
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
                    -1015.6287,
                    -514.6119
                ],
                "use_custom_color": true,
                "width": 140.0
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Character Info",
            "name": "characterinfo",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1017.0906,
                    -719.7971
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
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    137.0951,
                    254.0526
                ],
                "use_custom_color": true,
                "width": 140.0
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
                "location": [
                    -1014.3296,
                    -77.1974
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

class _NodeWrapperMpfbLips(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1027.3911, 150.8435]
        nodes["Group Input"].location = [-1014.3296, -77.1974]

        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [599.8683, 26.5137]}, input_socket_values={"Roughness": 0.2})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [329.0903, -352.9689]}, input_socket_values={"Strength": 0.3})
        node("MpfbValueRamp3", "Group.002", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [77.2454, -830.0649], "use_custom_color": True, "width": 247.2069})
        node("ShaderNodeTexNoise", "Noise Texture", attribute_values={"location": [-156.4584, -818.0838]}, input_socket_values={"Detail": 4.0, "Distortion": 2.0, "Scale": 50.0})
        node("ShaderNodeVectorMath", "Vector Math", attribute_values={"location": [-397.631, -906.7668], "operation": "MULTIPLY"}, input_socket_values={"Vector_001": [8.0, 1.0, 1.0]})
        node("ShaderNodeCombineXYZ", "Combine XYZ", attribute_values={"location": [-669.1196, -961.1784]}, input_socket_values={"X": 8.0, "Y": 1.0, "Z": 1.0})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-518.0641, -698.05], "operation": "DIVIDE"}, input_socket_values={"Value": 20.0})
        node("MpfbSkinNormalUnevenness", "Group", attribute_values={"color": [0.35, 0.0, 0.35], "height": 100.0, "location": [-338.2765, -408.3474], "use_custom_color": True, "width": 140.0})
        node("MpfbCharacterInfo", "characterinfo", label="Character Info", attribute_values={"color": [0.35, 0.35, 0.0], "height": 100.0, "location": [-1015.6287, -514.6119], "use_custom_color": True, "width": 140.0})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-1017.0906, -719.7971]})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [137.0951, 254.0526], "use_custom_color": True, "width": 140.0}, input_socket_values={"SSSScaleMultiplier": 1.0})

        link("Group Input", "LipsCreaseStretch", "Combine XYZ", "X")
        link("Group Input", "LipsCreaseScale", "Math", "Value")
        link("Group Input", "LipsCreaseStrength", "Bump", "Strength")
        link("Group Input", "LipsRoughness", "Principled BSDF", "Roughness")
        link("Group Input", "SSSWeight", "SSS", "SSSWeight")
        link("Group Input", "SSSRadiusMultiplyer", "SSS", "SSSScaleMultiplier")
        link("Group Input", "SSSIor", "SSS", "SSSIor")
        link("Group Input", "LipsColor", "Principled BSDF", "Base Color")
        link("Group Input", "Normal", "Group", "Normal")
        link("Group Input", "UnevennessScaleMultiplier", "Group", "UnevennessScaleMultiplier")
        link("Group Input", "UnevennessBumpStrength", "Group", "UnevennessBumpStrength")
        link("Group Input", "UnevennessDetail", "Group", "UnevennessDetail")
        link("Group Input", "UnevennessDistortion", "Group", "UnevennessDistortion")
        link("Group Input", "UnevennessRoughness", "Group", "UnevennessRoughness")
        link("Group Input", "SSSRadiusX", "SSS", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SSSRadiusZ")
        link("Group Input", "SSSAnisotropy", "SSS", "SSSAnisotropy")
        link("Group", "Normal", "Bump", "Normal")
        link("Vector Math", "Vector", "Noise Texture", "Vector")
        link("Texture Coordinate", "Object", "Vector Math", "Vector")
        link("characterinfo", "scale_factor", "Math", "Value_001")
        link("Math", "Value", "Noise Texture", "Scale")
        link("Combine XYZ", "Vector", "Vector Math", "Vector_001")
        link("SSS", "SSSRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SSSWeight", "Principled BSDF", "Subsurface Weight")
        link("SSS", "SSSIor", "Principled BSDF", "Subsurface IOR")
        link("Noise Texture", "Fac", "Group.002", "Value")
        link("Group.002", "Value", "Bump", "Height")
        link("Bump", "Normal", "Principled BSDF", "Normal")
        link("SSS", "SSSScale", "Principled BSDF", "Subsurface Scale")
        link("SSS", "SSSAnisotropy", "Principled BSDF", "Subsurface Anisotropy")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbLips = _NodeWrapperMpfbLips()
