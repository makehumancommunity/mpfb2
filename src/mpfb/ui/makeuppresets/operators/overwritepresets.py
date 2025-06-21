"""Functionality for overwriting an existing makeup preset"""

from ....services import LogService
from .genericpresets import generic_makeup_presets
from .... import ClassManager

_LOG = LogService.get_logger("makeuppresets.overwritepresets")


class MPFB_OT_Overwrite_Makeup_Presets_Operator(generic_makeup_presets):
    """This will overwrite the selected makeup presets, using values from the selected object"""
    bl_idname = "mpfb.overwrite_makeup_presets"
    bl_label = "Overwrite presets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """
        Executes the operator to overwrite an existing makeup preset with data from the current object in the Blender context.

        Parameters:
        context (bpy.types.Context): The Blender context in which the operator is executed.

        Returns:
        set: A set containing 'FINISHED' to indicate the operation completed successfully, or an error message if the operation failed.
        """
        _LOG.enter()

        result = self.check_valid(context)
        if result is not None:
            return result

        file_name = self.get_fn(context)
        if file_name == "" or file_name is None:
            self.report({'ERROR'}, "Presets must be chosen from the list")
            return {'FINISHED'}

        self.write_preset(context, file_name)

        self.report({'INFO'}, f"Preset was saved to {file_name}")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return generic_makeup_presets.is_bm(context)


ClassManager.add_class(MPFB_OT_Overwrite_Makeup_Presets_Operator)
