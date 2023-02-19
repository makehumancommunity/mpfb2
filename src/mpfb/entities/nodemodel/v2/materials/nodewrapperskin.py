import bpy, json

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Texture Coordinate",
            "from_socket": "UV",
            "to_node": "Image Texture",
            "to_socket": "Vector"
        },
        {
            "from_node": "Image Texture",
            "from_socket": "Color",
            "to_node": "colorgroup",
            "to_socket": "DiffuseTexture"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SkinColor",
            "to_node": "bodygroup",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "NavelCenterColor",
            "to_node": "bodygroup",
            "to_socket": "NavelCenterColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "AureolaeColor",
            "to_node": "aureolaegroup",
            "to_socket": "Color"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SkinColor",
            "to_node": "facegroup",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "LipsColor",
            "to_node": "lipsgroup",
            "to_socket": "LipsColor"
        },
        {
            "from_node": "bodygroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "DefaultBodyShader"
        },
        {
            "from_node": "aureolaegroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "AureolaeShader"
        },
        {
            "from_node": "facegroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "FaceShader"
        },
        {
            "from_node": "lipsgroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "LipsShader"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SpotColor",
            "to_node": "bodygroup",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "EyelidColor",
            "to_node": "facegroup",
            "to_socket": "EyelidColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "FingernailsColor",
            "to_node": "fingernailsgroup",
            "to_socket": "NailsColor"
        },
        {
            "from_node": "fingernailsgroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "FingernailsShader"
        },
        {
            "from_node": "toenailsgroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "ToenailsShader"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "ToenailsColor",
            "to_node": "toenailsgroup",
            "to_socket": "NailsColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SpotColor",
            "to_node": "facegroup",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "VeinColor",
            "to_node": "facegroup",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "VeinColor",
            "to_node": "bodygroup",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SkinColor",
            "to_node": "earsgroup",
            "to_socket": "SkinColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "SpotColor",
            "to_node": "earsgroup",
            "to_socket": "SpotColor"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "VeinColor",
            "to_node": "earsgroup",
            "to_socket": "VeinColor"
        },
        {
            "from_node": "earsgroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "EarsShader"
        },
        {
            "from_node": "colorgroup",
            "from_socket": "GenitalsColor",
            "to_node": "genitalsgroup",
            "to_socket": "Color"
        },
        {
            "from_node": "genitalsgroup",
            "from_socket": "BSDF",
            "to_node": "BodySectionsRouter",
            "to_socket": "GenitalsShader"
        },
        {
            "from_node": "BodySectionsRouter",
            "from_socket": "Shader",
            "to_node": "Material Output",
            "to_socket": "Surface"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "earsgroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "facegroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "bodygroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "lipsgroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "aureolaegroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "fingernailsgroup",
            "to_socket": "Normal"
        },
        {
            "from_node": "masternormal",
            "from_socket": "Normal",
            "to_node": "genitalsgroup",
            "to_socket": "Normal"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "image": {
                    "colorspace": "sRGB",
                    "filepath": "/home/joepal/source/makehuman/ComPlug/mpfb-dev-blends/materials/images/skin-reference.png"
                },
                "location": [
                    -556.7543,
                    602.395
                ]
            },
            "class": "ShaderNodeTexImage",
            "input_socket_values": {},
            "label": "Image Texture",
            "name": "Image Texture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -901.2983,
                    425.4302
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
                    1758.3746,
                    1035.8737
                ]
            },
            "class": "ShaderNodeOutputMaterial",
            "input_socket_values": {},
            "label": "Material Output",
            "name": "Material Output",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -144.3002,
                    132.2753
                ],
                "width": 293.9103
            },
            "class": "ShaderNodeNormalMap",
            "input_socket_values": {},
            "label": "Master normal map",
            "name": "masternormal",
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
                    1376.2086,
                    1011.9443
                ],
                "use_custom_color": false,
                "width": 282.3828
            },
            "class": "MpfbBodySectionsRouter",
            "input_socket_values": {},
            "label": "Final Shader",
            "name": "BodySectionsRouter",
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
                    711.826,
                    2404.9126
                ],
                "use_custom_color": false,
                "width": 315.4109
            },
            "class": "MpfbBody",
            "input_socket_values": {
                "ColorVariationScaleMultiplier": 35.0,
                "ColorVariationStrength": 0.25
            },
            "label": "Body Settings",
            "name": "bodygroup",
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
                    709.2263,
                    1507.9869
                ],
                "use_custom_color": false,
                "width": 331.479
            },
            "class": "MpfbFace",
            "input_socket_values": {
                "ColorVariationScaleMultiplier": 40.0,
                "ColorVariationStrength": 0.25
            },
            "label": "Face Settings",
            "name": "facegroup",
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
                    704.827,
                    661.9699
                ],
                "use_custom_color": false,
                "width": 331.479
            },
            "class": "MpfbEars",
            "input_socket_values": {},
            "label": "Ears Settings",
            "name": "earsgroup",
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
                    708.2214,
                    -157.2171
                ],
                "use_custom_color": false,
                "width": 323.4168
            },
            "class": "MpfbLips",
            "input_socket_values": {},
            "label": "Lips Settings",
            "name": "lipsgroup",
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
                    -142.4896,
                    867.0698
                ],
                "use_custom_color": false,
                "width": 294.3394
            },
            "class": "MpfbSkinMasterColor",
            "input_socket_values": {
                "AureolaeColor": [
                    0.6975,
                    0.3997,
                    0.3149,
                    1.0
                ],
                "LipsColor": [
                    0.8,
                    0.3834,
                    0.3199,
                    1.0
                ],
                "SkinColor": [
                    0.71,
                    0.45,
                    0.32,
                    1.0
                ]
            },
            "label": "Master Color Settings",
            "name": "colorgroup",
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
                    710.5547,
                    -1317.3098
                ],
                "use_custom_color": false,
                "width": 310.2192
            },
            "class": "MpfbGenitals",
            "input_socket_values": {},
            "label": "Genitals Settings",
            "name": "genitalsgroup",
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
                    704.3395,
                    -1079.4694
                ],
                "use_custom_color": false,
                "width": 320.2273
            },
            "class": "MpfbNails",
            "input_socket_values": {},
            "label": "Toenails Settings",
            "name": "toenailsgroup",
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
                    705.4062,
                    -841.0432
                ],
                "use_custom_color": false,
                "width": 320.2273
            },
            "class": "MpfbNails",
            "input_socket_values": {},
            "label": "Fingernails Settings",
            "name": "fingernailsgroup",
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
                    706.7771,
                    -442.8696
                ],
                "use_custom_color": false,
                "width": 323.4169
            },
            "class": "MpfbAureolae",
            "input_socket_values": {},
            "label": "Aureolae Settings",
            "name": "aureolaegroup",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractmaterialwrapper import AbstractMaterialWrapper

class _NodeWrapperSkin(AbstractMaterialWrapper):
    def __init__(self):
        AbstractMaterialWrapper.__init__(self, "Skin", _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes):

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None):
            nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)

        def link(from_node, from_socket, to_node, to_socket):
            AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Material Output"].location = [1758.3746, 1035.8737]

        node("ShaderNodeTexImage", "Image Texture", attribute_values={"image": {"filepath": "/home/joepal/source/makehuman/ComPlug/mpfb-dev-blends/materials/images/skin-reference.png", "colorspace": "sRGB"}, "location": [-556.7543, 602.395]})
        node("ShaderNodeTexCoord", "Texture Coordinate", attribute_values={"location": [-901.2983, 425.4302]})
        node("ShaderNodeNormalMap", "masternormal", label="Master normal map", attribute_values={"location": [-144.3002, 132.2753], "width": 293.9103})
        node("MpfbBodySectionsRouter", "BodySectionsRouter", label="Final Shader", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [1376.2086, 1011.9443], "use_custom_color": False, "width": 282.3828})
        node("MpfbBody", "bodygroup", label="Body Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [711.826, 2404.9126], "use_custom_color": False, "width": 315.4109}, input_socket_values={"ColorVariationStrength": 0.25, "ColorVariationScaleMultiplier": 35.0})
        node("MpfbFace", "facegroup", label="Face Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [709.2263, 1507.9869], "use_custom_color": False, "width": 331.479}, input_socket_values={"ColorVariationStrength": 0.25, "ColorVariationScaleMultiplier": 40.0})
        node("MpfbEars", "earsgroup", label="Ears Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [704.827, 661.9699], "use_custom_color": False, "width": 331.479})
        node("MpfbLips", "lipsgroup", label="Lips Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [708.2214, -157.2171], "use_custom_color": False, "width": 323.4168})
        node("MpfbSkinMasterColor", "colorgroup", label="Master Color Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [-142.4896, 867.0698], "use_custom_color": False, "width": 294.3394}, input_socket_values={"SkinColor": [0.71, 0.45, 0.32, 1.0], "AureolaeColor": [0.6975, 0.3997, 0.3149, 1.0], "LipsColor": [0.8, 0.3834, 0.3199, 1.0]})
        node("MpfbGenitals", "genitalsgroup", label="Genitals Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [710.5547, -1317.3098], "use_custom_color": False, "width": 310.2192})
        node("MpfbNails", "toenailsgroup", label="Toenails Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [704.3395, -1079.4694], "use_custom_color": False, "width": 320.2273})
        node("MpfbNails", "fingernailsgroup", label="Fingernails Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [705.4062, -841.0432], "use_custom_color": False, "width": 320.2273})
        node("MpfbAureolae", "aureolaegroup", label="Aureolae Settings", attribute_values={"color": [0.608, 0.608, 0.608], "height": 100.0, "location": [706.7771, -442.8696], "use_custom_color": False, "width": 323.4169})

        link("Texture Coordinate", "UV", "Image Texture", "Vector")
        link("Image Texture", "Color", "colorgroup", "DiffuseTexture")
        link("colorgroup", "SkinColor", "bodygroup", "SkinColor")
        link("colorgroup", "NavelCenterColor", "bodygroup", "NavelCenterColor")
        link("colorgroup", "AureolaeColor", "aureolaegroup", "Color")
        link("colorgroup", "SkinColor", "facegroup", "SkinColor")
        link("colorgroup", "LipsColor", "lipsgroup", "LipsColor")
        link("bodygroup", "BSDF", "BodySectionsRouter", "DefaultBodyShader")
        link("aureolaegroup", "BSDF", "BodySectionsRouter", "AureolaeShader")
        link("facegroup", "BSDF", "BodySectionsRouter", "FaceShader")
        link("lipsgroup", "BSDF", "BodySectionsRouter", "LipsShader")
        link("colorgroup", "SpotColor", "bodygroup", "SpotColor")
        link("colorgroup", "EyelidColor", "facegroup", "EyelidColor")
        link("colorgroup", "FingernailsColor", "fingernailsgroup", "NailsColor")
        link("fingernailsgroup", "BSDF", "BodySectionsRouter", "FingernailsShader")
        link("toenailsgroup", "BSDF", "BodySectionsRouter", "ToenailsShader")
        link("colorgroup", "ToenailsColor", "toenailsgroup", "NailsColor")
        link("colorgroup", "SpotColor", "facegroup", "SpotColor")
        link("colorgroup", "VeinColor", "facegroup", "VeinColor")
        link("colorgroup", "VeinColor", "bodygroup", "VeinColor")
        link("colorgroup", "SkinColor", "earsgroup", "SkinColor")
        link("colorgroup", "SpotColor", "earsgroup", "SpotColor")
        link("colorgroup", "VeinColor", "earsgroup", "VeinColor")
        link("earsgroup", "BSDF", "BodySectionsRouter", "EarsShader")
        link("colorgroup", "GenitalsColor", "genitalsgroup", "Color")
        link("genitalsgroup", "BSDF", "BodySectionsRouter", "GenitalsShader")
        link("BodySectionsRouter", "Shader", "Material Output", "Surface")
        link("masternormal", "Normal", "earsgroup", "Normal")
        link("masternormal", "Normal", "facegroup", "Normal")
        link("masternormal", "Normal", "bodygroup", "Normal")
        link("masternormal", "Normal", "lipsgroup", "Normal")
        link("masternormal", "Normal", "aureolaegroup", "Normal")
        link("masternormal", "Normal", "fingernailsgroup", "Normal")
        link("masternormal", "Normal", "genitalsgroup", "Normal")

NodeWrapperSkin = _NodeWrapperSkin()
