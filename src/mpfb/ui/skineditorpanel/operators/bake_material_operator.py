# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Merges material textures together using Blener bake system and Compositor
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.skineditorservices import SkinEditorService
from ....services.locationservice import LocationService
from ....  import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.bake_material_operator")


class MPFB_OT_BakeMaterial_Operator(bpy.types.Operator):
    """Bake material and save its textures"""

    bl_idname = "mpfb.bake_material_operator"
    bl_label = "Bake material"
    bl_options = {'REGISTER'}
    texture_resolution: bpy.props.StringProperty()
    baking_type: bpy.props.StringProperty()


    def execute(self, context):
        scene = context.scene
        self.report({'INFO'}, ("Baking material, it might take a while..."))

        # Swich viewport shading to solid for better performance
        original_shading = context.space_data.shading.type
        context.space_data.shading.type = 'SOLID'

        # Swich to cycles render engine and tweak parameters
        original_engine = scene.render.engine
        original_osa = scene.cycles.shading_system
        original_samples = scene.cycles.samples
        scene.render.engine = 'CYCLES'
        # scene.cycles.use_open_shading_language = False #TODO:Doesnt work - wrong name
        scene.cycles.shading_system=False
        scene.cycles.samples = 10
        scene.cycles.use_denoising = False

        # Configure baking settings ?will this work for normal?
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_clear = True
        bpy.context.scene.render.film_transparent = True
        if(scene.bake_with_gpu):
            scene.cycles.device = 'GPU'
        else:
            scene.cycles.device = 'CPU'

        SkinEditorService.bake_skin_categories(context, self.texture_resolution, self.baking_type)

        if(self.baking_type=='diffuse' or self.baking_type=='both'):
            scene.diffuse_baked=True
        if(self.baking_type=='normal' or self.baking_type=='both'):
            scene.normal_baked=True

        # Restore original settings
        scene.render.engine = original_engine
        scene.cycles.use_open_shading_language = original_osa
        scene.cycles.samples = original_samples
        context.space_data.shading.type = original_shading

        # Turn off material editing UI
        if(scene.normal_baked and scene.diffuse_baked):
            scene.material_baked = True
            scene["textures_loaded"] = False

        self.report({'INFO'}, "Textures successfully baked!")

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_BakeMaterial_Operator)