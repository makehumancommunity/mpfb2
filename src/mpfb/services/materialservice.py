import os, bpy

from .logservice import LogService
from .objectservice import ObjectService
from .nodeservice import NodeService
_LOG = LogService.get_logger("services.materialservice")

class MaterialService():

    def __init__(self):
        raise RuntimeError("You should not instance MaterialService. Use its static methods instead.")

    @staticmethod
    def delete_all_materials(blender_object, also_destroy_groups=False):
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

        for node in nodes:
            node_info = NodeService.get_node_info(node)
            if node_info and node_info["type"] == "ShaderNodeGroup" and node_info["values"]:
                # Material is potentially a procedural type material
                _LOG.debug("node_info", node_info)
                if "Pore detail" in node_info["values"]:
                    return "enhanced_skin"
                if "IrisSection4Color" in node_info["values"]:
                    return "procedural_eyes"

        # Since we're not enhanced skin nor procedural eyes, next guess is makeskin
        # This might give a false positive if someone added a material with a principled node
        # to a MH object
        if NodeService.find_node_by_name(material.node_tree, "Principled BSDF"):
            return "makeskin"

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

        if material_type == "makeskin":
            MaterialService._set_normalmap_in_nodetree(material.node_tree, filename)
            return

        raise ValueError('Cannot set normalmap in material of type ' + material_type)

    @staticmethod
    def assign_new_or_existing_material(name, blender_object):
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
        if not blender_object is None:
            blender_object.data.materials.append(material)
        return material

    @staticmethod
    def as_blend_path(path):
        """
        Converts a relative path to an asset in a blender library to an absolute path to the blend,
        the location of the asset in the blend and the name of the asset, ie return:

        (path, location, name)
        """
        blendPath, dirName, assetName = (part.strip() for part in path.rsplit('/', 2))
        return blendPath, dirName, assetName

    @staticmethod
    def save_material_in_blend_file(blender_object, path_to_blend_file, material_number=None, fake_user=False):
        """
        Save the material(s) on the active object to a blend file. If material_number is None, save all
        the object's materials. Otherwise, save material slot with that number. This writes into the file
        but will not overwrite it, although it might overwrite something already in it.
        """
        if not material_number is None:
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
        path, dirName, assetName = MaterialService.as_blend_path(path)
        print('Loading material @: ', path, dirName, assetName)
        with bpy.data.libraries.load(path) as (inBasket, outBasket):
            # Weird syntax.
            setattr(outBasket, dirName, [assetName])

        mat = getattr(outBasket, dirName)[0]
        mat.make_local()

        if not blender_object is None:
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
        if not MaterialService.has_materials(basemesh):
            raise ValueError("Basemesh must have the initial material created before calling this method")

        _LOG.debug("basemesh, proxymesh", (basemesh, bodyproxy))

        base_material = basemesh.material_slots[0].material

        prefix = str(basemesh.name).split(".")[0]

        _LOG.debug("prefix", prefix)

        if not bodyproxy is None:
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

        if not info or not "values" in info:
            raise ValueError('Could not find values:' + str(info))

        return info["values"]

    @staticmethod
    def apply_color_adjustment(blender_object, color_adjustment):
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
    def get_skin_diffuse_color():
        return [0.721, 0.568, 0.431, 1.0]

    @staticmethod
    def get_generic_bodypart_diffuse_color():
        return [0.194, 0.030, 0.014, 1.0]

    @staticmethod
    def get_generic_clothes_diffuse_color():
        return [0.6, 0.6, 0.6, 1.0]

    @staticmethod
    def get_eye_diffuse_color():
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_teeth_diffuse_color():
        return [0.95, 0.95, 0.95, 1.0]

    @staticmethod
    def get_diffuse_colors():
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
