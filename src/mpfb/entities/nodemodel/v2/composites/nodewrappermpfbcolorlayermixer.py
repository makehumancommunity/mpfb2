import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbColorLayerMixer",
    "inputs": {
        "Input_0": {
            "name": "DefaultColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                1.0
            ]
        },
        "Input_1": {
            "name": "MixinColor",
            "identifier": "Input_1",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                1.0,
                1.0,
                1.0,
                1.0
            ]
        },
        "Input_2": {
            "name": "OverlayColor",
            "identifier": "Input_2",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0075,
                0.0,
                1.0,
                1.0
            ]
        },
        "Input_3": {
            "name": "DefaultColorStrength",
            "identifier": "Input_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": 0.0,
            "max_value": 0.0
        },
        "Input_4": {
            "name": "MixinOverrideStrength",
            "identifier": "Input_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_6": {
            "name": "OverlayStrength",
            "identifier": "Input_6",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        }
    },
    "outputs": {
        "Output_5": {
            "name": "Result",
            "identifier": "Output_5",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.0,
                0.0,
                0.0,
                0.0
            ]
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
                -391.5401,
                855.0407
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
            "value": 273.9324
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "MixinOverrideStrength",
            "to_node": "Math.001",
            "to_socket": "Value_001"
        },
        {
            "from_node": "Math.001",
            "from_socket": "Value",
            "to_node": "DefaultVsMixin",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "Group Input",
            "from_socket": "MixinColor",
            "to_node": "DefaultVsMixin",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DefaultColor",
            "to_node": "DefaultVsMixin",
            "to_socket": "B_Color"
        },
        {
            "from_node": "DefaultVsMixin",
            "from_socket": "Result_Color",
            "to_node": "UnderlyingVsOverlay",
            "to_socket": "A_Float"
        },
        {
            "from_node": "DefaultVsMixin",
            "from_socket": "Result_Color",
            "to_node": "UnderlyingVsOverlay",
            "to_socket": "A_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OverlayColor",
            "to_node": "UnderlyingVsOverlay",
            "to_socket": "B_Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "OverlayStrength",
            "to_node": "UnderlyingVsOverlay",
            "to_socket": "Factor_Float"
        },
        {
            "from_node": "UnderlyingVsOverlay",
            "from_socket": "Result_Color",
            "to_node": "Group Output",
            "to_socket": "Result"
        },
        {
            "from_node": "Group Input",
            "from_socket": "DefaultColorStrength",
            "to_node": "Math.001",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    652.2991,
                    -29.6639
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
                    361.5432,
                    -36.2742
                ],
                "width": 218.5016
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Underlying vs Overlay Color",
            "name": "UnderlyingVsOverlay",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -142.6111,
                    129.4947
                ],
                "operation": "SUBTRACT",
                "use_clamp": true
            },
            "class": "ShaderNodeMath",
            "input_socket_values": {},
            "label": "Math.001",
            "name": "Math.001",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "data_type": "RGBA",
                "location": [
                    82.0026,
                    75.6516
                ],
                "width": 182.7397
            },
            "class": "ShaderNodeMix",
            "input_socket_values": {},
            "label": "Default vs Mixin Color",
            "name": "DefaultVsMixin",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -654.4488,
                    -102.0787
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

class _NodeWrapperMpfbColorLayerMixer(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [652.2991, -29.6639]
        nodes["Group Input"].location = [-654.4488, -102.0787]

        node("ShaderNodeMix", "UnderlyingVsOverlay", label="Underlying vs Overlay Color", attribute_values={"data_type": "RGBA", "location": [361.5432, -36.2742], "width": 218.5016})
        node("ShaderNodeMath", "Math.001", attribute_values={"location": [-142.6111, 129.4947], "operation": "SUBTRACT", "use_clamp": True})
        node("ShaderNodeMix", "DefaultVsMixin", label="Default vs Mixin Color", attribute_values={"data_type": "RGBA", "location": [82.0026, 75.6516], "width": 182.7397})

        link("Group Input", "MixinOverrideStrength", "Math.001", "Value_001")
        link("Group Input", "MixinColor", "DefaultVsMixin", "A_Color")
        link("Group Input", "DefaultColor", "DefaultVsMixin", "B_Color")
        link("Group Input", "OverlayColor", "UnderlyingVsOverlay", "B_Color")
        link("Group Input", "OverlayStrength", "UnderlyingVsOverlay", "Factor_Float")
        link("Group Input", "DefaultColorStrength", "Math.001", "Value")
        link("Math.001", "Value", "DefaultVsMixin", "Factor_Float")
        link("DefaultVsMixin", "Result_Color", "UnderlyingVsOverlay", "A_Float")
        link("DefaultVsMixin", "Result_Color", "UnderlyingVsOverlay", "A_Color")
        link("UnderlyingVsOverlay", "Result_Color", "Group Output", "Result")

NodeWrapperMpfbColorLayerMixer = _NodeWrapperMpfbColorLayerMixer()
