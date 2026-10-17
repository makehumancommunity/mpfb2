# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025 - updated 06.10.2026
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
                              CARDS_MODIFIER_NAME, get_default_bake_directory, set_cards_flag,
                              snapshot_cards_properties, remember_cards_settings,
                              get_bake_target, get_atlas_fraction, get_light_mode,
                              resolve_custom_surface, remember_custom_mesh_materials,
                              get_light_strength,
                              get_cards_mode,
                              resolve_body_surface,
                              body_surfaces_to_hide_behind, body_has_material)
from .. import bodyoverlay
from .. import cardgenerators as cg

import bpy, os, tempfile, collections
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

# When baking on body shell ray start position and length are calculated based on hair geometry.
# To avoid missing start/end of strand due to float precision on the boundary, there is this tolerance.
_SHELL_CAPTURE_MARGIN = 0.002

# With atlas baking enabled, only certain cards are baked.
# UV space has coordinates 0..1, so cards with value like 10 will not interfere
_UV_PARKING_OFFSET = 10.0


_PORTAL_DIRECTION_NODE = "PortalDirection"
_PORTAL_LIFT_NODE = "PortalLift"


def _build_ray_portal_material(capture_depth=0.0, outward=False):
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


def _limit_shader_to_range(node_tree, shader_socket, ray_range):
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


def _range_limited_copies(hair_obj, ray_range):
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
            _limit_shader_to_range(copy.node_tree, original_socket, ray_range), surface)
        copies.append(copy)
    return copies

def _build_holdout_material():
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

def _build_emit_material(name, color_socket_builder, options):
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
        surface = _limit_shader_to_range(material.node_tree, surface, options["ray_range"])
    links.new(surface, output.inputs['Surface'])
    return material


def _encode_direction(nodes, links, vector_socket, vector_type):
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


def _normal_color(nodes, links, options):
    """The hair's surface normal, in object space, encoded as a colour (0.5 = no deviation)."""

    geometry = nodes.new(type='ShaderNodeNewGeometry')
    geometry.location = (-600, 0)
    return _encode_direction(nodes, links, geometry.outputs['Normal'], 'NORMAL')


def _flow_color(nodes, links, options):
    """The direction the hair runs, in object space, for an anisotropic hair shader to align to."""
    geometry = nodes.new(type='ShaderNodeNewGeometry')
    geometry.location = (-600, 0)
    return _encode_direction(nodes, links, geometry.outputs['Tangent'], 'VECTOR')


def _depth_color(nodes, links, options):
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


def _ao_color(nodes, links, options):
    ao_node = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao_node.samples = 16
    ao_node.inputs['Distance'].default_value = 0.05
    return ao_node.outputs['Color']


def _root_tip_color(nodes, links, options):
    hair_info = nodes.new(type='ShaderNodeHairInfo')
    return hair_info.outputs['Intercept']


def _side_on_color(nodes, links, options):
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


_EXTRA_MAP_BUILDERS = collections.OrderedDict([
    ("normal", ("cards_bake_normal", _normal_color)),
    ("ao", ("cards_bake_ao", _ao_color)),
    ("root_tip", ("cards_bake_root_tip", _root_tip_color)),
    ("flow", ("cards_bake_flow", _flow_color)),
    ("depth", ("cards_bake_depth", _depth_color)),
    ("side_on", ("cards_bake_side_on", _side_on_color)),
    ])

# Every map except the colour texture carries numbers, not colors
_DATA_MAP_COLORSPACE = 'Non-Color'


def _find_uv_islands(bm):
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


def _hair_points_world(hair_obj):
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


def _card_vertex_sparsity(card_obj, hair_obj, neighbours=8):
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

    hair_points = _hair_points_world(hair_obj)
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


def _island_exposure(islands, sparsity):
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


def _pick_atlas_variants(islands, fraction, exposure=None):
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
        for position, index in enumerate(members):
            if index not in chosen:
                assignment[index] = chosen[position % len(chosen)]
    return sorted(variant_indices), assignment


def _smart_project_selection(select_all=False):
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


def _prepare_card_atlas(card_obj, fraction, exposure=None):
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

        islands = _find_uv_islands(bm)
        variant_indices, assignment = _pick_atlas_variants(
            islands, fraction, _island_exposure(islands, exposure) if exposure is not None else None)
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
    _smart_project_selection()

    bm = bmesh.new()
    try:
        bm.from_mesh(card_obj.data)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv[0]
        islands = _find_uv_islands(bm)

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


def _has_generated_card_uvs(bm, islands, uv_layer):
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


def _card_uv_cell_grid(islands, cell_count):
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


def _pack_card_uvs_into_grid(card_obj, fraction, resolution=1024, exposure=None):
    """Pack the generator's own per-card UVs into a grid of atlas cells.

    Returns a plan for _apply_card_atlas(), keyed by face index so island ordering cannot throw it
    off.
    """
    import bmesh

    bm = bmesh.new()
    try:
        bm.from_mesh(card_obj.data)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv[0]
        islands = _find_uv_islands(bm)
        variant_indices, assignment = _pick_atlas_variants(
            islands, fraction, _island_exposure(islands, exposure) if exposure is not None else None)
        cells = {index: slot for slot, index in enumerate(variant_indices)}
        columns, rows, _aspect = _card_uv_cell_grid(islands, max(1, len(variant_indices)))

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


def _dilate_image_colour(image, passes=4):
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
        for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
            neighbour_colour += np.roll(colour * weight[:, :, None], shift, axis=axis)
            neighbour_weight += np.roll(weight, shift, axis=axis)
        spread = (~filled) & (neighbour_weight > 0)
        if not spread.any():
            break
        colour[spread] = (neighbour_colour[spread]
                          / neighbour_weight[spread][:, None])
        filled = filled | spread

    pixels[:, :, :3] = colour
    HairEditorService.write_image_pixels(image, pixels)


def _apply_card_atlas(card_obj, plan):
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

        islands = _find_uv_islands(bm)

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


def resolve_bake_path(asset_name, destination, suffix=""):
    if destination:
        destination = bpy.path.abspath(destination)
    if not destination:
        destination = get_default_bake_directory()
    try:
        os.makedirs(destination, exist_ok=True)
    except Exception as e:
        _LOG.warn("Could not create bake directory, falling back to temp dir", (destination, e))
        destination = tempfile.gettempdir()
    return os.path.join(destination, f"{asset_name}_texture{suffix}.png")


def _bake_extra_maps(state):
    """Bake the optional extra maps by temporarily swapping the hair object material."""
    hair_obj = state["hair_obj"]
    original_hair_materials = [slot.material for slot in hair_obj.material_slots]
    saved_paths = {}
    try:
        for key, (_propname, color_builder) in _EXTRA_MAP_BUILDERS.items():
            if not state["wanted_maps"].get(key):
                continue
            temp_material = _build_emit_material(
                f"HairBakeExtra_{key}", color_builder, state["shader_options"])
            hair_obj.data.materials.clear()
            hair_obj.data.materials.append(temp_material)

            image = _bake_image(f"{state['asset_name']}_cards_{key}", state["resolution"],
                                alpha=False, colorspace=_DATA_MAP_COLORSPACE)
            state["bake_texture_node"].image = image
            state["card_material"].node_tree.nodes.active = state["bake_texture_node"]

            _run_bake_passes(state, 'EMIT')

            path = resolve_bake_path(state["asset_name"], state["destination"], suffix=f"_{key}")
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


def _white_color(nodes, links, options):
    value = nodes.new(type='ShaderNodeValue')
    value.outputs[0].default_value = 1.0
    value.location = (-200, 0)
    return value.outputs[0]


def _flip_portal_direction(material):
    """Negate the ray portal direction, so the capture looks the other way."""
    node = material.node_tree.nodes.get(_PORTAL_DIRECTION_NODE)
    if node is None:
        return False
    current = node.inputs[1].default_value
    node.inputs[1].default_value = (-current[0], -current[1], -current[2])
    return True


def _set_portal_lift(material, scale):
    """Move the ray start along the surface normal. Returns the scale it replaced."""
    node = material.node_tree.nodes.get(_PORTAL_LIFT_NODE)
    if node is None:
        return None
    previous = node.inputs['Scale'].default_value
    node.inputs['Scale'].default_value = scale
    return previous


def _bake_other_side(state):
    """Bake the hair on the far side of each card as well and blend it into the result.

    For double sided bake only.

    """
    import numpy as np

    bake_image = state["bake_image"]
    card_material = state["card_material"]
    hair_obj = state["hair_obj"]
    if not _flip_portal_direction(card_material):
        _LOG.warn("The ray portal has no direction node to flip, so the second side was skipped")
        return False

    # The first shell pass starts above the tips and looks inward. Flipping only the
    # direction would look out into empty space, so the second pass starts just
    # outside the skin and looks outward. The first hit is then the inner side.
    previous_lift = None
    if state.get("target") == cg.BAKE_TARGET_BODY_SHELL:
        shell_height = float(state.get("shell_height") or 0.0)
        inset = shell_height - _SHELL_CAPTURE_MARGIN
        if inset < _SHELL_CAPTURE_MARGIN:
            inset = shell_height * 0.5
        previous_lift = _set_portal_lift(card_material, -inset)

    original_hair_materials = [slot.material for slot in hair_obj.material_slots]
    colour_image = None
    coverage_image = None
    coverage_material = None
    try:
        # The far side colour, with the own hair materials, same as the first pass was baked
        colour_image = _bake_image(f"{state['asset_name']}_cards_far_colour", state["resolution"],
                                   alpha=True, colorspace='sRGB')
        state["bake_texture_node"].image = colour_image
        card_material.node_tree.nodes.active = state["bake_texture_node"]
        _run_bake_passes(state, 'GLOSSY' if state["glossy"] else 'DIFFUSE')

        # And its coverage, the same way the near side gets alpha
        coverage_material = _build_emit_material(
            "HairBakeFarCoverage", _white_color, state["shader_options"])
        hair_obj.data.materials.clear()
        hair_obj.data.materials.append(coverage_material)
        coverage_image = _bake_image(f"{state['asset_name']}_cards_far_coverage",
                                     state["resolution"], alpha=False,
                                     colorspace=_DATA_MAP_COLORSPACE)
        state["bake_texture_node"].image = coverage_image
        card_material.node_tree.nodes.active = state["bake_texture_node"]
        _run_bake_passes(state, 'EMIT')

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
        _flip_portal_direction(card_material)
        if previous_lift is not None:
            _set_portal_lift(card_material, previous_lift)
        hair_obj.data.materials.clear()
        for material in original_hair_materials:
            hair_obj.data.materials.append(material)
        if coverage_material is not None:
            bpy.data.materials.remove(coverage_material, do_unlink=True)
        for image in (colour_image, coverage_image):
            if image is not None:
                bpy.data.images.remove(image, do_unlink=True)


def _bake_coverage_into_alpha(state):
    """Replace alpha of the colour texture with a mask of where the hair actually is."""
    import numpy as np

    hair_obj = state["hair_obj"]
    bake_image = state["bake_image"]
    original_hair_materials = [slot.material for slot in hair_obj.material_slots]
    coverage_material = None
    coverage_image = None
    try:
        coverage_material = _build_emit_material(
            "HairBakeCoverage", _white_color, state["shader_options"])
        hair_obj.data.materials.clear()
        hair_obj.data.materials.append(coverage_material)

        coverage_image = _bake_image(f"{state['asset_name']}_cards_coverage", state["resolution"],
                                     alpha=False, colorspace=_DATA_MAP_COLORSPACE)
        state["bake_texture_node"].image = coverage_image
        state["card_material"].node_tree.nodes.active = state["bake_texture_node"]

        _run_bake_passes(state, 'EMIT')

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


def _run_bake_passes(state, bake_type):
    """Run the bake."""
    ObjectService.deselect_and_deactivate_all()
    ObjectService.activate_blender_object(state["bake_target"])
    bpy.ops.object.bake(type=bake_type)


def _guarded(description):
    """Wrap each part of cleanup into try except, so one error does not break restoration of other settings."""
    def decorate(function):
        try:
            function()
        except Exception as e:
            _LOG.warn(f"Could not {description} while restoring the scene after baking", e)
    return decorate


def _restore_environment(state, keep_card_material):
    """Undo everything _prepare() did to the scene."""
    for obj, visibility in state.get("hidden_objects", []):
        @_guarded("unhide an object")
        def _restore(obj=obj, visibility=visibility):
            obj.hide_render, obj.hide_viewport = visibility

    bake_target = state.get("bake_target")
    if bake_target is not None:
        for key, value in state.get("original_card_visibility", {}).items():
            @_guarded("restore card ray visibility")
            def _restore(key=key, value=value):
                setattr(bake_target, key, value)

        @_guarded("unhide the cards")
        def _unhide():
            # Group baking hides the whole card object in favour of the per-group copies
            bake_target.hide_render = False

    for caster, was_casting in state.pop("shadow_casters", []):
        @_guarded("restore an object's shadow casting")
        def _restore(caster=caster, was_casting=was_casting):
            caster.visible_shadow = was_casting

    if "rest_posed_rig" in state:
        rig, previous_pose_position = state.pop("rest_posed_rig")

        @_guarded("restore the rig's pose position")
        def _restore(rig=rig, previous=previous_pose_position):
            rig.data.pose_position = previous

    for obj, materials in reversed(state.get("swapped_materials", [])):
        @_guarded("restore an object's materials")
        def _restore(obj=obj, materials=materials):
            obj.data.materials.clear()
            for material in materials:
                obj.data.materials.append(material)
    state["swapped_materials"] = []

    if "original_hair_materials" in state:
        @_guarded("restore the hair's own materials")
        def _restore():
            hair_obj = state["hair_obj"]
            hair_obj.data.materials.clear()
            for material in state["original_hair_materials"]:
                hair_obj.data.materials.append(material)
        for material in state.pop("range_limited_materials", []):
            @_guarded("remove a range limited material copy")
            def _remove(material=material):
                if material is not None and material.users == 0:
                    bpy.data.materials.remove(material, do_unlink=True)

    for key in ["basemesh_material"] + ([] if keep_card_material else ["card_material"]):
        material = state.get(key)
        if material is not None:
            state[key] = None
            @_guarded(f"remove the temporary {key}")
            def _remove(material=material):
                bpy.data.materials.remove(material, do_unlink=True)

    for light_obj in state.get("lights", []):
        @_guarded("remove a bake light")
        def _remove(light_obj=light_obj):
            light_data = light_obj.data
            bpy.data.objects.remove(light_obj, do_unlink=True)
            if light_data is not None and light_data.users == 0:
                bpy.data.lights.remove(light_data)
    state["lights"] = []

    if "scene_settings" in state:
        @_guarded("restore the render settings")
        def _restore():
            _restore_scene_settings(state["scene"], state["scene_settings"])

    @_guarded("reselect the character")
    def _reselect():
        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(state["basemesh"])


def _bake_image(name, resolution, alpha, colorspace):
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


def _push_bake_undo_step():
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


def _state_is_alive(state):
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


def _finish(state, bake_succeeded):
    """Everything that happens once the main bake call has finished (or failed/was cancelled)."""
    if not _state_is_alive(state):
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
                _bake_coverage_into_alpha(state)
            except Exception as e:
                _LOG.error("Could not bake the hair coverage mask into the alpha channel", e)
                report({'WARNING'}, f"The alpha channel could not be baked: {e}")

            if state.get("double_sided"):
                try:
                    _bake_other_side(state)
                except Exception as e:
                    _LOG.error("Could not bake the far side of the cards; keeping the near one", e)
                    report({'WARNING'},
                           f"The second side failed, so only the near side was baked: {e}")

            _dilate_image_colour(bake_image)

            bake_path = resolve_bake_path(asset_name, state["destination"])
            bake_image.filepath_raw = bake_path
            bake_image.file_format = 'PNG'
            bake_image.save()
            bake_image.filepath = bake_path
            bake_image.source = 'FILE'

            # Failure in optional maps bake must not throw the successful main pass away.
            try:
                extra_paths = _bake_extra_maps(state)
            except Exception as e:
                _LOG.error("Could not bake the extra maps; keeping the main texture", e)
                report({'WARNING'}, f"The colour texture was baked, but the extra maps failed: {e}")

            if state["atlas_plan"] is not None:
                _apply_card_atlas(bake_target, state["atlas_plan"])

            if not state["direct_to_body"]:
                fade_attribute = None
                if state["edge_fade"]:
                    if cg.store_shell_edge_fade(bake_target.data, state["edge_fade_width"]):
                        fade_attribute = cg.SHELL_EDGE_FADE_ATTRIBUTE
                    else:
                        _LOG.warn("The shell has no border to fade towards, so the edge fade was "
                                  "skipped", bake_target.name)
                        report({'WARNING'},
                               "This shell has no open edge, so there was nothing to fade")
                baked_material = bodyoverlay.build_baked_material(
                    f"{asset_name}_baked", state["baked_images"],
                    edge_fade_attribute=fade_attribute)
                bake_target.data.materials.clear()
                bake_target.data.materials.append(baked_material)

            success = True
    except Exception as e:
        _LOG.error("Failed while wrapping up the bake", e)
    finally:
        _restore_environment(state, keep_card_material=not success)

    if not success:
        _discard_bake_target(state)
        report({'ERROR'}, "Baking failed or was cancelled; nothing was replaced")
        return False

    if state["direct_to_body"]:
        # No card object to swap in; the result is a shader blended over the skin.
        applied = bodyoverlay.apply_overlay(state["body_surface"], asset_name, state["baked_images"])
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
            baked_material = bodyoverlay.build_baked_material(f"{asset_name}_baked",
                                                              state["baked_images"])
        # The original materials kept as a backup
        remember_custom_mesh_materials(custom_surface)
        custom_surface.data.materials.clear()
        custom_surface.data.materials.append(baked_material)
        _discard_bake_target(state)
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
            _remove_orphan_geometry(datablock)

        bake_target.name = f"{asset_name}{CARDS_OBJECT_SUFFIX}"

        if state["target"] == cg.BAKE_TARGET_BODY_SHELL:
            # Converting to a mesh applied every modifier including the armature, so shell no longer moves with the character.
            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
            if rig is not None:
                try:
                    cg.weight_body_shell_to_rig(bake_target, state["body_surface"], rig)
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


def _remove_orphan_geometry(datablock):
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


def _discard_bake_target(state):
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
            _remove_orphan_geometry(datablock)

    # Ray portal material is the last thing holding on the bake image.
    card_material = state.get("card_material")
    if card_material is not None:
        state["card_material"] = None
        bpy.data.materials.remove(card_material, do_unlink=True)

    bake_image = state.get("bake_image")
    if bake_image is not None and bake_image.users == 0 and not bake_image.use_fake_user:
        state["bake_image"] = None
        bpy.data.images.remove(bake_image, do_unlink=True)


def _restore_scene_settings(scene, settings):
    scene.render.engine = settings["engine"]
    scene.render.film_transparent = settings["film_transparent"]
    for key, value in settings["cycles"].items():
        setattr(scene.cycles, key, value)
    for key, value in settings.get("bake", {}).items():
        setattr(scene.render.bake, key, value)

    world = scene.world
    if settings["background"] is not None and world and world.use_nodes and "Background" in world.node_tree.nodes:
        world.node_tree.nodes["Background"].inputs[0].default_value = settings["background"]


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
            exposure = _card_vertex_sparsity(bake_target, hair_obj)

        generated_uvs = False
        island_count = 0
        if prefer_generated_uvs:
            bm = bmesh.new()
            try:
                bm.from_mesh(bake_target.data)
                bm.faces.ensure_lookup_table()
                uv_layer = bm.loops.layers.uv[0] if bm.loops.layers.uv else None
                islands = _find_uv_islands(bm)
                island_count = len(islands)
                generated_uvs = _has_generated_card_uvs(bm, islands, uv_layer)
            finally:
                bm.free()

        if generated_uvs:
            _LOG.debug("Packing the generator's own UV layout into the atlas")
            return _pack_card_uvs_into_grid(bake_target, atlas_fraction, resolution,
                                            exposure=exposure), orphaned

        _LOG.debug("Unwrapping without a generated UV layout",
                   (bake_target.name, prefer_generated_uvs, island_count))
        if prefer_generated_uvs and island_count > 1:
            self.report({'WARNING'},
                        "These cards have no generated UV layout, so they were unwrapped - "
                        "individual cards may come out rotated")

        if atlas_fraction >= 0.999:
            _smart_project_selection(select_all=True)
            return None, orphaned

        return _prepare_card_atlas(bake_target, atlas_fraction, exposure=exposure), orphaned

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

        share = cg.light_base_energy(mode) * strength
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
            for key, (propname, _builder) in _EXTRA_MAP_BUILDERS.items()
            }
        # The end-on cutoff of the volume shell is built out of these two maps, so they are forced.
        # Not for a direct body bake.
        if cards_mode == cg.CARDS_MODE_SHELL and target != cg.BAKE_TARGET_BODY_DIRECT:
            wanted_maps["side_on"] = True
            wanted_maps["root_tip"] = True
        analytic_uvs = properties.get_value(f"{asset_name}_cards_analytic_uvs", False, entity_reference=basemesh)
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
            extent = cg.hair_extent_above_surface(
                body_surface, hair_obj, context.evaluated_depsgraph_get())
            above_shell = max(0.0, extent - shell_height)
            if above_shell > 0.0:
                capture_depth += above_shell + _SHELL_CAPTURE_MARGIN
                _LOG.debug("Body shell capture lifted above the hair",
                           (extent, shell_height, capture_depth))

            # The forced range limit has to reach from the lifted start through the hair to the skin.
            reach = capture_depth + shell_height + _SHELL_CAPTURE_MARGIN
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
                state["range_limited_materials"] = _range_limited_copies(hair_obj, ray_range)
                hair_obj.data.materials.clear()
                for material in state["range_limited_materials"]:
                    hair_obj.data.materials.append(material)

            state["original_card_visibility"] = {key: getattr(bake_target, key) for key in _RAY_VISIBILITY}
            state["scene_settings"] = self._store_scene_settings(scene)

            # Everything but the character, the hair and the cards is hidden, as the cards capture whatever is behind them.
            # Both flags are saved, since visible_get() only covers the viewport.
            hidden_objects = []
            keep_visible = {basemesh.name, hair_obj.name, bake_target.name, body_surface.name}
            # Lights are not captured by the cards, so with the current scene lighting they stay on
            use_scene_lighting = glossy and light_mode == cg.LIGHT_MODE_SCENE
            for obj in bpy.data.objects:
                if obj.name in keep_visible:
                    continue
                if use_scene_lighting and obj.type == 'LIGHT':
                    continue
                if obj.visible_get():
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
            if use_scene_lighting and not any(obj.type == 'LIGHT' and obj.visible_get() for obj in scene.objects):
                self.report({'WARNING'}, "Baking with the current scene lighting, but there are no visible "
                                         "lights in the scene. Only the world will light the hair")

            state["card_material"] = _build_ray_portal_material(capture_depth, outward=direct_to_body)
            if direct_to_body:
                # The target is the body itself, so its skin has to come back afterwards.
                swap_materials(bake_target, state["card_material"])
            else:
                # Not recorded as a swap - the restore would put the original materials back over the baked result.
                bake_target.data.materials.clear()
                bake_target.data.materials.append(state["card_material"])

            state["bake_image"] = _bake_image(f"{asset_name}_cards_texture", resolution,
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
                state["basemesh_material"] = _build_holdout_material()
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
            _restore_environment(state, keep_card_material=False)
            _discard_bake_target(state)
            self.report({'ERROR'}, f"Could not set the scene up for baking: {e}")
            return None

        return state

    def hardened_execute(self, context):
        """Fully synchronous path, used by scripts/tests and whenever invoke() is bypassed."""
        _LOG.enter()

        state = self._prepare(context)
        if state is None:
            return {'CANCELLED'}

        self.report({'INFO'}, "Baking cards... It might take a while")
        bake_succeeded = False
        try:
            _run_bake_passes(state, 'GLOSSY' if state["glossy"] else 'DIFFUSE')
            bake_succeeded = True
        except Exception as e:
            _LOG.error("Bake call raised an exception", e)

        if not _finish(state, bake_succeeded):
            return {'CANCELLED'}
        _push_bake_undo_step()
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

        # The operator is freed after invoke returns, so nothing that runs later may use it.
        state["report"] = lambda level, message: _LOG.info(f"{'/'.join(sorted(level))}: {message}")

        self.report({'INFO'}, "Baking cards in the background...")

        # The post-bake pass edits images and materials, which is not safe inside an app handler
        # while the viewport may be syncing - it caused a crash in EEVEE.
        # So the handler only queues the work on a timer, which runs from the main loop.
        pending = {"finish": None}

        def _queue_finish(succeeded):
            def _finish_later():
                pending["finish"] = None
                _unregister(scene_guards=True)
                try:
                    if _finish(state, succeeded):
                        _push_bake_undo_step()
                except Exception as e:
                    _LOG.crash("Finishing the background bake failed", e)
                return None  # one shot

            pending["finish"] = _finish_later
            bpy.app.timers.register(_finish_later)

        def _on_complete(*_args):
            _unregister(scene_guards=False)
            _queue_finish(True)

        def _on_cancel(*_args):
            _unregister(scene_guards=False)
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
            _LOG.warn("The scene was replaced while a bake was pending; abandoning the bake state")

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

        started = None
        try:
            started = bpy.ops.object.bake('INVOKE_DEFAULT', type='GLOSSY' if state["glossy"] else 'DIFFUSE')
        except Exception as e:
            _LOG.error("Could not start background bake, falling back to a blocking bake", e)

        # A refused INVOKE_DEFAULT can either raise or return CANCELLED, in which case no handler will fire.
        if started is None or 'RUNNING_MODAL' not in started:
            _unregister(scene_guards=True)
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
            _push_bake_undo_step()

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_BakeHair_Operator)
