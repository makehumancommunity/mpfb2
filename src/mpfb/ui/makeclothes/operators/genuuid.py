"""Operator for generating an UUID."""

import bpy, os, shutil, uuid
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from ....services import LogService
from ....services import LocationService
from ....services import ObjectService
from mpfb.entities.meshcrossref import MeshCrossRef
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.genuuid")

class MPFB_OT_GenerateUUIDOperator(bpy.types.Operator):
    """Generate a new UUID for the asset"""
    bl_idname = "mpfb.genuuid"
    bl_label = "Generate UUID"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        clothes = None
        for obj in context.selected_objects:
            if not ObjectService.object_is_basemesh(obj):
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not clothes:
            self.report({'ERROR'}, "No clothes selected")
            return {'CANCELED'}

        GeneralObjectProperties.set_value("uuid", str(uuid.uuid4()), entity_reference=clothes)

        self.report({'INFO'}, "A new UUID was set in the text box")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_GenerateUUIDOperator)
