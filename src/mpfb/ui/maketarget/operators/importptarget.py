"""Operator for importing MHMAT target."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.ui.maketarget import MakeTargetObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.importptarget")

class MPFB_OT_ImportPtargetOperator(bpy.types.Operator, ImportHelper):
    """Import proxy-specific target"""
    bl_idname = "mpfb.import_maketarget_ptarget"
    bl_label = "Import proxy-specific target"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.ptarget', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            return False

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        if not object_type or object_type == "Skeleton" or object_type == "Basemesh":
            return False

        return not context.active_object.data.shape_keys

    def invoke(self, context, event):
        blender_object = context.active_object
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".ptarget"
        return super().invoke(context, event)

    def execute(self, context):

        blender_object = context.active_object
        target_string = Path(self.filepath).read_text()

        TargetService.target_string_to_shape_key(target_string, "PrimaryTarget", blender_object)

        # This might look strange, but it is to ensure the name attribute of the object
        # is not still null if left at its default
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        MakeTargetObjectProperties.set_value("name", name, entity_reference=blender_object)

        self.report({'INFO'}, "Target was imported as shape key")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ImportPtargetOperator)
