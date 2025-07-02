# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Saves mapped tattoo texture
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.skineditorservices import SkinEditorService
from ....services.locationservice import LocationService
from ....  import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.save_tattoo_texture_operator")


class MPFB_OT_SaveTattooTexture_Operator(bpy.types.Operator):
    """Saves maped tattoo to give folder, returns original viewport"""

    bl_idname = "mpfb.save_tattoo_texture_operator"
    bl_label = "save tattoo texture"
    bl_options = {'REGISTER'}


    def execute(self, context):
        scene = context.scene
        tattoo_path = scene.tattoo_texture_path
        self.report({'INFO'}, ("Saving new tattoo file, it might take a while..."))


        obj = context.object
        if not obj or not obj.active_material:
            self.report({'ERROR'}, "No active material found on the selected object.")
            return {'CANCELLED'}
        mat = obj.active_material

        # Get active node (activated in add_tattoo op.)
        active_node = mat.node_tree.nodes.active
        if not active_node:
            self.report({'ERROR'}, "No active node found.")
            return {'CANCELLED'}

        if active_node.type != 'TEX_IMAGE' or not active_node.image:
            self.report({'ERROR'}, "Active node is not an image texture or has no image.")
            return {'CANCELLED'}

        # Get image
        image = active_node.image

        # Path to tatto save
        dest_dir = scene.tattoo_texture_destination
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Save image
        dest_path = os.path.join(dest_dir, image.name + ".png")
        try:
            image.filepath_raw = dest_path
            image.file_format = 'PNG'
            image.save()
            self.report({'INFO'}, f"Saved tattoo texture to {dest_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save image: {e}")
            return {'CANCELLED'}


        SkinEditorService.add_tattoo_influence_property(scene,image.name)
        scene.tattoos_editing=False


        # Swich back to obj mode
        bpy.ops.object.mode_set(mode='OBJECT')


        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_SaveTattooTexture_Operator)