# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         135.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  unused
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.skineditorservices import SkinEditorService
from ....services.locationservice import LocationService
from ....  import ClassManager
import bpy, os, json

_LOG = LogService.get_logger("skineditorpanel.update_mix_factor_operator")


class MPFB_OT_UpdateMixFactor_Operator(bpy.types.Operator):
    """Update Mix Factor based on the property in the scene"""
    bl_idname = "mpfb.update_mix_factor_operator"
    bl_label = "Update Mix Factor"
    bl_options = {'REGISTER'}

    tex_name: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        prop_name = f"mix_factor_{self.tex_name}"
        factor_value = scene.get(prop_name, 0.0)

        # Find the texture node and corresponding mix node
        mat = bpy.context.object.active_material
        if mat and mat.node_tree:
            nodes = mat.node_tree.nodes
            #texture_node = next((n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == self.tex_name), None)
            texture_node = next((n for n in nodes if n.type == 'TEX_IMAGE' and n.label == self.tex_name), None)
            if texture_node:
                mix_rgb_node = SkinEditorService.find_next_mix_rgb_node(texture_node)
                if mix_rgb_node:
                    mix_rgb_node.inputs[0].default_value = factor_value

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_UpdateMixFactor_Operator)