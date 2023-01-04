import bpy, json, os, copy
from mpfb.services.locationservice import LocationService

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
                -664.4424,
                391.6324
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
    "class": "MpfbSystemValueTextureLips",
    "inputs": {},
    "outputs": {
        "Output_0": {
            "class": "NodeSocketFloat",
            "default_value": 0.0,
            "identifier": "Output_0",
            "name": "Value",
            "value_type": "VALUE"
        }
    }
}""")

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "RGB to BW",
            "from_socket": "Val",
            "to_node": "Group Output",
            "to_socket": "Value"
        },
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
        }
    ],
    "nodes": [
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
                "image": {
                    "colorspace": "sRGB",
                    "filepath": ""
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

class NodeWrapperMpfbSystemValueTexture(AbstractGroupWrapper):
    def __init__(self, filename, wrapper_class_name):
        nodedef = copy.deepcopy(_ORIGINAL_NODE_DEF)
        treedef = copy.deepcopy(_ORIGINAL_TREE_DEF)

        nodedef["class"] = wrapper_class_name

        textures = LocationService.get_mpfb_data("textures")
        self.imagevals = dict(treedef["nodes"][4]["attribute_values"]["image"])
        self.imagevals["filepath"] = os.path.join(textures, filename)

        AbstractGroupWrapper.__init__(self, nodedef, treedef)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractGroupWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractGroupWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Group Output"].location = [512.8692, 36.2249]
        nodes["Group Input"].location = [-498.7281, -0.0]

        node("ShaderNodeRGBToBW", "RGB to BW", attribute_values={"location": [298.7282, 37.9499]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-298.7281, -37.9499]})
        node("ShaderNodeTexImage", "System texture", attribute_values={"image": self.imagevals, "location": [-21.1222, 13.8]})

        link("Texture Coordinate", "UV", "System texture", "Vector")
        link("System texture", "Color", "RGB to BW", "Color")

        link("RGB to BW", "Val", "Group Output", "Value")

