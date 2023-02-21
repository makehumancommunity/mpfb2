"""Functionality for replacing a node tree with v2 skin"""

from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
from mpfb.services.materialservice import MaterialService
from mpfb.services.nodeservice import NodeService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.nodemodel.v2.materials import NodeWrapperSkin
from mpfb._classmanager import ClassManager
from mpfb.ui.developer.developerpanel import DEVELOPER_PROPERTIES
import bpy, os, json, pprint

_LOG = LogService.get_logger("matops.createv2skin")

class MPFB_OT_Create_V2_Skin_Operator(bpy.types.Operator):
    """Wipe all current materials and add a v2 skin material on the selected object"""
    bl_idname = "mpfb.create_v2_skin"
    bl_label = "Create v2 skin"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        obj = context.object
        if not obj:
            return False
        return ObjectService.object_is_basemesh_or_body_proxy(obj)

    def _find_textures_in_enhanced_skin(self, material):
        textures = { "diffuse": None, "normal": None }
        group = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        principled = NodeService.find_first_node_by_type_name(group.node_tree, "ShaderNodeBsdfPrincipled")
        normal = NodeService.find_first_node_by_type_name(group.node_tree, "ShaderNodeNormalMap")

        _LOG.debug("group", group)
        _LOG.debug("principled", principled)
        _LOG.debug("normal", normal)

        if principled:
            bright = NodeService.find_node_linked_to_socket(group.node_tree, principled, "Base Color")
            mix = None
            if bright:
                mix = NodeService.find_node_linked_to_socket(group.node_tree, bright, "Color")
            tex = None
            if mix:
                _LOG.debug("mix", mix)
                for link in group.node_tree.links:
                    if link.to_node == mix and link.from_node.__class__.__name__ == "ShaderNodeTexImage":
                        _LOG.debug("link", (link, link.to_node, link.from_node))
                        tex = link.from_node
            _LOG.debug("tex (diffuse)", tex)
            if tex:
                textures["diffuse"] = NodeService.get_image_file_path(tex)

        if normal:
            tex = NodeService.find_node_linked_to_socket(group.node_tree, normal, "Color")
            _LOG.debug("tex (normal)", tex)
            if tex:
                textures["normal"] = NodeService.get_image_file_path(tex)

        return textures

    def execute(self, context):
        _LOG.enter()

        scene = context.scene
        object = context.object

        from mpfb.ui.matops.matopspanel import MATOPS_PROPERTIES
        recreate_groups = MATOPS_PROPERTIES.get_value("recreate_groups", entity_reference=scene)
        reuse_textures = MATOPS_PROPERTIES.get_value("reuse_textures", entity_reference=scene)

        textures = { "diffuse": None, "normal": None }
        if reuse_textures:
            material = MaterialService.get_material(object)
            if material:
                mat_type = MaterialService.identify_material(material)
                if mat_type == "enhanced_skin":
                    textures = self._find_textures_in_enhanced_skin(material)
            _LOG.debug("textures", textures)

        if recreate_groups:
            for node_tree in bpy.data.node_groups:
                if str(node_tree.name).lower().startswith("mpfb"):
                    bpy.data.node_groups.remove(node_tree)

        MaterialService.delete_all_materials(object)
        material = MaterialService.create_empty_material("v2 skin material", object)
        node_tree = material.node_tree

        if not node_tree:
            self.report({'ERROR'}, "Could not deduce node tree from new empty material")
            return {'FINISHED'}

        NodeWrapperSkin.create_instance(node_tree)

        if reuse_textures and textures and material:
            texco = NodeService.create_node(node_tree, "ShaderNodeTexCoord", name="TexCoord", label="Texture Coordinates", xpos=-901, ypos=425)
            uvsocket = texco.outputs["UV"]
            if textures["diffuse"]:
                diffuse = NodeService.create_image_texture_node(node_tree, name="DiffuseTexture", label="Diffuse Texture", xpos=-556, ypos=602, image_path_absolute=textures["diffuse"])
                mastercol = NodeService.find_first_group_node_by_tree_name(node_tree, "MpfbSkinMasterColor")
                from_socket = diffuse.outputs["Color"]
                to_socket = mastercol.inputs["DiffuseTexture"]
                node_tree.links.new(from_socket, to_socket)
                mastercol.inputs["DiffuseTextureStrength"].default_value = 1.0
                to_socket = diffuse.inputs["Vector"]
                node_tree.links.new(uvsocket, to_socket)
            if textures["normal"]:
                normaltex = NodeService.create_image_texture_node(node_tree, name="NormalmapTexture", label="Normalmap Texture", xpos=-556, ypos=78, image_path_absolute=textures["normal"], colorspace="Non-Color")
                normal = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeNormalMap")
                from_socket = normaltex.outputs["Color"]
                to_socket = normal.inputs["Color"]
                node_tree.links.new(from_socket, to_socket)
                to_socket = normaltex.inputs["Vector"]
                node_tree.links.new(uvsocket, to_socket)
        else:
            _LOG.debug("Not reusing any textures")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Create_V2_Skin_Operator)
