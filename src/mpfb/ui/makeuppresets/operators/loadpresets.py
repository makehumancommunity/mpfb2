"""Functionality for loading makeup presets"""

from ....services import AssetService
from ....services import LogService
from ....services import MaterialService
from .genericpresets import generic_makeup_presets
from .... import ClassManager
import json

_LOG = LogService.get_logger("makeuppresets.loadpresets")


class MPFB_OT_Load_Makeup_Presets_Operator(generic_makeup_presets):
    """This will load the selected makeup presets, overwriting any existing makeup on the body"""
    bl_idname = "mpfb.load_makeup_presets"
    bl_label = "Load presets"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Executes the operator to load makeup presets onto the current object in the Blender context.

        Parameters:
        context (bpy.types.Context): The Blender context in which the operator is executed.

        Returns:
        set: A set containing 'FINISHED' to indicate the operation completed successfully, or an error message if the operation failed.
        """
        _LOG.enter()

        result = self.check_valid(context, check_for_ink_layers=False)
        if result is not None:
            return result

        file_name = self.get_fn(context)
        if file_name == "" or file_name is None:
            self.report({'ERROR'}, "Presets must be chosen from the list")
            return {'FINISHED'}

        with open(file_name, 'r', encoding="utf-8") as json_file:
            ink_layers = json.load(json_file)

        basemesh = context.object
        material = MaterialService.get_material(basemesh)

        MaterialService.remove_all_makeup(material, basemesh)

        for ink_layer in ink_layers:
            ink_path = AssetService.find_asset_absolute_path(ink_layer, asset_subdir="ink_layers")
            MaterialService.load_ink_layer(basemesh, ink_path)

        self.report({'INFO'}, "Makeup preset was loaded successfully")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Makeup_Presets_Operator)
