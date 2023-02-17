import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbBodySectionsRouter",
    "inputs": {
        "Input_0": {
            "name": "DefaultBodyShader",
            "identifier": "Input_0",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_3": {
            "name": "AureolaeShader",
            "identifier": "Input_3",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_1": {
            "name": "FaceShader",
            "identifier": "Input_1",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_7": {
            "name": "EarsShader",
            "identifier": "Input_7",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_2": {
            "name": "LipsShader",
            "identifier": "Input_2",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_4": {
            "name": "FingernailsShader",
            "identifier": "Input_4",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_5": {
            "name": "ToenailsShader",
            "identifier": "Input_5",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        },
        "Input_8": {
            "name": "GenitalsShader",
            "identifier": "Input_8",
            "class": "NodeSocketShader",
            "value_type": "SHADER",
            "default_value": null
        }
    },
    "outputs": {
        "Output_6": {
            "name": "Shader",
            "identifier": "Output_6",
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
                1376.2086,
                1011.9443
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
            "value": 282.3828
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "IsAureolae",
            "from_socket": "Value",
            "to_node": "Mix Shader",
            "to_socket": "Fac"
        },
        {
            "from_node": "Mix Shader",
            "from_socket": "Shader",
            "to_node": "Mix Shader.001",
            "to_socket": "Shader"
        },
        {
            "from_node": "IsFace",
            "from_socket": "Value",
            "to_node": "Mix Shader.001",
            "to_socket": "Fac"
        },
        {
            "from_node": "IsLips",
            "from_socket": "Value",
            "to_node": "Mix Shader.002",
            "to_socket": "Fac"
        },
        {
            "from_node": "Mix Shader.001",
            "from_socket": "Shader",
            "to_node": "Mix Shader.002",
            "to_socket": "Shader"
        },
        {
            "from_node": "IsFingernails",
            "from_socket": "Value",
            "to_node": "Mix Shader.003",
            "to_socket": "Fac"
        },
        {
            "from_node": "Mix Shader.002",
            "from_socket": "Shader",
            "to_node": "Mix Shader.003",
            "to_socket": "Shader"
        },
        {
            "from_node": "Mix Shader.003",
            "from_socket": "Shader",
            "to_node": "Mix Shader.004",
            "to_socket": "Shader"
        },
        {
            "from_node": "IsToenails",
            "from_socket": "Value",
            "to_node": "Mix Shader.004",
            "to_socket": "Fac"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DefaultBodyShader",
            "to_node": "Mix Shader",
            "to_socket": "Shader"
        },
        {
            "from_node": "Group Input",
            "from_socket": "AureolaeShader",
            "to_node": "Mix Shader",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FaceShader",
            "to_node": "Mix Shader.001",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "LipsShader",
            "to_node": "Mix Shader.002",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "FingernailsShader",
            "to_node": "Mix Shader.003",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "ToenailsShader",
            "to_node": "Mix Shader.004",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Mix Shader.004",
            "from_socket": "Shader",
            "to_node": "Mix Shader.005",
            "to_socket": "Shader"
        },
        {
            "from_node": "Group Input",
            "from_socket": "EarsShader",
            "to_node": "Mix Shader.005",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "IsEars",
            "from_socket": "Value",
            "to_node": "Mix Shader.005",
            "to_socket": "Fac"
        },
        {
            "from_node": "IsGenitals",
            "from_socket": "Value",
            "to_node": "Mix Shader.006",
            "to_socket": "Fac"
        },
        {
            "from_node": "Mix Shader.005",
            "from_socket": "Shader",
            "to_node": "Mix Shader.006",
            "to_socket": "Shader"
        },
        {
            "from_node": "Group Input",
            "from_socket": "GenitalsShader",
            "to_node": "Mix Shader.006",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Mix Shader.006",
            "from_socket": "Shader",
            "to_node": "Group Output",
            "to_socket": "Shader"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -90.473,
                    188.4992
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.001",
            "name": "Mix Shader.001",
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
                    -94.0441,
                    50.065
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureLips",
            "input_socket_values": {},
            "label": "IsLips",
            "name": "IsLips",
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
                    -492.2594,
                    446.2881
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureAureolae",
            "input_socket_values": {},
            "label": "IsAureolae",
            "name": "IsAureolae",
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
                    -299.4578,
                    204.701
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureFace",
            "input_socket_values": {},
            "label": "IsFace",
            "name": "IsFace",
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
                    94.1688,
                    -115.6434
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureFingernails",
            "input_socket_values": {},
            "label": "IsFingernails",
            "name": "IsFingernails",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    303.818,
                    -212.4323
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.003",
            "name": "Mix Shader.003",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -298.6343,
                    337.6847
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader",
            "name": "Mix Shader",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    92.2244,
                    19.7351
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.002",
            "name": "Mix Shader.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    492.2595,
                    -446.2881
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.004",
            "name": "Mix Shader.004",
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
                    304.4512,
                    -354.7517
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureToenails",
            "input_socket_values": {},
            "label": "IsToenails",
            "name": "IsToenails",
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
                    491.7747,
                    -590.6022
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureEars",
            "input_socket_values": {},
            "label": "IsEars",
            "name": "IsEars",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    717.0477,
                    -632.5438
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.005",
            "name": "Mix Shader.005",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    928.4091,
                    -808.446
                ]
            },
            "class": "ShaderNodeMixShader",
            "input_socket_values": {},
            "label": "Mix Shader.006",
            "name": "Mix Shader.006",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    1188.4442,
                    -818.9216
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
                    715.5232,
                    -781.2327
                ],
                "use_custom_color": false,
                "width": 140.0
            },
            "class": "MpfbSystemValueTextureGenitals",
            "input_socket_values": {},
            "label": "IsGenitals",
            "name": "IsGenitals",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -813.1845,
                    -11.987
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

class _NodeWrapperMpfbBodySectionsRouter(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [1188.4442, -818.9216]
        nodes["Group Input"].location = [-813.1845, -11.987]

        node("ShaderNodeMixShader", "Mix Shader.001", attribute_values={"location": [-90.473, 188.4992]})
        node("MpfbSystemValueTextureLips", "IsLips", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-94.0441, 50.065], "use_custom_color": False, "width": 140.0})
        node("MpfbSystemValueTextureAureolae", "IsAureolae", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-492.2594, 446.2881], "use_custom_color": False, "width": 140.0})
        node("MpfbSystemValueTextureFace", "IsFace", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-299.4578, 204.701], "use_custom_color": False, "width": 140.0})
        node("MpfbSystemValueTextureFingernails", "IsFingernails", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [94.1688, -115.6434], "use_custom_color": False, "width": 140.0})
        node("ShaderNodeMixShader", "Mix Shader.003", attribute_values={"location": [303.818, -212.4323]})
        node("ShaderNodeMixShader", "Mix Shader", attribute_values={"location": [-298.6343, 337.6847]})
        node("ShaderNodeMixShader", "Mix Shader.002", attribute_values={"location": [92.2244, 19.7351]})
        node("ShaderNodeMixShader", "Mix Shader.004", attribute_values={"location": [492.2595, -446.2881]})
        node("MpfbSystemValueTextureToenails", "IsToenails", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [304.4512, -354.7517], "use_custom_color": False, "width": 140.0})
        node("MpfbSystemValueTextureEars", "IsEars", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [491.7747, -590.6022], "use_custom_color": False, "width": 140.0})
        node("ShaderNodeMixShader", "Mix Shader.005", attribute_values={"location": [717.0477, -632.5438]})
        node("ShaderNodeMixShader", "Mix Shader.006", attribute_values={"location": [928.4091, -808.446]})
        node("MpfbSystemValueTextureGenitals", "IsGenitals", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [715.5232, -781.2327], "use_custom_color": False, "width": 140.0})

        link("Group Input", "DefaultBodyShader", "Mix Shader", "Shader")
        link("Group Input", "AureolaeShader", "Mix Shader", "Shader_001")
        link("Group Input", "FaceShader", "Mix Shader.001", "Shader_001")
        link("Group Input", "LipsShader", "Mix Shader.002", "Shader_001")
        link("Group Input", "FingernailsShader", "Mix Shader.003", "Shader_001")
        link("Group Input", "ToenailsShader", "Mix Shader.004", "Shader_001")
        link("Group Input", "EarsShader", "Mix Shader.005", "Shader_001")
        link("Group Input", "GenitalsShader", "Mix Shader.006", "Shader_001")
        link("IsAureolae", "Value", "Mix Shader", "Fac")
        link("Mix Shader", "Shader", "Mix Shader.001", "Shader")
        link("IsFace", "Value", "Mix Shader.001", "Fac")
        link("IsLips", "Value", "Mix Shader.002", "Fac")
        link("Mix Shader.001", "Shader", "Mix Shader.002", "Shader")
        link("IsFingernails", "Value", "Mix Shader.003", "Fac")
        link("Mix Shader.002", "Shader", "Mix Shader.003", "Shader")
        link("Mix Shader.003", "Shader", "Mix Shader.004", "Shader")
        link("IsToenails", "Value", "Mix Shader.004", "Fac")
        link("Mix Shader.004", "Shader", "Mix Shader.005", "Shader")
        link("IsEars", "Value", "Mix Shader.005", "Fac")
        link("IsGenitals", "Value", "Mix Shader.006", "Fac")
        link("Mix Shader.005", "Shader", "Mix Shader.006", "Shader")
        link("Mix Shader.006", "Shader", "Group Output", "Shader")

NodeWrapperMpfbBodySectionsRouter = _NodeWrapperMpfbBodySectionsRouter()
