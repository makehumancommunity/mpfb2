# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for setting up scene for adding hair
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
from ..haireditorpanel import HAIR_PROPERTIES

import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.setup_hair_operator")


class MPFB_OT_SetupHair_Operator(bpy.types.Operator):
    """Adds empty hair to mesh and actualizes UI"""
    bl_idname = "mpfb.setup_hair_operator"
    bl_label = "Setup hair"
    bl_options = {'REGISTER'}

    def execute(self, context):

        scene = context.scene

        self.report({'INFO'}, ("Setting up hair interface"))


        # Get material
        obj = context.object
        if (not obj or not obj.name == 'Human'):
            self.report({'ERROR'}, "Object Human must be active")
            return {'CANCELLED'}

        # Add empty hair or the hair asset wont behave correctly
        bpy.ops.object.curves_empty_hair_add()

        # For eevee set curves render as strip
        if scene.render.engine == 'BLENDER_EEVEE_NEXT':
            scene.render.hair_type = 'STRIP'


        # Reselect Human
        human_obj = bpy.data.objects.get("Human")
        if human_obj:
            bpy.ops.object.select_all(action='DESELECT')
            human_obj.select_set(True)
            context.view_layer.objects.active = human_obj
        else:
            self.report({'WARNING'}, "Human object not found in bpy.data.objects")

        propdef = {
                    "type": "boolean",
                    "name": "hair_setup",
                    "label": "Hair has been set up",
                    "description": "Mesh has empty hair applied",
                    "default": False
                    }

        HAIR_PROPERTIES.set_value_dynamic("hair_setup", True, propdef, human_obj)

        testdef = {
                    "type": "boolean",
                    "name": "getter_setter",
                    "label": "Getter and setter test",
                    "description": "Getter and setter test",
                    "default": False
                    }

        HAIR_PROPERTIES.set_value_dynamic("getter_setter", True, testdef, human_obj)

        # Update UI
        #=======================================================================
        # if not hasattr(bpy.types.Scene, "hair_setup"):
        #     bpy.types.Scene.hair_setup = bpy.props.BoolProperty(
        #         name="hair_setup",
        #         description="Mesh has empty hair applied",
        #         default=False
        #     )
        # scene.hair_setup = True
        #=======================================================================

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_SetupHair_Operator)