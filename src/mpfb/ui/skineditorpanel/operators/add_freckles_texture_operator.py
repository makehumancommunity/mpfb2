# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Adds texture for freckles in first call and sets up freckles editing interface
# ------------------------------------------------------------------------------
from mpfb.services.logservice import LogService
from mpfb.services.skineditorservices import SkinEditorService
from mpfb.services.locationservice import LocationService
from mpfb._classmanager import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.add_freckles_texture_operator")

MAX_TEXTURES = 24

class MPFB_OT_AddFrecklesTexture_Operator(bpy.types.Operator):
    """Loads tatto from file, saves original image, setups stencil paint for that freckles"""
    bl_idname = "mpfb.add_freckles_texture_operator"
    bl_label = "Add freckles texture"
    bl_options = {'REGISTER'}


    material_complexity: bpy.props.StringProperty()

    def execute(self, context):

        scene = context.scene
        freckles_path = scene.freckles_texture_destination
        self.report({'INFO'}, ("Setting up freckles interface, it might take a while..."))
        texture_name = "freckles"


        # Get material
        obj = context.object
        if not obj or not obj.active_material:
            self.report({'ERROR'}, "No active material found")
            return {'CANCELLED'}

        mat = obj.active_material
        if not mat.use_nodes:
            mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Check the number of existing texture nodes in the material to prevent EEVEE crash
        if(not scene.freckles_applied):
            if(self.material_complexity == "EEVEE"):
                texture_count = sum(1 for node in nodes if node.type == 'TEX_IMAGE')
                if texture_count >= MAX_TEXTURES:
                    self.report({'ERROR'}, f"Cannot add more than {MAX_TEXTURES} textures to EEVEE compatible material. Use Complex instead.")
                    return {'CANCELLED'}

        # Find principleled node
        principled_node = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled_node = node
                break
        if not principled_node:
            self.report({'ERROR'}, "No Principled BSDF node found")
            return {'CANCELLED'}

        # Find canvas texture in case of editing freckles
        if(scene.freckles_applied):
            for node in nodes:
                if (node.label == 'freckles' and node.type=='TEX_IMAGE'):
                    alpha_texture = node.image
                    alpha_tex_node = node

        # When called for first time put freckles texture into material
        if(not scene.freckles_applied):
            # Create an 8K blank alpha texture
            alpha_texture = bpy.data.images.new(texture_name, width=8192, height=8192, alpha=True, float_buffer=False)
            alpha_texture.generated_color = (0, 0, 0, 0)
            alpha_tex_node = nodes.new(type="ShaderNodeTexImage")
            alpha_tex_node.image = alpha_texture
            alpha_tex_node.label = texture_name
            alpha_tex_node.location = (principled_node.location.x - 600, principled_node.location.y + 200)

            principeled_shader_input = principled_node.inputs.get("Base Color")

            # Put freckles to material using mix rgb node
            mix_node = nodes.new(type="ShaderNodeMixRGB")
            mix_node.blend_type = 'MIX'
            mix_node.label =texture_name
            mix_node.name =texture_name
            mix_node.inputs[0].default_value = 1.0
            mix_node.location = (principled_node.location.x - 300, principled_node.location.y +400)

            mix_node_blend = nodes.new(type="ShaderNodeMixRGB")
            mix_node_blend.blend_type = 'MIX'
            mix_node_blend.name = "Freckles Mix"
            mix_node_blend.label =texture_name
            mix_node_blend.inputs[0].default_value = 1.0
            mix_node_blend.location = (principled_node.location.x - 300, principled_node.location.y+200)

            # Manage links
            prev_link = None
            if principeled_shader_input.is_linked:
                prev_link = principeled_shader_input.links[0]
            from_node = prev_link.from_node
            from_socket = prev_link.from_socket
            links.remove(prev_link)
            links.new(from_node.outputs[from_socket.name], mix_node.inputs[1])
            links.new(from_node.outputs[from_socket.name], mix_node_blend.inputs[1])
            links.new(alpha_tex_node.outputs["Alpha"], mix_node.inputs[0])
            links.new(mix_node_blend.outputs["Color"], mix_node.inputs[2])
            links.new(alpha_tex_node.outputs["Color"], mix_node_blend.inputs[2])
            links.new(mix_node.outputs["Color"], principeled_shader_input)


        # Swich to texture paint
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D' and space.shading.type not in ['MATERIAL', 'RENDERED']:
                        space.shading.type = 'MATERIAL' if self.material_complexity == "EEVEE" else 'RENDERED'
                        break
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')

        tool_settings = context.scene.tool_settings
        tool_settings.image_paint.mode = 'MATERIAL'
        tool_settings.image_paint.canvas = alpha_texture
        nodes.active = alpha_tex_node

        # Get brush
        brush = bpy.context.tool_settings.image_paint.brush
        if not brush:
            self.report({'ERROR'}, "No active brush found")
            return {'CANCELLED'}

        # Prepare voronoi texture
        brush.texture = bpy.data.textures.new(name="FrecklesBrush", type='VORONOI')
        brush.texture_slot.map_mode = 'RANDOM'

        brush.texture.use_color_ramp = True
        brush.texture.color_ramp.elements[0].position = 0.3
        brush.texture.color_ramp.elements[1].position = 0.8

        brush.texture.color_ramp.elements[0].color = (*scene.freckles_color, 1)  # freckles color
        brush.texture.color_ramp.elements[1].color = (0, 0, 0, 0)  # Transparent sides

        brush.texture.noise_intensity = scene.voronoi_intensity
        brush.texture.noise_scale = scene.voronoi_size

        # Enable random in brush settings
        brush.texture_slot.use_random = True
        brush.use_pressure_size = True

        scene.freckles_editing=True
        scene.freckles_applied = True

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_AddFrecklesTexture_Operator)