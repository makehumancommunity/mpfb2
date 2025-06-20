# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading tattoo texture and seting up tattoo paint interface
# ------------------------------------------------------------------------------
from mpfb.services.logservice import LogService
from mpfb.services.skineditorservices import SkinEditorService
from mpfb.services.locationservice import LocationService
from mpfb._classmanager import ClassManager
import bpy, os, json, shutil

_LOG = LogService.get_logger("skineditorpanel.add_tattoo_texture_operator")

# maximum textures eevee can handle
MAX_TEXTURES = 24

class MPFB_OT_AddTattooTexture_Operator(bpy.types.Operator):
    """Loads tatto from file, saves original image, setups stencil paint for that tattoo"""
    bl_idname = "mpfb.add_tattoo_texture_operator"
    bl_label = "Add tattoo texture"
    bl_options = {'REGISTER'}

    material_complexity: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        tattoo_path = scene.tattoo_texture_path

        self.report({'INFO'}, ("Setting up tattoo interface, it might take a while..."))

        if not tattoo_path or not os.path.exists(tattoo_path):
            self.report({'ERROR'}, "Invalid tattoo texture path")
            return {'CANCELLED'}

        texture_name = os.path.splitext(os.path.basename(tattoo_path))[0]
        is_normal_map = texture_name.endswith("_norm")


        # Load picture
        try:
            tattoo_image = bpy.data.images.load(tattoo_path)
            tattoo_image.name = "mapped"+texture_name
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load tattoo image: {e}")
            return {'CANCELLED'}

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




        # Create an 8K blank alpha texture
        alpha_texture = bpy.data.images.new(texture_name, width=8192, height=8192, alpha=True, float_buffer=False)
        alpha_texture.generated_color = (0, 0, 0, 0)
        alpha_tex_node = nodes.new(type="ShaderNodeTexImage")
        alpha_tex_node.image = alpha_texture
        alpha_tex_node.label = tattoo_image.name
        alpha_tex_node.location = (principled_node.location.x - 600, principled_node.location.y - 200)

        # Set different positions for normal map and color influenced tattoos
        if(is_normal_map):
            normal_input = principled_node.inputs.get("Normal").links[0].from_node
            principeled_shader_input = normal_input.inputs.get("Color")
            alpha_tex_node.image.colorspace_settings.name = 'Non-Color'
        else:
            if(scene.tattoo_color_influence):
                from_node = principled_node.inputs.get("Base Color").links[0].from_node
                gamma_input =from_node
                # Skip eventual non color influenced tattoos
                while(gamma_input.type != "GAMMA"):
                    from_node = gamma_input.inputs.get("Color1").links[0].from_node
                    gamma_input = from_node
                multiply_input = gamma_input.inputs.get("Color").links[0].from_node
                principeled_shader_input = multiply_input.inputs.get("Color1")
            else:
                principeled_shader_input = principled_node.inputs.get("Base Color")

        # Put tattoo after color and gama corection using mix rgb node
        mix_node = nodes.new(type="ShaderNodeMixRGB")
        mix_node.blend_type = 'MIX'
        mix_node.label =texture_name
        mix_node.name =texture_name
        mix_node.inputs[0].default_value = 1.0
        mix_node.location = (principled_node.location.x - 300, principled_node.location.y)

        mix_node_blend = nodes.new(type="ShaderNodeMixRGB")
        mix_node_blend.blend_type = 'MIX'
        mix_node_blend.name = "Tattoo Mix"
        mix_node_blend.label =tattoo_image.name
        mix_node_blend.inputs[0].default_value = 1.0
        mix_node_blend.location = (principled_node.location.x - 300, principled_node.location.y-200)

        # Link it all together
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

        # Set up texture painting with stencil mode
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if(space.shading.type != 'MATERIAL' and space.shading.type != 'RENDERED'):
                            if(self.material_complexity == "EEVEE"):
                                space.shading.type = 'MATERIAL'
                            else:
                                space.shading.type = 'RENDERED'
                        region = space.region_3d
                        break
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')

        tool_settings = context.scene.tool_settings
        tool_settings.image_paint.mode = 'MATERIAL'
        tool_settings.image_paint.canvas = alpha_texture
        nodes.active = alpha_tex_node

        # Assign tattoo as stencil texture
        brush = tool_settings.image_paint.brush
        brush = bpy.data.brushes.get("TexDraw") or bpy.data.brushes.new(name="TexDraw")
        brush.texture_slot.map_mode = 'STENCIL'
        brush.texture = bpy.data.textures.new(name="Tattoo_Stencil", type='IMAGE')
        brush.texture.image = tattoo_image

        # Enable stencil mask for precise placement
        brush.texture_slot.map_mode = 'STENCIL'
        brush.mask_texture_slot.map_mode = 'STENCIL'

        # Print help message
        self.report({'INFO'}, (
            "MANUAL: "
            "LMB = Paint, "
            "RMB = Pan, "
            "Shift+RMB = Scale, "
            "Ctrl+RMB = Rotate, "
            "Save via 'Save Tattoo' button."
        ))

        scene.tattoos_editing = True
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_AddTattooTexture_Operator)