"""Functionality for saving new makeup presets"""

from ....services import LogService
from .genericpresets import generic_makeup_presets
from .... import ClassManager
import os

_LOG = LogService.get_logger("makeuppresets.savenewpresets")


class MPFB_OT_Save_New_Makeup_Presets_Operator(generic_makeup_presets):
    """This will save new makeup preset"""
    bl_idname = "mpfb.save_new_makeup_presets"
    bl_label = "Save new presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """
        Executes the operator to save a new makeup preset from the current object in the Blender context.

        Parameters:
        context (bpy.types.Context): The Blender context in which the operator is executed.

        Returns:
        set: A set containing 'FINISHED' to indicate the operation completed successfully, or an error message if the operation failed.
        """
        _LOG.enter()

        result = self.check_valid(context)
        if result is not None:
            return result

        file_name = self.get_fn(context, from_text_box=True)
        if file_name == "" or file_name is None:
            self.report({'ERROR'}, "Presets name must be given")
            return {'FINISHED'}

        if os.path.exists(file_name):
            self.report({'ERROR'}, "Presets with that name already exist")
            return {'FINISHED'}

        self.write_preset(context, file_name)

        self.report({'INFO'}, f"Preset was saved to {file_name}")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return generic_makeup_presets.is_bm(context)


ClassManager.add_class(MPFB_OT_Save_New_Makeup_Presets_Operator)
