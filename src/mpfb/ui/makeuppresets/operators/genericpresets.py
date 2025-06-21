"""Functionality shared across all makeup presets operators"""

from ....services import LocationService
from ....services import LogService
from ....services import ObjectService
from ....services import MaterialService
from ..makeuppresetspanel import MAKEUP_PRESETS_PROPERTIES
import bpy, os, json

_LOG = LogService.get_logger("makeuppresets.genericpresets")


class generic_makeup_presets(bpy.types.Operator):
    """This is the base class for all makeup presets operators"""

    def write_preset(self, context, file_name):
        """
        Writes the current makeup preset data to a specified JSON file.

        This function extracts ink layer information from the current object's material and saves it as a JSON file.
        Each ink layer's information is inferred from the image name associated with the layer.

        Parameters:
        context (bpy.types.Context): The Blender context containing the object whose makeup preset is to be saved.
        file_name (str): The path to the file where the preset data will be written.

        Returns:
        None
        """
        basemesh = context.object
        material = MaterialService.get_material(basemesh)
        number_of_layers = MaterialService.get_number_of_ink_layers(material)

        layers = []
        for layer in range(number_of_layers):
            ink_info = MaterialService.get_ink_layer_info(basemesh, ink_layer=layer + 1)
            image_name = ink_info[1]
            json_name = os.path.splitext(image_name)[0] + ".json"  # Possibly we should have a better way than to infer from image name
            layers.append(json_name)

        with open(file_name, 'w', encoding="utf-8") as json_file:
            json.dump(layers, json_file, indent=4)

    def check_valid(self, context, check_for_ink_layers=True):
        """
        Validates the current context and object for suitability in makeup preset operations.

        This function checks if the current object in the Blender context is a valid basemesh with the appropriate material.
        It also verifies the presence of ink layers if required.

        Parameters:
        context (bpy.types.Context): The Blender context containing the object to be validated.
        check_for_ink_layers (bool): A flag indicating whether to check for the presence of ink layers in the material.

        Returns:
        str or None: Returns 'FINISHED' if validation fails with an error message reported, or None if validation is successful.
        """
        if context.object is None:
            self.report({'ERROR'}, "Must have a selected object")
            return {'FINISHED'}

        basemesh = None
        if ObjectService.object_is_basemesh(context.object):
            basemesh = context.object

        if basemesh is None:
            self.report({'ERROR'}, "Must have basemesh selected")
            return {'FINISHED'}

        material = MaterialService.get_material(basemesh)
        if material is None:
            self.report({'ERROR'}, "Basemesh must have a material")
            return {'FINISHED'}

        material_type = MaterialService.identify_material(material)
        if material_type not in ["makeskin", "layered_skin"]:
            self.report({'ERROR'}, "Basemesh material must be MakeSkin or Layered Skin")
            return {'FINISHED'}

        if check_for_ink_layers:
            number_of_layers = MaterialService.get_number_of_ink_layers(material)
            if number_of_layers == 0:
                self.report({'ERROR'}, "No ink layers found in the material")
                return {'FINISHED'}

            inkpath = LocationService.get_user_data("ink_layers")

            for layer in range(number_of_layers):
                ink_info = MaterialService.get_ink_layer_info(basemesh, ink_layer=layer + 1)
                image_name = ink_info[1]
                json_name = os.path.splitext(image_name)[0] + ".json"  # Possibly we should have a better way than to infer from image name
                json_path = os.path.join(inkpath, json_name)
                _LOG.debug("Ink layer", (layer + 1, ink_info, image_name, json_path))
                if not os.path.isfile(json_path):
                    self.report({'ERROR'}, f"Ink layer file '{json_name}' not found at '{inkpath}'. Was the layer loaded/created outside the apply assets panel?")
                    return {'FINISHED'}

        return None

    def get_fn(self, context, from_text_box=False):
        """
        Constructs the file path for a makeup preset JSON file based on the current context.

        This function retrieves the name of the makeup preset from the context, either from a text box or from available presets,
        and constructs the full file path where the preset JSON file is stored.

        Parameters:
        context (bpy.types.Context): The Blender context containing the scene and properties.
        from_text_box (bool): A flag indicating whether to retrieve the preset name from a text box or from available presets.

        Returns:
        str or None: The full file path to the makeup preset JSON file, or None if the name is not valid.
        """
        if from_text_box:
            name = MAKEUP_PRESETS_PROPERTIES.get_value("name", entity_reference=context.scene)
        else:
            name = MAKEUP_PRESETS_PROPERTIES.get_value("available_presets", entity_reference=context.scene)

        if name is not None:
            name = str(name).strip()

        if not name:
            return None

        confdir = LocationService.get_user_config()
        file_name = os.path.join(confdir, "makeup." + name + ".json")

        return file_name

    @classmethod
    def is_bm(cls, context):
        obj = context.active_object
        if not obj:
            return False

        if ObjectService.object_is_basemesh(obj):
            return True

        return False
