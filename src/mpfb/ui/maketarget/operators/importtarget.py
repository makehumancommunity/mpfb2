"""Operator for importing MHMAT target."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import TargetService
from ...maketarget import MakeTargetObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("maketarget.importtarget")

class MPFB_OT_ImportTargetOperator(bpy.types.Operator, ImportHelper):
    """Import target"""
    bl_idname = "mpfb.import_maketarget_target"
    bl_label = "Import target"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.target', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        blender_object = context.active_object
        if blender_object is None:
            _LOG.trace("Blender object is None")
            return False

        object_type = ObjectService.get_object_type(blender_object)

        if object_type != "Basemesh":
            _LOG.trace("Wrong object type", object_type)
            return False

        if not context.active_object.data.shape_keys:
            _LOG.trace("No shape keys", object_type)

        return not TargetService.has_target(blender_object, "PrimaryTarget")

    def invoke(self, context, event):
        blender_object = context.active_object
        name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        self.filepath = bpy.path.clean_name(name, replace="-") + ".target"
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

ClassManager.add_class(MPFB_OT_ImportTargetOperator)
