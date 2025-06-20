# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Saves freckles texture
# ------------------------------------------------------------------------------
from mpfb.services.logservice import LogService
from mpfb.services.skineditorservices import SkinEditorService
from mpfb.services.locationservice import LocationService
from mpfb._classmanager import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.save_freckles_texture_operator")


class MPFB_OT_SaveFrecklesTexture_Operator(bpy.types.Operator):
    """Saves maped freckles to give folder, returns original viewport"""

    bl_idname = "mpfb.save_freckles_texture_operator"
    bl_label = "save freckles texture"
    bl_options = {'REGISTER'}


    def execute(self, context):
        scene = context.scene
        self.report({'INFO'}, ("Saving new freckles file, it might take a while..."))


        obj = context.object
        if not obj or not obj.active_material:
            self.report({'ERROR'}, "No active material found on the selected object.")
            return {'CANCELLED'}
        mat = obj.active_material

        # Get active node (activated in add_freckles op.)
        active_node = mat.node_tree.nodes.active
        if not active_node:
            self.report({'ERROR'}, "No active node found.")
            return {'CANCELLED'}

        if active_node.type != 'TEX_IMAGE' or not active_node.image:
            self.report({'ERROR'}, "Active node is not an image texture or has no image.")
            return {'CANCELLED'}

        # Get image
        image = active_node.image

        # Path to freckle save
        dest_dir = scene.freckles_texture_destination
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Save image
        dest_path = os.path.join(dest_dir, image.name + ".png")
        try:
            image.filepath_raw = dest_path
            image.file_format = 'PNG'
            image.save()
            self.report({'INFO'}, f"Saved freckles texture to {dest_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save image: {e}")
            return {'CANCELLED'}



        # Swich back to obj mode
        bpy.ops.object.mode_set(mode='OBJECT')



        scene.freckles_editing=False

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_SaveFrecklesTexture_Operator)