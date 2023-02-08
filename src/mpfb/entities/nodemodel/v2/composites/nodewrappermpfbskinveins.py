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
                -458.1821,
                638.4954
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
            "value": 210.2823
        }
    },
    "class": "MpfbSkinVeins",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketColor",
            "default_value": [
                0.2414,
                0.2432,
                0.5,
                1.0
            ],
            "identifier": "Input_0",
            "name": "SkinColor",
            "value_type": "RGBA"
        },
        "Input_2": {
            "class": "NodeSocketFloat",
            "default_value": 1.1,
            "identifier": "Input_2",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "SmallVeinScale",
            "value_type": "VALUE"
        },
        "Input_3": {
            "class": "NodeSocketFloat",
            "default_value": 0.6,
            "identifier": "Input_3",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "LargeVeinScale",
            "value_type": "VALUE"
        },
        "Input_4": {
            "class": "NodeSocketColor",
            "default_value": [
                0.1413,
                0.1301,
                0.5029,
                1.0
            ],
            "identifier": "Input_4",
            "name": "VeinColor",
            "value_type": "RGBA"
        },
        "Input_5": {
            "class": "NodeSocketFloat",
            "default_value": 0.08,
            "identifier": "Input_5",
            "max_value": 10000.0,
            "min_value": -10000.0,
            "name": "VeinStrength",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_1": {
            "class": "NodeSocketColor",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "identifier": "Output_1",
            "name": "Color",
            "value_type": "RGBA"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "SkinColor",
            "to_node": "Mix",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Mix",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SmallVeinScale",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LargeVeinScale",
            "to_node": "Math.005",
            "to_socket": "Value"
        },
        {
            "from_node": "Mapping",
            "from_socket": "Vector",
            "to_node": "Wave Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Mapping",
            "to_socket": "Vector"
        },
        {
            "from_node": "Texture Coordinate",
            "from_socket": "Object",
            "to_node": "Wave Texture.001",
            "to_socket": "Vector"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.003",
            "from_socket": "Value",
            "to_node": "Math.004",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Wave Texture.001",
            "from_socket": "Fac",
            "to_node": "Math.003",
            "to_socket": "Value"
        },
        {
            "from_node": "Wave Texture",
            "from_socket": "Fac",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Math.004",
            "from_socket": "Value",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Mix",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Wave Texture",
            "to_socket": "Scale"
        },
        {
            "from_node": "Math.005",
            "from_socket": "Value",
            "to_node": "Wave Texture.001",
            "to_socket": "Scale"
        },
        {
            "from_node": "Group.001",
            "from_socket": "scale_factor",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group.001",
            "from_socket": "scale_factor",
            "to_node": "Math.005",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinColor",
            "to_node": "Mix",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "VeinStrength",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Combine XYZ",
            "from_socket": "Vector",
            "to_node": "Mapping",
            "to_socket": "Rotation"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -27.9507,
                    98.9416
                ]
            },
            "class": "ShaderNodeTexWave",
            "input_socket_values": {
                "Detail": 3.0,
                "Detail Scale": 4.0,
                "Distortion": 20.0,
                "Scale": 15.0
            },
            "label": "Wave Texture",
            "name": "Wave Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -17.5811,
                    -236.9527
                ]
            },
            "class": "ShaderNodeTexWave",
            "input_socket_values": {
                "Detail Roughness": 0.4,
                "Detail Scale": 4.0,
                "Distortion": 15.0,
                "Phase Offset": 0.5,
                "Scale": 9.0
            },
            "label": "Wave Texture.001",
            "name": "Wave Texture.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    188.0281,
                    124.3216
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.99
            },
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    191.2188,
                    -162.9038
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.995
            },
            "label": "Math.003",
            "name": "Math.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    427.4991,
                    -13.7494
                ],
                "operation": "MAXIMUM"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.98
            },
            "label": "Math.004",
            "name": "Math.004",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -713.6621,
                    108.2156
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -705.2716,
                    -68.955
                ],
                "operation": "DIVIDE"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.005",
            "name": "Math.005",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -983.2101,
                    236.9527
                ]
            },
            "class": "MpfbCharacterInfo",
            "input_socket_values": {},
            "label": "Group.001",
            "name": "Group.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -959.918,
                    -224.9666
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
                    1215.6146,
                    30.6328
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
                "data_type": "RGBA",
                "location": [
                    983.21,
                    29.0103
                ]
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {
                "A_Color": [
                    0.2414,
                    0.2432,
                    0.5,
                    1.0
                ],
                "B_Color": [
                    0.0015,
                    0.0,
                    0.5,
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
                    708.0868,
                    167.1202
                ],
                "operation": "MULTIPLY"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.05
            },
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -713.4092,
                    280.1944
                ]
            },
            "class": "ShaderNodeCombineXYZ",
            "input_socket_values": {
                "Z": 90.0
            },
            "label": "Combine XYZ",
            "name": "Combine XYZ",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -276.5124,
                    435.6444
                ]
            },
            "class": "ShaderNodeMapping",
            "input_socket_values": {},
            "label": "Mapping",
            "name": "Mapping",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -1205.5903,
                    -37.7019
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

class _NodeWrapperMpfbSkinVeins(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1215.6146, 30.6328]
        nodes["Group Input"].location = [-1205.5903, -37.7019]

        node("ShaderNodeTexWave", "Wave Texture", attribute_values={"location": [-27.9507, 98.9416]}, input_socket_values={"Detail": 3.0, "Detail Scale": 4.0, "Distortion": 20.0, "Scale": 15.0})
        node("ShaderNodeTexWave", "Wave Texture.001", attribute_values={"location": [-17.5811, -236.9527]}, input_socket_values={"Detail Roughness": 0.4, "Detail Scale": 4.0, "Distortion": 15.0, "Phase Offset": 0.5, "Scale": 9.0})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [188.0281, 124.3216], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.99})
        node("ShaderNodeMath", "Math.003", attribute_values={"location": [191.2188, -162.9038], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.995})
        node("ShaderNodeMath", "Math.004", attribute_values={"location": [427.4991, -13.7494], "operation": "MAXIMUM"}, input_socket_values={"Value_001": 0.98})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [-713.6621, 108.2156], "operation": "DIVIDE"})
        node("ShaderNodeMath", "Math.005", attribute_values={"location": [-705.2716, -68.955], "operation": "DIVIDE"})
        node("MpfbCharacterInfo", "Group.001", attribute_values={"location": [-983.2101, 236.9527]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-959.918, -224.9666]})
        node("ShaderNodeMix", "Mix", attribute_values={"data_type": "RGBA", "location": [983.21, 29.0103]}, input_socket_values={"A_Color": [0.2414, 0.2432, 0.5, 1.0], "B_Color": [0.0015, 0.0, 0.5, 1.0]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [708.0868, 167.1202], "operation": "MULTIPLY"}, input_socket_values={"Value_001": 0.05})
        node("ShaderNodeCombineXYZ", "Combine XYZ", attribute_values={"location": [-713.4092, 280.1944]}, input_socket_values={"Z": 90.0})
        node("ShaderNodeMapping", "Mapping", attribute_values={"location": [-276.5124, 435.6444]})

        link("Group Input", "SkinColor", "Mix", "A_Color")
        link("Group Input", "SmallVeinScale", "Math.002", "Value")
        link("Group Input", "LargeVeinScale", "Math.005", "Value")
        link("Group Input", "VeinColor", "Mix", "B_Color")
        link("Group Input", "VeinStrength", "Math", "Value_001")
        link("Mapping", "Vector", "Wave Texture", "Vector")
        link("Texture Coordinate", "Object", "Mapping", "Vector")
        link("Texture Coordinate", "Object", "Wave Texture.001", "Vector")
        link("Math.001", "Value", "Math.004", "Value")
        link("Math.003", "Value", "Math.004", "Value_001")
        link("Wave Texture.001", "Fac", "Math.003", "Value")
        link("Wave Texture", "Fac", "Math.001", "Value")
        link("Math.004", "Value", "Math", "Value")
        link("Math", "Value", "Mix", "Factor_Float")
        link("Math.002", "Value", "Wave Texture", "Scale")
        link("Math.005", "Value", "Wave Texture.001", "Scale")
        link("Group.001", "scale_factor", "Math.002", "Value_001")
        link("Group.001", "scale_factor", "Math.005", "Value_001")
        link("Combine XYZ", "Vector", "Mapping", "Rotation")
        link("Mix", "Result_Color", "Group Output", "Color")

NodeWrapperMpfbSkinVeins = _NodeWrapperMpfbSkinVeins()
