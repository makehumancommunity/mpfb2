"""Operator for importing MHCLO clothes."""

import bpy
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.mhclo import Mhclo
from mpfb import ClassManager

_LOG = LogService.get_logger("loadclothes.loadclothes")

class MPFB_OT_Load_Clothes_Operator(bpy.types.Operator, ImportHelper):
    """Load clothes from MHCLO file."""
    bl_idname = "mpfb.load_clothes"
    bl_label = "Load clothes"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default='*.mhclo', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return ObjectService.object_is_basemesh(context.active_object)

    def invoke(self, context, event):
        blender_object = context.active_object
        #name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
        #self.filepath = bpy.path.clean_name(name, replace="-") + ".target"
        return super().invoke(context, event)

    def execute(self, context):

        blender_object = context.active_object
        mhclo = Mhclo()
        mhclo.load(self.filepath)
        mhclo.load_mesh(context)
        mhclo.update(blender_object)
        mhclo.set_scalings(context, blender_object)

        self.report({'INFO'}, "Clothes were loaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Clothes_Operator)
