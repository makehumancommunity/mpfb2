
import os, bpy

from .logservice import LogService
_LOG = LogService.get_logger("services.materialservice")


class MaterialService():

    def __init__(self):
        raise RuntimeError("You should not instance MaterialService. Use its static methods instead.")

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
        return [0.9, 0.9, 0.9, 1.0]

    @staticmethod
    def get_teeth_diffuse_color():
        return [0.9, 0.9, 0.9, 1.0]

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
        colors["Bodypart"] = MaterialService.get_generic_bodypart_diffuse_color()
        return colors
