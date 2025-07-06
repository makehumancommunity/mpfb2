# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for setting up scene for adding hair
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
from ..hairproperties import HAIR_PROPERTIES

import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.setup_hair_operator")


class MPFB_OT_SetupHair_Operator(bpy.types.Operator):
    """Adds empty hair to mesh and actualizes UI"""
    bl_idname = "mpfb.setup_hair_operator"
    bl_label = "Setup hair"
    bl_options = {'REGISTER'}

    def execute(self, context):

        if context.object is None:
            self.report({'ERROR'}, "Must have an active object")
            return {'FINISHED'}

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)

        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'FINISHED'}

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        scene = context.scene

        # Add empty hair or the hair asset wont behave correctly
        bpy.ops.object.curves_empty_hair_add()

        # For eevee set curves render as strip
        if scene.render.engine == 'BLENDER_EEVEE_NEXT':
            scene.render.hair_type = 'STRIP'

        hair_prop = {
            "name": "hair_setup",
            "type": "boolean",
            "description": "Hair has been initialized for this object",
            "label": "Setup hair",
            "default": False
            }

        HAIR_PROPERTIES.set_value_dynamic("hair_setup", True, hair_prop, basemesh)
        self.report({'INFO'}, ("Initialized hair for this basemesh"))

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_SetupHair_Operator)