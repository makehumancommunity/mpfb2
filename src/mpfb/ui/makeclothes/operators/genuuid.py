"""Operator for generating an UUID."""

import bpy, os, shutil, uuid
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.meshcrossref import MeshCrossRef
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

        basemesh = None
        clothes = None
        for obj in context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not clothes:
            self.report({'ERROR'}, "No clothes selected")
            return {'CANCELED'}

        from mpfb.ui.makeclothes import MakeClothesObjectProperties
        MakeClothesObjectProperties.set_value("uuid", str(uuid.uuid4()), entity_reference=clothes)

        self.report({'INFO'}, "A new UUID was set in the text box")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_GenerateUUIDOperator)
