# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Unused
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.apply_material_operator")


class MPFB_OT_ApplyMaterial_Operator(bpy.types.Operator):
    """Adds material to selected hair asset"""
    bl_idname = "mpfb.apply_material_operator"
    bl_label = "Apply material"
    bl_options = {'REGISTER'}


    #material_complexity: bpy.props.StringProperty()

    def execute(self, context):

        scene = context.scene

        self.report({'INFO'}, ("Applying hair material..."))


        # Get Human mesh
        obj = context.object
        if (not obj or not obj.name == 'Human'):
            self.report({'ERROR'}, "Object Human must be active")
            return {'CANCELLED'}



        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_ApplyMaterial_Operator)