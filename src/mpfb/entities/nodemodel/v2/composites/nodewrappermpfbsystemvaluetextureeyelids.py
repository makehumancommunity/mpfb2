import bpy, json

_ORIGINAL_NODE_DEF = json.loads("""
{
    "class": "MpfbSystemValueTextureEyelids",
    "inputs": {},
    "outputs": {
        "Output_Socket_Value": {
            "name": "Value",
            "identifier": "Socket_0",
            "class": "NodeSocketFloat",
            "value_type": "VALUE",
            "default_value": 0.0
        }
    },
    "attributes": {
        "color": {
            "name": "color",
            "class": "Color",
            "value": [
                0.35,
                0.35,
                0.0
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
                -1468.9873,
                748.6599
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
            "value": 297.9847
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Texture Coordinate",
            "from_socket": "UV",
            "to_node": "System texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "System texture",
            "from_socket": "Color",
            "to_node": "RGB to BW",
            "to_socket": "Color"
        },
        {
            "from_node": "RGB to BW",
            "from_socket": "Val",
            "to_node": "Group Output",
            "to_socket": "Value"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    -498.7281,
                    -0.0
                ]
            },
            "class": "NodeGroupInput",
            "input_socket_values": {},
            "label": "Group Input",
            "name": "Group Input",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    512.8692,
                    36.2249
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
                    298.7282,
                    37.9499
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
                "location": [
                    -298.7281,
                    -37.9499
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
                "image": {
                    "colorspace": "sRGB",
                    "filepath": "/home/joepal/source/makehuman/ComPlug/mpfb2/src/mpfb/data/textures/mpfb_eyelids.jpg"
                },
                "location": [
                    -21.1222,
                    13.8
                ]
            },
            "class": "ShaderNodeTexImage",
            "input_socket_values": {},
            "label": "System texture",
            "name": "System texture",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractgroupwrapper import AbstractGroupWrapper

class _NodeWrapperMpfbSystemValueTextureEyelids(AbstractGroupWrapper):
    def __init__(self):
        AbstractGroupWrapper.__init__(self, _ORIGINAL_NODE_DEF, _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Input"].location = [-498.7281, -0.0]
        nodes["Group Output"].location = [512.8692, 36.2249]

        node("ShaderNodeRGBToBW", "RGB to BW", attribute_values={"location": [298.7282, 37.9499]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-298.7281, -37.9499]})
        node("ShaderNodeTexImage", "System texture", attribute_values={"image": {"filepath": "/home/joepal/source/makehuman/ComPlug/mpfb2/src/mpfb/data/textures/mpfb_eyelids.jpg", "colorspace": "sRGB"}, "location": [-21.1222, 13.8]})

        link("Texture Coordinate", "UV", "System texture", "Vector")
        link("System texture", "Color", "RGB to BW", "Color")
        link("RGB to BW", "Val", "Group Output", "Value")

NodeWrapperMpfbSystemValueTextureEyelids = _NodeWrapperMpfbSystemValueTextureEyelids()
