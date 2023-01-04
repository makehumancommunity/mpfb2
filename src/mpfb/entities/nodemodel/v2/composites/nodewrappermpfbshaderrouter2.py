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
                -32.0294,
                393.0536
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
            "value": 265.8835
        }
    },
    "class": "MpfbShaderRouter2",
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
            "name": "Threshold",
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
        }
    },
    "outputs": {
        "Output_4": {
            "class": "NodeSocketShader",
            "default_value": null,
            "identifier": "Output_4",
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
            "from_socket": "Threshold",
            "to_node": "Math",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section1Shader",
            "to_node": "Mix Shader",
            "to_socket": "Shader"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Section2Shader",
            "to_node": "Mix Shader",
            "to_socket": "Shader_001"
        },
        {
            "from_node": "Mix Shader",
            "from_socket": "Shader",
            "to_node": "Group Output",
            "to_socket": "Shader"
        },
        {
            "from_node": "Math",
            "from_socket": "Value",
            "to_node": "Mix Shader",
            "to_socket": "Fac"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    345.2334,
                    -122.9751
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
                    131.0485,
                    -127.719
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
                    -111.9022,
                    18.8559
                ],
                "operation": "GREATER_THAN"
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
                    -383.4491,
                    -122.9751
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

class _NodeWrapperMpfbShaderRouter2(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [345.2334, -122.9751]
        nodes["Group Input"].location = [-383.4491, -122.9751]

        node("ShaderNodeMixShader", "Mix Shader", attribute_values={"location": [131.0485, -127.719]})
        node("ShaderNodeMath", "Math", attribute_values={"location": [-111.9022, 18.8559], "operation": "GREATER_THAN"})

        link("Group Input", "Value", "Math", "Value")
        link("Group Input", "Threshold", "Math", "Value_001")
        link("Group Input", "Section1Shader", "Mix Shader", "Shader")
        link("Group Input", "Section2Shader", "Mix Shader", "Shader_001")
        link("Math", "Value", "Mix Shader", "Fac")
        link("Mix Shader", "Shader", "Group Output", "Shader")

NodeWrapperMpfbShaderRouter2 = _NodeWrapperMpfbShaderRouter2()
