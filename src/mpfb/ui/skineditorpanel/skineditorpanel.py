# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  UI panel for material editor
# ------------------------------------------------------------------------------
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.skineditorservices import SkinEditorService
from mpfb.ui.abstractpanel import Abstract_Panel
import bpy,os, json

_LOG = LogService.get_logger("ui.skineditorpanel")


_LOC = os.path.dirname(__file__)
MATERIAL_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MATERIAL_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MATERIAL_PROPERTIES_DIR, prefix="SKE_")


class MPFB_PT_Skin_Editor_Panel(Abstract_Panel):
    bl_label = "Skin Editor"
    bl_category = UiService.get_value("SKINEDITORCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    #TODO: add base texture normal influence
    #TODO: REAPLY MATERIAL FOR EDITING AND REBAKE

    # Initial box with operator for creating material
    def _create_modular_material(self, scene, layout):
        box = layout.box()
        box.label(text="Create modular and editable skin material")

        MATERIAL_PROPERTIES.draw_properties(scene, box, ["material_complexity"])

        op = box.operator("mpfb.create_modular_material")
        op.material_complexity = MATERIAL_PROPERTIES.get_value("material_complexity", entity_reference=scene)


    # Interface for editing material
    def _display_textures(self, scene, layout):
        """Displays texture information boxes in UI panel."""

        textures_data = scene.get("textures_data", {})
        all_textures = textures_data.get("albedo", []) + textures_data.get("normal", [])
        alternative_texture_paths = scene.get("alternative_texture_paths", {})

        # Group textures to drawers
        drawers = {}
        for tex in all_textures:
            drawer_name = tex.get("drawer", "others")
            if drawer_name not in drawers:
                drawers[drawer_name] = {}

            # Join normal and diffuse textures by box attribute
            box_name = tex.get("box", "Default")
            if box_name not in drawers[drawer_name]:
                drawers[drawer_name][box_name] = []

            drawers[drawer_name][box_name].append(tex)
        # Add tattoo and freckles drawer
        drawers["tattoos"] = {}
        drawers["freckles"] = {}


        # Show drawers
        for drawer_name, boxes in drawers.items():

            col = layout.column()
            is_open = scene.get(f"drawer_open_{drawer_name}", False)

            # Show/hide button
            icon = 'TRIA_DOWN' if is_open else 'TRIA_RIGHT'
            col.prop(scene, f'["drawer_open_{drawer_name}"]', text=drawer_name, emboss=True, toggle=False, icon=icon)


            if is_open:
                # Tattoo drawer
                if drawer_name == "tattoos":
                    box_tattoo = col.box()
                    if(not scene.freckles_editing):
                        if(not scene.tattoos_editing):
                            box_tattoo.label(text="Create tattoo")
                            box_tattoo.prop(scene, "tattoo_texture_path", text="Texture file")
                            box_tattoo.prop(scene, "tattoo_color_influence", text="Color influence")
                            op = box_tattoo.operator("mpfb.add_tattoo_texture_operator", text="Add tattoo texture")
                            op.material_complexity = MATERIAL_PROPERTIES.get_value("material_complexity", entity_reference=scene)
                        box_tattoo.prop(scene, "tattoo_texture_destination", text="Save destination")
                        op = box_tattoo.operator("mpfb.save_tattoo_texture_operator", text="Save tattoo")
                    else:
                        box_tattoo.label(text="Save freckles before creating tattoo.")

                    for prop in scene.bl_rna.properties:
                        if prop.identifier.startswith("tattoo_influence_"):
                            tattoo_name = prop.identifier.replace("tattoo_influence_", "")
                            box = col.box()
                            box.label(text=f"Tattoo Influence: {tattoo_name}")
                            box.prop(scene, prop.identifier, text="Influence", slider=True)
                            op = box.operator("mpfb.remove_tattoo_texture_operator", text="Remove tattoo")
                            op.tattoo_name =tattoo_name
                    continue

                # Freckles drawer
                if drawer_name == "freckles":
                    if(not scene.tattoos_editing):
                        box_freckles = col.box()
                        if(not scene.freckles_applied):
                            box_freckles.label(text="Create freckles")
                            op = box_freckles.operator("mpfb.add_freckles_texture_operator", text="Add freckles texture")
                            op.material_complexity = MATERIAL_PROPERTIES.get_value("material_complexity", entity_reference=scene)

                        if(scene.freckles_applied):
                            if(scene.freckles_editing):
                                box_freckles.label(text="Brush settings:")
                                box_freckles.prop(scene, "freckles_color", text="Color")
                                box_freckles.prop(scene, "voronoi_size", text="Size", slider=True)
                                box_freckles.prop(scene, "voronoi_intensity", text="Distance", slider=True)
                            else:
                                op = box_freckles.operator("mpfb.add_freckles_texture_operator", text="Edit freckles")
                                op.material_complexity = MATERIAL_PROPERTIES.get_value("material_complexity", entity_reference=scene)

                        box_freckles.prop(scene, "freckles_texture_destination", text="Save destination")
                        op = box_freckles.operator("mpfb.save_freckles_texture_operator", text="Save freckles")

                        if(scene.freckles_applied):
                            op = box_freckles.operator("mpfb.remove_freckles_texture_operator", text="Remove freckles")
                    else:
                        box_freckles = col.box()
                        box_freckles.label(text="Save your tattoo before editing freckles")
                    continue


                # Editing textures and their influences for each category
                for box_name, tex_list in boxes.items():
                    box = col.box()
                    box.label(text=box_name)

                    if box_name == 'base':
                        box.prop(scene, "multiply_color", text="Skin color")
                        box.prop(scene, "multiply_factor", text="Color influence", slider=True)
                        box.prop(scene, "gamma_value", text="Gamma Correction", slider=True)

                    for tex in tex_list:
                        tex_label = tex.get("label", "")
                        display_name = "Normal map" if tex_label.endswith("_norm") else "Texture"

                        # Texture picker
                        alt_prop_name = f"alt_texture_{tex.get('label', '').replace(' ', '_')}"
                        if hasattr(scene, alt_prop_name):
                            box.prop(scene, alt_prop_name, text=display_name)


                        # Texture influence slider
                        tex_name = os.path.basename(tex.get("label", "N/A"))
                        mat = bpy.context.object.active_material
                        if mat and mat.node_tree:
                            nodes = mat.node_tree.nodes
                            texture_node = next((n for n in nodes if n.type == 'TEX_IMAGE' and n.label == tex_name), None)
                            mix_rgb_node = SkinEditorService.find_next_mix_rgb_node(texture_node)

                            if mix_rgb_node:
                                prop_name = f"mix_factor_{tex_name}"
                                box.prop(scene, prop_name, text="Influence", slider=True)

    # Box with bake settings and operators
    def _bake_modular_material(self, scene, layout):
        box = layout.box()
        box.label(text="Bake the material for export")
        MATERIAL_PROPERTIES.draw_properties(scene, box, ["texture_resolution"])


        box.prop(scene, "bake_color", text="Bake skin color")
        box.prop(scene, "bake_muscles", text="Bake muscles")
        box.prop(scene, "bake_wrinkles", text="Bake wrinkles")
        box.prop(scene, "bake_tattoos", text="Bake tattoos")
        box.prop(scene, "bake_freckles", text="Bake freckles")
        box.prop(scene, "bake_others", text="Bake others")

        box.label(text="WARNING: Save your project before baking. Baking might cause blender to crash especially for high-res textures.")
        box.prop(scene, "bake_at_once", text="Bake at once")
        box.prop(scene, "bake_with_gpu", text="Bake with GPU")
        box.prop(scene, "bake_texture_destination", text="Save destination")

        if(scene.bake_at_once):
            # bake material
            op = box.operator("mpfb.bake_material_operator")
            op.texture_resolution = MATERIAL_PROPERTIES.get_value("texture_resolution", entity_reference=scene)
            op.baking_type = "both"
        if(not scene.bake_at_once):
            # bake diffuse
            if(not scene.diffuse_baked):
                op = box.operator("mpfb.bake_material_operator",text="Bake diffuse textures")
                op.texture_resolution = MATERIAL_PROPERTIES.get_value("texture_resolution", entity_reference=scene)
                op.baking_type = "diffuse"
            else:
                box.label(text="Diffuse textures baked succesfully!")
            #bake normal
            if(not scene.normal_baked):
                op = box.operator("mpfb.bake_material_operator",text="Bake normal textures")
                op.texture_resolution = MATERIAL_PROPERTIES.get_value("texture_resolution", entity_reference=scene)
                op.baking_type = "normal"
            else:
                box.label(text="Normal textures baked succesfully!")


    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._create_modular_material(scene, layout)

        # Show texture editor only after material is created
        if scene.get("textures_loaded", False):
            self._display_textures(scene, layout)
            if(not scene.material_baked):
                self._bake_modular_material(scene, layout)

ClassManager.add_class(MPFB_PT_Skin_Editor_Panel)