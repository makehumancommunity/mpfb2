# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for baking hair asset onto a card asset as a texture
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
import bpy, os, json, shutil, bpy_extras
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from mathutils import Vector
import bmesh
import tempfile

_LOG = LogService.get_logger("haireditorpanel.bake_hair_operator")


class MPFB_OT_BakeHair_Operator(bpy.types.Operator):
    """Bakes hair asset as a texture for card asset"""
    bl_idname = "mpfb.bake_hair_operator"
    bl_label = "Bake hair cards"
    bl_options = {'REGISTER'}


    hair_asset: bpy.props.StringProperty()
    card_asset: bpy.props.StringProperty()

    def execute(self, context):

        scene = context.scene

        # Get Human mesh
        human_obj = context.object
        if (not human_obj or not human_obj.name == 'Human'):
            self.report({'ERROR'}, "Object Human must be active")
            return {'CANCELLED'}
        original_human_materials = [slot.material for slot in human_obj.material_slots]

        # Get hair asset
        hair_obj = None
        for child in human_obj.children:
            if child.name == self.hair_asset:
                hair_obj = child
                break
        if not hair_obj:
            self.report({'WARNING'}, f"Hair object '{self.hair_asset}' not found")
            return {'CANCELLED'}

        # Get card asset
        card_obj = None
        for child in human_obj.children:
            if child.name == self.card_asset:
                card_obj = child
                break
        if not card_obj:
            self.report({'WARNING'}, f"Card object '{self.card_asset}' not found")
            return {'CANCELLED'}

        # Convert card asset to card mesh
        if card_obj.type != 'MESH':
            bpy.ops.object.select_all(action='DESELECT')
            card_obj.select_set(True)
            bpy.context.view_layer.objects.active = card_obj
            bpy.ops.object.convert(target='MESH')

        # Unwrap cards (smart uv project)
        bpy.ops.object.select_all(action='DESELECT')
        card_obj.select_set(True)
        bpy.context.view_layer.objects.active = card_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        human_obj.select_set(True)
        bpy.context.view_layer.objects.active = human_obj

        # Set scene bg as transparent, hide other assets in viewport and render (all besides hair asset, human and card)
        scene.render.film_transparent = True
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,0)
        hidden_objects = []
        for obj in bpy.data.objects:
            if obj.name not in {human_obj.name, hair_obj.name, card_obj.name}:
                if obj.visible_get():
                    hidden_objects.append(obj)
                    obj.hide_render = True
                    obj.hide_viewport = True

        # Switch to cycles
        scene.render.engine = 'CYCLES'

        # Turn off all hair card objects ray visibilities besides camera
        card_obj.visible_shadow = False
        card_obj.visible_diffuse = False
        card_obj.visible_glossy = False
        card_obj.visible_transmission = False
        card_obj.visible_volume_scatter = False

        # Add new material for card object
        card_mat = bpy.data.materials.new(name="HairCardRayPortal")
        card_mat.use_nodes = True
        nodes = card_mat.node_tree.nodes
        links = card_mat.node_tree.links
        nodes.clear()

        output    = nodes.new(type='ShaderNodeOutputMaterial')
        portal    = nodes.new(type='ShaderNodeBsdfRayPortal')
        geometry  = nodes.new(type='ShaderNodeNewGeometry')
        invert    = nodes.new(type='ShaderNodeVectorMath')
        invert.operation = 'MULTIPLY'
        invert.inputs[1].default_value = (-1.0, -1.0, -1.0)

        links.new(geometry.outputs['Position'], portal.inputs['Position'])
        links.new(geometry.outputs['Normal'],   invert.inputs['Vector'])
        links.new(invert.outputs['Vector'],     portal.inputs['Direction'])
        links.new(portal.outputs['BSDF'],     output.inputs['Surface'])

        card_obj.data.materials.clear()
        card_obj.data.materials.append(card_mat)

        baking_res = getattr(scene, f"{self.card_asset}_resolution")
        bake_image = bpy.data.images.new("BakedHairTexture", alpha=True, width=baking_res, height=baking_res)
        card_nodes = card_mat.node_tree.nodes
        bake_tex_node = card_nodes.new(type='ShaderNodeTexImage')
        bake_tex_node.image = bake_image
        card_mat.node_tree.nodes.active = bake_tex_node

        # Add new holdout material for Human mesh to hide everything behind
        human_mat = bpy.data.materials.new(name="HumanHoldout")
        human_mat.use_nodes = True
        human_nodes = human_mat.node_tree.nodes
        human_links = human_mat.node_tree.links
        human_nodes.clear()

        output = human_nodes.new(type='ShaderNodeOutputMaterial')
        holdout = human_nodes.new(type='ShaderNodeHoldout')

        human_links.new(holdout.outputs['Holdout'], output.inputs['Surface'])

        human_obj.data.materials.clear()
        human_obj.data.materials.append(human_mat)

        # Add new light so hair asset is lit correctly for glossy bake
        light_data_f = bpy.data.lights.new(name="BakeHairLight", type='POINT')
        light_data_f.energy = 1000
        light_obj_f = bpy.data.objects.new(name="BakeHairLight", object_data=light_data_f)
        scene.collection.objects.link(light_obj_f)
        light_obj_f.location = human_obj.location + Vector((0, -2, 3))

        light_data_b = bpy.data.lights.new(name="BakeHairLight", type='POINT')
        light_data_b.energy = 1000
        light_obj_b = bpy.data.objects.new(name="BakeHairLight", object_data=light_data_b)
        scene.collection.objects.link(light_obj_b)
        light_obj_b.location = human_obj.location + Vector((0, 2, 3))

        # Select object and activate texture image
        bpy.ops.object.select_all(action='DESELECT')
        card_obj.select_set(True)
        bpy.context.view_layer.objects.active = card_obj
        card_mat.node_tree.nodes.active = bake_tex_node

        # Select texture and bake as glossy or diffuse with propper render settings
        bpy.ops.object.select_all(action='DESELECT')
        card_obj.select_set(True)
        bpy.context.view_layer.objects.active = card_obj

        bake_settings = context.scene.render.bake
        baking_samples = getattr(scene, f"{self.card_asset}_samples")
        scene.cycles.samples = baking_samples
        scene.cycles.max_bounces = 64
        scene.cycles.diffuse_bounces = 64
        scene.cycles.glossy_bounces = 64
        scene.cycles.transparent_max_bounces = 64
        scene.cycles.transmission_bounces = 64
        scene.cycles.volume_bounces = 64
        scene.cycles.transparent_min_bounces = 64
        scene.cycles.use_denoising = True
        self.report({'INFO'}, f"Baking cards... It might take a while")
        if getattr(scene, f"{self.card_asset}_glossy"):
            bake_settings.use_pass_direct = True
            bake_settings.use_pass_indirect = True
            bpy.ops.object.bake(type='GLOSSY')
        else:
            bake_settings.use_pass_direct = False
            bake_settings.use_pass_indirect = False
            bpy.ops.object.bake(type='DIFFUSE')



        # Save texture and plug it into principledBSDF shader of card asset
        if getattr(scene, f"{self.card_asset}_texture_dst"):
            bake_path = os.path.join(getattr(scene, f"{self.card_asset}_texture_dst"), f"{self.hair_asset}_texture.png")
        else:
            bake_path = os.path.join(tempfile.gettempdir(), f"{self.hair_asset}_texture.png")

        bake_image.filepath_raw = bake_path
        bake_image.file_format = 'PNG'
        bake_image.save()

        # Replace material with principledBSDF shader and baked texture
        new_card_mat = bpy.data.materials.new(name=f"{self.hair_asset}_baked")
        new_card_mat.use_nodes = True
        nodes = new_card_mat.node_tree.nodes
        links = new_card_mat.node_tree.links
        nodes.clear()

        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs[2].default_value = 0.0
        bsdf.inputs[3].default_value = 1.0
        tex_image = nodes.new(type='ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(bake_path)

        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex_image.outputs['Alpha'], bsdf.inputs['Alpha'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        card_obj.data.materials.clear()
        card_obj.data.materials.append(new_card_mat)

        # Hide original hair asset (show previously hidden assets)
        hair_obj.hide_set(True)
        hair_obj.hide_render = True

        for obj in hidden_objects:
            obj.hide_render = False
            obj.hide_viewport = False

        # Return original material to human and remove portal materials and lights
        human_obj.data.materials.clear()
        for mat in original_human_materials:
            human_obj.data.materials.append(mat)

        bpy.data.materials.remove(human_mat, do_unlink=True)
        bpy.data.materials.remove(card_mat, do_unlink=True)


        bpy.data.objects.remove(light_obj_f, do_unlink=True)
        bpy.data.objects.remove(light_obj_b, do_unlink=True)

        # Property to update UI
        prop_id = f"{self.card_asset}_baked"
        if not hasattr(bpy.types.Scene, prop_id):
            setattr(
                bpy.types.Scene,
                prop_id,
                bpy.props.BoolProperty(
                name=prop_id,
                description=f"Card asset baked.",
                default=True
                )
            )
        if hasattr(scene, prop_id):
            setattr(scene, prop_id, True)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_BakeHair_Operator)