"""Various functions for working with materials"""

import os, bpy

from .logservice import LogService
from .objectservice import ObjectService
from .nodeservice import NodeService
from ..entities.nodemodel.v2.materials import NodeWrapperSkin

_LOG = LogService.get_logger("services.materialservice")


class MaterialService():
    """The MaterialService class is a utility class designed to handle various operations related to MPFB materials in Blender.
    It provides a collection of static methods that facilitate the creation, modification, and management of materials assigned
    to Blender objects. The class is not meant to be instantiated; instead, its static methods should be used directly.

    Its key responsibilities are:

    - Creating, adding and removing materials
    - Identifying material
    - Checking the validity of materials
    - I/O operations for loading and saving materials

    Overall, the MaterialService class provides a comprehensive set of tools for managing MPFB materials in Blender,
    making it easier to work with complex material setups and ensuring consistency across different objects and scenes."""

    def __init__(self):
        """You should not instance MaterialService. Use its static methods instead."""
        raise RuntimeError("You should not instance MaterialService. Use its static methods instead.")

    @staticmethod
    def delete_all_materials(blender_object, also_destroy_groups=False):
        """Deletes all materials from the given blender object.

        Args:
            blender_object (bpy.types.Object): The blender object to delete materials from.
            also_destroy_groups (bool): Whether to also destroy the groups that were created for the materials.
        """
        _LOG.dump("Current materials", (blender_object.data.materials, len(blender_object.data.materials)))
        for material in blender_object.data.materials:
            material.name = material.name + ".unused"
            if also_destroy_groups:
                NodeService.clear_node_tree(material.node_tree, also_destroy_groups=True)
        while len(blender_object.data.materials) > 0:
            blender_object.data.materials.pop()
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

    @staticmethod
    def has_materials(blender_object):
        """Check if object has any materials at all assigned"""
        if not blender_object.material_slots:
            return False
        return len(blender_object.material_slots) > 0

    @staticmethod
    def get_material(blender_object, slot=0):
        """Return the material in the object's given material slot"""
        if not blender_object.material_slots or len(blender_object.material_slots) < 1:
            return None
        return blender_object.material_slots[slot].material

    @staticmethod
    def identify_material(material):
        """Try to figure out which kind of material we have"""
        if not material:
            return "empty"
        nodes = material.node_tree.nodes

        if len(nodes) == 0:
            return "empty"

        for node in nodes:
            node_info = NodeService.get_node_info(node)
            if node_info and node_info["type"] == "ShaderNodeGroup" and node_info["values"]:
                # Material is potentially a procedural type material
                _LOG.debug("node_info", node_info)
                if "Pore detail" in node_info["values"]:
                    return "enhanced_skin"
                if "IrisSection4Color" in node_info["values"]:
                    return "procedural_eyes"
                if "NavelCenterOverride" in node_info["values"]:
                    return "layered_skin"

        # Since we're not enhanced skin nor procedural eyes, next guess is makeskin. The
        # diffuseIntensity node should always be there even if there is no diffuse texture.
        if NodeService.find_node_by_name(material.node_tree, "diffuseIntensity"):
            return "makeskin"

        # The final guess is GameEngine.
        # This might give a false positive if someone added a material with a principled node
        # to a MH object
        if NodeService.find_node_by_name(material.node_tree, "Principled BSDF"):
            return "gameengine"

        return "unknown"

    @staticmethod
    def _set_normalmap_in_nodetree(node_tree, filename):
        _LOG.debug("Will set normalmap", filename)

        links = node_tree.links

        normalmap = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeNormalMap")
        _LOG.debug("Normalmap in initial sweep", normalmap)

        image_node = None
        if normalmap:
            # There is already a normalmap, no need to create another
            image_node = NodeService.find_node_linked_to_socket(node_tree, normalmap, "Color")
            _LOG.debug("Image node in pre-existing setup", image_node)
        else:
            # Will need to create setup for normalmap and its texture node
            principled = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeBsdfPrincipled")
            _LOG.debug("Principled", principled)

            normalmap = NodeService.create_normal_map_node(node_tree, xpos=-300)
            _LOG.debug("Normalmap", normalmap)

            bump = NodeService.find_node_linked_to_socket(node_tree, principled, "Normal")
            to_socket = None
            _LOG.debug("Bump", bump)
            if bump:
                # There is a bump map, so hook the normalmap to that
                to_socket = bump.inputs["Normal"]
            else:
                to_socket = principled.inputs["Normal"]

            _LOG.debug("to_socket", to_socket)

            from_socket = normalmap.outputs["Normal"]
            _LOG.debug("from_socket", from_socket)

            links.new(from_socket, to_socket)

        if not image_node:
            image_node = NodeService.create_image_texture_node(node_tree, xpos=-600)
            _LOG.debug("Image node, newly created", image_node)

            from_socket = image_node.outputs["Color"]
            to_socket = normalmap.inputs["Color"]

            links.new(from_socket, to_socket)

        image_file_name = os.path.basename(filename)
        image = None
        if image_file_name in bpy.data.images:
            _LOG.debug("image was previously loaded", filename)
            image = bpy.data.images[image_file_name]
        else:
            image = bpy.data.images.load(filename)
        image.colorspace_settings.name = "Non-Color"

        image_node.image = image

    @staticmethod
    def set_normalmap(material, filename):
        """Try to modify the material so that it uses the normal map"""
        material_type = MaterialService.identify_material(material)

        if material_type == "enhanced_skin":
            group = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
            MaterialService._set_normalmap_in_nodetree(group.node_tree, filename)
            return

        if material_type in ["makeskin", "layered_skin"]:
            MaterialService._set_normalmap_in_nodetree(material.node_tree, filename)
            return

        raise ValueError('Cannot set normalmap in material of type ' + material_type)

    @staticmethod
    def assign_new_or_existing_material(name, blender_object):
        """Assigns a new material to the given blender object.

        Args:
            name (str): The name of the material to assign.
            blender_object (bpy.types.Object): The blender object to assign the material to.

        Returns:
            bpy.types.Material: The material that was assigned.
        """
        if name in bpy.data.materials:
            material = bpy.data.materials[name]
            if not blender_object is None:
                blender_object.data.materials.append(material)
        else:
            material = MaterialService.create_empty_material(name, blender_object)
        return material

    @staticmethod
    def create_empty_material(name, blender_object=None):
        """
        Create a new empty material with the given name, and assign it to the blender object
        if given.
        """

        material = bpy.data.materials.new(name)
        material.use_nodes = True
        material.blend_method = 'HASHED'
        if blender_object is not None:
            blender_object.data.materials.append(material)
        return material

    @staticmethod
    def create_v2_skin_material(name, blender_object=None, mhmat_file=None):
        """Create a new v2 skin material with the given name, and assign it to the blender object.

        Args:
            name (str): The name of the material to assign.
            blender_object (bpy.types.Object): The blender object to assign the material to.
            mhmat_file (str): The path to the mhmat file to use.

        Returns:
            bpy.types.Material: The material that was assigned.
        """

        if blender_object is None:
            raise ValueError("Object needed when creating a v2 skin")

        MaterialService.delete_all_materials(blender_object)
        material = MaterialService.create_empty_material(name, blender_object)

        node_tree = material.node_tree

        if not node_tree:
            raise ValueError("Could not deduce node tree from new empty material")

        NodeWrapperSkin.create_instance(node_tree)

        mastercolor = NodeService.find_first_group_node_by_tree_name(node_tree, "MpfbSkinMasterColor")
        if mastercolor:
            # In case we do not find a diffuse texture later on
            mastercolor.inputs["DiffuseTextureStrength"].default_value = 0.0
        else:
            _LOG.warn("Could not find master color control in v2 skin")

        if mhmat_file:
            from ..entities.material.makeskinmaterial import MakeSkinMaterial
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(mhmat_file)

            diffuse = makeskin_material.get_value("diffuseTexture")
            normalmap = makeskin_material.get_value("normalmapTexture")

            _LOG.debug("Textures", (diffuse, normalmap))

            if normalmap or diffuse:
                texco = NodeService.create_node(node_tree, "ShaderNodeTexCoord", name="TexCoord", label="Texture Coordinates", xpos=-901, ypos=425)
                uvsocket = texco.outputs["UV"]

            if normalmap:
                MaterialService.set_normalmap(material, normalmap)
                # TODO: link to texco for completeness

            if diffuse:
                node_tree = material.node_tree
                diffuse = NodeService.create_image_texture_node(node_tree,
                                                                name="DiffuseTexture",
                                                                label="Diffuse Texture",
                                                                xpos=-556,
                                                                ypos=602,
                                                                image_path_absolute=diffuse)
                from_socket = diffuse.outputs["Color"]
                to_socket = mastercolor.inputs["DiffuseTexture"]
                node_tree.links.new(from_socket, to_socket)
                mastercolor.inputs["DiffuseTextureStrength"].default_value = 1.0
                to_socket = diffuse.inputs["Vector"]
                node_tree.links.new(uvsocket, to_socket)

        material.diffuse_color = MaterialService.get_skin_diffuse_color()

        return material

    @staticmethod
    def as_blend_path(path):
        """
        Converts a relative path to an asset in a blender library to an absolute path to the blend,
        the location of the asset in the blend and the name of the asset, ie return:

        (path, location, name)
        """
        blend_path, dir_name, asset_name = (part.strip() for part in path.rsplit('/', 2))
        return blend_path, dir_name, asset_name

    @staticmethod
    def save_material_in_blend_file(blender_object, path_to_blend_file, material_number=None, fake_user=False):
        """
        Save the material(s) on the active object to a blend file. If material_number is None, save all
        the object's materials. Otherwise, save material slot with that number. This writes into the file
        but will not overwrite it, although it might overwrite something already in it.
        """
        if material_number is not None:
            for mat_slot in blender_object.material_slots:
                mat = mat_slot.material
                bpy.data.libraries.write(str(path_to_blend_file), {mat}, fake_user=fake_user)
        else:
            mat = blender_object.material_slots[material_number].material
            bpy.data.libraries.write(str(path_to_blend_file), {mat}, fake_user=fake_user)
        print('Wrote blend file into:', path_to_blend_file)

    @staticmethod
    def load_material_from_blend_file(path, blender_object=None):
        """
        Load a material from a blend file determined by path, to a new material slot.
        """
        path, dir_name, asset_name = MaterialService.as_blend_path(path)
        print('Loading material @: ', path, dir_name, asset_name)
        with bpy.data.libraries.load(path) as (in_basket, out_basket):
            # Weird syntax.
            setattr(out_basket, dir_name, [asset_name])

        mat = getattr(out_basket, dir_name)[0]
        mat.make_local()

        if blender_object is not None:
            blender_object.data.materials.append(mat)
        return mat

    @staticmethod
    def _assign_material_instance(blender_object, material, group_name):
        _LOG.enter()
        _LOG.debug("blender_object, material, group_name", (blender_object, material, group_name))

        if not ObjectService.has_vertex_group(blender_object, group_name):
            return

        ObjectService.activate_blender_object(blender_object)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        blender_object.data.materials.append(material)
        slot_number = blender_object.material_slots.find(material.name)
        _LOG.dump("slot_number", slot_number)

        bpy.context.object.active_material_index = slot_number

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group=group_name)
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    @staticmethod
    def create_and_assign_material_slots(basemesh, bodyproxy=None):
        """Creates and assigns material slots for each body vertex group.

        Args:
            basemesh (bpy.types.Mesh): The base mesh to assign material slots to.
            bodyproxy (bpy.types.Object): The body proxy to assign material slots to (optional).
        """

        if not MaterialService.has_materials(basemesh):
            raise ValueError("Basemesh must have the initial material created before calling this method")

        _LOG.debug("basemesh, proxymesh", (basemesh, bodyproxy))

        base_material = basemesh.material_slots[0].material

        prefix = str(basemesh.name).split(".")[0]

        _LOG.debug("prefix", prefix)

        if bodyproxy is not None:
            MaterialService.delete_all_materials(bodyproxy)
            MaterialService.assign_new_or_existing_material(base_material.name, bodyproxy)

        for group_name in ["nipple", "lips", "fingernails", "toenails", "ears", "genitals"]:
            _LOG.debug("About to create material instance for", group_name)
            material_instance = base_material.copy()
            material_instance.name = prefix + "." + group_name
            _LOG.debug("Material final name", material_instance.name)
            if basemesh and ObjectService.has_vertex_group(basemesh, group_name):
                MaterialService._assign_material_instance(basemesh, material_instance, group_name)
            if bodyproxy and ObjectService.has_vertex_group(bodyproxy, group_name):
                MaterialService._assign_material_instance(bodyproxy, material_instance, group_name)
            else:
                _LOG.debug("Not adding slot to bodyproxy because it is none or group does not exist", (bodyproxy, group_name))

    @staticmethod
    def find_color_adjustment(blender_object):
        """Return a dict with all color adjustments that were applied to the blender object's material slots.

        Args:
            blender_object (bpy.types.Object): The blender object to find color adjustments for.

        Returns:
            A dict with all color adjustments that were applied to the blender object's material slots.'
        """
        if not blender_object:
            _LOG.debug("The blender object was none")
            return None
        material = MaterialService.get_material(blender_object)
        if not material:
            _LOG.debug("The blender object did not have a material")
            return None

        if not material.node_tree:
            raise ValueError('Could not find node tree on material for ' + str(blender_object))

        principled = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeBsdfPrincipled")
        if not principled:
            _LOG.debug("The material did not have a principled node, maybe not a makeskin material? ", blender_object)
            return None

        mix = NodeService.find_node_linked_to_socket(material.node_tree, principled, "Base Color")

        if not mix:
            _LOG.debug("There was no mix node")
            return None

        info = NodeService.get_node_info(mix)

        if not info or "values" not in info:
            raise ValueError('Could not find values:' + str(info))

        return info["values"]

    @staticmethod
    def apply_color_adjustment(blender_object, color_adjustment):
        """Apply a color adjustment to the blender object's material slots.

        Args:
            blender_object (bpy.types.Object): The blender object to apply the color adjustment to.
            color_adjustment (dict): The color adjustment to apply.
        """
        if not blender_object:
            _LOG.debug("The blender object was none")
            return
        if not blender_object:
            _LOG.debug("The color adjustment was none")
            return

        material = MaterialService.get_material(blender_object)
        if not material:
            _LOG.debug("The blender object did not have a material")
            return

        if not material.node_tree:
            raise ValueError('Could not find node tree on material for ' + str(blender_object))

        principled = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeBsdfPrincipled")
        if not principled:
            _LOG.debug("The material did not have a principled node, maybe not a makeskin material? ", blender_object)
            return

        mix = NodeService.find_node_linked_to_socket(material.node_tree, principled, "Base Color")

        NodeService.set_socket_default_values(mix, color_adjustment)

    @staticmethod
    def _find_principled_and_connected_color_node(node_tree):
        """Find the principled and the node connected to base color."""

        # First find the principled node
        principled = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeBsdfPrincipled")
        if not principled:
            return None, None

        # Figure out which node that connects to the base color socket
        connected_node = NodeService.find_node_linked_to_socket(node_tree, principled, "Base Color")
        _LOG.debug("Connected node", connected_node)
        if connected_node is None:
            _LOG.debug("The principled node did not have a connected node to the Base Color socket")
        else:
            _LOG.debug("The principled node did have a connected node", connected_node)

        return principled, connected_node

    @staticmethod
    def _insert_first_ink_layer_nodes(node_tree, principled, diffuse_intensity):
        """Break the link between the principled node and the diffuseIntensity node, then add new nodes for ink layer 1."""

        # Remove the link between the principled node and the diffuseIntensity node
        NodeService.remove_link(node_tree, principled, "Base Color")

        # Create a mix rgb node
        mix_node = NodeService.create_mix_rgb_node(node_tree, "inkLayer1mix", "Ink Layer 1 Mix", xpos=-300, ypos=1000)

        # Create an image texture node
        texture = NodeService.create_image_texture_node(node_tree, "inkLayer1tex", "Ink layer 1 Texture", xpos=-700, ypos=1100)

        # Create an uv map node
        uvmap = NodeService.create_node(node_tree, "ShaderNodeUVMap", name="inkLayer1uv", label="Ink Layer 1 UV", xpos=-1000, ypos=1000)

        # Add links
        NodeService.add_link(node_tree, mix_node, principled, "Color", "Base Color")
        NodeService.add_link(node_tree, diffuse_intensity, mix_node, "Color", "Color1")
        NodeService.add_link(node_tree, texture, mix_node, "Color", "Color2")
        NodeService.add_link(node_tree, texture, mix_node, "Alpha", "Fac")
        NodeService.add_link(node_tree, uvmap, texture, "UV", "Vector")

        return uvmap, texture

    @staticmethod
    def add_focus_nodes(material, uv_map_name=None):
        """Add a node setup for a focus."""

        if not material:
            raise ValueError("A material must be provided")

        if MaterialService.identify_material(material) != "makeskin":
            raise ValueError("The material must be a makeskin material")

        _LOG.debug("material", material)

        principled, connected_node = MaterialService._find_principled_and_connected_color_node(material.node_tree)

        if not principled:
            raise ValueError("The material did not have a principled node, maybe not a makeskin material?")

        if not connected_node:
            raise ValueError("The material did not have anything connected to the principled node base color, maybe not a makeskin material?")

        if connected_node.name == "diffuseIntensity":
            _LOG.debug("The principled node is connected to from diffuseIntensity", connected_node)
        else:
            _LOG.debug("The principled node is connected to from something other than diffuseIntensity", connected_node)
            raise NotImplementedError("Only one ink layer is supported at the moment")

        uvmap_node, texture_node = MaterialService._insert_first_ink_layer_nodes(material.node_tree, principled, connected_node)

        if uv_map_name is not None:
            uvmap_node.uv_map = uv_map_name

        return uvmap_node, texture_node, 1

    @staticmethod
    def get_skin_diffuse_color():
        """Return a static color for the skin material, for example to be used in the viewport."""
        return [0.721, 0.568, 0.431, 1.0]

    @staticmethod
    def get_generic_bodypart_diffuse_color():
        """Return a static color for a bodypart material, for example to be used in the viewport."""
        return [0.194, 0.030, 0.014, 1.0]

    @staticmethod
    def get_generic_clothes_diffuse_color():
        """Return a static color for a clothes material, for example to be used in the viewport."""
        return [0.6, 0.6, 0.6, 1.0]

    @staticmethod
    def get_eye_diffuse_color():
        """Return a static color for the eye material, for example to be used in the viewport."""
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_teeth_diffuse_color():
        """Return a static color for the teeth material, for example to be used in the viewport."""
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_diffuse_colors():
        """Return all static colors for all materials."""
        colors = dict()
        colors["Eyes"] = MaterialService.get_eye_diffuse_color()
        colors["Teeth"] = MaterialService.get_teeth_diffuse_color()
        colors["Proxymeshes"] = MaterialService.get_skin_diffuse_color()
        colors["Proxymesh"] = MaterialService.get_skin_diffuse_color()
        colors["Bodyproxy"] = MaterialService.get_skin_diffuse_color()
        colors["Basemesh"] = MaterialService.get_skin_diffuse_color()
        colors["Clothes"] = MaterialService.get_generic_clothes_diffuse_color()

        for key in ["Bodypart", "Eyebrows", "Eyelashes", "Hair", "Tongue"]:
            colors[key] = MaterialService.get_generic_bodypart_diffuse_color()

        return colors
