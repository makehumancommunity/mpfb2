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
from ...services.dynamicconfigset import DynamicConfigSet
from ...services.haireditorservices import HairEditorService
from ...ui.abstractpanel import Abstract_Panel
import bpy, os, json

_LOG = LogService.get_logger("ui.haireditorpanel")
_LOG.set_level(LogService.DEBUG)

_LOC = os.path.dirname(__file__)
HAIR_PROPERTIES_DIR = os.path.join(_LOC, "properties")
HAIR_PROPERTIES = DynamicConfigSet.from_definitions_in_json_directory(HAIR_PROPERTIES_DIR, prefix="HAI_", dynamic_prefix="DYN_HAIR_")


class MPFB_PT_Hair_Editor_Panel(Abstract_Panel):
    bl_label = "Hair Editor"
    bl_category = UiService.get_value("HAIREDITORCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    # Operator to set up UI for hair editor
    def _setup_hair(self, layout):
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


        # Column with applied assets
        col = layout.column()
        HAIR_PROPERTIES.draw_properties(basemesh, col, ["hair_setup"])
        return

        for prop in HAIR_PROPERTIES.get_dynamic_keys(basemesh):
            if prop.endswith("_hair_asset_open"):
                asset_name = prop.replace("_hair_asset_open", "")
                toggle_prop = f"{asset_name}_hair_asset_open"

                # Toggle property
                is_open = HAIR_PROPERTIES.get_value(toggle_prop, False, basemesh)
                icon = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
                #col.prop(basemesh, f"{toggle_prop}", text=asset_name, icon=icon, emboss=True, toggle=False)
                HAIR_PROPERTIES.draw_properties(basemesh, col, [toggle_prop])

                if is_open and False:
                    box = col.box()
                    box.label(text=f"{asset_name}")

                    # Editing material and shape of curves
                    if not getattr(scene, f"{asset_name}_cards_baked",False):
                        box.prop(scene, f"{asset_name}_color1", text="Color 1")
                        box.prop(scene, f"{asset_name}_color2", text="Color 2")
                        box.prop(scene, f"{asset_name}_color_noise_scale", text="Color distribution", slider=True)
                        box.prop(scene, f"{asset_name}_darken_root", text="Darken root", slider=True)
                        box.prop(scene, f"{asset_name}_root_color_length", text="Root length", slider=True)

                        box.label(text="Shape:")
                        box.prop(scene, f"{asset_name}_length", text="Length", slider=True)
                        box.prop(scene, f"{asset_name}_density", text="Density", slider=True)
                        box.prop(scene, f"{asset_name}_thickness", text="Thickness", slider=True)
                        box.prop(scene, f"{asset_name}_frizz", text="Frizz", slider=True)

                        box.prop(scene, f"{asset_name}_roll", text="Roll", slider=True)
                        box.prop(scene, f"{asset_name}_roll_radius", text="Roll radius", slider=True)
                        box.prop(scene, f"{asset_name}_roll_length", text="Roll length", slider=True)

                        box.prop(scene, f"{asset_name}_clump", text="Clump", slider=True)
                        box.prop(scene, f"{asset_name}_clump_distance", text="Clump distance", slider=True)
                        box.prop(scene, f"{asset_name}_clump_shape", text="Clump shape", slider=True)
                        box.prop(scene, f"{asset_name}_clump_tip_spread", text="Clump tip spread", slider=True)

                        box.prop(scene, f"{asset_name}_noise", text="Noise", slider=True)
                        box.prop(scene, f"{asset_name}_noise_distance", text="Noise distance", slider=True)
                        box.prop(scene, f"{asset_name}_noise_scale", text="Noise scale", slider=True)
                        box.prop(scene, f"{asset_name}_noise_shape", text="Noise radius", slider=True)

                        box.prop(scene, f"{asset_name}_curl", text="Curl", slider=True)
                        box.prop(scene, f"{asset_name}_curl_guide_distance", text="Curl guide distance", slider=True)
                        box.prop(scene, f"{asset_name}_curl_radius", text="Curl radius", slider=True)
                        box.prop(scene, f"{asset_name}_curl_frequency", text="Curl frequency", slider=True)


                        # Generate cards operator
                        if not getattr(scene, f"{asset_name}_cards_generated",False):
                            op_gen = box.operator("mpfb.generate_hair_cards_operator", text="Convert to cards")
                            op_gen.hair_asset =asset_name
                            op_gen.card_asset=f"{asset_name}_cards"

                        # Cards editing
                        if getattr(scene, f"{asset_name}_cards_generated",False):
                            box.label(text="Hair cards:")

                            # Settings for eventual generated cards placement
                            if getattr(scene, f"{asset_name}_cards_scale",False):
                                box.prop(scene, f"{asset_name}_cards_scale", text="Scale of cards", slider=True)
                                box.prop(scene, f"{asset_name}_cards_density", text="Card density", slider=True)
                                box.prop(scene, f"{asset_name}_cards_placement", text="Seed for deleting random cards. No efect when density is 1.", slider=True)

                            # Bake hair cards settings
                            box.label(text="Warning: baking process is slow and might crash blender")
                            box.prop(scene, f"{asset_name}_cards_glossy", text="Bake as glossy(better in hi res), or diffuse(fater and more stable)?")
                            box.prop(scene, f"{asset_name}_cards_samples", text="Render samples used in baking", slider=True)
                            box.prop(scene, f"{asset_name}_cards_resolution", text="Resolution of baked texture (Idealy power of 2 values)", slider=True)
                            box.prop(scene, f"{asset_name}_cards_texture_dst", text="Export Save Path")
                            op_bake = box.operator("mpfb.bake_hair_operator", text="Bake cards")
                            op_bake.hair_asset =asset_name
                            op_bake.card_asset=f"{asset_name}_cards"

                    op_del = box.operator("mpfb.delete_hair_operator", text="Delete hair")
                    op_del.hair_asset =asset_name

    # UI panel for adding and editing of hair assets
    def _fur_panel(self, basemesh, layout):
        box = layout.box()
        box.label(text="Fur assets:")
        HAIR_PROPERTIES.draw_properties(basemesh, box, ["fur_assets"])

        # Apply fur operator
        other_op = box.operator("mpfb.apply_fur_operator")
        other_op.hair_asset = HAIR_PROPERTIES.get_value("fur_assets", entity_reference=basemesh)

        # UNTIL BELOW IS FIXED: leave method early
        return

        # Column with applied fur assets
        col = layout.column()
        for prop in scene.bl_rna.properties:
            if prop.identifier.endswith("_fur_asset_open"):
                asset_name = prop.identifier.replace("_fur_asset_open", "")
                toggle_prop = f"{asset_name}_fur_asset_open"

                # Toggle property
                is_open = getattr(scene, toggle_prop)
                icon = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
                col.prop(scene, f"{toggle_prop}", text=asset_name, icon=icon, emboss=True, toggle=False)


                if is_open:
                    box = col.box()
                    box.label(text=f"{asset_name}")

                    # Editing material and shape of curves
                    if not getattr(scene, f"{asset_name}_cards_baked",False):
                        box.prop(scene, f"{asset_name}_use_texture")
                        if not getattr(scene, f"{asset_name}_use_texture",False):
                            box.prop(scene, f"{asset_name}_color1", text="Color 1")
                            box.prop(scene, f"{asset_name}_color2", text="Color 2")
                        else:
                            box.prop(scene, f"{asset_name}_texture_path", text="Texture path")
                        box.prop(scene, f"{asset_name}_color_noise_scale", text="Color distribution", slider=True)
                        box.prop(scene, f"{asset_name}_darken_root", text="Darken root", slider=True)
                        box.prop(scene, f"{asset_name}_root_color_length", text="Root length", slider=True)


                        box.label(text="Shape:")
                        box.prop(scene, f"{asset_name}_length", text="Length", slider=True)
                        box.prop(scene, f"{asset_name}_density", text="Density", slider=True)
                        box.prop(scene, f"{asset_name}_thickness", text="Thickness", slider=True)
                        box.prop(scene, f"{asset_name}_frizz", text="Frizz", slider=True)

                        box.prop(scene, f"{asset_name}_roll", text="Roll", slider=True)
                        box.prop(scene, f"{asset_name}_roll_radius", text="Roll radius", slider=True)
                        box.prop(scene, f"{asset_name}_roll_length", text="Roll length", slider=True)

                        box.prop(scene, f"{asset_name}_clump", text="Clump", slider=True)
                        box.prop(scene, f"{asset_name}_clump_distance", text="Clump distance", slider=True)
                        box.prop(scene, f"{asset_name}_clump_shape", text="Clump shape", slider=True)
                        box.prop(scene, f"{asset_name}_clump_tip_spread", text="Clump tip spread", slider=True)

                        box.prop(scene, f"{asset_name}_noise", text="Noise", slider=True)
                        box.prop(scene, f"{asset_name}_noise_distance", text="Noise distance", slider=True)
                        box.prop(scene, f"{asset_name}_noise_scale", text="Noise scale", slider=True)
                        box.prop(scene, f"{asset_name}_noise_shape", text="Noise radius", slider=True)

                        box.prop(scene, f"{asset_name}_curl", text="Curl", slider=True)
                        box.prop(scene, f"{asset_name}_curl_guide_distance", text="Curl guide distance", slider=True)
                        box.prop(scene, f"{asset_name}_curl_radius", text="Curl radius", slider=True)
                        box.prop(scene, f"{asset_name}_curl_frequency", text="Curl frequency", slider=True)

                        box.prop(scene, f"{asset_name}_holes", text="Bald holes", slider=True)
                        box.prop(scene, f"{asset_name}_holes_scale", text="Holes scale", slider=True)


                        # Generate cards operator
                        if not getattr(scene, f"{asset_name}_cards_generated",False):
                            op_gen = box.operator("mpfb.generate_hair_cards_operator", text="Convert to cards")
                            op_gen.hair_asset =asset_name
                            op_gen.card_asset=f"{asset_name}_cards"

                        # Cards editing
                        if getattr(scene, f"{asset_name}_cards_generated",False):
                            box.label(text="Hair cards:")

                            # Settings for eventual generated cards placement
                            if getattr(scene, f"{asset_name}_cards_scale",False):
                                box.prop(scene, f"{asset_name}_cards_scale", text="Scale of cards", slider=True)
                                box.prop(scene, f"{asset_name}_cards_density", text="Card density", slider=True)
                                box.prop(scene, f"{asset_name}_cards_placement", text="Seed for deleting random cards. No efect when density is 1.", slider=True)

                            # Card baking settings
                            box.label(text="Warning: baking process is slow and might crash blender")
                            box.prop(scene, f"{asset_name}_cards_glossy", text="Bake as glossy(better in hi res), or diffuse(fater and more stable)?")
                            box.prop(scene, f"{asset_name}_cards_samples", text="Render samples used in baking", slider=True)
                            box.prop(scene, f"{asset_name}_cards_resolution", text="Resolution of baked texture (Idealy power of 2 values)", slider=True)
                            box.prop(scene, f"{asset_name}_cards_texture_dst", text="Export Save Path")
                            op_bake = box.operator("mpfb.bake_hair_operator", text="Bake cards")
                            op_bake.hair_asset =asset_name
                            op_bake.card_asset=f"{asset_name}_cards"

                    op_del = box.operator("mpfb.delete_hair_operator", text="Delete hair")
                    op_del.hair_asset =asset_name



    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        basemesh = self.get_basemesh(context)
        _LOG.debug("Basemesh", basemesh)
        if basemesh is None:
            layout.label(text="No Basemesh selected")
            return

        layout = self.layout
        scene = context.scene

        has_hair = False
        has_key = HAIR_PROPERTIES.has_key("hair_setup", entity_reference=basemesh)
        if has_key:
            has_hair = HAIR_PROPERTIES.get_value("hair_setup", False, entity_reference=basemesh)
        _LOG.debug("has key, has hair", (has_key, has_hair))

        if has_hair:
            self._hair_panel(basemesh, layout)
            self._fur_panel(basemesh, layout)
        else:
            self._setup_hair(layout)



ClassManager.add_class(MPFB_PT_Hair_Editor_Panel)