# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025  - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  UI panel for hair editor module
# ------------------------------------------------------------------------------

from ... import ClassManager
from ...services.logservice import LogService
from ...services.uiservice import UiService
from ...services.objectservice import ObjectService
from ...services.materialservice import MaterialService
from ...services.haireditorservices import HairEditorService
from ...ui.abstractpanel import Abstract_Panel
from .hairproperties import (get_light_mode, get_light_strength,
                             HAIR_PROPERTIES, FUR_PROPERTIES,
                             DYNAMIC_HAIR_PROPS_DEFINITIONS,
                             DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS, DYNAMIC_FUR_PROPS_DEFINITIONS,
                             DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS,
                             get_cards_flag,
                             has_cards_generator, get_cards_mode, get_cards_selection_method,
                             get_bake_target, resolve_body_surface, body_has_material,
                             resolve_custom_surface, CARDS_OBJECT_SUFFIX)
from . import cardgenerators as cg
from . import bodyoverlay
from .operators import toggle_section_operator

import bpy

_LOG = LogService.get_logger("ui.haireditorpanel")
#_LOG.set_level(LogService.DEBUG)

_HAIR_PICKERS = ["hair_assets", "facial_assets", "eyebrow_assets", "other_assets"]

# Baked whether they are ticked or not, for the modes where the end-on cutoff needs them.
_SHELL_FORCED_MAPS = ("cards_bake_root_tip", "cards_bake_side_on")


def _label(name):
    return str(name).replace("_", " ").capitalize()

# Grooming sliders grouped by the geometry nodes modifier they drive (first element of the DYNAMIC_*_PROPS_DEFINITIONS entries).
# This list only sets the order and names of the groups. Section keys avoid "shape", which the card shape section uses.
_GROOM_GROUPS = [
    ("Set Hair Curve Profile", "strands", "Strands"),
    ("Frizz Hair Curves", "frizz", "Frizz"),
    ("Roll Hair Curves", "roll", "Roll"),
    ("Clump Hair Curves", "clump", "Clump"),
    ("Hair Curves Noise", "noise", "Noise"),
    ("Curl Hair Curves", "curl", "Curl"),
    ]


class _Sink:
    """Returned by _section instead of the box when the section is folded - it discards every draw call."""

    def __getattr__(self, _name):
        return self._ignore

    def _ignore(self, *_args, **_kwargs):
        return self


class MPFB_PT_Hair_Editor_Panel(Abstract_Panel):
    bl_label = "Hair Editor"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 80

    @classmethod
    def poll(cls, context):
        """Only show up once there is a character to put hair on (active object is a basemesh or has one amongst relatives)."""
        if not context.active_object:
            return False
        return ObjectService.find_object_of_type_amongst_nearest_relatives(
            context.active_object, "Basemesh") is not None

    def _material_properties(self, basemesh, layout, asset_name, properties, definitions, is_fur):
        body = self._section(layout, basemesh, properties, asset_name, "colour", "Colour")

        # The fur shader can be driven either by a texture or by the two colors, never by both.
        uses_texture = False
        if is_fur:
            uses_texture = properties.get_value(f"{asset_name}_use_texture", False, entity_reference=basemesh)

        for name in definitions:
            if uses_texture and name in ["color1", "color2"]:
                continue
            properties.draw_properties(basemesh, body, [f"{asset_name}_{name}"], text=_label(name))

    def _shape_properties(self, basemesh, layout, asset_name, properties, definitions):
        """The grooming sliders, one foldable section per geometry nodes modifier they drive."""
        grouped = {}
        for name, definition in definitions.items():
            grouped.setdefault(definition[0], []).append(name)

        def draw(body, names):
            for name in names:
                properties.draw_properties(basemesh, body, [f"{asset_name}_{name}"],
                                            text=_label(name), slider=True)

        for modifier, key, title in _GROOM_GROUPS:
            names = grouped.pop(modifier, None)
            if names:
                draw(self._section(layout, basemesh, properties, asset_name, key, title), names)

        # Sliders of modifiers not listed in _GROOM_GROUPS
        leftovers = [name for names in grouped.values() for name in names]
        if leftovers:
            draw(self._section(layout, basemesh, properties, asset_name, "groom_other", "Other"),
                 leftovers)

    def _flag(self, layout, basemesh, properties, asset_name, setting, text, default=False,
              is_fur=False):
        """Draw a bake setting as a checkbox which does not push an undo step (operator instead of prop())."""
        value = bool(properties.get_value(f"{asset_name}_{setting}", default,
                                          entity_reference=basemesh))
        operator = layout.operator("mpfb.toggle_bake_flag", text=text, emboss=False,
                                   icon='CHECKBOX_HLT' if value else 'CHECKBOX_DEHLT')
        operator.hair_asset = asset_name
        operator.setting = setting
        operator.is_fur = is_fur
        operator.default_value = default
        return value

    def _draw_cards_props(self, basemesh, layout, asset_name, properties, names):
        # Not all of these are numeric, so no slider=True
        for name in names:
            properties.draw_properties(basemesh, layout, [f"{asset_name}_{name}"], text=_label(name.replace("cards_", "")))

    def _strand_count(self, basemesh, asset_name):
        """How many strands the asset has, or None if unknown. Read from the evaluated object, as modifiers change the count."""
        hair_obj = None
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == asset_name:
                hair_obj = child
                break
        if hair_obj is None:
            return None
        try:
            evaluated = hair_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            return len(evaluated.data.curves)
        except Exception:
            return None

    def _card_count_estimate(self, basemesh, layout, asset_name, properties, mode):
        """Roughly how many cards the current settings will produce."""
        if mode in cg.CLUSTER_MODES:
            count = properties.get_value(f"{asset_name}_cards_cluster_count", 40, entity_reference=basemesh)
            layout.label(text=f"~ {int(count)} cards", icon='INFO')
            return
        if mode not in cg.STRAND_BASED_MODES:
            return

        strands = self._strand_count(basemesh, asset_name)
        if not strands:
            return
        density = properties.get_value(f"{asset_name}_cards_density", 0.01, entity_reference=basemesh)
        kept = max(1, int(round(strands * density)))
        if mode == cg.CARDS_MODE_TILES:
            segments = properties.get_value(f"{asset_name}_cards_segments", 8, entity_reference=basemesh)
            layout.label(text=f"~ {kept} strands x {int(segments)} = {kept * int(segments)} cards", icon='INFO')
        else:
            layout.label(text=f"~ {kept} cards (of {strands} strands)", icon='INFO')

    def _placement_section(self, basemesh, layout, asset_name, properties, mode):
        box = self._section(layout, basemesh, properties, asset_name, "placement", "Placement")

        if mode in cg.STRAND_BASED_MODES:
            self._draw_cards_props(basemesh, box, asset_name, properties, ["cards_selection_method", "cards_density", "cards_seed"])
            box.label(text="Selection method applies on Regenerate", icon='FILE_REFRESH')
            selection_method = get_cards_selection_method(properties, basemesh, asset_name)
            if selection_method == cg.SELECTION_METHOD_EVERY_NTH:
                self._draw_cards_props(basemesh, box, asset_name, properties, ["cards_jitter"])
            elif selection_method == cg.SELECTION_METHOD_POISSON:
                self._draw_cards_props(basemesh, box, asset_name, properties, ["cards_poisson_radius"])
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_vertex_group", "cards_cluster_strength", "cards_offset"])
        elif mode == cg.CARDS_MODE_SHELL:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_shell_volume_density", "cards_seed"])
            box.label(text="Volume density is how finely the hair is sampled,", icon='INFO')
            box.label(text="not a card count - the shell is always one hull.")
        elif mode in cg.CLUSTER_MODES:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_cluster_count", "cards_cluster_min_strands", "cards_cluster_seed"])
            if mode == cg.CARDS_MODE_CLUSTER_RIBBON:
                self._draw_cards_props(basemesh, box, asset_name, properties, ["cards_cluster_samples"])
            box.label(text="Clustering happens on Regenerate", icon='FILE_REFRESH')

        self._card_count_estimate(basemesh, box, asset_name, properties, mode)

    def _card_shape_section(self, basemesh, layout, asset_name, properties, mode):
        box = self._section(layout, basemesh, properties, asset_name, "shape", "Card shape")

        if mode == cg.CARDS_MODE_TILES:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_segments", "cards_scale", "cards_width", "cards_length",
                                     "cards_width_random", "cards_length_random", "cards_tilt_random"])
        elif mode == cg.CARDS_MODE_RIBBON:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_profile_steps", "cards_width", "cards_extend_tip",
                                     "cards_taper", "cards_twist"])
        elif mode == cg.CARDS_MODE_CLUSTER_RIBBON:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_profile_steps", "cards_width", "cards_extend_tip",
                                     "cards_cluster_width_match",
                                     "cards_taper", "cards_twist", "cards_offset"])
        elif mode == cg.CARDS_MODE_SHELL:
            self._draw_cards_props(basemesh, box, asset_name, properties,
                                    ["cards_shell_samples", "cards_shell_radius", "cards_shell_hug",
                                     "cards_shell_voxel_size", "cards_shell_adaptivity", "cards_shell_smooth"])
            box.label(text="Lower radius + more samples + hug = tighter shell", icon='INFO')
        elif mode == cg.CARDS_MODE_CLUSTER_BOX:
            box.label(text="Shape follows each bundle's own PCA axes.", icon='INFO')

    def _section(self, layout, basemesh, properties, asset_name, section, title,
                 default_open=False):
        """A framed, foldable sub-section. Returns the layout to draw into, or a sink when folded.

        Header is a box with a row instead of UILayout.panel(), which paints a second background inside the box.
        Fold state is kept in toggle_section_operator, not in a property, to avoid undo steps.
        """
        box = layout.box()
        unfolded = toggle_section_operator.is_open(asset_name, section, default_open)
        header = box.row(align=True)
        header.alignment = 'LEFT'
        header.scale_y = 0.85
        operator = header.operator("mpfb.toggle_hair_section", text=title, emboss=False,
                                    icon='TRIA_DOWN' if unfolded else 'TRIA_RIGHT')
        operator.hair_asset = asset_name
        operator.section = section
        operator.default_open = default_open
        return box if unfolded else _Sink()

    def _appearance_section(self, basemesh, layout, asset_name, target, properties):
        """Shader knobs for an asset which has already been baked, drawn straight from the material nodes."""
        node_tree = self._baked_node_tree(basemesh, asset_name, target, properties)
        if node_tree is None:
            return
        shader = bodyoverlay.find_tagged_node(node_tree, bodyoverlay.ROLE_SHADER, asset_name)
        ramp = bodyoverlay.find_tagged_node(node_tree, bodyoverlay.ROLE_ALPHA_RAMP, asset_name)
        if shader is None and ramp is None:
            return

        body = self._section(layout, basemesh, properties, asset_name, "appearance", "Appearance")

        if ramp is not None and hasattr(body, "template_color_ramp"):
            body.label(text="How much hair survives:", icon='INFO')
            body.template_color_ramp(ramp, "color_ramp", expand=True)
            body.label(text="Drag the white stop left to make thin, half-covered")
            body.label(text="texels solid; drag the black stop right")
            body.label(text="to make them disappear.")

        side_on = bodyoverlay.find_tagged_node(node_tree, bodyoverlay.ROLE_SIDE_ON_CUTOFF,
                                               asset_name)
        if side_on is not None:
            body.separator()
            body.prop(side_on.inputs[0], "default_value",
                      text="Hide hair caught end-on", slider=True)
            body.label(text="Hides the parts where the ray looked", icon='INFO')
            body.label(text="along a strand instead of across it.")
            body.label(text="0 changes nothing.")
            # Only exists when the root/tip map was baked
            tips = bodyoverlay.find_tagged_node(node_tree, bodyoverlay.ROLE_SIDE_ON_TIPS,
                                                asset_name)
            if tips is not None:
                body.prop(tips.inputs[0], "default_value",
                          text="Also target the strand tips", slider=True)
                body.label(text="The patches sit at the ends of the hair,", icon='INFO')
                body.label(text="so a texel near the tips is a likelier")
                body.label(text="candidate than one mid-strand.")
            else:
                body.label(text="Bake the root/tip map too and this can", icon='INFO')
                body.label(text="weigh in where along the strand it is.")

        cutoff = bodyoverlay.find_tagged_node(node_tree, bodyoverlay.ROLE_DEPTH_CUTOFF, asset_name)
        if cutoff is not None:
            body.separator()
            body.prop(cutoff.inputs[1], "default_value", text="Hide hair found closer than",
                      slider=True)
            body.label(text="Uses the depth map. Hides the places", icon='INFO')
            body.label(text="where the surface sits on a strand.")

        if shader is not None:
            for socket_name in ("Metallic", "Roughness", "Anisotropic"):
                socket = shader.inputs.get(socket_name)
                # Linked sockets are driven by baked maps (roughness by root/tip, anisotropy by flow)
                if socket is not None and not socket.is_linked:
                    body.prop(socket, "default_value", text=socket_name)

    def _baked_node_tree(self, basemesh, asset_name, target, properties):
        """The node tree holding this asset's baked shader, wherever it ended up."""
        if target == cg.BAKE_TARGET_BODY_DIRECT:
            surface_obj = resolve_body_surface(basemesh)
            material = MaterialService.get_material(surface_obj) if surface_obj else None
        elif target == cg.BAKE_TARGET_CUSTOM:
            # The baked material went onto the user mesh, no card object
            surface_obj = resolve_custom_surface(properties, basemesh, asset_name)
            material = MaterialService.get_material(surface_obj) if surface_obj else None
        else:
            card_name = f"{asset_name}{CARDS_OBJECT_SUFFIX}"
            card_obj = next((child for child in ObjectService.get_list_of_children(basemesh)
                             if child.name == card_name), None)
            material = MaterialService.get_material(card_obj) if card_obj else None
        return material.node_tree if material and material.use_nodes else None

    def _bake_section(self, basemesh, layout, asset_name, properties, kind, mode, target):
        # Bake settings are drawn with _flag so that ticking one does not push an undo step
        is_fur = kind == "fur"
        box = layout.box()
        box.label(text="Baking is slow and might crash blender", icon='ERROR')

        atlas = self._section(box, basemesh, properties, asset_name, "texture", "Texture")
        # Atlas sharing needs several cards. Shell is one piece and body targets use the existing UV layout.
        if target == cg.BAKE_TARGET_CARDS and mode != cg.CARDS_MODE_SHELL:
            if self._flag(atlas, basemesh, properties, asset_name, "cards_atlas_enabled",
                          "Share textures between cards", is_fur=is_fur):
                sharing = atlas.box()
                properties.draw_properties(basemesh, sharing, [f"{asset_name}_cards_atlas_fraction"],
                                            text="Atlas fraction", slider=True)
                sharing.label(text="Lower = fewer baked variants,", icon='INFO')
                sharing.label(text="more resolution each, more repetition.")
                sharing.label(text="Variants are taken from the thin edge of", icon='INFO')
                sharing.label(text="the asset, so a shared texture already")
                sharing.label(text="ends in tips rather than in a straight cut.")
            if self._flag(atlas, basemesh, properties, asset_name, "cards_analytic_uvs",
                          "Pack UVs tighter", default=True, is_fur=is_fur):
                atlas.label(text="Tighter UV packing uses the texture space", icon='INFO')
                atlas.label(text="better, but can slightly deform the hair.")
        elif target == cg.BAKE_TARGET_CUSTOM:
            atlas.label(text="Baked 1:1 into the mesh's own UV layout,", icon='INFO')
            atlas.label(text="nothing is unwrapped or repacked.")
        elif target == cg.BAKE_TARGET_BODY_DIRECT:
            atlas.label(text="Baked 1:1 into the body's own UV layout.", icon='INFO')
        else:
            atlas.label(text="Baked into the shell's copy of the body UVs,", icon='INFO')
            atlas.label(text="rescaled so the patch uses the whole texture.")
        self._draw_cards_props(basemesh, atlas, asset_name, properties, ["cards_resolution"])

        if target == cg.BAKE_TARGET_BODY_SHELL:
            if self._flag(atlas, basemesh, properties, asset_name, "cards_body_edge_fade",
                          "Fade out at the edges", is_fur=is_fur):
                self._draw_cards_props(basemesh, atlas, asset_name, properties,
                                        ["cards_body_edge_fade_width"])
                atlas.label(text="Gradually thins the alpha towards the edge", icon='INFO')
                atlas.label(text="of the shell, so it doesn't end in a hard line.")
                dilation = int(properties.get_value(f"{asset_name}_cards_body_face_dilation", 1,
                                                    entity_reference=basemesh))
                width = int(properties.get_value(f"{asset_name}_cards_body_edge_fade_width", 2,
                                                 entity_reference=basemesh))
                if width > dilation:
                    # Dilation rings are the natural fade zone, a wider fade thins the area hair grows from
                    atlas.label(text=f"Fade is wider than Face dilation ({dilation}), so it", icon='ERROR')
                    atlas.label(text="potentially thins the fur itself,")
                    atlas.label(text="not only the added border.")

        capture = self._section(box, basemesh, properties, asset_name, "capture", "Capture")
        self._flag(capture, basemesh, properties, asset_name, "cards_glossy", "Glossy",
                   default=True, is_fur=is_fur)
        self._draw_cards_props(basemesh, capture, asset_name, properties, ["cards_samples"])
        if target in (cg.BAKE_TARGET_CARDS, cg.BAKE_TARGET_CUSTOM, cg.BAKE_TARGET_BODY_SHELL):
            if self._flag(capture, basemesh, properties, asset_name, "cards_double_sided",
                          "Capture both sides", is_fur=is_fur):
                capture.label(text="Bakes a second time from the other side and", icon='INFO')
                capture.label(text="mixes both by how much hair each one saw.")
                capture.label(text="Doubles the colour bake time.")
                if target == cg.BAKE_TARGET_BODY_SHELL:
                    capture.label(text="Pass starts just outside the skin")
                    capture.label(text="and looks outward, so the inner side")
                    capture.label(text="of the hair is captured too.")
                else:
                    capture.label(text="Meant for the cluster modes: on tiles and")
                    capture.label(text="ribbons it can double-count hair that")
                    capture.label(text="neighbouring cards already carry.")

        if target in cg.BODY_BAKE_TARGETS:
            # Forced on for body targets, otherwise rays pass through the body and pick up hair on the far side.
            properties.draw_properties(basemesh, capture, [f"{asset_name}_cards_ray_range"],
                                        text="Ray range / depth scale")
            if target == cg.BAKE_TARGET_BODY_SHELL:
                capture.label(text="Raised automatically if it is too short to")
                capture.label(text="reach through the hair to the skin.")
        else:
            limit_rays = self._flag(capture, basemesh, properties, asset_name,
                                    "cards_limit_ray_range", "Limit ray range", is_fur=is_fur)
            wants_depth = properties.get_value(f"{asset_name}_cards_bake_depth", False, entity_reference=basemesh)
            if limit_rays or wants_depth:
                properties.draw_properties(basemesh, capture, [f"{asset_name}_cards_ray_range"],
                                            text="Ray range / depth scale")

        maps = self._section(box, basemesh, properties, asset_name, "maps", "Maps")
        # The volume shell always bakes side-on and root/tip (the end-on cutoff needs them). Same condition as in the bake.
        # Shown as a note instead of ticked boxes, because the bake overrides the properties without changing them.
        forced = (get_cards_mode(properties, basemesh, asset_name) == cg.CARDS_MODE_SHELL
                  and get_bake_target(properties, basemesh, asset_name) != cg.BAKE_TARGET_BODY_DIRECT)
        optional = ["cards_bake_ao", "cards_bake_root_tip", "cards_bake_normal",
                    "cards_bake_flow", "cards_bake_depth", "cards_bake_side_on"]
        if forced:
            optional = [name for name in optional if name not in _SHELL_FORCED_MAPS]
            maps.label(text="Side on and Root tip are always baked", icon='INFO')
            maps.label(text="for the volume shell - they are what the")
            maps.label(text="end-on cutoff in Appearance is built from.")
        for start in range(0, len(optional), 3):
            maps_row = maps.row(align=True)
            for name in optional[start:start + 3]:
                self._flag(maps_row, basemesh, properties, asset_name, name,
                           _label(name.replace("cards_bake_", "")), is_fur=is_fur)
        if not forced and properties.get_value(f"{asset_name}_cards_bake_side_on", False,
                                               entity_reference=basemesh):
            maps.label(text="Side on says how each bit of hair was", icon='INFO')
            maps.label(text="caught: white across the strand, black")
            maps.label(text="down its length. With Root tip it adds the")
            maps.label(text="end-on cutoff to Appearance.")
        if properties.get_value(f"{asset_name}_cards_bake_normal", False, entity_reference=basemesh):
            maps.label(text="Normal map is OBJECT space, not tangent space", icon='ERROR')
            maps.label(text="Set the engine's normal map node to object space,")
            maps.label(text="or it will light the hair wrongly.")

        lights = self._section(box, basemesh, properties, asset_name, "lights", "Lights")
        # A diffuse bake is plain albedo (direct and indirect passes off), so lighting has no effect on it
        if not properties.get_value(f"{asset_name}_cards_glossy", True, entity_reference=basemesh):
            lights.label(text="The diffuse pass bakes unlit albedo, so", icon='INFO')
            lights.label(text="none of the lighting applies to it. Turn")
            lights.label(text="on Glossy in Capture to light the bake.")
            light_mode = None
        else:
            properties.draw_properties(basemesh, lights, [f"{asset_name}_cards_light_mode"],
                                        text="Lighting")
            light_mode = get_light_mode(properties, basemesh, asset_name)
        if light_mode is None:
            pass
        elif light_mode == cg.LIGHT_MODE_FIXED:
            lights.label(text="Two lights at a fixed offset from the", icon='INFO')
            lights.label(text="character. They cast shadows.")
        elif light_mode == cg.LIGHT_MODE_BBOX:
            lights.label(text="Two lights placed from the hair's own", icon='INFO')
            lights.label(text="bounding box. They cast shadows.")
        elif light_mode == cg.LIGHT_MODE_NO_SHADOW:
            lights.label(text="Like Bounding box, but without shadows:", icon='INFO')
            lights.label(text="highlights stay, no dark streaks.")
            lights.label(text="Bake the AO map for depth.")
        elif light_mode == cg.LIGHT_MODE_ACROSS_STRANDS:
            lights.label(text="Shadowless lights aimed across the", icon='INFO')
            lights.label(text="strands, from the asset's own root-to-tip")
            lights.label(text="directions. Strongest sheen band.")
        elif light_mode == cg.LIGHT_MODE_SCENE:
            scene_lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT'
                            and HairEditorService.is_rendered(obj, bpy.context.scene, bpy.context.view_layer)]
            lights.label(text="The lights and the world of the scene", icon='INFO')
            lights.label(text="are used as they are, no bake lights")
            lights.label(text="are added. Emissive meshes are hidden.")
            if scene_lights:
                lights.label(text=f"{len(scene_lights)} light(s) in the scene render")
            else:
                lights.label(text="No light in the scene is enabled for render,", icon='ERROR')
                lights.label(text="only the world will light the hair.")

        # The scene's own lights keep their own wattage - the strength slider only applies to the bake lights
        if light_mode is not None and light_mode != cg.LIGHT_MODE_SCENE:
            properties.draw_properties(basemesh, lights,
                                        [f"{asset_name}_cards_light_strength"],
                                        text="Light strength", slider=True)
            # Modes need different wattages, so the slider is a multiple of each mode's base energy
            strength = get_light_strength(properties, basemesh, asset_name)
            watts = cg.light_base_energy(light_mode) * strength
            lights.label(text=f"= {watts:.0f} W per light")
        # Only relevant while the lights cast shadows
        if light_mode in (cg.LIGHT_MODE_FIXED, cg.LIGHT_MODE_BBOX, cg.LIGHT_MODE_SCENE):
            self._flag(lights, basemesh, properties, asset_name, "cards_body_shadows",
                       "Body casts shadows", is_fur=is_fur)

        properties.draw_properties(basemesh, box, [f"{asset_name}_cards_texture_dst"], text="Destination")

        if target in cg.BODY_BAKE_TARGETS:
            label = "Bake onto body"
        elif target == cg.BAKE_TARGET_CUSTOM:
            label = "Bake onto mesh"
        else:
            label = "Bake cards"
        operator = box.operator("mpfb.bake_hair_operator", text=label)
        operator.hair_asset = asset_name
        operator.is_fur = (kind == "fur")

    def _body_shell_rig_note(self, basemesh, layout, asset_name):
        """Note about how this shell relates to the character's rig.

        The shell inherits bone weights from the body when it is cut, so a shell cut before the rig was added has none.
        """
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
        # Looked up among this character's children, another character can have the same asset
        shell_name = f"{asset_name}{CARDS_OBJECT_SUFFIX}"
        shell_obj = next((child for child in ObjectService.get_list_of_children(basemesh)
                          if child.name == shell_name), None)

        if rig is None:
            layout.label(text="No rig on this character yet.", icon='INFO')
            layout.label(text="The shell follows the body either way, but it")
            layout.label(text="only gets bone weights for export if you")
            layout.label(text="Regenerate it after adding a rig.")
            return

        if not cg.body_shell_is_weighted_to(shell_obj, rig):
            layout.label(text="Built before the rig was added.", icon='ERROR')
            layout.label(text="It still follows the body, but it carries no")
            layout.label(text="bone weights - Regenerate to weight it.")

    def _body_shell_section(self, basemesh, layout, asset_name, properties):
        box = layout.box()
        box.label(text="Shell:")
        self._draw_cards_props(basemesh, box, asset_name, properties,
                                ["cards_body_height", "cards_body_normal_smooth"])
        box.label(text="Height is how far off the skin the shell floats.", icon='INFO')
        box.label(text="Smoothing keeps concave places from folding in.")
        self._draw_cards_props(basemesh, box, asset_name, properties, ["cards_body_face_dilation"])
        box.label(text="Face dilation applies on Regenerate", icon='FILE_REFRESH')

    def _custom_mesh_picker(self, basemesh, layout, asset_name, properties):
        """Let the user pick a mesh from the scene, and say why one will not do. Returns it or None.

        The property only stores a name, so the choice can go stale - the bake repeats these checks.
        """
        layout.label(text="Baked into the mesh's own UV layout.", icon='INFO')
        layout.prop_search(basemesh, f"{properties.dynamic_prefix}{asset_name}_cards_custom_mesh",
                           bpy.data, "objects", text="Mesh")

        chosen = properties.get_value(f"{asset_name}_cards_custom_mesh", "",
                                      entity_reference=basemesh)
        if not chosen:
            layout.label(text="Pick a mesh to bake onto.", icon='ERROR')
            return None

        surface = bpy.data.objects.get(chosen)
        if surface is None:
            layout.label(text="That object is no longer in the file.", icon='ERROR')
            return None
        if surface.type != 'MESH':
            layout.label(text=f"'{surface.name}' is not a mesh.", icon='ERROR')
            return None
        if surface in (basemesh, self._asset_object(basemesh, asset_name)):
            layout.label(text="Pick a mesh of your own - the body and", icon='ERROR')
            layout.label(text="the hair cannot bake onto themselves.")
            return None
        if not surface.data.uv_layers:
            layout.label(text=f"'{surface.name}' has no UV layout, and", icon='ERROR')
            layout.label(text="this target bakes into the mesh's own.")
            return None

        layout.label(text=f"{len(surface.data.polygons)} faces, "
                          f"{len(surface.data.uv_layers)} UV layer"
                          f"{'s' if len(surface.data.uv_layers) != 1 else ''}.")
        layout.label(text="Only the material is changed; geometry,")
        layout.label(text="UVs and modifiers are left alone.")
        return surface

    def _asset_object(self, basemesh, asset_name):
        """The hair/fur curves object of this asset, if it is still around."""
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == asset_name:
                return child
        return None

    def _body_target_notes(self, layout, target):
        layout.label(text="Made for fur, stubble and short hair.", icon='INFO')
        if target == cg.BAKE_TARGET_BODY_DIRECT:
            layout.label(text="This edits the skin material.", icon='ERROR')
            layout.label(text="Changing the skin afterwards drops the")
            layout.label(text="overlay - use Reapply overlay to restore it.")

    def _cards_section(self, basemesh, layout, asset_name, properties, kind):
        cards_are_generated = get_cards_flag(properties, basemesh, asset_name, kind, "generated")
        cards_are_baked = get_cards_flag(properties, basemesh, asset_name, kind, "baked")
        target = get_bake_target(properties, basemesh, asset_name)

        if cards_are_baked:
            box = layout.box()
            if target == cg.BAKE_TARGET_BODY_DIRECT:
                box.label(text="Baked onto the body's texture.")
                operator = box.operator("mpfb.reapply_fur_overlay_operator",
                                        text="Reapply overlay", icon='FILE_REFRESH')
                operator.hair_asset = asset_name
                operator.is_fur = (kind == "fur")
                box.label(text="Use this after regenerating the skin material.")
            else:
                box.label(text="Cards have been baked.")
            self._appearance_section(basemesh, box, asset_name, target, properties)
            # Body-texture target is a shader blended over the skin, there is no own texture to write alpha into
            if target != cg.BAKE_TARGET_BODY_DIRECT:
                node_tree = self._baked_node_tree(basemesh, asset_name, target, properties)
                if node_tree is not None and any(
                        bodyoverlay.find_tagged_node(node_tree, role, asset_name) is not None
                        for role in (bodyoverlay.ROLE_ALPHA_RAMP, bodyoverlay.ROLE_SIDE_ON_CUTOFF,
                                     bodyoverlay.ROLE_DEPTH_CUTOFF, bodyoverlay.ROLE_EDGE_FADE)):
                    box.separator()
                    box.label(text="Happy with the alpha above?", icon='INFO')
                    box.label(text="This writes it into the colour texture")
                    box.label(text="so the export is one file, and takes the")
                    box.label(text="controls away. Unbake to start over.")
                    operator = box.operator("mpfb.flatten_hair_alpha_operator",
                                            text="Bake alpha into the texture", icon='IMAGE_ALPHA')
                    operator.hair_asset = asset_name
                    operator.is_fur = (kind == "fur")
            operator = box.operator("mpfb.unbake_hair_operator", text="Unbake", icon='LOOP_BACK')
            operator.hair_asset = asset_name
            operator.is_fur = (kind == "fur")
            return

        # Target and mode pickers exist as soon as the asset is applied
        mode_box = layout.box()
        mode_box.label(text="Cards:")
        properties.draw_properties(basemesh, mode_box, [f"{asset_name}_cards_bake_target"], text="Target")

        if target == cg.BAKE_TARGET_BODY_DIRECT:
            # No geometry step, the bake goes straight onto the body UVs
            self._body_target_notes(mode_box, target)
            surface_obj = resolve_body_surface(basemesh)
            if not body_has_material(surface_obj):
                mode_box.label(text="Apply a skin material first.", icon='ERROR')
                mode_box.label(text="There is nothing to blend the hair over yet.")
                return
            self._bake_section(basemesh, mode_box, asset_name, properties, kind, None, target)
            return

        if target == cg.BAKE_TARGET_CUSTOM:
            # No geometry step and no mode, the bake writes into the user mesh UV layout
            surface = self._custom_mesh_picker(basemesh, mode_box, asset_name, properties)
            if surface is None:
                return
            self._bake_section(basemesh, mode_box, asset_name, properties, kind, None, target)
            return

        if target == cg.BAKE_TARGET_BODY_SHELL:
            self._body_target_notes(mode_box, target)
            if not cards_are_generated:
                operator = mode_box.operator("mpfb.generate_hair_cards_operator", text="Create body shell")
                operator.hair_asset = asset_name
                operator.is_fur = (kind == "fur")
                return
            self._body_shell_section(basemesh, mode_box, asset_name, properties)
            self._body_shell_rig_note(basemesh, mode_box, asset_name)
            operator = mode_box.operator("mpfb.regenerate_hair_cards_operator",
                                         text="Regenerate", icon='FILE_REFRESH')
            operator.hair_asset = asset_name
            operator.is_fur = (kind == "fur")
            self._bake_section(basemesh, mode_box, asset_name, properties, kind, None, target)
            return

        properties.draw_properties(basemesh, mode_box, [f"{asset_name}_cards_mode"], text="Mode")
        mode = get_cards_mode(properties, basemesh, asset_name)

        if not cards_are_generated:
            operator = mode_box.operator("mpfb.generate_hair_cards_operator", text="Convert to cards")
            operator.hair_asset = asset_name
            operator.is_fur = (kind == "fur")
            return

        mode_box.label(text="Mode applies on Regenerate", icon='FILE_REFRESH')

        # Cards computed in python (cluster boxes) have no live node group to edit
        if has_cards_generator(asset_name):
            self._placement_section(basemesh, mode_box, asset_name, properties, mode)
            self._card_shape_section(basemesh, mode_box, asset_name, properties, mode)
        elif mode in cg.CLUSTER_MODES:
            self._placement_section(basemesh, mode_box, asset_name, properties, mode)

        operator = mode_box.operator("mpfb.regenerate_hair_cards_operator", text="Regenerate", icon='FILE_REFRESH')
        operator.hair_asset = asset_name
        operator.is_fur = (kind == "fur")

        self._bake_section(basemesh, mode_box, asset_name, properties, kind, mode, target)


    def _asset_block(self, basemesh, layout, asset_name, is_fur):
        properties = FUR_PROPERTIES if is_fur else HAIR_PROPERTIES
        kind = "fur" if is_fur else "hair"
        shape_definitions = DYNAMIC_FUR_PROPS_DEFINITIONS if is_fur else DYNAMIC_HAIR_PROPS_DEFINITIONS
        material_definitions = DYNAMIC_FUR_MATERIAL_PROPS_DEFINITIONS if is_fur else DYNAMIC_HAIR_MATERIAL_PROPS_DEFINITIONS

        toggle_prop = f"{asset_name}_{kind}_asset_open"
        properties.draw_properties(basemesh, layout, [toggle_prop])
        if not properties.get_value(toggle_prop, False, entity_reference=basemesh):
            return

        box = layout.box()

        # Once the hair has been baked into a texture, editing the curves has no visible effect
        if not get_cards_flag(properties, basemesh, asset_name, kind, "baked"):
            self._material_properties(basemesh, box, asset_name, properties, material_definitions, is_fur)
            self._shape_properties(basemesh, box, asset_name, properties, shape_definitions)

        self._cards_section(basemesh, box, asset_name, properties, kind)

        operator = box.operator("mpfb.delete_hair_operator", text="Delete hair", icon='TRASH')
        operator.hair_asset = asset_name
        operator.is_fur = is_fur

    def _hair_panel(self, basemesh, layout):
        box = layout.box()
        box.label(text="Hair assets:")

        for picker in _HAIR_PICKERS:
            HAIR_PROPERTIES.draw_properties(basemesh, box, [picker])
            operator = box.operator("mpfb.apply_hair_operator")
            operator.hair_asset = HAIR_PROPERTIES.get_value(picker, entity_reference=basemesh)

        column = layout.column()
        for key in sorted(HAIR_PROPERTIES.get_keys(basemesh)):
            if str(key).endswith("_hair_asset_open"):
                self._asset_block(basemesh, column, str(key).replace("_hair_asset_open", ""), is_fur=False)

    def _fur_panel(self, basemesh, layout):
        box = layout.box()
        box.label(text="Fur assets:")

        HAIR_PROPERTIES.draw_properties(basemesh, box, ["fur_assets"])
        operator = box.operator("mpfb.apply_fur_operator")
        operator.hair_asset = HAIR_PROPERTIES.get_value("fur_assets", entity_reference=basemesh)

        column = layout.column()
        for key in sorted(FUR_PROPERTIES.get_keys(basemesh)):
            if str(key).endswith("_fur_asset_open"):
                self._asset_block(basemesh, column, str(key).replace("_fur_asset_open", ""), is_fur=True)

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        basemesh = self.get_basemesh(context)

        # poll() guarantees this, this guard is for a redraw racing a deletion
        if not basemesh:
            return

        if not HairEditorService.is_hair_asset_installed():
            layout.label(text="Hair editor assets are not")
            layout.label(text="installed. Download from")
            layout.label(text="asset packs page.")
            return

        if HairEditorService.is_hair_pack_outdated():
            warning = layout.box()
            warning.label(text="Old hair editor asset pack", icon='ERROR')
            warning.label(text="Some features need the newer pack.")
            warning.label(text="Download the current version from")
            warning.label(text="the asset packs page.")

        self._hair_panel(basemesh, layout)

        if HairEditorService.is_fur_asset_installed():
            self._fur_panel(basemesh, layout)

ClassManager.add_class(MPFB_PT_Hair_Editor_Panel)
