# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         1.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for undoing a hair cards bake, so the live cards can be edited again
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import (HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_OBJECT_SUFFIX,
                              get_cards_flag, set_cards_flag,
                              baked_image_names, create_cards_properties, read_cards_settings,
                              get_bake_target, resolve_body_surface, get_cards_mode,
                              resolve_custom_surface, restore_custom_mesh_materials)
from .. import bodyoverlay
from .. import cardgenerators as cg
from .generate_hair_cards_operator import build_cards_for_asset

import bpy

_LOG = LogService.get_logger("haireditorpanel.unbake_hair_operator")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_UnbakeHair_Operator(MpfbOperator):
    """Undoes a hair cards bake and rebuilds the editable cards from the settings saved at bake time.

    The card mesh, its baked material and the baked image datablocks are destroyed. Texture files on disk are not affected.
    """
    bl_idname = "mpfb.unbake_hair_operator"
    bl_label = "Unbake cards"
    bl_options = {'REGISTER', 'UNDO'}

    hair_asset: bpy.props.StringProperty()
    is_fur: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return {'CANCELLED'}

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"

        if not get_cards_flag(properties, basemesh, self.hair_asset, kind, "baked"):
            self.report({'ERROR'}, "This asset's cards have not been baked")
            return {'CANCELLED'}

        hair_obj = None
        card_obj = None
        card_name = f"{self.hair_asset}{CARDS_OBJECT_SUFFIX}"
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == self.hair_asset:
                hair_obj = child
            if child.name == card_name:
                card_obj = child

        if hair_obj is not None:
            hair_obj.hide_set(False)
            hair_obj.hide_render = False

        target = get_bake_target(properties, basemesh, self.hair_asset)
        if target == cg.BAKE_TARGET_BODY_DIRECT:
            # Nothing was built for this target, the result is a Mix Shader inside the skin material
            surface_obj = resolve_body_surface(basemesh)
            removed = bodyoverlay.remove_overlay(surface_obj, self.hair_asset)
            _LOG.debug("Removed fur overlay from material slots", removed)

        if target == cg.BAKE_TARGET_CUSTOM:
            # Remove the baked material from the user mesh and restore its own slots, before the image sweep below
            surface_obj = resolve_custom_surface(properties, basemesh, self.hair_asset)
            if surface_obj is None:
                self.report({'WARNING'},
                            "The mesh this was baked onto is gone, so its material could not be put back")
            else:
                baked = [slot.material for slot in surface_obj.material_slots
                         if slot.material is not None
                         and slot.material.name.startswith(f"{self.hair_asset}_baked")]
                if not restore_custom_mesh_materials(surface_obj):
                    # Nothing was remembered (baked by an older version), clear the baked material anyway
                    surface_obj.data.materials.clear()
                for material in baked:
                    if material.users == 0:
                        bpy.data.materials.remove(material)

        if card_obj is not None:
            materials = [slot.material for slot in card_obj.material_slots]
            mesh = card_obj.data
            bpy.data.objects.remove(card_obj, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
            for material in materials:
                if material is not None and material.users == 0:
                    bpy.data.materials.remove(material)

        # Textures on disk are left alone, only the datablocks are removed
        for name in baked_image_names(self.hair_asset):
            image = bpy.data.images.get(name)
            if image is None:
                continue
            # The extra maps have a fake user, release it first
            image.use_fake_user = False
            if image.users == 0:
                bpy.data.images.remove(image)

        set_cards_flag(properties, basemesh, self.hair_asset, kind, "baked", False)

        # Rebuild the cards from the saved settings. If that fails, the "generated" flag is cleared so "Convert to cards" is offered again
        rebuilt = False
        if target in (cg.BAKE_TARGET_BODY_DIRECT, cg.BAKE_TARGET_CUSTOM):
            # These targets have no card object to put back
            pass
        elif hair_obj is not None:
            try:
                card_obj, used_generator = build_cards_for_asset(
                    context, basemesh, hair_obj, card_name, self.is_fur, properties, self.hair_asset)
                if used_generator:
                    create_cards_properties(properties, basemesh, self.hair_asset,
                                            values=read_cards_settings(basemesh, self.hair_asset),
                                            mode=get_cards_mode(properties, basemesh, self.hair_asset))
                rebuilt = True
            except Exception as e:
                _LOG.error("Could not rebuild the cards after unbaking", e)
                self.report({'WARNING'},
                            f"Unbaked, but the cards could not be rebuilt ({e}); use Convert to cards")

        set_cards_flag(properties, basemesh, self.hair_asset, kind, "generated", rebuilt)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Unbaked hair cards for '{self.hair_asset}'")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_UnbakeHair_Operator)
