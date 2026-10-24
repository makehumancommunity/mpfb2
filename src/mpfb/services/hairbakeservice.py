# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025 - updated 18.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  baking hair onto cards, the body or a custom mesh as a texture
# ------------------------------------------------------------------------------
"""Bake materials, atlas packing, extra maps and the scene clean up used by the hair bake operator."""

import bpy, os, tempfile, collections
from collections.abc import Callable
from typing import Any, TYPE_CHECKING
from mathutils import Vector

from .logservice import LogService
from .locationservice import LocationService
from .objectservice import ObjectService
from .haireditorservices import HairEditorService
from . import haircardservice as cg

if TYPE_CHECKING:
    import bmesh
    import numpy as np

_LOG = LogService.get_logger("services.hairbakeservice")

# When baking on body shell ray start position and length are calculated based on hair geometry.
# To avoid missing start/end of strand due to float precision on the boundary, there is this tolerance.
SHELL_CAPTURE_MARGIN = 0.002

# With atlas baking enabled, only certain cards are baked.
# UV space has coordinates 0..1, so cards with value like 10 will not interfere
_UV_PARKING_OFFSET = 10.0

_PORTAL_DIRECTION_NODE = "PortalDirection"

_PORTAL_LIFT_NODE = "PortalLift"

# Every map except the colour texture carries numbers, not colors
_DATA_MAP_COLORSPACE = 'Non-Color'


class HairBakeService():
    """Baking the hair into textures for the hair editor. All methods are static methods."""

    def __init__(self) -> None:
        raise RuntimeError("You should not instance HairBakeService. Use its static methods instead.")

    @staticmethod
    def get_default_bake_directory() -> str:
        """The directory baked card textures are written to unless the user picks another one."""
        return LocationService.get_user_home("baked_hair_cards")

    @staticmethod
    def build_ray_portal_material(capture_depth: float = 0.0, outward: bool = False) -> bpy.types.Material:
        """Material which makes the bake target invisible to the camera, so the hair is baked through it.

        ``capture_depth`` used by body shell only - user can set how far the body shell is from the skin.
        Casting ray from shell itself could therefore cause parts of longer hair to be "cut off" during bake.
        This moves the ray start position so that it is above the hair and captures whole length of strands.

        ``outward`` flips the ray direction. Cards and the body shell are above the hair and look down into it.
        Baking straight onto the body is the other way round.
        """
        material = bpy.data.materials.new(name="HairCardRayPortal")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()

        output = nodes.new(type='ShaderNodeOutputMaterial')
        portal = nodes.new(type='ShaderNodeBsdfRayPortal')
        geometry = nodes.new(type='ShaderNodeNewGeometry')
        invert = nodes.new(type='ShaderNodeVectorMath')
        invert.operation = 'MULTIPLY'
        # Named so that the double-sided pass can find it and negate it
        invert.name = _PORTAL_DIRECTION_NODE
        invert.inputs[1].default_value = (1.0, 1.0, 1.0) if outward else (-1.0, -1.0, -1.0)

        lift = nodes.new(type='ShaderNodeVectorMath')
        lift.operation = 'SCALE'
        lift.name = _PORTAL_LIFT_NODE
        lift.location = (-400, 200)
        links.new(geometry.outputs['Normal'], lift.inputs[0])
        lift.inputs['Scale'].default_value = capture_depth

        moved = nodes.new(type='ShaderNodeVectorMath')
        moved.operation = 'ADD'
        moved.location = (-200, 200)
        links.new(geometry.outputs['Position'], moved.inputs[0])
        links.new(lift.outputs['Vector'], moved.inputs[1])
        origin = moved.outputs['Vector']

        links.new(origin, portal.inputs['Position'])
        links.new(geometry.outputs['Normal'], invert.inputs['Vector'])
        links.new(invert.outputs['Vector'], portal.inputs['Direction'])
        links.new(portal.outputs['BSDF'], output.inputs['Surface'])

        return material

    @staticmethod
    def _limit_shader_to_range(node_tree: bpy.types.NodeTree, shader_socket: bpy.types.NodeSocket, ray_range: float) -> bpy.types.NodeSocket:
        """Make a shader fade to fully transparent beyond ``ray_range`` from where the ray started.

        Ray portal lets the ray run forever, which can cause card on one temple
        to capture hair from the other side of the head. This says how far from card can the hair be captured
        """
        nodes = node_tree.nodes
        links = node_tree.links

        light_path = nodes.new(type='ShaderNodeLightPath')
        light_path.location = (-600, -400)

        too_far = nodes.new(type='ShaderNodeMath')
        too_far.operation = 'GREATER_THAN'
        too_far.location = (-400, -400)
        links.new(light_path.outputs['Ray Length'], too_far.inputs[0])
        too_far.inputs[1].default_value = ray_range

        transparent = nodes.new(type='ShaderNodeBsdfTransparent')
        transparent.location = (-400, -560)

        mix = nodes.new(type='ShaderNodeMixShader')
        mix.location = (-200, -400)
        links.new(too_far.outputs[0], mix.inputs['Fac'])
        links.new(shader_socket, mix.inputs[1])
        links.new(transparent.outputs['BSDF'], mix.inputs[2])
        return mix.outputs['Shader']

    @staticmethod
    def range_limited_copies(hair_obj: bpy.types.Object, ray_range: float) -> list[bpy.types.Material | None]:
        """Copies of the hair object materials which ignore hair further than ``ray_range``.

        Works on copies so that the asset's own material is not affected.
        """
        copies = []
        for slot in hair_obj.material_slots:
            if slot.material is None:
                copies.append(None)
                continue
            copy = slot.material.copy()
            copy.name = f"{slot.material.name}_range_limited"
            output = next((n for n in copy.node_tree.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'), None)
            surface = output.inputs['Surface'] if output is not None else None
            if surface is None or not surface.links:
                _LOG.warn("Could not find a surface shader to range limit on", slot.material.name)
                bpy.data.materials.remove(copy, do_unlink=True)
                copies.append(slot.material)
                continue
            original_socket = surface.links[0].from_socket
            copy.node_tree.links.new(
                HairBakeService._limit_shader_to_range(copy.node_tree, original_socket, ray_range), surface)
            copies.append(copy)
        return copies

    @staticmethod
    def build_holdout_material() -> bpy.types.Material:
        """Material which cuts away everything behind the character, so only hair ends up in the bake."""
        material = bpy.data.materials.new(name="HumanHoldout")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()

        output = nodes.new(type='ShaderNodeOutputMaterial')
        holdout = nodes.new(type='ShaderNodeHoldout')
        links.new(holdout.outputs['Holdout'], output.inputs['Surface'])

        return material

    @staticmethod
    def _build_emit_material(name: str, color_socket_builder: Callable[[bpy.types.Nodes, bpy.types.NodeLinks, dict[str, Any]], bpy.types.NodeSocket], options: dict[str, Any]) -> bpy.types.Material:
        """A material which just emits a color built by ``color_socket_builder(nodes, links, options)``.

        Used to temporarily replace the hair object's material while baking one of the extra maps.
        """
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()

        output = nodes.new(type='ShaderNodeOutputMaterial')
        emission = nodes.new(type='ShaderNodeEmission')
        color_socket = color_socket_builder(nodes, links, options)
        links.new(color_socket, emission.inputs['Color'])

        surface = emission.outputs['Emission']
        if options.get("ray_range"):
            surface = HairBakeService._limit_shader_to_range(material.node_tree, surface, options["ray_range"])
        links.new(surface, output.inputs['Surface'])
        return material

    @staticmethod
    def _encode_direction(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, vector_socket: bpy.types.NodeSocket, vector_type: str) -> bpy.types.NodeSocket:
        """Object-space encoding of a direction, as a 0..1 colour."""

        to_object = nodes.new(type='ShaderNodeVectorTransform')
        to_object.vector_type = vector_type
        to_object.convert_from = 'WORLD'
        to_object.convert_to = 'OBJECT'
        to_object.location = (-400, 0)
        links.new(vector_socket, to_object.inputs['Vector'])

        encode = nodes.new(type='ShaderNodeVectorMath')
        encode.operation = 'MULTIPLY_ADD'
        encode.location = (-200, 0)
        encode.inputs[1].default_value = (0.5, 0.5, 0.5)
        encode.inputs[2].default_value = (0.5, 0.5, 0.5)
        links.new(to_object.outputs['Vector'], encode.inputs[0])
        return encode.outputs[0]

    @staticmethod
    def _normal_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        """The hair's surface normal, in object space, encoded as a colour (0.5 = no deviation)."""

        geometry = nodes.new(type='ShaderNodeNewGeometry')
        geometry.location = (-600, 0)
        return HairBakeService._encode_direction(nodes, links, geometry.outputs['Normal'], 'NORMAL')

    @staticmethod
    def _flow_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        """The direction the hair runs, in object space, for an anisotropic hair shader to align to."""
        geometry = nodes.new(type='ShaderNodeNewGeometry')
        geometry.location = (-600, 0)
        return HairBakeService._encode_direction(nodes, links, geometry.outputs['Tangent'], 'VECTOR')

    @staticmethod
    def _depth_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        """How far behind the card this bit of hair sits, scaled by the ray range, as a grey value."""

        light_path = nodes.new(type='ShaderNodeLightPath')
        light_path.location = (-600, 0)

        scaled = nodes.new(type='ShaderNodeMath')
        scaled.operation = 'DIVIDE'
        scaled.location = (-400, 0)
        links.new(light_path.outputs['Ray Length'], scaled.inputs[0])
        scaled.inputs[1].default_value = max(options.get("depth_scale", 0.1), 1e-4)

        clamped = nodes.new(type='ShaderNodeClamp')
        clamped.location = (-200, 0)
        links.new(scaled.outputs[0], clamped.inputs['Value'])
        return clamped.outputs['Result']

    @staticmethod
    def _ao_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
        ao_node.samples = 16
        ao_node.inputs['Distance'].default_value = 0.05
        return ao_node.outputs['Color']

    @staticmethod
    def _root_tip_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        hair_info = nodes.new(type='ShaderNodeHairInfo')
        return hair_info.outputs['Intercept']

    @staticmethod
    def _side_on_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        """How side-on the capture was at this texel: 1 across the strand, 0 along it.

        The quantity is 1 - |dot(strand tangent, ray direction)|.

        This serves to detect and hide dark patches on the bottom of some hair shells caused by strands captured from the bottom
        """

        geometry = nodes.new('ShaderNodeNewGeometry')
        geometry.location = (-700, 0)

        cosine = nodes.new('ShaderNodeVectorMath')
        cosine.operation = 'DOT_PRODUCT'
        cosine.location = (-500, 0)
        links.new(geometry.outputs['Tangent'], cosine.inputs[0])
        links.new(geometry.outputs['Incoming'], cosine.inputs[1])

        magnitude = nodes.new('ShaderNodeMath')
        magnitude.operation = 'ABSOLUTE'
        magnitude.location = (-320, 0)
        links.new(cosine.outputs['Value'], magnitude.inputs[0])

        side_on = nodes.new('ShaderNodeMath')
        side_on.operation = 'SUBTRACT'
        side_on.location = (-140, 0)
        side_on.use_clamp = True
        side_on.inputs[0].default_value = 1.0
        links.new(magnitude.outputs['Value'], side_on.inputs[1])
        return side_on.outputs['Value']

    @staticmethod
    def find_uv_islands(bm: "bmesh.types.BMesh") -> list[list["bmesh.types.BMFace"]]:
        """Group a bmesh's faces into connected islands for atlas bake (faces sharing an edge belong together)."""
        islands = []
        visited = set()
        for face in bm.faces:
            if face.index in visited:
                continue
            island = []
            stack = [face]
            visited.add(face.index)
            while stack:
                current = stack.pop()
                island.append(current)
                for edge in current.edges:
                    for linked in edge.link_faces:
                        if linked.index not in visited:
                            visited.add(linked.index)
                            stack.append(linked)
            islands.append(island)
        return islands

    @staticmethod
    def _hair_points_world(hair_obj: bpy.types.Object) -> "np.ndarray":
        """Every point of the hair in world space, as an (N, 3) array."""

        import numpy as np

        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = hair_obj.evaluated_get(depsgraph)
        data = evaluated.data

        source = getattr(data, "points", None)
        if source is None:
            # Some asset packs ship their hair as a mesh rather than as curves
            source = getattr(data, "vertices", None)
            attribute = "co"
        else:
            attribute = "position"
        if source is None or len(source) == 0:
            return np.zeros((0, 3), dtype=np.float64)

        flat = np.empty(len(source) * 3, dtype=np.float32)
        source.foreach_get(attribute, flat)
        points = flat.reshape(-1, 3).astype(np.float64)

        matrix = np.array(evaluated.matrix_world.transposed())
        return points @ matrix[:3, :3] + matrix[3, :3]

    @staticmethod
    def card_vertex_sparsity(card_obj: bpy.types.Object, hair_obj: bpy.types.Object, neighbours: int = 8) -> "np.ndarray":
        """How exposed each card vertex is, from 0 (deep in the hair mass) to 1 (most exposed).

        When using atlas fraction, we need to avoid choosing cards from the middle of the asset.
        Such cards are fully opaque and would create colored rectangles at the borders of hair.
        Aim is to only use cards, which capture tips of hair.
        """
        import numpy as np
        from mathutils.kdtree import KDTree

        vertex_count = len(card_obj.data.vertices)
        if vertex_count == 0:
            return np.zeros(0, dtype=np.float64)

        hair_points = HairBakeService._hair_points_world(hair_obj)
        if len(hair_points) == 0:
            _LOG.warn("No hair points to measure card exposure against", hair_obj.name)
            return np.zeros(vertex_count, dtype=np.float64)

        tree = KDTree(len(hair_points))
        for index, point in enumerate(hair_points):
            tree.insert(Vector(point), index)
        tree.balance()

        flat = np.empty(vertex_count * 3, dtype=np.float32)
        card_obj.data.vertices.foreach_get("co", flat)
        local = flat.reshape(-1, 3).astype(np.float64)
        matrix = np.array(card_obj.matrix_world.transposed())
        world = local @ matrix[:3, :3] + matrix[3, :3]

        wanted = max(1, min(neighbours, len(hair_points)))
        distances = np.empty(vertex_count, dtype=np.float64)
        for index, point in enumerate(world):
            found = tree.find_n(Vector(point), wanted)
            distances[index] = found[-1][2] if found else 0.0

        # Normalised on percentiles to avoid single stray card from flattening everything else to nearly zero.
        low, high = np.percentile(distances, 5.0), np.percentile(distances, 95.0)
        if high - low < 1e-9:
            return np.zeros(vertex_count, dtype=np.float64)
        return np.clip((distances - low) / (high - low), 0.0, 1.0)

    @staticmethod
    def _island_exposure(islands: list[list["bmesh.types.BMFace"]], sparsity: "np.ndarray") -> dict[int, float]:
        """How exposed each island is - the most exposed vertex it has."""
        exposure = {}
        for index, island in enumerate(islands):
            worst = 0.0
            for face in island:
                for loop in face.loops:
                    vertex_index = loop.vert.index
                    if 0 <= vertex_index < len(sparsity):
                        worst = max(worst, float(sparsity[vertex_index]))
            exposure[index] = worst
        return exposure

    @staticmethod
    def _pick_atlas_variants(islands: list[list["bmesh.types.BMFace"]], fraction: float, exposure: dict[int, float] | None = None) -> tuple[list[int], dict[int, int]]:
        """Decide which islands are baked and which one each of the rest copies.

        Islands are grouped by loop count first - card can only take over another card UV layout if both are built the same.

        Returns (variant_indices, assignment), where assignment maps every non-variant island index to
        the index of the variant it should copy.
        """
        groups = collections.OrderedDict()
        for index, island in enumerate(islands):
            groups.setdefault(sum(len(face.loops) for face in island), []).append(index)

        variant_indices = []
        assignment = {}
        for members in groups.values():
            variant_count = max(1, min(len(members), round(len(members) * fraction)))
            if exposure is None:
                step = len(members) / variant_count
                chosen = sorted({members[min(int(i * step), len(members) - 1)] for i in range(variant_count)})
            else:
                # Sorted by index as the tie break, so that the choice stays reproducible between runs
                ranked = sorted(members, key=lambda index: (-exposure.get(index, 0.0), index))
                chosen = sorted(ranked[:variant_count])
            variant_indices.extend(chosen)
            # Unbaked cards are assigned to variants in round-robin, so each baked island represents about the same number of copies.
            rest = [index for index in members if index not in chosen]
            for position, index in enumerate(rest):
                assignment[index] = chosen[position % len(chosen)]
        return sorted(variant_indices), assignment

    @staticmethod
    def smart_project_selection(select_all: bool = False) -> None:
        """Run smart UV project over the active object."""
        select_mode = tuple(bpy.context.tool_settings.mesh_select_mode)
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            if select_all:
                bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
        finally:
            bpy.context.tool_settings.mesh_select_mode = select_mode
            if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def prepare_card_atlas(card_obj: bpy.types.Object, fraction: float, exposure: "np.ndarray | None" = None) -> dict[str, Any]:
        """Unwrap a representative subset of the cards into an atlas.

        Smart-projecting every card from denser card asset into its own sliver of UV space causes low resolution per card.
        With card atlas bake, only some of the cards are unwrapped and baked, while other cards reuse their textures.
        """
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(card_obj.data)
            bm.faces.ensure_lookup_table()
            if not bm.loops.layers.uv:
                bm.loops.layers.uv.verify()

            islands = HairBakeService.find_uv_islands(bm)
            variant_indices, assignment = HairBakeService._pick_atlas_variants(
                islands, fraction, HairBakeService._island_exposure(islands, exposure) if exposure is not None else None)
            variants = set(variant_indices)

            for face in bm.faces:
                face.select = False
            for index in variant_indices:
                for face in islands[index]:
                    face.select = True

            bm.to_mesh(card_obj.data)
            card_obj.data.update()
        finally:
            bm.free()

        # Smart project packs everything it is given into the whole 0..1 square, so unwrapping just the variants is the atlas.
        HairBakeService.smart_project_selection()

        bm = bmesh.new()
        try:
            bm.from_mesh(card_obj.data)
            bm.faces.ensure_lookup_table()
            uv_layer = bm.loops.layers.uv[0]
            islands = HairBakeService.find_uv_islands(bm)

            variant_uvs = {}
            for index in variant_indices:
                variant_uvs[index] = [tuple(loop[uv_layer].uv) for face in islands[index] for loop in face.loops]

            for index, island in enumerate(islands):
                if index in variants:
                    continue
                for face in island:
                    for loop in face.loops:
                        uv = loop[uv_layer].uv
                        loop[uv_layer].uv = (uv.x + _UV_PARKING_OFFSET, uv.y)

            bm.to_mesh(card_obj.data)
            card_obj.data.update()
        finally:
            bm.free()

        return {"variant_uvs": variant_uvs, "assignment": assignment}

    @staticmethod
    def has_generated_card_uvs(bm: "bmesh.types.BMesh", islands: list[list["bmesh.types.BMFace"]], uv_layer: Any) -> bool:
        """Whether the cards already carry a per-card 0..1 UV layout from the generator.

        Tiles, ribbons and cluster cards have their own UVs, the shell modes have yet to be unwrapped.
        """
        if uv_layer is None or not islands:
            return False
        checked = 0
        for island in islands[::max(1, len(islands) // 8)]:
            us = [loop[uv_layer].uv.x for face in island for loop in face.loops]
            vs = [loop[uv_layer].uv.y for face in island for loop in face.loops]
            if not us:
                return False
            if min(us) < -0.01 or max(us) > 1.01 or min(vs) < -0.01 or max(vs) > 1.01:
                return False
            if (max(us) - min(us)) < 0.5 or (max(vs) - min(vs)) < 0.5:
                return False
            checked += 1
        return checked > 0

    @staticmethod
    def _card_uv_cell_grid(islands: list[list["bmesh.types.BMFace"]], cell_count: int) -> tuple[int, int, float]:
        """How many columns and rows to slice the atlas into for ``cell_count`` cards.

        The card's proportion is measured from the geometry.
        """
        import numpy as np

        aspects = []
        for island in islands[:200]:
            points = np.array([tuple(vertex.co) for face in island for vertex in face.verts])
            if len(points) < 4:
                continue
            spread = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)[1]
            if spread[1] > 1e-9:
                aspects.append(float(spread[0] / spread[1]))
        aspect = float(np.median(aspects)) if aspects else 1.0
        aspect = min(max(aspect, 1.0), 8.0)

        # cell is (1/columns) wide and (1/rows) tall, so its proportion is columns/rows
        rows = max(1, int(np.ceil(np.sqrt(cell_count / aspect))))
        columns = max(1, int(np.ceil(cell_count / rows)))
        return columns, rows, aspect

    @staticmethod
    def pack_card_uvs_into_grid(card_obj: bpy.types.Object, fraction: float, resolution: int = 1024, exposure: "np.ndarray | None" = None) -> dict[str, Any]:
        """Pack the generator's own per-card UVs into a grid of atlas cells.

        Returns a plan for apply_card_atlas(), keyed by face index so island ordering cannot throw it
        off.
        """
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(card_obj.data)
            bm.faces.ensure_lookup_table()
            uv_layer = bm.loops.layers.uv[0]
            islands = HairBakeService.find_uv_islands(bm)
            variant_indices, assignment = HairBakeService._pick_atlas_variants(
                islands, fraction, HairBakeService._island_exposure(islands, exposure) if exposure is not None else None)
            cells = {index: slot for slot, index in enumerate(variant_indices)}
            columns, rows, _aspect = HairBakeService._card_uv_cell_grid(islands, max(1, len(variant_indices)))

            # Two texels of margin inside each cell. The colour dilation bleeds a few
            # pixels outwards, so they would interfere without margin.
            inset = min(0.25, 2.0 / max(1.0, resolution / max(columns, rows)))

            def in_cell(uv, slot):
                column, row = slot % columns, slot // columns
                u = inset + uv.x * (1.0 - 2.0 * inset)
                v = inset + uv.y * (1.0 - 2.0 * inset)
                return ((column + u) / columns, (row + v) / rows)

            final_uvs = {}
            for index, island in enumerate(islands):
                slot = cells.get(index)
                if slot is None:
                    # Not baked itself: after bake it goes to the cell of the variant it was assigned.
                    # During bake, it is placed out of the texture so it does not interfere.
                    slot = cells.get(assignment.get(index))
                    for face in island:
                        if slot is not None:
                            final_uvs[face.index] = [in_cell(loop[uv_layer].uv, slot)
                                                     for loop in face.loops]
                        for loop in face.loops:
                            uv = loop[uv_layer].uv
                            loop[uv_layer].uv = (uv.x + _UV_PARKING_OFFSET, uv.y)
                else:
                    for face in island:
                        for loop in face.loops:
                            loop[uv_layer].uv = in_cell(loop[uv_layer].uv, slot)

            bm.to_mesh(card_obj.data)
            card_obj.data.update()
        finally:
            bm.free()

        return {"final_uvs": final_uvs}

    @staticmethod
    def _shifted(values: "np.ndarray", axis: int, shift: int) -> "np.ndarray":
        """``values`` moved by one pixel along ``axis``, with zeros coming in at the edge."""
        import numpy as np

        out = np.zeros_like(values)
        source = [slice(None)] * values.ndim
        target = [slice(None)] * values.ndim
        if shift > 0:
            source[axis], target[axis] = slice(None, -1), slice(1, None)
        else:
            source[axis], target[axis] = slice(1, None), slice(None, -1)
        out[tuple(target)] = values[tuple(source)]
        return out

    @staticmethod
    def dilate_image_colour(image: bpy.types.Image, passes: int = 4) -> None:
        """Bleed the baked colour a few pixels into the transparent area.

        Prevents mipmapping from mixing the hair against the black surrounding and dark borders around cards.

        Only colour is spread - alpha is left as baked so silhouette stays the same.
        """
        import numpy as np

        width, height = image.size
        if width == 0 or height == 0:
            return
        pixels = HairEditorService.read_image_pixels(image).reshape(height, width, 4)
        colour = pixels[:, :, :3]
        filled = pixels[:, :, 3] > 0.002
        if filled.all() or not filled.any():
            return

        for _ in range(passes):
            weight = filled.astype(np.float32)
            neighbour_colour = np.zeros_like(colour)
            neighbour_weight = np.zeros_like(weight)
            # Not wrapped around, the opposite edge of atlas belongs to another card
            for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
                neighbour_colour += HairBakeService._shifted(colour * weight[:, :, None], axis, shift)
                neighbour_weight += HairBakeService._shifted(weight, axis, shift)
            spread = (~filled) & (neighbour_weight > 0)
            if not spread.any():
                break
            colour[spread] = (neighbour_colour[spread]
                              / neighbour_weight[spread][:, None])
            filled = filled | spread

        pixels[:, :, :3] = colour
        HairEditorService.write_image_pixels(image, pixels)

    @staticmethod
    def apply_card_atlas(card_obj: bpy.types.Object, plan: dict[str, Any]) -> None:
        """Move the cards which were parked outside the atlas onto the variant they were assigned."""
        import bmesh

        bm = bmesh.new()
        unmatched = 0
        try:
            bm.from_mesh(card_obj.data)
            bm.faces.ensure_lookup_table()
            uv_layer = bm.loops.layers.uv[0]

            if "final_uvs" in plan:
                for face in bm.faces:
                    wanted = plan["final_uvs"].get(face.index)
                    if wanted is None:
                        continue
                    if len(wanted) != len(face.loops):
                        unmatched += 1
                        continue
                    for loop, uv in zip(face.loops, wanted):
                        loop[uv_layer].uv = uv
                bm.to_mesh(card_obj.data)
                card_obj.data.update()
                if unmatched:
                    _LOG.warn("Cards left without atlas UVs because the mesh changed", unmatched)
                return

            islands = HairBakeService.find_uv_islands(bm)

            for index, variant_index in plan["assignment"].items():
                if index >= len(islands):
                    continue
                variant_uvs = plan["variant_uvs"].get(variant_index)
                island_loops = [loop for face in islands[index] for loop in face.loops]
                if not variant_uvs or len(island_loops) != len(variant_uvs):
                    # Should not happen as variants are picked per loop-count group precisely
                    unmatched += 1
                    continue
                for loop, uv in zip(island_loops, variant_uvs):
                    loop[uv_layer].uv = uv

            bm.to_mesh(card_obj.data)
            card_obj.data.update()
        finally:
            bm.free()
        if unmatched:
            _LOG.warn("Cards left without atlas UVs because no matching variant was found", unmatched)

    @staticmethod
    def resolve_bake_path(asset_name: str, destination: str, suffix: str = "") -> str:
        if destination:
            destination = bpy.path.abspath(destination)
        if not destination:
            destination = HairBakeService.get_default_bake_directory()
        try:
            os.makedirs(destination, exist_ok=True)
        except Exception as e:
            _LOG.warn("Could not create bake directory, falling back to temp dir", (destination, e))
            destination = tempfile.gettempdir()
        return os.path.join(destination, f"{asset_name}_texture{suffix}.png")

    @staticmethod
    def bake_extra_maps(state: dict[str, Any]) -> dict[str, str]:
        """Bake the optional extra maps by temporarily swapping the hair object material."""
        hair_obj = state["hair_obj"]
        original_hair_materials = [slot.material for slot in hair_obj.material_slots]
        saved_paths = {}
        try:
            for key, (_propname, color_builder) in EXTRA_MAP_BUILDERS.items():
                if not state["wanted_maps"].get(key):
                    continue
                temp_material = HairBakeService._build_emit_material(
                    f"HairBakeExtra_{key}", color_builder, state["shader_options"])
                hair_obj.data.materials.clear()
                hair_obj.data.materials.append(temp_material)

                image = HairBakeService.bake_image(f"{state['asset_name']}_cards_{key}", state["resolution"],
                                    alpha=False, colorspace=_DATA_MAP_COLORSPACE)
                state["bake_texture_node"].image = image
                state["card_material"].node_tree.nodes.active = state["bake_texture_node"]

                HairBakeService.run_bake_passes(state, 'EMIT')

                path = HairBakeService.resolve_bake_path(state["asset_name"], state["destination"], suffix=f"_{key}")
                image.filepath_raw = path
                image.file_format = 'PNG'
                image.save()
                image.filepath = path
                image.source = 'FILE'
                # Some of the textures might end up without material and would not be saved
                image.use_fake_user = True
                saved_paths[key] = path
                state["baked_images"][key] = image

                hair_obj.data.materials.clear()
                bpy.data.materials.remove(temp_material, do_unlink=True)
        finally:
            hair_obj.data.materials.clear()
            for material in original_hair_materials:
                hair_obj.data.materials.append(material)
        return saved_paths

    @staticmethod
    def _white_color(nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, options: dict[str, Any]) -> bpy.types.NodeSocket:
        value = nodes.new(type='ShaderNodeValue')
        value.outputs[0].default_value = 1.0
        value.location = (-200, 0)
        return value.outputs[0]

    @staticmethod
    def _flip_portal_direction(material: bpy.types.Material) -> bool:
        """Negate the ray portal direction, so the capture looks the other way."""
        node = material.node_tree.nodes.get(_PORTAL_DIRECTION_NODE)
        if node is None:
            return False
        current = node.inputs[1].default_value
        node.inputs[1].default_value = (-current[0], -current[1], -current[2])
        return True

    @staticmethod
    def _set_portal_lift(material: bpy.types.Material, scale: float) -> float | None:
        """Move the ray start along the surface normal. Returns the scale it replaced."""
        node = material.node_tree.nodes.get(_PORTAL_LIFT_NODE)
        if node is None:
            return None
        previous = node.inputs['Scale'].default_value
        node.inputs['Scale'].default_value = scale
        return previous

    @staticmethod
    def bake_other_side(state: dict[str, Any]) -> bool:
        """Bake the hair on the far side of each card as well and blend it into the result.

        For double sided bake only.

        """
        import numpy as np

        bake_image = state["bake_image"]
        card_material = state["card_material"]
        hair_obj = state["hair_obj"]
        if not HairBakeService._flip_portal_direction(card_material):
            _LOG.warn("The ray portal has no direction node to flip, so the second side was skipped")
            return False

        # The first shell pass starts above the tips and looks inward. Flipping only the
        # direction would look out into empty space, so the second pass starts just
        # outside the skin and looks outward. The first hit is then the inner side.
        previous_lift = None
        if state.get("target") == cg.BAKE_TARGET_BODY_SHELL:
            shell_height = float(state.get("shell_height") or 0.0)
            inset = shell_height - SHELL_CAPTURE_MARGIN
            if inset < SHELL_CAPTURE_MARGIN:
                inset = shell_height * 0.5
            previous_lift = HairBakeService._set_portal_lift(card_material, -inset)

        original_hair_materials = [slot.material for slot in hair_obj.material_slots]
        colour_image = None
        coverage_image = None
        coverage_material = None
        try:
            # The far side colour, with the own hair materials, same as the first pass was baked
            colour_image = HairBakeService.bake_image(f"{state['asset_name']}_cards_far_colour", state["resolution"],
                                       alpha=True, colorspace='sRGB')
            state["bake_texture_node"].image = colour_image
            card_material.node_tree.nodes.active = state["bake_texture_node"]
            HairBakeService.run_bake_passes(state, 'GLOSSY' if state["glossy"] else 'DIFFUSE')

            # And its coverage, the same way the near side gets alpha
            coverage_material = HairBakeService._build_emit_material(
                "HairBakeFarCoverage", HairBakeService._white_color, state["shader_options"])
            hair_obj.data.materials.clear()
            hair_obj.data.materials.append(coverage_material)
            coverage_image = HairBakeService.bake_image(f"{state['asset_name']}_cards_far_coverage",
                                         state["resolution"], alpha=False,
                                         colorspace=_DATA_MAP_COLORSPACE)
            state["bake_texture_node"].image = coverage_image
            card_material.node_tree.nodes.active = state["bake_texture_node"]
            HairBakeService.run_bake_passes(state, 'EMIT')

            near = HairEditorService.read_image_pixels(bake_image).reshape(-1, 4)
            far = HairEditorService.read_image_pixels(colour_image).reshape(-1, 4)
            far_coverage = np.clip(
                HairEditorService.read_image_pixels(coverage_image).reshape(-1, 4)[:, :3].max(axis=1),
                0.0, 1.0)

            near_coverage = near[:, 3]

            near_weight, far_weight = near_coverage, far_coverage
            total = near_weight + far_weight
            blended = near.copy()
            lit = total > 1.0 / 255.0
            blended[lit, :3] = ((near[lit, :3] * near_weight[lit, None]
                                 + far[lit, :3] * far_weight[lit, None])
                                / total[lit, None])
            blended[:, 3] = np.maximum(near_coverage, far_coverage)
            HairEditorService.write_image_pixels(bake_image, blended)

            gained = float((blended[:, 3] > 0.5).mean() - (near_coverage > 0.5).mean())
            _LOG.debug("Blended in the far side of the cards", gained)
            return True
        finally:
            state["bake_texture_node"].image = bake_image
            HairBakeService._flip_portal_direction(card_material)
            if previous_lift is not None:
                HairBakeService._set_portal_lift(card_material, previous_lift)
            hair_obj.data.materials.clear()
            for material in original_hair_materials:
                hair_obj.data.materials.append(material)
            if coverage_material is not None:
                bpy.data.materials.remove(coverage_material, do_unlink=True)
            for image in (colour_image, coverage_image):
                if image is not None:
                    bpy.data.images.remove(image, do_unlink=True)

    @staticmethod
    def bake_coverage_into_alpha(state: dict[str, Any]) -> None:
        """Replace alpha of the colour texture with a mask of where the hair actually is."""
        import numpy as np

        hair_obj = state["hair_obj"]
        bake_image = state["bake_image"]
        original_hair_materials = [slot.material for slot in hair_obj.material_slots]
        coverage_material = None
        coverage_image = None
        try:
            coverage_material = HairBakeService._build_emit_material(
                "HairBakeCoverage", HairBakeService._white_color, state["shader_options"])
            hair_obj.data.materials.clear()
            hair_obj.data.materials.append(coverage_material)

            coverage_image = HairBakeService.bake_image(f"{state['asset_name']}_cards_coverage", state["resolution"],
                                         alpha=False, colorspace=_DATA_MAP_COLORSPACE)
            state["bake_texture_node"].image = coverage_image
            state["card_material"].node_tree.nodes.active = state["bake_texture_node"]

            HairBakeService.run_bake_passes(state, 'EMIT')

            coverage = HairEditorService.read_image_pixels(coverage_image).reshape(-1, 4)
            pixels = HairEditorService.read_image_pixels(bake_image).reshape(-1, 4)
            pixels[:, 3] = np.clip(coverage[:, :3].max(axis=1), 0.0, 1.0)
            HairEditorService.write_image_pixels(bake_image, pixels)
        finally:
            state["bake_texture_node"].image = bake_image
            hair_obj.data.materials.clear()
            for material in original_hair_materials:
                hair_obj.data.materials.append(material)
            if coverage_image is not None:
                bpy.data.images.remove(coverage_image, do_unlink=True)
            if coverage_material is not None:
                bpy.data.materials.remove(coverage_material, do_unlink=True)

    @staticmethod
    def run_bake_passes(state: dict[str, Any], bake_type: str) -> None:
        """Run the bake."""
        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(state["bake_target"])
        bpy.ops.object.bake(type=bake_type)

    @staticmethod
    def _guarded(description: str) -> Callable[[Callable[[], Any]], None]:
        """Wrap each part of cleanup into try except, so one error does not break restoration of other settings."""
        def decorate(function):
            try:
                function()
            except Exception as e:
                _LOG.warn(f"Could not {description} while restoring the scene after baking", e)
        return decorate

    @staticmethod
    def restore_environment(state: dict[str, Any], keep_card_material: bool) -> None:
        """Undo everything _prepare() did to the scene."""
        for obj, visibility in state.get("hidden_objects", []):
            @HairBakeService._guarded("unhide an object")
            def _restore(obj=obj, visibility=visibility):
                obj.hide_render, obj.hide_viewport = visibility

        bake_target = state.get("bake_target")
        if bake_target is not None:
            for key, value in state.get("original_card_visibility", {}).items():
                @HairBakeService._guarded("restore card ray visibility")
                def _restore(key=key, value=value):
                    setattr(bake_target, key, value)

            @HairBakeService._guarded("unhide the cards")
            def _unhide():
                # Group baking hides the whole card object in favour of the per-group copies
                bake_target.hide_render = False

        for caster, was_casting in state.pop("shadow_casters", []):
            @HairBakeService._guarded("restore an object's shadow casting")
            def _restore(caster=caster, was_casting=was_casting):
                caster.visible_shadow = was_casting

        if "rest_posed_rig" in state:
            rig, previous_pose_position = state.pop("rest_posed_rig")

            @HairBakeService._guarded("restore the rig's pose position")
            def _restore(rig=rig, previous=previous_pose_position):
                rig.data.pose_position = previous

        for obj, materials in reversed(state.get("swapped_materials", [])):
            @HairBakeService._guarded("restore an object's materials")
            def _restore(obj=obj, materials=materials):
                obj.data.materials.clear()
                for material in materials:
                    obj.data.materials.append(material)
        state["swapped_materials"] = []

        if "original_hair_materials" in state:
            @HairBakeService._guarded("restore the hair's own materials")
            def _restore():
                hair_obj = state["hair_obj"]
                hair_obj.data.materials.clear()
                for material in state["original_hair_materials"]:
                    hair_obj.data.materials.append(material)
            for material in state.pop("range_limited_materials", []):
                @HairBakeService._guarded("remove a range limited material copy")
                def _remove(material=material):
                    if material is not None and material.users == 0:
                        bpy.data.materials.remove(material, do_unlink=True)

        for key in ["basemesh_material"] + ([] if keep_card_material else ["card_material"]):
            material = state.get(key)
            if material is not None:
                state[key] = None
                @HairBakeService._guarded(f"remove the temporary {key}")
                def _remove(material=material):
                    bpy.data.materials.remove(material, do_unlink=True)

        for light_obj in state.get("lights", []):
            @HairBakeService._guarded("remove a bake light")
            def _remove(light_obj=light_obj):
                light_data = light_obj.data
                bpy.data.objects.remove(light_obj, do_unlink=True)
                if light_data is not None and light_data.users == 0:
                    bpy.data.lights.remove(light_data)
        state["lights"] = []

        if "scene_settings" in state:
            @HairBakeService._guarded("restore the render settings")
            def _restore():
                HairBakeService._restore_scene_settings(state["scene"], state["scene_settings"])

        @HairBakeService._guarded("reselect the character")
        def _reselect():
            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(state["basemesh"])

    @staticmethod
    def bake_image(name: str, resolution: int, alpha: bool, colorspace: str) -> bpy.types.Image:
        """An image to bake into. Reuses the datablock of that name if there already is one."""
        image = bpy.data.images.get(name)
        if image is None:
            image = bpy.data.images.new(name, alpha=alpha, width=resolution, height=resolution)
        else:
            image.source = 'GENERATED'
            image.generated_color = (0.0, 0.0, 0.0, 0.0)
            image.generated_width = resolution
            image.generated_height = resolution
            image.alpha_mode = 'STRAIGHT' if alpha else 'NONE'
            image.scale(resolution, resolution)
        image.colorspace_settings.name = colorspace
        return image

    @staticmethod
    def push_bake_undo_step() -> None:
        """Make the finished bake a single undo step of its own.

        The operator cannot let blender do it: on the interactive path it returns as soon as
        the background render has been started, so a step pushed then would capture the half-prepared
        scene instead of the result.

        Undo is unavailable in background mode, where this is simply a no-op.
        """
        try:
            bpy.ops.ed.undo_push(message="Bake hair cards")
        except Exception as e:
            _LOG.debug("Could not push an undo step for the bake", e)

    @staticmethod
    def state_is_alive(state: dict[str, Any]) -> bool:
        """Do the datablocks the bake was working on still exist?

        Before completion of bake, user could invoke undo, which could delete objects used by bake,
        causing reference error once touched.
        """
        for key in ("basemesh", "hair_obj", "live_card_obj", "bake_target",
                    "card_material", "basemesh_material", "bake_image"):
            value = state.get(key)
            if value is None:
                continue
            try:
                _unused = value.name
            except Exception:
                _LOG.warn("The bake's working state no longer refers to live data", key)
                return False
        return True

    @staticmethod
    def remove_orphan_geometry(datablock: bpy.types.ID | None) -> None:
        """Drop a mesh/curves datablock which nothing refers to any more."""
        if datablock is None:
            return
        if datablock.users > 0:
            if datablock.use_fake_user or any(bpy.data.user_map(subset=[datablock]).values()):
                return
            _LOG.debug("Clearing a stale user count before removing orphaned geometry", datablock.name)
            datablock.user_clear()
        if isinstance(datablock, bpy.types.Mesh):
            bpy.data.meshes.remove(datablock)
        elif isinstance(datablock, bpy.types.Curves):
            bpy.data.hair_curves.remove(datablock)

    @staticmethod
    def discard_bake_target(state: dict[str, Any]) -> None:
        """Throw away the working copy and everything that was created only for it."""
        bake_target = state.get("bake_target")
        if state.get("direct_to_body"):
            # The bake target is the body itself here so it cannot be thrown away.
            bake_target = None
        if bake_target is not None:
            state["bake_target"] = None
            leftovers = [bake_target.data] + state.get("orphaned_data", [])
            bpy.data.objects.remove(bake_target, do_unlink=True)
            for datablock in leftovers:
                HairBakeService.remove_orphan_geometry(datablock)

        # Ray portal material is the last thing holding on the bake image.
        card_material = state.get("card_material")
        if card_material is not None:
            state["card_material"] = None
            bpy.data.materials.remove(card_material, do_unlink=True)

        bake_image = state.get("bake_image")
        if bake_image is not None and bake_image.users == 0 and not bake_image.use_fake_user:
            state["bake_image"] = None
            bpy.data.images.remove(bake_image, do_unlink=True)

    @staticmethod
    def _restore_scene_settings(scene: bpy.types.Scene, settings: dict[str, Any]) -> None:
        scene.render.engine = settings["engine"]
        scene.render.film_transparent = settings["film_transparent"]
        for key, value in settings["cycles"].items():
            setattr(scene.cycles, key, value)
        for key, value in settings.get("bake", {}).items():
            setattr(scene.render.bake, key, value)

        world = scene.world
        if settings["background"] is not None and world and world.use_nodes and "Background" in world.node_tree.nodes:
            world.node_tree.nodes["Background"].inputs[0].default_value = settings["background"]


EXTRA_MAP_BUILDERS = collections.OrderedDict([
    ("normal", ("cards_bake_normal", HairBakeService._normal_color)),
    ("ao", ("cards_bake_ao", HairBakeService._ao_color)),
    ("root_tip", ("cards_bake_root_tip", HairBakeService._root_tip_color)),
    ("flow", ("cards_bake_flow", HairBakeService._flow_color)),
    ("depth", ("cards_bake_depth", HairBakeService._depth_color)),
    ("side_on", ("cards_bake_side_on", HairBakeService._side_on_color)),
    ])
