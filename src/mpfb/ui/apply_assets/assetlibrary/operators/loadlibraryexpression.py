"""Operator for loading an expression from the asset library."""

import bpy
from bpy.props import StringProperty, FloatProperty
from .....services import LogService
from .....services import ObjectService
from .....services.faceservice import FaceService
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.loadlibraryexpression")


class MPFB_OT_Load_Library_Expression_Operator(MpfbOperator):
    """Apply an expression to the active basemesh, appending it to the persistent stack."""

    bl_idname = "mpfb.load_library_expression"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")
    object_type: StringProperty(name="object_type", description="type of the object", default="Other")
    weight: FloatProperty(name="weight", description="Row weight for this expression",
                          default=1.0, min=0.0, max=1.0)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        if not FaceService.is_faceunits01_installed():
            self.report({'ERROR'}, "The faceunits01 asset pack is not installed")
            return {'CANCELLED'}

        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(obj, "Basemesh")
        if basemesh is None:
            self.report({'ERROR'}, "No basemesh found")
            return {'CANCELLED'}

        try:
            FaceService.apply_expression_file(basemesh, self.filepath, weight=float(self.weight), append=True)
        except (IOError, ValueError) as exc:
            _LOG.error("Failed to apply expression", exc)
            self.report({'ERROR'}, f"Failed to apply expression: {exc}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Expression applied: " + str(self.filepath))
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Library_Expression_Operator)
