"""Various functions for working with materials"""

import os, bpy, json, gzip, typing
from typing import Any

from .locationservice import LocationService
from .logservice import LogService
from .objectservice import ObjectService
from .nodeservice import NodeService
from .meshservice import MeshService
from ..entities.nodemodel.v2.materials import NodeWrapperSkin
from ..entities.nodemodel.v2.composites import NodeWrapperMpfbAlphaMixer

_LOG = LogService.get_logger("services.materialservice")

MaterialType = typing.Literal["empty", "enhanced_skin", "procedural_eyes", "layered_skin", "makeskin", "gameengine", "unknown"]
"""The seven answers ``identify_material()`` can give.

A literal rather than a bare ``str``, so that the type tests the rest of the module performs against
the result are checked against the same set of values the identifier can actually return."""

InkLayerNodes = tuple[bpy.types.Node, bpy.types.Node]
"""The ``(uvmap_node, texture_node)`` pair the four private ink layer builders return.

The nodes are a ``ShaderNodeUVMap`` and a ``ShaderNodeTexImage`` at runtime. The second is now typed
as such by ``NodeService.create_image_texture_node()``, but the first comes from the generic
``create_node()``, which answers the ``Node`` base class -- so naming the pair precisely would mean
a cast at each of the four returns for one caller's benefit. The base class is kept for both."""

# On the node finders: NodeService's find_* methods answer Node | None, and NodeService.add_link()
# does not check the nodes it is handed, so a None reaches links.new() as one. Where a method below
# passes a found node on without testing it, the cast records the precondition which makes the
# lookup safe -- usually that identify_material() has already answered for this material, or that
# the node was created by the same method a moment earlier. The one exception is
# remove_all_makeup(), which is noted at the site.
#
# On socket default values: NodeSocket does not declare default_value. It is declared on each concrete
# socket subclass instead, which is what nodeservice's own hasattr() guard acknowledges, so every read
# or write of one below casts the socket to the subclass it is at runtime. The colour writes then meet
# bpy_prop_array, which no python sequence satisfies although assigning a tuple to a fixed size float
# array is ordinary at runtime, so those additionally carry a narrow ignore.

ColorAdjustment = dict[str, Any]
"""The socket-name to default-value mapping that ``find_color_adjustment()`` returns and
``apply_color_adjustment()`` accepts.

The values are whatever ``NodeService.get_node_info()`` read off the sockets, which for a mix node
means a mixture of floats and RGBA sequences, so ``Any`` is the honest value type."""


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

    def __init__(self) -> None:
        """You should not instance MaterialService. Use its static methods instead."""
        raise RuntimeError("You should not instance MaterialService. Use its static methods instead.")

    @staticmethod
    def delete_all_materials(blender_object: bpy.types.Object, also_destroy_groups: bool = False) -> None:
        """Deletes all materials from the given blender object.

        Args:
            blender_object (bpy.types.Object): The blender object to delete materials from.
            also_destroy_groups (bool): Whether to also destroy the groups that were created for the materials.
        """
        materials = typing.cast(bpy.types.Mesh, blender_object.data).materials
        _LOG.dump("Current materials", (materials, len(materials)))
        for material in materials:            
            mat = typing.cast(bpy.types.Material, material)
            mat.name = mat.name + ".unused"
            if also_destroy_groups:
                # Material.node_tree is None until use_nodes is set, which every material MPFB
                # makes or loads has had set.
                NodeService.clear_node_tree(typing.cast(bpy.types.NodeTree, mat.node_tree), also_destroy_groups=True)
        while len(materials) > 0:
            materials.pop()
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

    @staticmethod
    def has_materials(blender_object: bpy.types.Object) -> bool:
        """Check if object has any materials at all assigned"""
        if not blender_object.material_slots:
            return False
        return len(blender_object.material_slots) > 0

    @staticmethod
    def get_material(blender_object: bpy.types.Object, slot: int = 0) -> bpy.types.Material | None:
        """Return the material in the object's given material slot"""
        if not blender_object.material_slots or len(blender_object.material_slots) < 1:
            return None
        return blender_object.material_slots[slot].material

    @staticmethod
    def identify_material(material: bpy.types.Material | None) -> MaterialType:
        """Try to figure out which kind of material we have"""
        if not material:
            return "empty"
        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)
        nodes = node_tree.nodes

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
        # diffuseIntensity is there in most cases.
        if NodeService.find_node_by_name(node_tree, "diffuseIntensity"):
            return "makeskin"

        # The final guess is GameEngine.
        # This might give a false positive if someone added a material with a principled node
        # to a MH object
        if NodeService.find_node_by_name(node_tree, "Principled BSDF"):
            return "gameengine"

        return "unknown"

    @staticmethod
    def _set_normalmap_in_nodetree(node_tree: bpy.types.NodeTree, filename: str) -> None:
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

            # A material without a principled node would raise out of find_node_linked_to_socket()
            # here, which tests its own arguments; see the note at the top of the module.
            bump = NodeService.find_node_linked_to_socket(node_tree, typing.cast(bpy.types.Node, principled), "Normal")
            to_socket = None
            _LOG.debug("Bump", bump)
            if bump:
                # There is a bump map, so hook the normalmap to that
                to_socket = bump.inputs["Normal"]
            else:
                # find_node_linked_to_socket() raises on a None node, so the call on the line above
                # has already ruled out a missing principled node by the time we get here.
                to_socket = typing.cast(bpy.types.Node, principled).inputs["Normal"]

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
        image: bpy.types.Image
        if image_file_name in bpy.data.images:
            _LOG.debug("image was previously loaded", filename)
            image = bpy.data.images[image_file_name]
        else:
            image = bpy.data.images.load(filename)
        # Image.colorspace_settings cannot be None: DNA_image_types.h:246 declares it as an embedded
        # ColorManagedColorspaceSettings struct rather than a pointer, so there is nothing for it to be
        # null for. The RNA enum behind its name carries only "NONE" statically, because the real
        # colorspace list is populated from OCIO at runtime, so no stub can know "Non-Color".
        colorspace = typing.cast(bpy.types.ColorManagedInputColorspaceSettings, image.colorspace_settings)
        colorspace.name = "Non-Color"  # pyright: ignore[reportAttributeAccessIssue]

        # Only ShaderNodeTexImage carries an image. image_node is either the node found linked to
        # the normal map's Color socket, which is one, or the one created above.
        typing.cast(bpy.types.ShaderNodeTexImage, image_node).image = image

    @staticmethod
    def set_normalmap(material: bpy.types.Material, filename: str) -> None:
        """Try to modify the material so that it uses the normal map"""
        material_type = MaterialService.identify_material(material)

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        if material_type == "enhanced_skin":
            # identify_material() only answers enhanced_skin after finding a ShaderNodeGroup whose
            # values carry "Pore detail", so the same search here cannot come back empty.
            group = typing.cast(bpy.types.ShaderNodeGroup, NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeGroup"))
            MaterialService._set_normalmap_in_nodetree(typing.cast(bpy.types.NodeTree, group.node_tree), filename)
            return

        if material_type in ["makeskin", "layered_skin"]:
            MaterialService._set_normalmap_in_nodetree(node_tree, filename)
            return

        raise ValueError('Cannot set normalmap in material of type ' + material_type)

    @staticmethod
    def assign_new_or_existing_material(name: str, blender_object: bpy.types.Object | None) -> bpy.types.Material:
        """Assigns a new material to the given blender object.

        Args:
            name (str): The name of the material to assign.
            blender_object (bpy.types.Object | None): The blender object to assign the material to.

        Returns:
            bpy.types.Material: The material that was assigned.
        """
        if name in bpy.data.materials:
            material = bpy.data.materials[name]
            if not blender_object is None:
                typing.cast(bpy.types.Mesh, blender_object.data).materials.append(material)
        else:
            material = MaterialService.create_empty_material(name, blender_object)
        return material

    @staticmethod
    def create_empty_material(name: str, blender_object: bpy.types.Object | None = None) -> bpy.types.Material:
        """
        Create a new empty material with the given name, and assign it to the blender object
        if given.
        """

        material = bpy.data.materials.new(name)
        material.use_nodes = True
        material.blend_method = 'HASHED'
        if blender_object is not None:
            typing.cast(bpy.types.Mesh, blender_object.data).materials.append(material)
        return material

    @staticmethod
    def create_v2_skin_material(name: str, blender_object: bpy.types.Object | None = None,
                                mhmat_file: str | None = None) -> bpy.types.Material:
        """Create a new v2 skin material with the given name, and assign it to the blender object.

        Args:
            name (str): The name of the material to assign.
            blender_object (bpy.types.Object | None): The blender object to assign the material to. A
                None object raises, despite the default; the argument is only optional in form.
            mhmat_file (str | None): The path to the mhmat file to use.

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
            # In case we do not find a diffuse texture later on. NodeSocket does not declare
            # default_value; it is declared on each concrete socket subclass.
            typing.cast(bpy.types.NodeSocketFloat, mastercolor.inputs["DiffuseTextureStrength"]).default_value = 0.0
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
                # Re-read rather than reuse the local: set_normalmap() above has rewritten the tree,
                # and the declared type of material.node_tree is optional again on every read.
                node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)
                diffuse = NodeService.create_image_texture_node(node_tree,
                                                                name="DiffuseTexture",
                                                                label="Diffuse Texture",
                                                                xpos=-556,
                                                                ypos=602,
                                                                image_path_absolute=diffuse)
                from_socket = diffuse.outputs["Color"]
                # NodeWrapperSkin.create_instance() above unconditionally builds the
                # MpfbSkinMasterColor group, so the lookup that set mastercolor cannot have missed. The
                # branch that merely warns above is defensive against a broken node data install, and
                # this dereference would fail in that case too.
                master = typing.cast(bpy.types.Node, mastercolor)
                to_socket = master.inputs["DiffuseTexture"]
                node_tree.links.new(from_socket, to_socket)
                typing.cast(bpy.types.NodeSocketFloat, master.inputs["DiffuseTextureStrength"]).default_value = 1.0
                to_socket = diffuse.inputs["Vector"]
                node_tree.links.new(uvsocket, to_socket)

        # Material.diffuse_color is declared bpy_prop_array[float], which no python sequence satisfies,
        # although assigning a list to a fixed size float array is ordinary at runtime.
        material.diffuse_color = MaterialService.get_skin_diffuse_color()  # pyright: ignore[reportAttributeAccessIssue]

        return material

    @staticmethod
    def as_blend_path(path: str) -> tuple[str, str, str]:
        """
        Converts a relative path to an asset in a blender library to an absolute path to the blend,
        the location of the asset in the blend and the name of the asset, ie return:

        (path, location, name)
        """
        blend_path, dir_name, asset_name = (part.strip() for part in path.rsplit('/', 2))
        return blend_path, dir_name, asset_name

    @staticmethod
    def save_material_in_blend_file(blender_object: bpy.types.Object, path_to_blend_file: str,
                                    material_number: int | None = None, fake_user: bool = False) -> None:
        """
        Save the material(s) on the active object to a blend file. If material_number is None, save all
        the object's materials. Otherwise, save material slot with that number. This writes into the file
        but will not overwrite it, although it might overwrite something already in it.

        TODO: Note that the two branches below are the wrong way round, so the method does the opposite of
        what this docstring says and raises when material_number is left at its default.
        """
        if material_number is not None:
            for mat_slot in blender_object.material_slots:
                mat = mat_slot.material
                bpy.data.libraries.write(str(path_to_blend_file), {typing.cast(bpy.types.Material, mat)}, fake_user=fake_user)
        else:
            # The index is None on this branch, which is the inverted test described above.
            mat = blender_object.material_slots[typing.cast(int, material_number)].material
            bpy.data.libraries.write(str(path_to_blend_file), {typing.cast(bpy.types.Material, mat)}, fake_user=fake_user)
        print('Wrote blend file into:', path_to_blend_file)

    @staticmethod
    def load_material_from_blend_file(path: str, blender_object: bpy.types.Object | None = None) -> bpy.types.Material:
        """
        Load a material from a blend file determined by path, to a new material slot.
        """
        path, dir_name, asset_name = MaterialService.as_blend_path(path)
        print('Loading material @: ', path, dir_name, asset_name)
        # BlendDataLibraries.load() is declared -> None in the stubs, although its own docstring there
        # says it returns the context manager this with statement relies on.
        with bpy.data.libraries.load(path) as (in_basket, out_basket):  # pyright: ignore[reportGeneralTypeIssues]
            # Weird syntax.
            setattr(out_basket, dir_name, [asset_name])

        mat = getattr(out_basket, dir_name)[0]
        mat.make_local()

        if blender_object is not None:
            typing.cast(bpy.types.Mesh, blender_object.data).materials.append(mat)
        return mat

    @staticmethod
    def _assign_material_instance(blender_object: bpy.types.Object, material: bpy.types.Material,
                                  group_name: str) -> None:
        _LOG.enter()
        _LOG.debug("blender_object, material, group_name", (blender_object, material, group_name))

        if not ObjectService.has_vertex_group(blender_object, group_name):
            return

        ObjectService.activate_blender_object(blender_object)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        typing.cast(bpy.types.Mesh, blender_object.data).materials.append(material)
        slot_number = blender_object.material_slots.find(material.name)
        _LOG.dump("slot_number", slot_number)

        # activate_blender_object() above made blender_object the active one, so context.object is set.
        typing.cast(bpy.types.Object, bpy.context.object).active_material_index = slot_number

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group=group_name)
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    @staticmethod
    def create_and_assign_material_slots(basemesh: bpy.types.Object, bodyproxy: bpy.types.Object | None = None) -> None:
        """Creates and assigns material slots for each body vertex group.

        Args:
            basemesh (bpy.types.Object): The base mesh to assign material slots to.
            bodyproxy (bpy.types.Object | None): The body proxy to assign material slots to (optional).
        """

        if not MaterialService.has_materials(basemesh):
            raise ValueError("Basemesh must have the initial material created before calling this method")

        _LOG.debug("basemesh, proxymesh", (basemesh, bodyproxy))

        # has_materials() above established that there is at least one slot, and a slot created by
        # MPFB always carries a material.
        base_material = typing.cast(bpy.types.Material, basemesh.material_slots[0].material)

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
    def find_color_adjustment(blender_object: bpy.types.Object | None) -> ColorAdjustment | None:
        """Return a dict with all color adjustments that were applied to the blender object's material slots.

        Args:
            blender_object (bpy.types.Object | None): The blender object to find color adjustments for. A
                None object is logged and None is returned.

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
    def apply_color_adjustment(blender_object: bpy.types.Object | None, color_adjustment: ColorAdjustment) -> None:
        """Apply a color adjustment to the blender object's material slots.

        Args:
            blender_object (bpy.types.Object | None): The blender object to apply the color adjustment
                to. A None object is logged and the method returns without doing anything.
            color_adjustment (ColorAdjustment): The color adjustment to apply.
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

        # find_color_adjustment() returns early when there is no mix node; this method does not
        # test, and set_socket_default_values() silently does nothing for a None, so applying an
        # adjustment to a material without one changes nothing and reports nothing.
        NodeService.set_socket_default_values(typing.cast(bpy.types.Node, mix), color_adjustment)

    @staticmethod
    def _find_principled_and_connected_color_node(node_tree: bpy.types.NodeTree) -> tuple[bpy.types.Node | None, bpy.types.Node | None]:
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
    def _makeskin_first_ink_layer_nodes(material: bpy.types.Material) -> InkLayerNodes:
        """Break the link between the principled node and the diffuseIntensity node, then add new nodes for ink layer 1."""

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        principled, diffuse_intensity = MaterialService._find_principled_and_connected_color_node(node_tree)

        if not principled:
            raise ValueError("The material did not have a principled node, maybe not a makeskin material?")

        if not diffuse_intensity:
            raise ValueError("The material did not have a diffuse intensity connected to the principled node base color, maybe not a makeskin material?")

        # Remove the link between the principled node and the diffuseIntensity node
        NodeService.remove_link(node_tree, principled, "Base Color")

        # Create a mix rgb node
        # mix_node = NodeService.create_mix_rgb_node(node_tree, "inkLayer1mix", "Ink Layer 1 Mix", xpos=-300, ypos=1000)
        mix_node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree, name="inkLayer1mix", label="Ink Layer 1 Mix")
        mix_node.location.x = -300
        mix_node.location.y = 1000
        # Socket default values; see the note at the top of the module.
        upper_color = typing.cast(bpy.types.NodeSocketColor, mix_node.inputs["UpperLayerColor"])
        upper_alpha = typing.cast(bpy.types.NodeSocketFloat, mix_node.inputs["UpperLayerAlpha"])
        upper_color.default_value = (0.0, 0.0, 0.0, 1.0)  # pyright: ignore[reportAttributeAccessIssue]
        upper_alpha.default_value = 0.0

        # Create an image texture node
        texture = NodeService.create_image_texture_node(node_tree, "inkLayer1tex", "Ink layer 1 Texture", xpos=-900, ypos=1100)

        # Create an uv map node
        uvmap = NodeService.create_node(node_tree, "ShaderNodeUVMap", name="inkLayer1uv", label="Ink Layer 1 UV", xpos=-1200, ypos=1000)

        # Add links
        NodeService.add_link(node_tree, mix_node, principled, "ResultingColor", "Base Color")
        NodeService.add_link(node_tree, diffuse_intensity, mix_node, "Color", "BackgroundColor")
        NodeService.add_link(node_tree, texture, mix_node, "Color", "LowerLayerColor")
        NodeService.add_link(node_tree, texture, mix_node, "Alpha", "LowerLayerAlpha")
        NodeService.add_link(node_tree, uvmap, texture, "UV", "Vector")

        return uvmap, texture

    @staticmethod
    def _makeskin_secondary_ink_layer_nodes(material: bpy.types.Material) -> InkLayerNodes:
        """Add an additional ink layer, stacking it over the pre-existing ones."""

        if not material:
            raise ValueError("A material must be provided")

        material_type = MaterialService.identify_material(material)

        if material_type != "makeskin":
            raise ValueError("This method only works with makeskin materials")

        _LOG.debug("material", material)

        number_of_layers = MaterialService.get_number_of_ink_layers(material)
        _LOG.debug("Number of layers", number_of_layers)

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        ybase = 300 * number_of_layers

        lnum = number_of_layers + 1

        # Create an image texture node
        texture = NodeService.create_image_texture_node(node_tree, f"inkLayer{lnum}tex", f"Ink layer {lnum} Texture", xpos=-900, ypos=ybase + 1100)

        # Create an uv map node
        uvmap = NodeService.create_node(node_tree, "ShaderNodeUVMap", name=f"inkLayer{lnum}uv", label=f"Ink Layer {lnum} UV", xpos=-1200, ypos=ybase + 1000)

        NodeService.add_link(node_tree, uvmap, texture, "UV", "Vector")

        if number_of_layers > 1:
            mix_node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree, name=f"inkLayer{number_of_layers}mix", label=f"Ink Layer {number_of_layers} Mix")
            _LOG.debug("mix_node", mix_node)
            mix_node.location.x = -300
            mix_node.location.y = ybase + 1000
        # Socket default values; see the note at the top of the module.
            upper_color = typing.cast(bpy.types.NodeSocketColor, mix_node.inputs["UpperLayerColor"])
            upper_alpha = typing.cast(bpy.types.NodeSocketFloat, mix_node.inputs["UpperLayerAlpha"])
            upper_color.default_value = (0.0, 0.0, 0.0, 1.0)  # pyright: ignore[reportAttributeAccessIssue]
            upper_alpha.default_value = 0.0

            last_mix_node = NodeService.find_node_by_name(node_tree, f"inkLayer{number_of_layers - 1}mix")
            if last_mix_node is None:
                raise ValueError(f"No such node: inkLayer{number_of_layers - 1}mix")
            last_tex_node = NodeService.find_node_by_name(node_tree, f"inkLayer{number_of_layers}tex")
            if last_tex_node is None:
                raise ValueError(f"No such node: inkLayer{number_of_layers}tex")

            NodeService.remove_link(node_tree, last_mix_node, "UpperLayerColor")
            NodeService.remove_link(node_tree, last_mix_node, "UpperLayerAlpha")

            NodeService.add_link(node_tree, mix_node, last_mix_node, "ResultingColor", "UpperLayerColor")
            NodeService.add_link(node_tree, mix_node, last_mix_node, "ResultingAlpha", "UpperLayerAlpha")

            NodeService.add_link(node_tree, last_tex_node, mix_node, "Color", "LowerLayerColor")
            NodeService.add_link(node_tree, last_tex_node, mix_node, "Alpha", "LowerLayerAlpha")

            diffuse_intensity = NodeService.find_node_by_name(node_tree, "diffuseIntensity")
            # _makeskin_first_ink_layer_nodes() raises unless a diffuse intensity node is connected
            # to the principled base colour, and this method only runs for a second layer, so layer
            # one has already been added and the node is there.
            NodeService.add_link(node_tree, typing.cast(bpy.types.Node, diffuse_intensity), mix_node, "Color", "BackgroundColor")
        else:
            # This branch runs for the second layer, so layer one's mixer exists. The two sibling
            # lookups above raise on a missing node rather than casting; this one is the odd one
            # out, which is why the cast is here and not another raise.
            mix_node = typing.cast(bpy.types.Node, NodeService.find_node_by_name(node_tree, "inkLayer1mix"))
            _LOG.debug("mix_node", mix_node)

        NodeService.add_link(node_tree, texture, mix_node, "Color", "UpperLayerColor")
        NodeService.add_link(node_tree, texture, mix_node, "Alpha", "UpperLayerAlpha")

        return uvmap, texture

    @staticmethod
    def _layered_first_ink_layer_nodes(material: bpy.types.Material) -> InkLayerNodes:
        """Add new nodes for ink layer 1, linked to color control"""

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        color_control: bpy.types.Node | None = None
        diffuse_texture: bpy.types.Node | None = None
        for node in node_tree.nodes:
            _LOG.debug("node", (node, node.name, node.type))
            if node.type == "GROUP" and node.name == "colorgroup":
                color_control = node
            if node.name == "DiffuseTexture":
                diffuse_texture = node

        if color_control is None:
            raise ValueError("Could not find a color control group in the material. Not a layered material?")

        # This is the RGBA value for the skin if no diffuse texture is used
        default_skin_color = typing.cast(bpy.types.NodeSocketColor, color_control.inputs["SkinColor"]).default_value

        # Create the first alpha layer mixer
        mix_node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree, name="inkLayer1mix", label="Ink Layer 1 Mix")
        mix_node.location.x = -500
        mix_node.location.y = 1000
        # Socket default values; see the note at the top of the module.
        background_color = typing.cast(bpy.types.NodeSocketColor, mix_node.inputs["BackgroundColor"])
        upper_color = typing.cast(bpy.types.NodeSocketColor, mix_node.inputs["UpperLayerColor"])
        upper_alpha = typing.cast(bpy.types.NodeSocketFloat, mix_node.inputs["UpperLayerAlpha"])
        background_color.default_value = default_skin_color
        upper_color.default_value = (0.0, 0.0, 0.0, 1.0)  # pyright: ignore[reportAttributeAccessIssue]
        upper_alpha.default_value = 0.0

        # Create an image texture node
        texture = NodeService.create_image_texture_node(node_tree, "inkLayer1tex", "Ink layer 1 Texture", xpos=-900, ypos=1100)

        # Create an uv map node
        uvmap = NodeService.create_node(node_tree, "ShaderNodeUVMap", name="inkLayer1uv", label="Ink Layer 1 UV", xpos=-1200, ypos=1000)

        # Add links
        NodeService.add_link(node_tree, mix_node, color_control, "ResultingColor", "InkLayerColor")
        NodeService.add_link(node_tree, mix_node, color_control, "ResultingAlpha", "InkLayerStrength")
        NodeService.add_link(node_tree, texture, mix_node, "Color", "LowerLayerColor")
        NodeService.add_link(node_tree, texture, mix_node, "Alpha", "LowerLayerAlpha")
        NodeService.add_link(node_tree, uvmap, texture, "UV", "Vector")

        # Add a link from the diffuse texture if it exists
        if diffuse_texture:
            NodeService.add_link(node_tree, diffuse_texture, mix_node, "Color", "BackgroundColor")

        return uvmap, texture

    @staticmethod
    def _layered_secondary_ink_layer_nodes(material: bpy.types.Material) -> InkLayerNodes:
        """Add an additional ink layer, stacking it over the pre-existing ones."""

        if not material:
            raise ValueError("A material must be provided")

        material_type = MaterialService.identify_material(material)

        if material_type != "layered_skin":
            raise ValueError("This method only works with layered skin materials")

        _LOG.debug("material", material)

        number_of_layers = MaterialService.get_number_of_ink_layers(material)
        _LOG.debug("Number of layers", number_of_layers)

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        color_control: bpy.types.Node | None = None
        diffuse_texture: bpy.types.Node | None = None
        for node in node_tree.nodes:
            _LOG.debug("node", (node, node.name, node.type))
            if node.type == "GROUP" and node.name == "colorgroup":
                color_control = node
            if node.name == "DiffuseTexture":
                diffuse_texture = node

        if color_control is None:
            raise ValueError("Could not find a color control group in the material. Not a layered material?")

        ybase = 300 * number_of_layers

        lnum = number_of_layers + 1

        # Create an image texture node
        texture = NodeService.create_image_texture_node(node_tree, f"inkLayer{lnum}tex", f"Ink layer {lnum} Texture", xpos=-900, ypos=ybase + 1100)

        # Create an uv map node
        uvmap = NodeService.create_node(node_tree, "ShaderNodeUVMap", name=f"inkLayer{lnum}uv", label=f"Ink Layer {lnum} UV", xpos=-1200, ypos=ybase + 1000)

        NodeService.add_link(node_tree, uvmap, texture, "UV", "Vector")

        if number_of_layers > 1:
            mix_node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree, name=f"inkLayer{number_of_layers}mix", label=f"Ink Layer {number_of_layers} Mix")
            _LOG.debug("mix_node", mix_node)
            mix_node.location.x = -300
            mix_node.location.y = ybase + 1000
        # Socket default values; see the note at the top of the module.
            upper_color = typing.cast(bpy.types.NodeSocketColor, mix_node.inputs["UpperLayerColor"])
            upper_alpha = typing.cast(bpy.types.NodeSocketFloat, mix_node.inputs["UpperLayerAlpha"])
            upper_color.default_value = (0.0, 0.0, 0.0, 1.0)  # pyright: ignore[reportAttributeAccessIssue]
            upper_alpha.default_value = 0.0

            last_mix_node = NodeService.find_node_by_name(node_tree, f"inkLayer{number_of_layers - 1}mix")
            if last_mix_node is None:
                raise ValueError(f"No such node: inkLayer{number_of_layers - 1}mix")
            last_tex_node = NodeService.find_node_by_name(node_tree, f"inkLayer{number_of_layers}tex")
            if last_tex_node is None:
                raise ValueError(f"No such node: inkLayer{number_of_layers}tex")

            NodeService.remove_link(node_tree, last_mix_node, "UpperLayerColor")
            NodeService.remove_link(node_tree, last_mix_node, "UpperLayerAlpha")

            NodeService.add_link(node_tree, mix_node, last_mix_node, "ResultingColor", "UpperLayerColor")
            NodeService.add_link(node_tree, mix_node, last_mix_node, "ResultingAlpha", "UpperLayerAlpha")

            NodeService.add_link(node_tree, last_tex_node, mix_node, "Color", "LowerLayerColor")
            NodeService.add_link(node_tree, last_tex_node, mix_node, "Alpha", "LowerLayerAlpha")

        else:
            # This branch runs for the second layer, so layer one's mixer exists. The two sibling
            # lookups above raise on a missing node rather than casting; this one is the odd one
            # out, which is why the cast is here and not another raise.
            mix_node = typing.cast(bpy.types.Node, NodeService.find_node_by_name(node_tree, "inkLayer1mix"))
            _LOG.debug("mix_node", mix_node)

        NodeService.add_link(node_tree, texture, mix_node, "Color", "UpperLayerColor")
        NodeService.add_link(node_tree, texture, mix_node, "Alpha", "UpperLayerAlpha")

        # Add a link from the diffuse texture if it exists
        if diffuse_texture:
            NodeService.add_link(node_tree, diffuse_texture, mix_node, "Color", "BackgroundColor")

        return uvmap, texture

    @staticmethod
    def add_focus_nodes(material: bpy.types.Material, uv_map_name: str | None = None) -> tuple[bpy.types.Node, bpy.types.Node, int]:
        """Add a node setup for a focus."""

        if not material:
            raise ValueError("A material must be provided")

        material_type = MaterialService.identify_material(material)

        if material_type not in ["makeskin", "layered_skin"]:
            raise ValueError("The material must be makeskin or layered skin")

        _LOG.debug("material", material)

        number_of_layers = MaterialService.get_number_of_ink_layers(material)
        _LOG.debug("Number of layers", number_of_layers)

        # The four branches below are exhaustive for the two material types the guard above allows, but
        # the checker cannot see that, so the pair is bound once up front.
        uvmap_node: bpy.types.Node
        texture_node: bpy.types.Node

        if material_type == "makeskin" and number_of_layers == 0:
            uvmap_node, texture_node = MaterialService._makeskin_first_ink_layer_nodes(material)

        if material_type == "makeskin" and number_of_layers > 0:
            _LOG.debug("Adding a secondary ink layer")
            uvmap_node, texture_node = MaterialService._makeskin_secondary_ink_layer_nodes(material)

        if material_type == "layered_skin" and number_of_layers == 0:
            uvmap_node, texture_node = MaterialService._layered_first_ink_layer_nodes(material)

        if material_type == "layered_skin" and number_of_layers > 0:
            _LOG.debug("Adding a secondary ink layer")
            uvmap_node, texture_node = MaterialService._layered_secondary_ink_layer_nodes(material)

        if uv_map_name is not None and uvmap_node is not None:
            typing.cast(bpy.types.ShaderNodeUVMap, uvmap_node).uv_map = uv_map_name

        # The four branches are exhaustive for the two material types the guard at the top of the method
        # allows, so neither name can be unbound here, but the checker cannot follow that.
        return typing.cast(bpy.types.Node, uvmap_node), typing.cast(bpy.types.Node, texture_node), number_of_layers + 1

    @staticmethod
    def get_number_of_ink_layers(material: bpy.types.Material | None) -> int:
        """Return information about how many ink layers are present in the material."""

        if not material:
            raise ValueError("A material must be provided")

        if MaterialService.identify_material(material) not in ["makeskin", "layered_skin"]:
            raise ValueError("The material must be makeskin or layered_skin")

        max_layer_number = 0

        for node in typing.cast(bpy.types.NodeTree, material.node_tree).nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage) and node.name.startswith("inkLayer"):
                _LOG.debug("Found a node named", node.name)
                layer_number = int(node.name.split("inkLayer")[1].split("tex")[0])
                if layer_number > max_layer_number:
                    max_layer_number = layer_number

        return max_layer_number

    @staticmethod
    def get_ink_layer_info(mesh_object: bpy.types.Object, ink_layer: int = 1) -> tuple[str, str]:
        """Return information about UV map and texture name for a specific ink layer."""

        material = MaterialService.get_material(mesh_object)

        if not material:
            raise ValueError("A material must be provided")

        if MaterialService.identify_material(material) not in ["makeskin", "layered_skin"]:
            raise ValueError("The material must be makeskin or layered skin material")

        tex_name = f"inkLayer{ink_layer}tex"
        uv_name = f"inkLayer{ink_layer}uv"

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        tex_node = NodeService.find_node_by_name(node_tree, tex_name)
        if tex_node is None:
            raise ValueError(f"The material does not have a node named {tex_name}")

        uv_node = NodeService.find_node_by_name(node_tree, uv_name)
        if uv_node is None:
            raise ValueError(f"The material does not have a node named {uv_name}")

        deduced_uv_name = typing.cast(bpy.types.ShaderNodeUVMap, uv_node).uv_map
        if "UV" in deduced_uv_name:
            deduced_uv_name = ""  # This is assumed to be the basemesh standard UV map

        decuced_image_texture_name = typing.cast(bpy.types.Image, typing.cast(bpy.types.ShaderNodeTexImage, tex_node).image).name

        return deduced_uv_name, decuced_image_texture_name

    @staticmethod
    def load_ink_layer(mesh_object: bpy.types.Object, ink_layer_json_path: str) -> tuple[bpy.types.Node, bpy.types.Node, int]:
        """Load an ink layer from a JSON file. This will also add a new UV map to the mesh object if needed."""

        _LOG.debug("Loading ink layer from", ink_layer_json_path)

        with open(ink_layer_json_path, 'r', encoding="utf-8") as json_file:
            ink_layer_data = json.load(json_file)

        _LOG.debug("ink_layer_data", ink_layer_data)

        if "name" not in ink_layer_data or not ink_layer_data["name"]:
            ink_layer_name = os.path.basename(ink_layer_json_path)
            ink_layer_name = ink_layer_name.replace(".json", "").replace("_", " ")
        else:
            ink_layer_name = ink_layer_data["name"]

        focus_name = ink_layer_data["focus"]
        image_name = ink_layer_data["image_name"]

        if not image_name:
            raise ValueError("The ink layer definition must refer to an image file")

        ink_dirname = os.path.dirname(ink_layer_json_path)
        image_path = os.path.join(ink_dirname, image_name)

        if not os.path.isfile(image_path):
            raise ValueError(f"The image file '{image_name}' does not exist at '{ink_dirname}'")

        uv_map = typing.cast(bpy.types.Mesh, mesh_object.data).uv_layers[0]
        uv_map_name = uv_map.name

        material = MaterialService.get_material(mesh_object)

        if focus_name:
            ink_layer_number = MaterialService.get_number_of_ink_layers(material) + 1
            uv_map_name = f"inkLayer{ink_layer_number}"
            focus_name_full = str(focus_name).replace(" ", "_") + ".json.gz"
            focus_filename = os.path.join(LocationService.get_user_data("uv_layers"), focus_name_full)
            if not os.path.exists(focus_filename):
                focus_filename = os.path.join(LocationService.get_mpfb_data("uv_layers"), focus_name_full)
                if not os.path.exists(focus_filename):
                    raise ValueError(f"The focus file '{focus_name_full}' does not exist")

            with gzip.open(focus_filename, 'rt') as json_file:
                uv_map_dict = json.load(json_file)

            MeshService.add_uv_map_from_dict(mesh_object, uv_map_name, uv_map_dict)

        # add_focus_nodes() raises on a None material, so the narrowing is only moved, not asserted.
        uvmap_node, texture_node, ink_layer_id = MaterialService.add_focus_nodes(
            typing.cast(bpy.types.Material, material), uv_map_name=uv_map_name)
        typing.cast(bpy.types.ShaderNodeTexImage, texture_node).image = bpy.data.images.load(image_path)

        return uvmap_node, texture_node, ink_layer_id

    @staticmethod
    def remove_all_makeup(material: bpy.types.Material | None, basemesh: bpy.types.Object | None = None) -> None:
        """Remove all ink layers from a material, and optionally remove ink layer UVs from the corresponding basemesh"""
        _LOG.debug("Removing all makeup")
        if not material:
            _LOG.debug("No material provided")
            return

        material_type = MaterialService.identify_material(material)
        _LOG.debug("Material type:", material_type)

        if material_type not in ["makeskin", "layered_skin"]:
            _LOG.warn("Not a compatible material type")
            return

        inks = MaterialService.get_number_of_ink_layers(material)

        if inks < 1:
            _LOG.warn("No ink layers found")
            return

        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        for node in node_tree.nodes:
            if node.name.startswith("inkLayer"):
                _LOG.debug("Removing node", node.name)
                node_tree.nodes.remove(node)

        if material_type == "makeskin":
            principled = NodeService.find_first_node_by_type_name(node_tree, "ShaderNodeBsdfPrincipled")
            _LOG.debug("Principled node:", principled)
            diffuse_intensity = NodeService.find_node_by_name(node_tree, "diffuseIntensity")
            _LOG.debug("Connected color node:", diffuse_intensity)
            if principled and diffuse_intensity:
                NodeService.add_link(node_tree, diffuse_intensity, principled, "Color", "Base Color")
            else:
                diffuse_tex = NodeService.find_node_by_name(node_tree, "diffuseTexture")
                _LOG.debug("Diffuse texture", diffuse_tex)
                if diffuse_tex:                    
                    # The else branch is reached when principled is empty as well as when
                    # diffuse_intensity is, and it re-uses principled without re-testing it. The ink
                    # layer nodes have already been deleted by this point, so a makeskin material
                    # with a diffuse texture and no principled node loses its base colour link and
                    # raises a TypeError out of links.new(). Re-testing principled, or splitting the
                    # condition, is the fix; it is a logic change rather than an annotation, so the
                    # cast only records that the code assumes a principled node here.
                    NodeService.add_link(node_tree, diffuse_tex, typing.cast(bpy.types.Node, principled), "Color", "Base Color")

        if basemesh:
            basemesh_data = typing.cast(bpy.types.Mesh, basemesh.data)
            for uv_layer in basemesh_data.uv_layers:
                _LOG.debug("Uv layer:", uv_layer.name)
                if uv_layer.name.startswith("inkLayer"):
                    basemesh_data.uv_layers.remove(uv_layer)

    @staticmethod
    def get_skin_diffuse_color() -> list[float]:
        """Return a static color for the skin material, for example to be used in the viewport."""
        return [0.721, 0.568, 0.431, 1.0]

    @staticmethod
    def get_generic_bodypart_diffuse_color() -> list[float]:
        """Return a static color for a bodypart material, for example to be used in the viewport."""
        return [0.194, 0.030, 0.014, 1.0]

    @staticmethod
    def get_generic_clothes_diffuse_color() -> list[float]:
        """Return a static color for a clothes material, for example to be used in the viewport."""
        return [0.6, 0.6, 0.6, 1.0]

    @staticmethod
    def get_eye_diffuse_color() -> list[float]:
        """Return a static color for the eye material, for example to be used in the viewport."""
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_teeth_diffuse_color() -> list[float]:
        """Return a static color for the teeth material, for example to be used in the viewport."""
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_diffuse_colors() -> dict[str, list[float]]:
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
