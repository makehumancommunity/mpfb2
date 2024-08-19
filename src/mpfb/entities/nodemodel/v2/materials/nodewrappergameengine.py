import bpy, json

_ORIGINAL_TREE_DEF = json.loads("""
{
    "links": [
        {
            "from_node": "Principled BSDF",
            "from_socket": "BSDF",
            "to_node": "Material Output",
            "to_socket": "Surface"
        },
        {
            "from_node": "DiffuseTexture",
            "from_socket": "Color",
            "to_node": "Principled BSDF",
            "to_socket": "Base Color"
        },
        {
            "from_node": "AlphaMapTexture",
            "from_socket": "Alpha",
            "to_node": "Principled BSDF",
            "to_socket": "Alpha"
        },
        {
            "from_node": "NormalMapTextue",
            "from_socket": "Color",
            "to_node": "Normal Map",
            "to_socket": "Color"
        },
        {
            "from_node": "Normal Map",
            "from_socket": "Normal",
            "to_node": "Principled BSDF",
            "to_socket": "Normal"
        }
    ],
    "nodes": [
        {
            "attribute_values": {
                "location": [
                    66.8581,
                    305.9093
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
                "location": [
                    511.9255,
                    322.1646
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
                    -522.3278,
                    500.8321
                ]
            },
            "class": "ShaderNodeTexImage",
            "input_socket_values": {},
            "label": "Diffuse texture",
            "name": "DiffuseTexture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -526.7584,
                    223.7562
                ]
            },
            "class": "ShaderNodeTexImage",
            "input_socket_values": {},
            "label": "Alpha map texture",
            "name": "AlphaMapTexture",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -529.7121,
                    -63.5768
                ]
            },
            "class": "ShaderNodeTexImage",
            "input_socket_values": {},
            "label": "Normal map texture",
            "name": "NormalMapTextue",
            "output_socket_values": {}
        },
        {
            "attribute_values": {
                "location": [
                    -194.4711,
                    34.6653
                ]
            },
            "class": "ShaderNodeNormalMap",
            "input_socket_values": {},
            "label": "Normal Map",
            "name": "Normal Map",
            "output_socket_values": {}
        }
    ]
}""")

from .abstractmaterialwrapper import AbstractMaterialWrapper

from .....services import LogService
_LOG = LogService.get_logger("material.gameengine")
_LOG.set_level(LogService.DEBUG)

class _NodeWrapperGameEngine(AbstractMaterialWrapper):
    def __init__(self):
        AbstractMaterialWrapper.__init__(self, "GameEngine", _ORIGINAL_TREE_DEF)

    def setup_group_nodes(self, node_tree, nodes, mhmat=None):
        _LOG.debug("setup_group_nodes", mhmat)

        def node(node_class_name, name, label=None, input_socket_values=None, attribute_values=None, output_socket_values=None, mhmat_key=None):
            if not mhmat_key:
                nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)
            if mhmat_key and mhmat.get_value(mhmat_key):
                nodes[name] = AbstractMaterialWrapper.node(node_class_name, node_tree, name, label=label, input_socket_values=input_socket_values, attribute_values=attribute_values, output_socket_values=output_socket_values)
                if "Texture" in mhmat_key:
                    self.assign_mhmat_image(nodes[name], mhmat_key, mhmat)

        def link(from_node, from_socket, to_node, to_socket, mhmat_key=None):
            if not mhmat_key:
                AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

            if mhmat_key and mhmat.get_value(mhmat_key):
                AbstractMaterialWrapper.create_link(node_tree, nodes[from_node], from_socket, nodes[to_node], to_socket)

        nodes["Material Output"].location = [511.9255, 322.1646]

        node("ShaderNodeBsdfPrincipled", "Principled BSDF", attribute_values={"location": [66.8581, 305.9093]}, mhmat_key="")
        node("ShaderNodeTexImage", "DiffuseTexture", label="Diffuse texture", attribute_values={"location": [-522.3278, 500.8321]}, mhmat_key="diffuseTexture")
        node("ShaderNodeTexImage", "AlphaMapTexture", label="Alpha map texture", attribute_values={"location": [-526.7584, 223.7562]}, mhmat_key="diffuseTexture")
        node("ShaderNodeTexImage", "NormalMapTextue", label="Normal map texture", attribute_values={"location": [-529.7121, -63.5768]}, mhmat_key="normalmapTexture")
        node("ShaderNodeNormalMap", "Normal Map", attribute_values={"location": [-194.4711, 34.6653]}, mhmat_key="normalmapTexture")

        link("Principled BSDF", "BSDF", "Material Output", "Surface", mhmat_key="")
        link("DiffuseTexture", "Color", "Principled BSDF", "Base Color", mhmat_key="diffuseTexture")
        link("AlphaMapTexture", "Alpha", "Principled BSDF", "Alpha", mhmat_key="diffuseTexture")
        link("NormalMapTextue", "Color", "Normal Map", "Color", mhmat_key="normalmapTexture")
        link("Normal Map", "Normal", "Principled BSDF", "Normal", mhmat_key="normalmapTexture")

        principled = nodes["Principled BSDF"]
        self.update_principled_sockets_from_mhmat(principled, mhmat)


NodeWrapperGameEngine = _NodeWrapperGameEngine()
