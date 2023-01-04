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
                -85.398,
                445.1363
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
            "value": 273.6433
        }
    },
    "class": "MpfbShaderRouter4",
    "inputs": {
        "Input_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_0",
            "name": "Value",
            "value_type": "VALUE"
        },
        "Input_1": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_1",
            "name": "Threshold1",
            "value_type": "VALUE"
        },
        "Input_2": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Input_2",
            "name": "Section1Shader",
            "value_type": "SHADER"
        },
        "Input_3": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Input_3",
            "name": "Section2Shader",
            "value_type": "SHADER"
        },
        "Input_4": {
            "class": "NodeSocketFloat",
            "default_value": 0.5,
            "identifier": "Input_4",
            "name": "Threshold2",
            "value_type": "VALUE"
        },
        "Input_6": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Input_6",
            "name": "Section3Shader",
            "value_type": "SHADER"
        },
        "Input_8": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Input_8",
            "name": "Section4Shader",
            "value_type": "SHADER"
        },
        "Input_9": {
            "class": "NodeSocketFloat",
            "default_value": 0.8,
            "identifier": "Input_9",
            "name": "Threshold3",
            "value_type": "VALUE"
        }
    },
    "outputs": {
        "Output_5": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Output_5",
            "name": "Shader",
            "value_type": "SHADER"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold1",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math",
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
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "Mix Shader.001",
            "to_socket": "Fac"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Shader",
            "to_node": "Mix Shader",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section2Shader",
            "to_node": "Mix Shader",
            "to_socket": "Shader"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold2",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.001",
            "to_socket": "Value"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section3Shader",
            "to_node": "Mix Shader.001",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Value",
            "to_node": "Math.002",
            "to_socket": "Value"
        },
        {
            "from_node": "Mix Shader.001",
            "from_socket": "Shader",
            "to_node": "Mix Shader.002",
            "to_socket": "Shader"
        },
        {
            "from_node": "Mix Shader.002",
            "from_socket": "Shader",
            "to_node": "Group Output",
            "to_socket": "Shader"
        },
        {
            "from_node": "Math.002",
            "from_socket": "Value",
            "to_node": "Mix Shader.002",
            "to_socket": "Fac"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section4Shader",
            "to_node": "Mix Shader.002",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Threshold3",
            "to_node": "Math.002",
            "to_socket": "Value_001"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -396.522,
                    281.5724
                ],
                "operation": "LESS_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math",
            "name": "Math",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -185.4732,
                    172.0834
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
                    -190.4527,
                    39.2202
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    555.4822,
                    -85.3839
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
                    113.7154,
                    -27.1456
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
                "location": [
                    111.3227,
                    -152.2468
                ],
                "operation": "GREATER_THAN"
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {
                "Value_001": 0.8
            },
            "label": "Math.002",
            "name": "Math.002",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    369.1914,
                    -293.1106
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
                    -724.9921,
                    -59.51
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

class _NodeWrapperMpfbShaderRouter4(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [555.4822, -85.3839]
        nodes["Group Input"].location = [-724.9921, -59.51]

        node("ShaderNodeMath", "Math", attribute_values={"location": [-396.522, 281.5724], "operation": "LESS_THAN"})
        node("ShaderNodeMixShader", "Mix Shader", attribute_values={"location": [-185.4732, 172.0834]})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-190.4527, 39.2202], "operation": "GREATER_THAN"})
        node("ShaderNodeMixShader", "Mix Shader.001", attribute_values={"location": [113.7154, -27.1456]})
        node("ShaderNodeMath", "Math.002", attribute_values={"location": [111.3227, -152.2468], "operation": "GREATER_THAN"}, input_socket_values={"Value_001": 0.8})
        node("ShaderNodeMixShader", "Mix Shader.002", attribute_values={"location": [369.1914, -293.1106]})

        link("Group Input", "Value", "Math", "Value")
        link("Group Input", "Threshold1", "Math", "Value_001")
        link("Group Input", "Section1Shader", "Mix Shader", "Shader_001")
        link("Group Input", "Section2Shader", "Mix Shader", "Shader")
        link("Group Input", "Threshold2", "Math.001", "Value_001")
        link("Group Input", "Value", "Math.001", "Value")
        link("Group Input", "Section3Shader", "Mix Shader.001", "Shader_001")
        link("Group Input", "Value", "Math.002", "Value")
        link("Group Input", "Section4Shader", "Mix Shader.002", "Shader_001")
        link("Group Input", "Threshold3", "Math.002", "Value_001")
        link("Math", "Value", "Mix Shader", "Fac")
        link("Mix Shader", "Shader", "Mix Shader.001", "Shader")
        link("Math.001", "Value", "Mix Shader.001", "Fac")
        link("Mix Shader.001", "Shader", "Mix Shader.002", "Shader")
        link("Math.002", "Value", "Mix Shader.002", "Fac")
        link("Mix Shader.002", "Shader", "Group Output", "Shader")

NodeWrapperMpfbShaderRouter4 = _NodeWrapperMpfbShaderRouter4()
