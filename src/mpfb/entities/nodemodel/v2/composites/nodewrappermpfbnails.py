import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbNails",
    "inputs": {
        "Input_0": {
            "name": "NailsColor",
            "identifier": "Input_0",
            "class": "NodeSocketColor",
            "value_type": "RGBA",
            "default_value": [
                0.8,
                0.8,
                0.8,
                1.0
            ]
        },
        "Input_2": {
            "name": "NailsSSSStrength",
            "identifier": "Input_2",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.1,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_5": {
            "name": "NailsSSSIor",
            "identifier": "Input_5",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 1.4,
            "min_value": 1.01,
            "max_value": 3.8
        },
        "Input_6": {
            "name": "NailsSSSRadiusMutiplier",
            "identifier": "Input_6",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.7,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_7": {
            "name": "NailsMetallic",
            "identifier": "Input_7",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.0,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_10": {
            "name": "NailsRoughness",
            "identifier": "Input_10",
            "class": "NodeSocketFloatFactor",
            "value_type": "VALUE",
            "default_value": 0.2,
            "min_value": 0.0,
            "max_value": 1.0
        },
        "Input_23": {
            "name": "Normal",
            "identifier": "Input_23",
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
        "Output_1": {
            "name": "BSDF",
            "identifier": "Output_1",
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
                705.4062,
                -841.0432
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
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Group Output",
            "to_socket": "BSDF"
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
            "from_socket": "NailsColor",
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
            "from_node": "Group Input",
            "from_socket": "NailsSSSStrength",
            "to_node": "SSS",
            "to_socket": "SubsurfaceStrength"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NailsSSSRadiusMutiplier",
            "to_node": "SSS",
            "to_socket": "SubsurfaceRadiusMultiplyer"
        },
        {
            "from_node": "Group Input",
            "from_socket": "NailsSSSIor",
            "to_node": "SSS",
            "to_socket": "SubsurfaceIor"
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
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    290.0,
                    -0.0
                ]
            },
            "class": "NodeGroupOutput",
            "input_socket_values": {},
            "label": "Group Output",
            "name": "Group Output",
            "output_socket_values": {}
        },
        {
            "attribute_values": {},
            "class": "ShaderNodeBsdfPrincipled",
            "input_socket_values": {},
            "label": "Principled BSDF",
            "name": "Principled BSDF",
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
                    -463.1018,
                    64.6132
                ],
                "use_custom_color": false,
                "width": 232.2694
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
                "location": [
                    -785.7612,
                    -232.5622
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

        nodes["Group Output"].location = [290.0, -0.0]
        nodes["Group Input"].location = [-785.7612, -232.5622]

        node("ShaderNodeBsdfPrincipled", "Principled BSDF")
        node("MpfbSSSControl", "SSS", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-463.1018, 64.6132], "use_custom_color": False, "width": 232.2694}, input_socket_values={"SubsurfaceRadiusMultiplyer": 1.0})

        link("Group Input", "NailsColor", "Principled BSDF", "Base Color")
        link("Group Input", "NailsMetallic", "Principled BSDF", "Metallic")
        link("Group Input", "NailsRoughness", "Principled BSDF", "Roughness")
        link("Group Input", "Normal", "Principled BSDF", "Normal")
        link("Group Input", "NailsColor", "SSS", "SubsurfaceColor")
        link("Group Input", "NailsSSSStrength", "SSS", "SubsurfaceStrength")
        link("Group Input", "NailsSSSRadiusMutiplier", "SSS", "SubsurfaceRadiusMultiplyer")
        link("Group Input", "NailsSSSIor", "SSS", "SubsurfaceIor")
        #link("SSS", "SubsurfaceColor", "Principled BSDF", "Subsurface Color")
        link("SSS", "SubsurfaceRadius", "Principled BSDF", "Subsurface Radius")
        link("SSS", "SubsurfaceStrength", "Principled BSDF", "Subsurface Weight")
        link("SSS", "SubsurfaceIor", "Principled BSDF", "Subsurface IOR")
        link("Principled BSDF", "BSDF", "Group Output", "BSDF")

NodeWrapperMpfbNails = _NodeWrapperMpfbNails()
