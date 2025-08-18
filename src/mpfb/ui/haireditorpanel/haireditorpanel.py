# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  UI panel for hair editor module
# ------------------------------------------------------------------------------

from ... import ClassManager
from ...services.logservice import LogService
from ...services.uiservice import UiService
from ...services.sceneconfigset import SceneConfigSet
from ...services.haireditorservices import HairEditorService
from ...ui.abstractpanel import Abstract_Panel
from .hairproperties import HAIR_PROPERTIES, FUR_PROPERTIES, DYNAMIC_HAIR_PROPS_DEFINITIONS, DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS, DYNAMIC_FUR_PROPS_DEFINITIONS, DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS
import bpy,os, json

_LOG = LogService.get_logger("ui.haireditorpanel")
#_LOG.set_level(LogService.DEBUG)

class MPFB_PT_Hair_Editor_Panel(Abstract_Panel):
    bl_label = "Hair Editor"
    bl_category = UiService.get_value("HAIREDITORCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    # Operator to set up UI for hair editor
    def _setup_hair(self, scene, layout):
        box = layout.box()
        box.label(text="Setup mesh for hair editing")

        op = box.operator("mpfb.setup_hair_operator")

    # UI panel for adding and editing of hair assets
    def _hair_panel(self, basemesh, layout):
        box = layout.box()
        box.label(text="Hair assets:")

        # Add operators (hair, facial hair, eybrow, others)
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["hair_assets"])
        hair_op = box.operator("mpfb.apply_hair_operator")
        hair_op.hair_asset = HAIR_PROPERTIES.get_value("hair_assets", entity_reference=basemesh)
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["facial_assets"])
        facial_op = box.operator("mpfb.apply_hair_operator")
        facial_op.hair_asset = HAIR_PROPERTIES.get_value("facial_assets", entity_reference=basemesh)
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["eyebrow_assets"])
        eyebrow_op = box.operator("mpfb.apply_hair_operator")
        eyebrow_op.hair_asset = HAIR_PROPERTIES.get_value("eyebrow_assets", entity_reference=basemesh)
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["other_assets"])
        other_op = box.operator("mpfb.apply_hair_operator")
        other_op.hair_asset = HAIR_PROPERTIES.get_value("other_assets", entity_reference=basemesh)

        #_LOG.debug("Hair keys", HAIR_PROPERTIES.get_keys(basemesh))


        # Column with applied assets
        col = layout.column()

        for key in HAIR_PROPERTIES.get_keys(basemesh):
            _LOG.debug("HAIR key", key)
            if str(key).endswith("_hair_asset_open"):
                asset_name = str(key).replace("_hair_asset_open", "")
                toggle_prop = f"{asset_name}_hair_asset_open"
                HAIR_PROPERTIES.draw_properties(basemesh, col, [toggle_prop])
                is_open = HAIR_PROPERTIES.get_value(toggle_prop, entity_reference=basemesh)

                cards_gen_prop = f"{asset_name}_hair_cards_are_generated"
                cards_are_generated = HAIR_PROPERTIES.get_value(cards_gen_prop, entity_reference=basemesh)

                cards_baked_prop = f"{asset_name}_hair_cards_are_baked"
                cards_are_baked = HAIR_PROPERTIES.get_value(cards_baked_prop, entity_reference=basemesh)

                if is_open:
                    box = col.box()
                    #box.label(text=f"{asset_name}")

                    for prop in DYNAMIC_HAIR_PROPS_DEFINITIONS.keys():
                        propname = f"{HAIR_PROPERTIES.dynamic_prefix}{asset_name}_{prop}"
                        box.prop(basemesh, propname, text=prop, slider=True)
                    for prop in DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS.keys():
                        propname = f"{HAIR_PROPERTIES.dynamic_prefix}{asset_name}_{prop}"
                        box.prop(basemesh, propname, text=prop)
                    
                    if not cards_are_generated:
                        # generate cards button
                        pass
                    elif(cards_are_generated and not cards_are_baked):
                        # properties and bake button
                        pass

        # TODO: Port cards, delete etc

#===============================================================================
#                         # Generate cards operator
#                         if not getattr(basemesh, f"{asset_name}_cards_generated",False):
#                             op_gen = box.operator("mpfb.generate_hair_cards_operator", text="Convert to cards")
#                             op_gen.hair_asset =asset_name
#                             op_gen.card_asset=f"{asset_name}_cards"
#
#                         # Cards editing
#                         if getattr(basemesh, f"{asset_name}_cards_generated",False):
#                             box.label(text="Hair cards:")
#
#                             # Settings for eventual generated cards placement
#                             if getattr(basemesh, f"{asset_name}_cards_scale",False):
#                                 box.prop(basemesh, f"{asset_name}_cards_scale", text="Scale of cards", slider=True)
#                                 box.prop(basemesh, f"{asset_name}_cards_density", text="Card density", slider=True)
#                                 box.prop(basemesh, f"{asset_name}_cards_placement", text="Seed for deleting random cards. No efect when density is 1.", slider=True)
#
#                             # Bake hair cards settings
#                             box.label(text="Warning: baking process is slow and might crash blender")
#                             box.prop(basemesh, f"{asset_name}_cards_glossy", text="Bake as glossy(better in hi res), or diffuse(fater and more stable)?")
#                             box.prop(basemesh, f"{asset_name}_cards_samples", text="Render samples used in baking", slider=True)
#                             box.prop(basemesh, f"{asset_name}_cards_resolution", text="Resolution of baked texture (Idealy power of 2 values)", slider=True)
#                             box.prop(basemesh, f"{asset_name}_cards_texture_dst", text="Export Save Path")
#                             op_bake = box.operator("mpfb.bake_hair_operator", text="Bake cards")
#                             op_bake.hair_asset =asset_name
#                             op_bake.card_asset=f"{asset_name}_cards"
#
#                     op_del = box.operator("mpfb.delete_hair_operator", text="Delete hair")
#                     op_del.hair_asset =asset_name
#===============================================================================

        return

    # UI panel for adding and editing of hair assets
    def _fur_panel(self, basemesh, layout):
        box = layout.box()
        box.label(text="Fur assets:")
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["fur_assets"])

        # Apply fur operator
        other_op = box.operator("mpfb.apply_fur_operator")
        other_op.hair_asset = HAIR_PROPERTIES.get_value("fur_assets", entity_reference=basemesh)

        # Column with applied assets
        col = layout.column()

        for key in FUR_PROPERTIES.get_keys(basemesh):
            _LOG.debug("FUR key", key)
            if str(key).endswith("_fur_asset_open"):
                asset_name = str(key).replace("_fur_asset_open", "")
                toggle_prop = f"{asset_name}_fur_asset_open"

                FUR_PROPERTIES.draw_properties(basemesh, col, [toggle_prop])
                is_open = FUR_PROPERTIES.get_value(toggle_prop, entity_reference=basemesh)

                cards_gen_prop = f"{asset_name}_fur_cards_are_generated"
                cards_are_generated = FUR_PROPERTIES.get_value(cards_gen_prop, entity_reference=basemesh)

                cards_baked_prop = f"{asset_name}_fur_cards_are_baked"
                cards_are_baked = FUR_PROPERTIES.get_value(cards_baked_prop, entity_reference=basemesh)

                if is_open:
                    box = col.box()
                    #box.label(text=f"{asset_name}")

                    for prop in DYNAMIC_FUR_PROPS_DEFINITIONS.keys():
                        propname = f"{FUR_PROPERTIES.dynamic_prefix}{asset_name}_{prop}"
                        box.prop(basemesh, propname, text=prop, slider=True)
                    for prop in DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS.keys():
                        propname = f"{FUR_PROPERTIES.dynamic_prefix}{asset_name}_{prop}"
                        box.prop(basemesh, propname, text=prop)
                    
                    if not cards_are_generated:
                        # generate cards button
                        pass
                    elif(cards_are_generated and not cards_are_baked):
                        # properties and bake button
                        pass



# TODO: fur card and delete stuff
#===============================================================================
#
#                         # Generate cards operator
#                         if not getattr(basemesh, f"{asset_name}_cards_generated",False):
#                             op_gen = box.operator("mpfb.generate_hair_cards_operator", text="Convert to cards")
#                             op_gen.hair_asset =asset_name
#                             op_gen.card_asset=f"{asset_name}_cards"
#
#                         # Cards editing
#                         if getattr(basemesh, f"{asset_name}_cards_generated",False):
#                             box.label(text="Hair cards:")
#
#                             # Settings for eventual generated cards placement
#                             if getattr(basemesh, f"{asset_name}_cards_scale",False):
#                                 box.prop(basemesh, f"{asset_name}_cards_scale", text="Scale of cards", slider=True)
#                                 box.prop(basemesh, f"{asset_name}_cards_density", text="Card density", slider=True)
#                                 box.prop(basemesh, f"{asset_name}_cards_placement", text="Seed for deleting random cards. No efect when density is 1.", slider=True)
#
#                             # Card baking settings
#                             box.label(text="Warning: baking process is slow and might crash blender")
#                             box.prop(basemesh, f"{asset_name}_cards_glossy", text="Bake as glossy(better in hi res), or diffuse(fater and more stable)?")
#                             box.prop(basemesh, f"{asset_name}_cards_samples", text="Render samples used in baking", slider=True)
#                             box.prop(basemesh, f"{asset_name}_cards_resolution", text="Resolution of baked texture (Idealy power of 2 values)", slider=True)
#                             box.prop(basemesh, f"{asset_name}_cards_texture_dst", text="Export Save Path")
#                             op_bake = box.operator("mpfb.bake_hair_operator", text="Bake cards")
#                             op_bake.hair_asset =asset_name
#                             op_bake.card_asset=f"{asset_name}_cards"
#
#                     op_del = box.operator("mpfb.delete_hair_operator", text="Delete hair")
#                     op_del.hair_asset =asset_name
#===============================================================================

        return




    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        basemesh = self.get_basemesh(context)

        if not basemesh:
            layout.label(text="No basemesh selected.")
            return

        if not HairEditorService.is_hair_asset_installed():
            layout.label(text="Hair editor assets are not")
            layout.label(text="installed. Download from")
            layout.label(text="asset packs page.")
            return

        hair_setup = False
        if HAIR_PROPERTIES.has_key("hair_setup", entity_reference=basemesh):
            hair_setup = HAIR_PROPERTIES.get_value("hair_setup", False, entity_reference=basemesh)

        if (not hair_setup):
            self._setup_hair(basemesh, layout)
        else:
            self._hair_panel(basemesh, layout)
            self._fur_panel(basemesh, layout)


ClassManager.add_class(MPFB_PT_Hair_Editor_Panel)