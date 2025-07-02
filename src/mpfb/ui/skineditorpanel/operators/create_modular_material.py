# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  Creates modular editable skin material based on texture_paths file and sets it up for editing
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.skineditorservices import SkinEditorService
from ....services.locationservice import LocationService
from ....  import ClassManager
import bpy, os, json

_LOG = LogService.get_logger("skineditorpanel.create_modular_material")

class MPFB_OT_CreateModularMaterial_Operator(bpy.types.Operator):
    """Creates prototype of modular material and applies it to body mesh"""
    bl_idname = "mpfb.create_modular_material"
    bl_label = "Apply material"
    bl_options = {'REGISTER'}

    material_complexity: bpy.props.StringProperty()

    def execute(self, context):
        self.report({'INFO'}, "CreatingComplexMaterial")

        # Get human mesh
        obj = bpy.data.objects.get("Human")
        if not obj:
            self.report({'ERROR'}, "Object 'Human' not found")
            return {'CANCELLED'}

        # Get texture paths file
        material_name = self.material_complexity.lower()
        texture_file_path = os.path.join(os.path.dirname(__file__), f"../texture_paths/{material_name}_texture_paths.json")

        # Load texures
        albedo_textures, normal_textures = SkinEditorService.load_textures(texture_file_path)
        #albedo_textures,normal_textures = SkinEditorService.load_textures(os.path.join(os.path.dirname(__file__), "../texture_paths/texture_paths.json"))

        if not albedo_textures or not normal_textures:
            self.report({'ERROR'}, "No textures found")
            return {'CANCELLED'}

        # Add textures to the scene
        SkinEditorService.add_textures_to_scene(context.scene, albedo_textures, normal_textures)

        # Create material
        material = bpy.data.materials.new(name="M_HumanSkin")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Remove current nodes
        for node in nodes:
            nodes.remove(node)

        # Principled BSDF
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        bsdf.location = (4000, 0)

        # Material output node
        material_output = nodes.new(type="ShaderNodeOutputMaterial")
        material_output.location = (4200, 0)
        links.new(bsdf.outputs["BSDF"], material_output.inputs["Surface"])

        # Albedo textures
        _, a_mix_nodes = SkinEditorService.create_texture_nodes(
            material, albedo_textures, location_x=200, location_y=-400, mix_node_offset=550
        )

        # Skin color and gama
        mix_rgb = nodes.new(type="ShaderNodeMixRGB")
        mix_rgb.blend_type = 'MULTIPLY'
        mix_rgb.inputs["Fac"].default_value = 0.0
        mix_rgb.location = (3500, -100)

        gamma_node = nodes.new(type="ShaderNodeGamma")
        gamma_node.location = (3700, -100)

        # Add color properties
        SkinEditorService.add_gamma_color_property(context.scene, gamma_node)
        SkinEditorService.add_multiply_factor_property(context.scene, mix_rgb)
        SkinEditorService.add_multiply_color_property(context.scene, mix_rgb)

        # Connect final albedo mix node to Base Color through color mixing
        if a_mix_nodes:
            links.new(a_mix_nodes[-2].outputs["Color"], mix_rgb.inputs["Color1"])
            #links.new(color_input.outputs["Color"], mix_rgb.inputs["Color2"])
            links.new(mix_rgb.outputs["Color"], gamma_node.inputs["Color"])
            links.new(gamma_node.outputs["Color"], bsdf.inputs["Base Color"])

        # normal textures
        _, n_mix_nodes = SkinEditorService.create_texture_nodes(
            material, normal_textures, location_x=-8550, location_y=-2000, mix_node_offset=550
        )

        # Connect final normal mix node to Normal Map
        if n_mix_nodes:
            normal_map = nodes.new(type="ShaderNodeNormalMap")
            normal_map.inputs["Strength"].default_value = 2.5
            normal_map.location = (3800, -100)
            links.new(n_mix_nodes[-2].outputs["Color"], normal_map.inputs["Color"])
            links.new(normal_map.outputs[0], bsdf.inputs["Normal"])


        # Applying material on body
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)

        self.report({'INFO'}, "Material created and applied")


        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_CreateModularMaterial_Operator)