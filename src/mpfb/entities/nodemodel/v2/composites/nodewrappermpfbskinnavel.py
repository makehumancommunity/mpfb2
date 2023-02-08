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
                -1477.5059,
                126.2919
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
            "value": 140.0
        }
    },
    "class": "MpfbSkinNavel",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.01,
            "identifier": "Input_0",
            "max_value": 0.2,
            "min_value": 0.001,
            "name": "NavelWidth",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketFloatFactor",
            "default_value": 0.2,
            "identifier": "Input_2",
            "name": "NavelBumpStrength",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Input_3",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Input_4": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_4",
            "name": "SkinMainColor",
            "value_type": "RGBA"
        },
        "Input_5": {
            "class": "NodeSocketColor",
            "default_value": [
                0.5,
                0.5,
                0.5,
                1.0
            ],
            "identifier": "Input_5",
            "name": "SkinNavelCenterColor",
            "value_type": "RGBA"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketVector",
            "default_value": [
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Normal",
            "value_type": "VECTOR"
        },
        "Output_6": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_6",
            "name": "SkinColor",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Bump",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelWidth",
            "to_node": "Map Range",
            "to_socket": "From Max"
        },
        {
            "from_node": "Group",
            "from_socket": "NavelCoordinate",
            "to_node": "Group.001",
            "to_socket": "Coordinate1"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "UV",
            "to_node": "Group.001",
            "to_socket": "Coordinate2"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelWidth",
            "to_node": "Group.001",
            "to_socket": "MaxDist"
        },
        {
            "from_node": "Mix.001",
            "from_socket": "Result_Color",
            "to_node": "RGB to BW",
            "to_socket": "Color"
        },
        {
            "from_node": "RGB to BW",
            "from_socket": "Val",
            "to_node": "Bump",
            "to_socket": "Height"
        },
        {
            "from_node": "Bump",
            "from_socket": "Normal",
            "to_node": "Group Output",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group.001",
            "from_socket": "ActualDistance",
            "to_node": "Map Range",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinMainColor",
            "to_node": "Mix.002",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Mix.002",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "Map Range",
            "from_socket": "Result",
            "to_node": "Group.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group.002",
            "from_socket": "Value",
            "to_node": "Mix.001",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group.002",
            "from_socket": "Value",
            "to_node": "Mix.002",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NavelBumpStrength",
            "to_node": "Bump",
            "to_socket": "Strength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SkinNavelCenterColor",
            "to_node": "Mix.002",
            "to_socket": "A_Color"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -891.4319,
                    364.4258
                ]
            },
            "class": "MpfbBodyConstants",
            "input_socket_values": {},
            "label": "Group",
            "name": "Group",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -895.7065,
                    152.4116
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
                "location": [
                    -531.4623,
                    287.2665
                ]
            },
            "class": "MpfbWithinDistance",
            "input_socket_values": {},
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    809.7256,
                    137.4486
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
                    643.614,
                    -57.1532
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
                    471.1248,
                    128.1947
                ]
            },
            "class": "ShaderNodeRGBToBW",
            "input_socket_values": {},
            "label": "RGB to BW",
            "name": "RGB to BW",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    219.3004,
                    225.231
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.0,
                    0.0,
                    0.0,
                    1.0
                ],
                "B_Color": [
                    0.0476,
                    0.0476,
                    0.0476,
                    1.0
                ]
            },
            "label": "Mix.001",
            "name": "Mix.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    218.4381,
                    -22.3544
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.5138,
                    0.2284,
                    0.0983,
                    1.0
                ],
                "B_Color": [
                    1.0,
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "label": "Mix.002",
            "name": "Mix.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -339.5393,
                    104.6521
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
                    -121.9947,
                    167.238
                ],
                "width": 208.9785
            },
            "class": "MpfbValueRamp3",
            "input_socket_values": {
                "Input_6": 0.8
            },
            "label": "Group.002",
            "name": "Group.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -782.376,
                    -258.9218
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

class _NodeWrapperMpfbSkinNavel(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [809.7256, 137.4486]
        nodes["Group Input"].location = [-782.376, -258.9218]

        node("MpfbBodyConstants", "Group", attribute_values={"location": [-891.4319, 364.4258]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-895.7065, 152.4116]})
        node("MpfbWithinDistance", "Group.001", attribute_values={"location": [-531.4623, 287.2665]})
        node("ShaderNodeBump", "Bump", attribute_values={"location": [643.614, -57.1532]}, input_socket_values={"Strength": 0.3})
        node("ShaderNodeRGBToBW", "RGB to BW", attribute_values={"location": [471.1248, 128.1947]})
        node("ShaderNodeMix", "Mix.001", attribute_values={"data_type": "RGBA", "location": [219.3004, 225.231]}, input_socket_values={"A_Color": [0.0, 0.0, 0.0, 1.0], "B_Color": [0.0476, 0.0476, 0.0476, 1.0]})
        node("ShaderNodeMix", "Mix.002", attribute_values={"data_type": "RGBA", "location": [218.4381, -22.3544]}, input_socket_values={"A_Color": [0.5138, 0.2284, 0.0983, 1.0], "B_Color": [1.0, 1.0, 1.0, 1.0]})
        node("ShaderNodeMapRange", "Map Range", attribute_values={"location": [-339.5393, 104.6521]})
        node("MpfbValueRamp3", "Group.002", attribute_values={"location": [-121.9947, 167.238], "width": 208.9785}, input_socket_values={"Input_6": 0.8})

        link("Group Input", "Normal", "Bump", "Normal")
        link("Group Input", "NavelWidth", "Map Range", "From Max")
        link("Group Input", "NavelWidth", "Group.001", "MaxDist")
        link("Group Input", "SkinMainColor", "Mix.002", "B_Color")
        link("Group Input", "NavelBumpStrength", "Bump", "Strength")
        link("Group Input", "SkinNavelCenterColor", "Mix.002", "A_Color")
        link("Group", "NavelCoordinate", "Group.001", "Coordinate1")
        link("Texture Coordinate", "UV", "Group.001", "Coordinate2")
        link("Mix.001", "Result_Color", "RGB to BW", "Color")
        link("RGB to BW", "Val", "Bump", "Height")
        link("Group.001", "ActualDistance", "Map Range", "Value")
        link("Map Range", "Result", "Group.002", "Value")
        link("Group.002", "Value", "Mix.001", "Factor_Float")
        link("Group.002", "Value", "Mix.002", "Factor_Float")
        link("Bump", "Normal", "Group Output", "Normal")
        link("Mix.002", "Result_Color", "Group Output", "SkinColor")

NodeWrapperMpfbSkinNavel = _NodeWrapperMpfbSkinNavel()
