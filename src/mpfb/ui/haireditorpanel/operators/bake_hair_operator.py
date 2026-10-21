# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025 - updated 21.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for baking hair asset onto a card asset as a texture
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from ....services.haireditorservices import HairEditorService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import (HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_OBJECT_SUFFIX,
                              CARDS_MODIFIER_NAME, set_cards_flag,
                              snapshot_cards_properties, remember_cards_settings,
                              get_bake_target, get_atlas_fraction, get_light_mode,
                              resolve_custom_surface, remember_custom_mesh_materials,
                              get_light_strength,
                              get_cards_mode,
                              resolve_body_surface,
                              body_surfaces_to_hide_behind, body_has_material)
from ....services import haircardservice as cg
from ....services.haircardservice import HairCardService
from ....services.hairoverlayservice import HairOverlayService
from ....services.hairbakeservice import HairBakeService, SHELL_CAPTURE_MARGIN, EXTRA_MAP_BUILDERS
from .bake_result_operator import (remember_bake_result, forget_bake_result, show_bake_result_popup,
                                   BAKE_FAILED, BAKE_CANCELLED, BAKE_ABANDONED, BAKE_WARNINGS)

import bpy
from mathutils import Vector

_LOG = LogService.get_logger("haireditorpanel.bake_hair_operator")

# Ray visibility settings which have to be off for the cards while the hair is baked
_RAY_VISIBILITY = ["visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"]

# Cycles settings which are forced while baking. Read defensively - names differ between blender versions
_CYCLES_BAKE_SETTINGS = {
    "max_bounces": 64,
    "diffuse_bounces": 64,
    "glossy_bounces": 64,
    "transmission_bounces": 64,
    "volume_bounces": 64,
    "transparent_max_bounces": 64,
    "transparent_min_bounces": 64,
    "use_denoising": True
    }

# Saving scene.render.bake settings so they can be restored after bake.
_BAKE_PASS_SETTINGS = ["use_pass_direct", "use_pass_indirect", "use_selected_to_active", "use_clear"]

# Still waiting background bakes are cleaned up if MPFB2 is disabled mid-bake
_PENDING_BAKES = {}


def abandon_pending_bakes():
    """Remove handlers and queued finish timers of still running bakes. Called from unregister()."""
    for abandon in list(_PENDING_BAKES.values()):
        try:
            abandon()
        except Exception as e:
            _LOG.error("Could not abandon a pending bake", e)
    _PENDING_BAKES.clear()


def _message_level(level):
    """report() takes a set like {'WARNING'}, the result keeps just the most severe one."""
    if 'ERROR' in level:
        return 'ERROR'
    if 'WARNING' in level:
        return 'WARNING'
    return 'INFO'


def _announce_background_result(basemesh_name, asset_name, status, messages):
    """Tell the user how a background bake ended. A clean bake only clears an older result."""
    if status is None:
        forget_bake_result(basemesh_name, asset_name)
        return
    remember_bake_result(basemesh_name, asset_name, status, messages)
    show_bake_result_popup(status, messages)


def _finish(state, bake_succeeded):
    """Everything that happens once the main bake call has finished (or failed/was cancelled)."""
    if not HairBakeService.state_is_alive(state):
        state["report"]({'WARNING'},
                        "The scene changed while the cards were baking, so the result was discarded")
        return False

    scene = state["scene"]
    basemesh = state["basemesh"]
    hair_obj = state["hair_obj"]
    live_card_obj = state["live_card_obj"]
    bake_target = state["bake_target"]
    card_material = state["card_material"]
    bake_image = state["bake_image"]
    asset_name = state["asset_name"]
    report = state["report"]

    bake_path = None
    extra_paths = {}
    success = False
    try:
        if bake_succeeded:
            try:
                HairBakeService.bake_coverage_into_alpha(state)
            except Exception as e:
                _LOG.error("Could not bake the hair coverage mask into the alpha channel", e)
                report({'WARNING'}, f"The alpha channel could not be baked: {e}")

            if state.get("double_sided"):
                try:
                    HairBakeService.bake_other_side(state)
                except Exception as e:
                    _LOG.error("Could not bake the far side of the cards; keeping the near one", e)
                    report({'WARNING'},
                           f"The second side failed, so only the near side was baked: {e}")

            HairBakeService.dilate_image_colour(bake_image)

            bake_path = HairBakeService.resolve_bake_path(asset_name, state["destination"])
            bake_image.filepath_raw = bake_path
            bake_image.file_format = 'PNG'
            bake_image.save()
            bake_image.filepath = bake_path
            bake_image.source = 'FILE'

            # Failure in optional maps bake must not throw the successful main pass away.
            try:
                extra_paths = HairBakeService.bake_extra_maps(state)
            except Exception as e:
                _LOG.error("Could not bake the extra maps; keeping the main texture", e)
                report({'WARNING'}, f"The colour texture was baked, but the extra maps failed: {e}")

            if state["atlas_plan"] is not None:
                HairBakeService.apply_card_atlas(bake_target, state["atlas_plan"])

            if not state["direct_to_body"]:
                fade_attribute = None
                if state["edge_fade"]:
                    if HairCardService.store_shell_edge_fade(bake_target.data, state["edge_fade_width"]):
                        fade_attribute = cg.SHELL_EDGE_FADE_ATTRIBUTE
                    else:
                        _LOG.warn("The shell has no border to fade towards, so the edge fade was "
                                  "skipped", bake_target.name)
                        report({'WARNING'},
                               "This shell has no open edge, so there was nothing to fade")
                baked_material = HairOverlayService.build_baked_material(
                    f"{asset_name}_baked", state["baked_images"],
                    edge_fade_attribute=fade_attribute)
                bake_target.data.materials.clear()
                bake_target.data.materials.append(baked_material)

            success = True
    except Exception as e:
        _LOG.error("Failed while wrapping up the bake", e)
    finally:
        HairBakeService.restore_environment(state, keep_card_material=not success)

    if not success:
        HairBakeService.discard_bake_target(state)
        report({'ERROR'}, "Baking failed or was cancelled; nothing was replaced")
        return False

    if state["direct_to_body"]:
        # No card object to swap in; the result is a shader blended over the skin.
        applied = HairOverlayService.apply_overlay(state["body_surface"], asset_name, state["baked_images"])
        if not applied:
            report({'ERROR'}, "The hair was baked, but no skin material could be found to blend it over")
            return False
    elif state["target"] == cg.BAKE_TARGET_CUSTOM:
        # Custom user mesh keeps everything it had and gains the baked material.
        # Working copy is discarded.
        custom_surface = state["custom_surface"]
        baked_material = (bake_target.data.materials[0]
                          if bake_target.data.materials else None)
        if baked_material is None:
            baked_material = HairOverlayService.build_baked_material(f"{asset_name}_baked",
                                                              state["baked_images"])
        # The original materials kept as a backup
        remember_custom_mesh_materials(custom_surface)
        custom_surface.data.materials.clear()
        custom_surface.data.materials.append(baked_material)
        HairBakeService.discard_bake_target(state)
    else:
        # Replace the live card object with the baked one.
        old_modifier_node_group = None
        modifier = live_card_obj.modifiers.get(CARDS_MODIFIER_NAME)
        if modifier is not None:
            old_modifier_node_group = modifier.node_group
        old_data = live_card_obj.data
        bpy.data.objects.remove(live_card_obj, do_unlink=True)
        if old_modifier_node_group is not None and old_modifier_node_group.users == 0:
            bpy.data.node_groups.remove(old_modifier_node_group)
        # old_data is the live card object geometry, orphaned_data is what mesh conversion of working copy left behind.
        for datablock in [old_data] + state["orphaned_data"]:
            HairBakeService.remove_orphan_geometry(datablock)

        bake_target.name = f"{asset_name}{CARDS_OBJECT_SUFFIX}"

        if state["target"] == cg.BAKE_TARGET_BODY_SHELL:
            # Converting to a mesh applied every modifier including the armature, so shell no longer moves with the character.
            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
            if rig is not None:
                try:
                    HairCardService.weight_body_shell_to_rig(bake_target, state["body_surface"], rig)
                except Exception as e:
                    _LOG.error("Could not re-attach the baked body shell to the rig", e)
                    report({'WARNING'},
                           "The shell was baked, but it could not be re-attached to the rig")

    hair_obj.hide_set(True)
    hair_obj.hide_render = True

    set_cards_flag(state["properties"], basemesh, asset_name, state["kind"], "baked", True)

    message = f"Baked hair texture to {bake_path}"
    if extra_paths:
        message += f" (+ {', '.join(extra_paths.keys())})"
    report({'INFO'}, message)
    return True


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_BakeHair_Operator(MpfbOperator):
    """Bakes hair asset as a texture for card asset"""
    bl_idname = "mpfb.bake_hair_operator"
    bl_label = "Bake hair cards"
    bl_options = {'REGISTER'}

    hair_asset: bpy.props.StringProperty()
    is_fur: bpy.props.BoolProperty(default=False)

    def get_logger(self):
        return _LOG

    def _store_scene_settings(self, scene):
        settings = {
            "engine": scene.render.engine,
            "film_transparent": scene.render.film_transparent,
            "background": None,
            "cycles": {},
            "bake": {key: getattr(scene.render.bake, key) for key in _BAKE_PASS_SETTINGS}
            }
        for key in ["samples"] + list(_CYCLES_BAKE_SETTINGS.keys()):
            if hasattr(scene.cycles, key):
                settings["cycles"][key] = getattr(scene.cycles, key)

        world = scene.world
        if world and world.use_nodes and "Background" in world.node_tree.nodes:
            settings["background"] = tuple(world.node_tree.nodes["Background"].inputs[0].default_value)

        return settings

    def _apply_bake_settings(self, scene, samples, keep_world=False):
        scene.render.engine = 'CYCLES'
        scene.render.film_transparent = True
        scene.cycles.samples = samples
        for key, value in _CYCLES_BAKE_SETTINGS.items():
            if hasattr(scene.cycles, key):
                setattr(scene.cycles, key, value)

        # With the current scene lighting the world may be part of the light (an HDRI), so it is left alone
        world = scene.world
        if not keep_world and world and world.use_nodes and "Background" in world.node_tree.nodes:
            world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 0)

    def _unwrap_cards(self, bake_target, atlas_fraction, prefer_generated_uvs, resolution=1024, hair_obj=None):
        """Turn the working copy into a mesh and give it UVs. Returns the atlas plan.

        The shell modes have no layout of their own, so they fall through to the unwrapper.
        """
        import bmesh

        orphaned = []
        # Cluster ribbons are also just edge chains with modifiers which only become card geometry once the generator has run.
        if bake_target.type != 'MESH' or bake_target.modifiers:
            generated_from = bake_target.data
            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(bake_target)
            bpy.ops.object.convert(target='MESH')
            # convert() swaps in a brand new mesh and leaves the original data behind as an orphan
            if generated_from is not bake_target.data:
                orphaned.append(generated_from)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(bake_target)

        # Measured only when something is actually shared
        exposure = None
        if hair_obj is not None and atlas_fraction < 0.999:
            exposure = HairBakeService.card_vertex_sparsity(bake_target, hair_obj)

        generated_uvs = False
        island_count = 0
        if prefer_generated_uvs:
            bm = bmesh.new()
            try:
                bm.from_mesh(bake_target.data)
                bm.faces.ensure_lookup_table()
                uv_layer = bm.loops.layers.uv[0] if bm.loops.layers.uv else None
                islands = HairBakeService.find_uv_islands(bm)
                island_count = len(islands)
                generated_uvs = HairBakeService.has_generated_card_uvs(bm, islands, uv_layer)
            finally:
                bm.free()

        if generated_uvs:
            _LOG.debug("Packing the generator's own UV layout into the atlas")
            return HairBakeService.pack_card_uvs_into_grid(bake_target, atlas_fraction, resolution,
                                            exposure=exposure), orphaned

        _LOG.debug("Unwrapping without a generated UV layout",
                   (bake_target.name, prefer_generated_uvs, island_count))
        if prefer_generated_uvs and island_count > 1:
            self.report({'WARNING'},
                        "These cards have no generated UV layout, so they were unwrapped - "
                        "individual cards may come out rotated")

        if atlas_fraction >= 0.999:
            HairBakeService.smart_project_selection(select_all=True)
            return None, orphaned

        return HairBakeService.prepare_card_atlas(bake_target, atlas_fraction, exposure=exposure), orphaned

    def _hair_bounds(self, hair_obj):
        """Centre and radius of the hair bounding box, in world space."""
        corners = [hair_obj.matrix_world @ Vector(corner) for corner in hair_obj.bound_box]
        if not corners:
            return hair_obj.matrix_world.translation.copy(), 1.0
        centre = sum(corners, Vector()) / len(corners)
        radius = max((corner - centre).length for corner in corners)
        return centre, max(radius, 1e-4)

    def _strand_axes(self, hair_obj):
        """The direction the strands mostly run in, and two unit vectors across them.

        The strand direction comes from the asset's own root-to-tip vector.

        Returns (direction, across_a, across_b), or None if the asset has no usable curves.
        """
        import numpy as np

        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = hair_obj.evaluated_get(depsgraph)
        data = evaluated.data
        curves = getattr(data, "curves", None)
        points = getattr(data, "points", None)
        if not curves or not points or len(curves) == 0:
            _LOG.warn("No curves to read a strand direction from", hair_obj.name)
            return None

        positions = np.empty(len(points) * 3, dtype=np.float32)
        points.foreach_get("position", positions)
        positions = positions.reshape(-1, 3).astype(np.float64)

        first = np.empty(len(curves), dtype=np.int32)
        length = np.empty(len(curves), dtype=np.int32)
        curves.foreach_get("first_point_index", first)
        curves.foreach_get("points_length", length)
        usable = length > 1
        if not usable.any():
            return None
        roots = positions[first[usable]]
        tips = positions[first[usable] + length[usable] - 1]

        # Rotation only
        matrix = np.array(evaluated.matrix_world.transposed())[:3, :3]
        offsets = (tips - roots) @ matrix
        offsets = offsets[np.linalg.norm(offsets, axis=1) > 1e-9]
        if len(offsets) == 0:
            return None

        _u, _s, vt = np.linalg.svd(offsets, full_matrices=False)
        direction = Vector(vt[0].tolist())
        if direction.length < 1e-9:
            return None
        direction.normalize()

        # Seeded from world axis least aligned with the strands, so that the cross product cannot collapse.
        seed = min((Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
                   key=lambda axis: abs(direction.dot(axis)))
        across_a = direction.cross(seed).normalized()
        across_b = direction.cross(across_a).normalized()
        return direction, across_a, across_b

    def _light_placement(self, basemesh, hair_obj, mode):
        """Where the bake lights go, and whether they cast. Returns (locations, casts_shadows)."""
        if mode == cg.LIGHT_MODE_SCENE:
            # The scenes own lights are used, nothing is added
            return [], False
        if mode == cg.LIGHT_MODE_FIXED:
            return [basemesh.location + Vector((0, -2, 3)),
                    basemesh.location + Vector((0, 2, 3))], True

        centre, radius = self._hair_bounds(hair_obj)
        bbox_pair = [centre + Vector((0, -radius, radius)), centre + Vector((0, radius, radius))]

        if mode == cg.LIGHT_MODE_BBOX:
            return bbox_pair, True
        if mode == cg.LIGHT_MODE_NO_SHADOW:
            return bbox_pair, False
        if mode == cg.LIGHT_MODE_ACROSS_STRANDS:
            axes = self._strand_axes(hair_obj)
            if axes is None:
                # Nothing to align to, so fall back on the bounding box pair with no shadows
                self.report({'WARNING'},
                            "Could not read a strand direction from this asset, so the lights "
                            "were placed from its bounding box instead")
                return bbox_pair, False
            _direction, across_a, across_b = axes
            # Distance comparable to the bounding box pair
            return [centre + across_a * radius * 1.5, centre + across_b * radius * 1.5], False
        return bbox_pair, False

    def _add_bake_lights(self, scene, basemesh, hair_obj, mode, strength):
        """Bake lights, placed and told whether to cast according to the chosen mode."""

        locations, casts_shadows = self._light_placement(basemesh, hair_obj, mode)
        if not locations:
            return []

        share = HairCardService.light_base_energy(mode) * strength
        lights = []
        for location in locations:
            light_data = bpy.data.lights.new(name="BakeHairLight", type='POINT')
            light_data.energy = share
            if hasattr(light_data, "use_shadow"):
                light_data.use_shadow = casts_shadows
            light_obj = bpy.data.objects.new(name="BakeHairLight", object_data=light_data)
            scene.collection.objects.link(light_obj)
            light_obj.location = location
            lights.append(light_obj)
        _LOG.debug("Added bake lights", (mode, len(lights), casts_shadows))
        return lights

    def _prepare(self, context):
        """Everything that has to happen before the main bake call.

        Returns a state dict on success, or None if a fatal problem was found.
        """
        if not hasattr(bpy.types, "ShaderNodeBsdfRayPortal"):
            self.report({'ERROR'}, "This blender version has no ray portal shader, which the bake depends on")
            return None

        scene = context.scene
        if not hasattr(scene, "cycles"):
            self.report({'ERROR'}, "Baking hair cards requires the cycles render engine to be enabled")
            return None

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"
        asset_name = self.hair_asset

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            self.report({'ERROR'}, "Could not find basemesh amongst relatives of selected object")
            return None

        hair_obj = None
        live_card_obj = None
        card_name = f"{asset_name}{CARDS_OBJECT_SUFFIX}"
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == asset_name:
                hair_obj = child
            if child.name == card_name:
                live_card_obj = child

        if hair_obj is None:
            self.report({'ERROR'}, f"Hair object '{asset_name}' not found amongst the children of the basemesh")
            return None

        # Baking straight onto the body without card object.
        # The bake lands on the body UVs and result is blended over its skin material afterwards.
        target = get_bake_target(properties, basemesh, asset_name)
        direct_to_body = target == cg.BAKE_TARGET_BODY_DIRECT
        custom_target = target == cg.BAKE_TARGET_CUSTOM
        body_surface = resolve_body_surface(basemesh)

        custom_surface = None
        if custom_target:
            custom_surface = resolve_custom_surface(properties, basemesh, asset_name)
            if custom_surface is None:
                self.report({'ERROR'},
                            "Pick a mesh from the scene to bake onto - the chosen one is missing, renamed, or not a mesh")
                return None
            if not custom_surface.data.uv_layers:
                self.report({'ERROR'},
                            f"'{custom_surface.name}' has no UV layout, and this target bakes into the mesh's own layout")
                return None
            if custom_surface in (basemesh, hair_obj, body_surface):
                self.report({'ERROR'},
                            "Pick a mesh of your own")
                return None

        if direct_to_body:
            if not body_surface.data.uv_layers:
                self.report({'ERROR'}, f"'{body_surface.name}' has no UV layout to bake onto")
                return None
            if not body_has_material(body_surface):
                self.report({'ERROR'},
                            "Apply a skin material first - baking onto the body blends the hair "
                            "over the skin material, and there is none to blend over yet")
                return None
        elif not custom_target and live_card_obj is None:
            self.report({'ERROR'}, f"Card object '{card_name}' not found amongst the children of the basemesh")
            return None

        resolution = properties.get_value(f"{asset_name}_cards_resolution", 1024, entity_reference=basemesh)
        samples = properties.get_value(f"{asset_name}_cards_samples", 32, entity_reference=basemesh)
        glossy = properties.get_value(f"{asset_name}_cards_glossy", True, entity_reference=basemesh)
        destination = properties.get_value(f"{asset_name}_cards_texture_dst", "", entity_reference=basemesh)
        atlas_fraction = get_atlas_fraction(properties, basemesh, asset_name)

        cards_mode = get_cards_mode(properties, basemesh, asset_name)
        if target != cg.BAKE_TARGET_CARDS or cards_mode == cg.CARDS_MODE_SHELL:
            atlas_fraction = 1.0
        sharing = atlas_fraction < 0.999
        body_shadows = properties.get_value(f"{asset_name}_cards_body_shadows", False, entity_reference=basemesh)
        light_mode = get_light_mode(properties, basemesh, asset_name)
        light_strength = get_light_strength(properties, basemesh, asset_name)
        wanted_maps = {
            key: bool(properties.get_value(f"{asset_name}_{propname}", False, entity_reference=basemesh))
            for key, (propname, _builder) in EXTRA_MAP_BUILDERS.items()
            }
        # The end-on cutoff of the volume shell is built out of these two maps, so they are forced.
        # Not for a direct body bake.
        if cards_mode == cg.CARDS_MODE_SHELL and target != cg.BAKE_TARGET_BODY_DIRECT:
            wanted_maps["side_on"] = True
            wanted_maps["root_tip"] = True
        analytic_uvs = properties.get_value(f"{asset_name}_cards_analytic_uvs", True, entity_reference=basemesh)
        edge_fade = properties.get_value(f"{asset_name}_cards_body_edge_fade", False, entity_reference=basemesh)
        edge_fade_width = int(properties.get_value(f"{asset_name}_cards_body_edge_fade_width", 2, entity_reference=basemesh))
        # Zero for everything except the body shell, which measures its own lift below.
        capture_depth = 0.0
        # Body texture stays one-sided: its ray already looks outward
        double_sided = (bool(properties.get_value(f"{asset_name}_cards_double_sided", False, entity_reference=basemesh))
                        and target in (cg.BAKE_TARGET_CARDS, cg.BAKE_TARGET_CUSTOM, cg.BAKE_TARGET_BODY_SHELL))
        limit_rays = properties.get_value(f"{asset_name}_cards_limit_ray_range", False, entity_reference=basemesh)
        ray_range = properties.get_value(f"{asset_name}_cards_ray_range", 0.1, entity_reference=basemesh)

        # Forced for the body targets - without it the rays go through the body and capture the hair on the far side.
        if target in cg.BODY_BAKE_TARGETS:
            limit_rays = True

        shell_height = 0.0
        if target == cg.BAKE_TARGET_BODY_SHELL:
            # Ray starting on the shell would only capture the hair below the shell height and miss the tips.
            shell_height = float(properties.get_value(
                f"{asset_name}_cards_body_height", 0.006, entity_reference=basemesh))
            extent = HairCardService.hair_extent_above_surface(
                body_surface, hair_obj, context.evaluated_depsgraph_get())
            above_shell = max(0.0, extent - shell_height)
            if above_shell > 0.0:
                capture_depth += above_shell + SHELL_CAPTURE_MARGIN
                _LOG.debug("Body shell capture lifted above the hair",
                           (extent, shell_height, capture_depth))

            # The forced range limit has to reach from the lifted start through the hair to the skin.
            reach = capture_depth + shell_height + SHELL_CAPTURE_MARGIN
            if ray_range < reach:
                _LOG.debug("Raising the body shell ray range to cover the capture slab",
                           (ray_range, reach))
                ray_range = reach

        # Baking replaces the generator with a plain mesh, so the card settings are saved for unbake.
        remember_cards_settings(basemesh, asset_name,
                                snapshot_cards_properties(properties, basemesh, asset_name))

        if direct_to_body:
            # The bake writes into the body UVs and is blended over the skin material.
            bake_target = body_surface
        elif custom_target:
            # Working on a copy, so the user mesh does not lose its modifiers when converted.
            # Only the finished material goes onto the real object.
            bake_target = custom_surface.copy()
            bake_target.data = custom_surface.data.copy()
            bake_target.name = f"{custom_surface.name}_baking_in_progress"
            context.collection.objects.link(bake_target)
        else:
            # Working on a copy of the card object, the live one is replaced only once baking succeeded.
            # If anything fails, the original card object with its generator stays untouched.
            bake_target = live_card_obj.copy()
            bake_target.data = live_card_obj.data.copy()
            bake_target.name = f"{card_name}_baking_in_progress"
            context.collection.objects.link(bake_target)

        state = {
            "scene": scene, "properties": properties, "kind": kind, "basemesh": basemesh,
            "hair_obj": hair_obj, "live_card_obj": live_card_obj, "bake_target": bake_target,
            "asset_name": asset_name, "resolution": resolution, "glossy": glossy,
            "destination": destination, "wanted_maps": wanted_maps, "orphaned_data": [],
            "bake_image": None, "atlas_plan": None, "report": self.report,
            "baked_images": {}, "double_sided": double_sided,
            "target": target, "direct_to_body": direct_to_body, "body_surface": body_surface,
            "custom_surface": custom_surface,
            "swapped_materials": [],
            "edge_fade": bool(edge_fade) and target == cg.BAKE_TARGET_BODY_SHELL,
            "edge_fade_width": edge_fade_width,
            "shell_height": shell_height,
            # Passed to the extra map shader builders. The depth map is scaled by the ray range.
            "shader_options": {
                "ray_range": ray_range if limit_rays else None,
                "depth_scale": ray_range,
                },
            }

        # From here on the scene is being modified, so any failure has to restore all of it.
        try:
            def swap_materials(obj, material):
                """Put a temporary material on an object, remembering what was there before."""
                state["swapped_materials"].append((obj, [slot.material for slot in obj.material_slots]))
                obj.data.materials.clear()
                obj.data.materials.append(material)

            # Converting the body shell to a mesh freezes the current pose, which the armature would then apply again.
            # So the rig is held in rest pose for the whole bake.
            if target == cg.BAKE_TARGET_BODY_SHELL:
                rig = ObjectService.find_object_of_type_amongst_nearest_relatives(
                    basemesh, "Skeleton")
                if rig is not None and rig.data.pose_position != 'REST':
                    state["rest_posed_rig"] = (rig, rig.data.pose_position)
                    rig.data.pose_position = 'REST'
                    context.view_layer.update()

            # Not for the custom target, which keeps the UV layout made by the user.
            if not direct_to_body and not custom_target:
                state["atlas_plan"], state["orphaned_data"] = self._unwrap_cards(
                    bake_target, atlas_fraction, analytic_uvs, resolution,
                    hair_obj=hair_obj)

            if limit_rays:
                state["original_hair_materials"] = [slot.material for slot in hair_obj.material_slots]
                state["range_limited_materials"] = HairBakeService.range_limited_copies(hair_obj, ray_range)
                hair_obj.data.materials.clear()
                for material in state["range_limited_materials"]:
                    hair_obj.data.materials.append(material)

            state["original_card_visibility"] = {key: getattr(bake_target, key) for key in _RAY_VISIBILITY}
            state["scene_settings"] = self._store_scene_settings(scene)

            # Everything but the character, the hair and the cards is hidden, as the cards capture whatever is behind them.
            # Both flags are saved. An object hidden only in the viewport still renders.
            hidden_objects = []
            keep_visible = {basemesh.name, hair_obj.name, bake_target.name, body_surface.name}
            # Lights are not captured by the cards, so with the current scene lighting they stay on
            use_scene_lighting = glossy and light_mode == cg.LIGHT_MODE_SCENE
            for obj in bpy.data.objects:
                if obj.name in keep_visible:
                    continue
                if use_scene_lighting and obj.type == 'LIGHT':
                    continue
                if obj.visible_get() or HairEditorService.is_rendered(obj, scene, context.view_layer):
                    hidden_objects.append((obj, (obj.hide_render, obj.hide_viewport)))
                    obj.hide_render = True
                    obj.hide_viewport = True
            state["hidden_objects"] = hidden_objects

            # Shadow of the body would bake in as a hard dark band across the cards, so the body does not cast it unless asked for.
            if not body_shadows and glossy:
                shadow_casters = []
                for obj in {basemesh.name, body_surface.name}:
                    caster = bpy.data.objects.get(obj)
                    if caster is None or caster.name == bake_target.name:
                        continue
                    shadow_casters.append((caster, caster.visible_shadow))
                    caster.visible_shadow = False
                state["shadow_casters"] = shadow_casters

            for key in _RAY_VISIBILITY:
                setattr(bake_target, key, False)

            self._apply_bake_settings(scene, samples, keep_world=use_scene_lighting)
            if use_scene_lighting and not any(
                    obj.type == 'LIGHT' and HairEditorService.is_rendered(obj, scene, context.view_layer)
                    for obj in scene.objects):
                self.report({'WARNING'}, "Baking with the current scene lighting, but no light in the scene"
                                         "is enabled for render. Only the world will light the hair")

            state["card_material"] = HairBakeService.build_ray_portal_material(capture_depth, outward=direct_to_body)
            if direct_to_body:
                # The target is the body itself, so its skin has to come back afterwards.
                swap_materials(bake_target, state["card_material"])
            else:
                # Not recorded as a swap - the restore would put the original materials back over the baked result.
                bake_target.data.materials.clear()
                bake_target.data.materials.append(state["card_material"])

            state["bake_image"] = HairBakeService.bake_image(f"{asset_name}_cards_texture", resolution,
                                              alpha=True, colorspace='sRGB')
            state["baked_images"]["color"] = state["bake_image"]

            bake_texture_node = state["card_material"].node_tree.nodes.new(type='ShaderNodeTexImage')
            bake_texture_node.image = state["bake_image"]
            state["card_material"].node_tree.nodes.active = bake_texture_node
            state["bake_texture_node"] = bake_texture_node

            if direct_to_body:
                # No holdout - the body is the target itself.
                state["basemesh_material"] = None
            else:
                # Every body mesh has to be held out, with a proxy there are two of them.
                state["basemesh_material"] = HairBakeService.build_holdout_material()
                for surface in body_surfaces_to_hide_behind(basemesh):
                    swap_materials(surface, state["basemesh_material"])

            # Only a glossy pass uses lights, diffuse bake has direct and indirect passes off.
            if glossy:
                state["lights"] = self._add_bake_lights(
                    scene, basemesh, hair_obj, light_mode, light_strength)

            bake_settings = scene.render.bake
            bake_settings.use_pass_direct = bool(glossy)
            bake_settings.use_pass_indirect = bool(glossy)
            bake_settings.use_selected_to_active = False

            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(bake_target)
        except Exception as e:
            _LOG.error("Could not set the scene up for baking", e)
            HairBakeService.restore_environment(state, keep_card_material=False)
            HairBakeService.discard_bake_target(state)
            self.report({'ERROR'}, f"Could not set the scene up for baking: {e}")
            return None

        return state

    def hardened_execute(self, context):
        """Fully synchronous path, used by scripts/tests and whenever invoke() is bypassed."""
        _LOG.enter()

        state = self._prepare(context)
        if state is None:
            return {'CANCELLED'}
        forget_bake_result(state["basemesh"].name, state["asset_name"])

        self.report({'INFO'}, "Baking cards... It might take a while")
        bake_succeeded = False
        try:
            HairBakeService.run_bake_passes(state, 'GLOSSY' if state["glossy"] else 'DIFFUSE')
            bake_succeeded = True
        except Exception as e:
            _LOG.error("Bake call raised an exception", e)

        if not _finish(state, bake_succeeded):
            return {'CANCELLED'}
        HairBakeService.push_bake_undo_step()
        return {'FINISHED'}

    def invoke(self, context, event):
        """Interactive, non-blocking path: the render runs in a blender background bake job.

        Cleanup and replacing the cards with the baked result run later, from a bake-completion/cancel handler.
        The extra maps still bake synchronously, right after the main pass.
        """
        try:
            state = self._prepare(context)
        except Exception as e:
            _LOG.crash("Could not prepare the bake", e)
            self.report({'ERROR'}, f"Could not prepare the bake: {e}")
            return {'CANCELLED'}
        if state is None:
            return {'CANCELLED'}

        basemesh_name = state["basemesh"].name
        asset_name = state["asset_name"]
        forget_bake_result(basemesh_name, asset_name)

        # The operator is freed after invoke returns, so nothing that runs later may use it.
        # Messages are collected instead, and shown once the bake has ended.
        state["messages"] = []

        def _collect(level, message):
            _LOG.info(f"{'/'.join(sorted(level))}: {message}")
            if _message_level(level) != 'INFO':
                state["messages"].append((_message_level(level), message))

        state["report"] = _collect

        self.report({'INFO'}, "Baking cards in the background...")

        # The post-bake pass edits images and materials, which is not safe inside an app handler
        # while the viewport may be syncing - it caused a crash in EEVEE.
        # So the handler only queues the work on a timer, which runs from the main loop.
        pending = {"finish": None}

        def _queue_finish(succeeded):
            def _finish_later():
                pending["finish"] = None
                _unregister(scene_guards=True)
                _PENDING_BAKES.pop(id(state), None)
                finished = False
                try:
                    finished = _finish(state, succeeded)
                    if finished:
                        HairBakeService.push_bake_undo_step()
                except Exception as e:
                    _LOG.crash("Finishing the background bake failed", e)
                    state["messages"].append(('ERROR', f"Finishing the bake failed: {e}"))
                if not finished:
                    status = BAKE_CANCELLED if state.get("cancelled") else BAKE_FAILED
                elif state["messages"]:
                    status = BAKE_WARNINGS
                else:
                    status = None
                _announce_background_result(basemesh_name, asset_name, status, state["messages"])
                return None  # one shot

            pending["finish"] = _finish_later
            bpy.app.timers.register(_finish_later)

        def _on_complete(*_args):
            _unregister(scene_guards=False)
            _queue_finish(True)

        def _on_cancel(*_args):
            _unregister(scene_guards=False)
            state["cancelled"] = True
            _queue_finish(False)

        def _on_scene_replaced(*_args):
            """Undo, redo or a file load has replaced the whole database.

            Everything the pending finish would touch has been freed, so the bake state is dropped,
            including a finish already queued on the timer.
            """
            queued = pending["finish"]
            pending["finish"] = None
            if queued is not None and bpy.app.timers.is_registered(queued):
                bpy.app.timers.unregister(queued)
            _unregister(scene_guards=True)
            _PENDING_BAKES.pop(id(state), None)
            _LOG.warn("The scene was replaced while a bake was pending; abandoning the bake state")
            _announce_background_result(basemesh_name, asset_name, BAKE_ABANDONED, [
                ('ERROR', "Undo, redo or opening a file replaced the scene while the bake was running,"),
                ('ERROR', "so its result was dropped. Bake again to get the textures.")])

        def _abandon():
            """MPFB2 is being disabled while the bake runs - only drop what would otherwise be left behind."""
            queued = pending["finish"]
            pending["finish"] = None
            if queued is not None and bpy.app.timers.is_registered(queued):
                bpy.app.timers.unregister(queued)
            _unregister(scene_guards=True)
            _LOG.warn("MPFB2 was disabled while a bake was pending; its handlers were removed")

        def _unregister(scene_guards):
            """Drop the bake handlers, and optionally the undo/redo/load guards as well.

            The guards protect the queued finish, so they are removed only once it has run.
            """
            handlers = [(bpy.app.handlers.object_bake_complete, _on_complete),
                        (bpy.app.handlers.object_bake_cancel, _on_cancel)]
            if scene_guards:
                handlers += [(bpy.app.handlers.undo_post, _on_scene_replaced),
                             (bpy.app.handlers.redo_post, _on_scene_replaced),
                             (bpy.app.handlers.load_post, _on_scene_replaced)]
            for handler_list, handler in handlers:
                if handler in handler_list:
                    handler_list.remove(handler)

        bpy.app.handlers.object_bake_complete.append(_on_complete)
        bpy.app.handlers.object_bake_cancel.append(_on_cancel)
        bpy.app.handlers.undo_post.append(_on_scene_replaced)
        bpy.app.handlers.redo_post.append(_on_scene_replaced)
        bpy.app.handlers.load_post.append(_on_scene_replaced)
        _PENDING_BAKES[id(state)] = _abandon

        started = None
        try:
            started = bpy.ops.object.bake('INVOKE_DEFAULT', type='GLOSSY' if state["glossy"] else 'DIFFUSE')
        except Exception as e:
            _LOG.error("Could not start background bake, falling back to a blocking bake", e)

        # A refused INVOKE_DEFAULT can either raise or return CANCELLED, in which case no handler will fire.
        if started is None or 'RUNNING_MODAL' not in started:
            _unregister(scene_guards=True)
            _PENDING_BAKES.pop(id(state), None)
            self.report({'WARNING'}, "Could not start a background bake; baking synchronously instead")
            state["report"] = self.report
            bake_succeeded = False
            try:
                bpy.ops.object.bake(type='GLOSSY' if state["glossy"] else 'DIFFUSE')
                bake_succeeded = True
            except Exception as e2:
                _LOG.error("Bake call raised an exception", e2)
            if not _finish(state, bake_succeeded):
                return {'CANCELLED'}
            HairBakeService.push_bake_undo_step()

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_BakeHair_Operator)
