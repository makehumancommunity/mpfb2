# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for deleting hair asset and removing its properties
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.locationservice import LocationService
from .... import ClassManager
from ....services.haireditorservices import HairEditorService
import bpy, os, json, shutil

_LOG = LogService.get_logger("haireditorpanel.delete_hair_operator")

class MPFB_OT_DeleteHair_Operator(bpy.types.Operator):
    """Deletes hair asset and removes all properties"""
    bl_idname = "mpfb.delete_hair_operator"
    bl_label = "Delete hair"
    bl_options = {'REGISTER'}

    hair_asset: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene

        self.report({'INFO'}, ("Deleting hair asset..."))

        # Get Human object
        human_obj = context.object
        if not human_obj or human_obj.name != 'Human':
            self.report({'ERROR'}, "Object 'Human' must be active")
            return {'CANCELLED'}

        # Get hair and eventual card assets
        hair_obj = None
        card_obj = None
        for child in human_obj.children:
            if child.name == self.hair_asset:
                hair_obj = child
            if child.name == f"{self.hair_asset}_cards":
                card_obj = child

        # Delete Geo Nodes modifier from card object
        modifier_name = f"{self.hair_asset}_cards_HairCards"
        if card_obj and modifier_name in card_obj.modifiers:
            mod = card_obj.modifiers.get(modifier_name)
            if mod and mod.type == 'NODES':
                mod.node_group = None
                card_obj.modifiers.remove(mod)
            node_group = bpy.data.node_groups.get(modifier_name)
            if node_group:
                bpy.data.node_groups.remove(node_group, do_unlink=True)
        for suffix in ["_cards_scale", "_cards_density", "_cards_placement"]:
            prop_name = f"{self.hair_asset}{suffix}"
            if hasattr(scene.__class__, prop_name):
                delattr(scene.__class__, prop_name)
            if prop_name in scene:
                del scene[prop_name]

        # Delete hair and card objects
        if hair_obj:
            bpy.data.objects.remove(hair_obj, do_unlink=True)
        else:
            self.report({'WARNING'}, f"Hair object '{self.hair_asset}' not found")
            return {'CANCELLED'}
        if card_obj:
            bpy.data.objects.remove(card_obj, do_unlink=True)

        # Force _cards_generated and _cards_baked to be false
        prop_name = f"{self.hair_asset}_cards_generated"
        if hasattr(scene, prop_name):
            setattr(scene, prop_name, False)
        prop_name = f"{self.hair_asset}_cards_baked"
        if hasattr(scene, prop_name):
            setattr(scene, prop_name, False)


        # Remove assetes properties
        prop_prefix = f"{self.hair_asset}_"
        for name in [
            "length", "density", "thickness", "frizz", "roll", "roll_radius",
            "roll_length", "clump", "clump_distance", "clump_shape", "clump_tip_spread",
            "noise", "noise_distance", "noise_scale", "noise_shape",
            "curl", "curl_guide_distance", "curl_radius", "curl_frequency",
            "holes", "holes_scale",
            "fur_asset_open", "hair_asset_open",
            "_cards_scale", "_cards_density", "_cards_placement",
            "_cards_resolution", "_cards_samples", "_cards_glossy", "_cards_generated", "_cards_texture_dst", "_cards_baked"
        ]:
            prop_id = f"{prop_prefix}{name}"
            if hasattr(scene.__class__, prop_id):
                delattr(scene.__class__, prop_id)

        # Remove material properties
        mat_name = f"{self.hair_asset}"
        material_props = [
            "color1", "color2", "coror_noise_scale", "darken_root", "root_color_length"
        ]
        for name in material_props:
            prop_id = f"{mat_name}_{name}"
            if hasattr(scene.__class__, prop_id):
                delattr(scene.__class__, prop_id)

        # Delete material
        material = bpy.data.materials.get(self.hair_asset)
        if material:
            for obj in bpy.data.objects:
                for i, slot in enumerate(obj.material_slots):
                    if slot.material == material:
                        obj.material_slots[i].material = None
            bpy.data.materials.remove(material)
        else:
            self.report({'INFO'}, f"No material named '{self.hair_asset}' found.")
        material = bpy.data.materials.get(f"{self.hair_asset}_baked")
        if material:
            for obj in bpy.data.objects:
                for i, slot in enumerate(obj.material_slots):
                    if slot.material == material:
                        obj.material_slots[i].material = None
            bpy.data.materials.remove(material)
        else:
            self.report({'INFO'}, f"No material named '{self.hair_asset}_baked' found.")

        # Reselect Human
        human_obj = bpy.data.objects.get("Human")
        if human_obj:
            bpy.ops.object.select_all(action='DESELECT')
            human_obj.select_set(True)
            context.view_layer.objects.active = human_obj
        else:
            self.report({'WARNING'}, "Human object not found in bpy.data.objects")

        self.report({'INFO'}, "Hair asset deleted successfully.")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_DeleteHair_Operator)