import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbNails",
    "inputs": {
        "Input_Socket_NailsColor": {
            "name": "NailsColor",
            "identifier": "Socket_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.8,
                0.8,
                0.8,
                1.0
            ]
        },
        "Input_Socket_SSSWeight": {
            "name": "SSSWeight",
            "identifier": "Socket_1",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSRadiusMutiplier": {
            "name": "SSSRadiusMutiplier",
            "identifier": "Socket_3",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_SSSRadiusX": {
            "name": "SSSRadiusX",
            "identifier": "Socket_8",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.0,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusY": {
            "name": "SSSRadiusY",
            "identifier": "Socket_9",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSRadiusZ": {
            "name": "SSSRadiusZ",
            "identifier": "Socket_10",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": -10000.0,
            "max_value": 10000.0
        },
        "Input_Socket_SSSIor": {
            "name": "SSSIor",
            "identifier": "Socket_2",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 1.01,
            "max_value": 3.8
        },
        "Input_Socket_SSSAnisotropy": {
            "name": "SSSAnisotropy",
            "identifier": "Socket_11",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_NailsMetallic": {
            "name": "NailsMetallic",
            "identifier": "Socket_4",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_NailsRoughness": {
            "name": "NailsRoughness",
            "identifier": "Socket_5",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_Socket_Normal": {
            "name": "Normal",
            "identifier": "Socket_6",
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
            "identifier": "Socket_7",
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
                701.1013,
                -1015.853
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
            "value": 320.2273
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Group Input",
            "from_socket": "NailsColor",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NailsMetallic",
            "to_node": "Principled BSDF",
            "to_socket": "Metallic"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NailsRoughness",
            "to_node": "Principled BSDF",
            "to_socket": "Roughness"
        },
        {
            "from_node": "Group Input",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSWeight",
            "to_node": "SSS",
            "to_socket": "SSSWeight"
        },
        {
            "from_node": "Group Input",
            "from_socket": "SSSRadiusMutiplier",
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
                    451.004,
                    -6.028
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
                    161.004,
                    -6.028
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
                "color": [
                    0.4,
                    0.4,
                    0.5
                ],
                "height": 100.0,
                "location": [
                    -230.6362,
                    -328.0659
                ],
                "use_custom_color": true,
                "width": 232.2694
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
                    -740.9901,
                    -254.0907
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

class _NodeWrapperMpfbNails(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [451.004, -6.028]
        nodes["Group Input"].location = [-740.9901, -254.0907]

        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [161.004, -6.028]})
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.4, 0.4, 0.5], "height": 100.0, "location": [-230.6362, -328.0659], "use_custom_color": True, "width": 232.2694}, input_socket_values={"SSSScaleMultiplier": 1.0})

        link("Group Input", "NailsColor", "Principled BSDF", "Base Color")
        link("Group Input", "NailsMetallic", "Principled BSDF", "Metallic")
        link("Group Input", "NailsRoughness", "Principled BSDF", "Roughness")
        link("Group Input", "Normal", "Principled BSDF", "Normal")
        link("Group Input", "SSSWeight", "SSS", "SSSWeight")
        link("Group Input", "SSSRadiusMutiplier", "SSS", "SSSScaleMultiplier")
        link("Group Input", "SSSIor", "SSS", "SSSIor")
        link("Group Input", "SSSRadiusX", "SSS", "SSSRadiusX")
        link("Group Input", "SSSRadiusY", "SSS", "SSSRadiusY")
        link("Group Input", "SSSRadiusZ", "SSS", "SSSRadiusZ")
        link("Group Input", "SSSAnisotropy", "SSS", "SSSAnisotropy")
        link("SSS", "SSSRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SSSWeight", "Principled BSDF", "Subsurface Weight")
        link("SSS", "SSSIor", "Principled BSDF", "Subsurface IOR")
        link("SSS", "SSSScale", "Principled BSDF", "Subsurface Scale")
        link("SSS", "SSSAnisotropy", "Principled BSDF", "Subsurface Anisotropy")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbNails = _NodeWrapperMpfbNails()
