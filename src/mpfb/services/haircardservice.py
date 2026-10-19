# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         19.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  builders for the geometry node groups behind each hair cards generation mode
#               and meshes build in python for cluster-based modes
# ------------------------------------------------------------------------------
"""One geometry-nodes builder per ``cards_mode`` value (except CLUSTER_BOX, which builds a static mesh in python).

Mode and strand-selection method change the node graph itself, so they only apply on regenerate.
Every other parameter is a live modifier input socket.
"""

import math

import bpy
from contextlib import contextmanager
from mathutils import Vector

# Shared with hairproperties
CLUSTER_RIBBON_PROFILE_STEPS = 5

CARDS_MODE_TILES = "TILES"

CARDS_MODE_RIBBON = "RIBBON"

CARDS_MODE_SHELL = "SHELL"

CARDS_MODE_CLUSTER_BOX = "CLUSTER_BOX"

CARDS_MODE_CLUSTER_RIBBON = "CLUSTER_RIBBON"

CARDS_MODE_ITEMS = [
    (CARDS_MODE_TILES, "Random tiles", "A quad is instanced on resampled points along each kept strand"),
    (CARDS_MODE_RIBBON, "Ribbon", "Each kept strand becomes a single continuous, taperable ribbon mesh"),
    (CARDS_MODE_SHELL, "Shell (volume)", "A single closed shell wrapped around the whole hairstyle, good for LODs"),
    (CARDS_MODE_CLUSTER_BOX, "Cluster boxes", "One flat oriented card per bundle of nearby strands, computed in python (PCA)"),
    (CARDS_MODE_CLUSTER_RIBBON, "Cluster ribbons", "One curved ribbon per bundle of nearby strands, following the bundle's average curve"),
    ]

# Where the hair gets baked to.
BAKE_TARGET_CARDS = "CARDS" # generated card object

BAKE_TARGET_BODY_DIRECT = "BODY_DIRECT" # body geometry - hair baked onto skin texture

BAKE_TARGET_BODY_SHELL = "BODY_SHELL" # copy of body geometry hovering above skin

BAKE_TARGET_CUSTOM = "CUSTOM" # users own mesh

BAKE_TARGET_ITEMS = [
    (BAKE_TARGET_CARDS, "Hair cards", "Project the hair onto generated cards (the modes below)"),
    (BAKE_TARGET_BODY_DIRECT, "Body texture",
     "Project the hair straight onto the body and blend the result over the skin material."),
    (BAKE_TARGET_BODY_SHELL, "Body shell",
     "Projects hair onto duplicate of body faces the hair asset grows from (faces will be howering just above the skin)"),
    (BAKE_TARGET_CUSTOM, "Custom mesh",
     "Projects the hair onto your own modelled mesh picked from the scene (mesh needs its own UV layout)."
     "Nothing about the mesh is changed except that it gains the baked material."),
    ]

# How the hair is lit while it is baked.
LIGHT_MODE_FIXED = "FIXED"

LIGHT_MODE_BBOX = "BBOX"

LIGHT_MODE_NO_SHADOW = "NO_SHADOW"

LIGHT_MODE_ACROSS_STRANDS = "ACROSS_STRANDS"

LIGHT_MODE_SCENE = "SCENE"

LIGHT_MODE_ITEMS = [
    (LIGHT_MODE_FIXED, "Two lights, fixed offset",
     "Two point lights at a fixed offset from the character's origin"),
    (LIGHT_MODE_BBOX, "Two lights, from hair bounding box",
     "Two point lights placed from the hair's own bounding box"),
    (LIGHT_MODE_NO_SHADOW, "Two lights, no shadows",
     "As above, but the lights dont cast shadows."),
    (LIGHT_MODE_ACROSS_STRANDS, "Two lights, across the strands",
     "Two shadowless lights placed perpendicular to the main hair growth direction, so the hair is lit from the side."),
    (LIGHT_MODE_SCENE, "Current scene lighting",
     "Use the lights and the world already in the scene, as they are. No bake lights are added"),
    ]

# Full strength in watts per mode so they can use same scale in UI
LIGHT_MODE_BASE_ENERGY = {
    LIGHT_MODE_FIXED: 1000.0,
    LIGHT_MODE_BBOX: 200.0,
    LIGHT_MODE_NO_SHADOW: 10.0,
    LIGHT_MODE_ACROSS_STRANDS: 10.0,
    LIGHT_MODE_SCENE: 0.0,     # No lights added, scenes own lights keep their own strength
    }

BODY_BAKE_TARGETS = (BAKE_TARGET_BODY_DIRECT, BAKE_TARGET_BODY_SHELL)

SELECTION_METHOD_RANDOM = "RANDOM"

SELECTION_METHOD_EVERY_NTH = "EVERY_NTH"

SELECTION_METHOD_POISSON = "POISSON_SCALP"

SELECTION_METHOD_ITEMS = [
    (SELECTION_METHOD_RANDOM, "Random", "Each strand has an independent chance of becoming a card"),
    (SELECTION_METHOD_EVERY_NTH, "Even spacing", "Every Nth strand is kept"),
    (SELECTION_METHOD_POISSON, "Scalp sample points", "Strands nearest to an evenly distributed set of points on the scalp are kept"),
    ]

STRAND_BASED_MODES = (CARDS_MODE_TILES, CARDS_MODE_RIBBON)

CLUSTER_MODES = (CARDS_MODE_CLUSTER_BOX, CARDS_MODE_CLUSTER_RIBBON)

# The UV map that the tiles / ribbon / cluster modes lay out and which the bake packs into the atlas
CARDS_UV_MAP = "UVMap"

_CARD_U_ATTRIBUTE = "_card_u"

_CARD_V_ATTRIBUTE = "_card_v"

CLUSTER_WIDTH_ATTRIBUTE = "cluster_half_width"

# Roots * clusters up to which k-means is run several times and the best run is kept.
# Above it a single run is made for performance reasons.
_KMEANS_RESTART_BUDGET = 2_000_000

# Max strands averaged per cluster, bigger clusters are strided down. More members do not change the average visibly
_MAX_MEMBERS_PER_BUNDLE = 200

# Roots are sampled for speed, more more samples would not bring much change to final mesh
_MAX_ROOT_SAMPLES = 4000

# Keeps the shell on the body when the body moves
BODY_SHELL_FOLLOW_MODIFIER_NAME = "Follow body"

# Attribute the store_shell_edge_fade() writes. The baked shader than multiplies it into the alpha
SHELL_EDGE_FADE_ATTRIBUTE = "mpfb_shell_edge_fade"


class HairCardService():
    """Building the hair cards: geometry node groups for the generated modes, and meshes computed in python. All methods are static methods."""

    def __init__(self):
        raise RuntimeError("You should not instance HairCardService. Use its static methods instead.")

    @staticmethod
    def light_base_energy(mode):
        """Watts per light at strength 1.0 for the given mode."""
        return LIGHT_MODE_BASE_ENERGY.get(mode, 200.0)

    @staticmethod
    def _new_group(name):
        node_group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
        interface = node_group.interface
        interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        for node in list(node_group.nodes):
            node_group.nodes.remove(node)
        node_group.nodes.new('NodeGroupInput')
        node_group.nodes.new('NodeGroupOutput')
        return node_group

    @staticmethod
    def _add_input(node_group, socket_name, socket_type, default=None, value_range=None):
        socket = node_group.interface.new_socket(socket_name, in_out='INPUT', socket_type=socket_type)
        if default is not None:
            socket.default_value = default
        if value_range is not None and hasattr(socket, "min_value"):
            socket.min_value = value_range[0]
            socket.max_value = value_range[1]
        return socket

    @staticmethod
    def _group_input_node(node_group):
        return next(n for n in node_group.nodes if n.bl_idname == 'NodeGroupInput')

    @staticmethod
    def _use_voxel_size(node):
        """Use a voxel size instead of voxel count.

        Blender 4.2 keeps that choice on the node.
        Later versions expose it as a socket.
        """
        socket = node.inputs.get("Resolution Mode")
        if socket is not None:
            socket.default_value = "Size"
        else:
            node.resolution_mode = "VOXEL_SIZE"

    @staticmethod
    def _enabled_socket(sockets, name):
        """The live socket of this name.

        Blender 5.1 keeps every data-type variant in collection and disables the unused ones.
        Blender 5.2 leaves only the live socket, so index which was ok on 5.1 is out of range.
        """
        enabled = [socket for socket in sockets if socket.name == name and socket.enabled]
        if enabled:
            return enabled[0]
        for socket in sockets:
            if socket.name == name:
                return socket
        raise KeyError(name)

    @staticmethod
    def _strand_root_position(node_group, location):
        """Where each strand grows out of the scalp.

        A plain Position on the curve domain is averaged over the strand.
        """
        nodes = node_group.nodes
        links = node_group.links

        curve_index = nodes.new('GeometryNodeInputIndex')
        curve_index.location = (location[0] - 360, location[1])

        points_of_curve = nodes.new('GeometryNodePointsOfCurve')
        points_of_curve.location = (location[0] - 180, location[1])
        points_of_curve.inputs['Sort Index'].default_value = 0
        links.new(curve_index.outputs['Index'], points_of_curve.inputs['Curve Index'])

        position = nodes.new('GeometryNodeInputPosition')
        position.location = (location[0] - 180, location[1] - 120)

        root = nodes.new('GeometryNodeFieldAtIndex')
        root.data_type = 'FLOAT_VECTOR'
        root.domain = 'POINT'
        root.location = location
        links.new(position.outputs['Position'], root.inputs['Value'])
        links.new(points_of_curve.outputs['Point Index'], root.inputs['Index'])
        return root.outputs['Value']

    @staticmethod
    def _build_strand_selection(node_group, selection_method, basemesh,
                                density_socket='Density', density_default=0.01):
        """Build the part of the graph which decides which curves are kept as cards.

        Returns the boolean output socket meaning "delete this curve", going into a Delete Geometry Selection input.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        HairCardService._add_input(node_group, density_socket, 'NodeSocketFloat', density_default, (0.0, 1.0))
        HairCardService._add_input(node_group, 'Seed', 'NodeSocketInt', 0, (0, 9999))
        HairCardService._add_input(node_group, 'Weight vertex group', 'NodeSocketString', "")

        random_value = nodes.new('FunctionNodeRandomValue')
        random_value.data_type = 'FLOAT'
        random_value.location = (-1400, -300)
        links.new(group_in.outputs['Seed'], random_value.inputs['Seed'])

        # The weight map is a vertex group painted on the basemesh, so it is sampled there at the point nearest to each strand
        named_attr = nodes.new('GeometryNodeInputNamedAttribute')
        named_attr.data_type = 'FLOAT'
        named_attr.location = (-1620, -80)
        links.new(group_in.outputs['Weight vertex group'], named_attr.inputs['Name'])

        # Unset or misspelled vertex group means a neutral weight of 1.0
        weight_switch = nodes.new('GeometryNodeSwitch')
        weight_switch.input_type = 'FLOAT'
        weight_switch.location = (-1400, -80)
        links.new(named_attr.outputs['Exists'], weight_switch.inputs[0])
        weight_switch.inputs[1].default_value = 1.0  # False branch: no vertex group, neutral weight
        links.new(named_attr.outputs['Attribute'], weight_switch.inputs[2])  # True branch: painted weight

        weight = weight_switch.outputs[0]
        if basemesh is not None:
            weight_source = nodes.new('GeometryNodeObjectInfo')
            weight_source.location = (-1400, 40)
            weight_source.inputs['Object'].default_value = basemesh
            weight_source.transform_space = 'RELATIVE'

            strand_position = HairCardService._strand_root_position(node_group, (-1400, -240))

            # The switch above is evaluated in the sampled mesh context, so the lookup happens against the basemesh
            sample_weight = nodes.new('GeometryNodeSampleNearestSurface')
            sample_weight.data_type = 'FLOAT'
            sample_weight.location = (-1180, -80)
            links.new(weight_source.outputs['Geometry'], sample_weight.inputs['Mesh'])
            links.new(weight_switch.outputs[0], sample_weight.inputs['Value'])
            links.new(strand_position, sample_weight.inputs['Sample Position'])
            weight = sample_weight.outputs['Value']

        effective_density = nodes.new('ShaderNodeMath')
        effective_density.operation = 'MULTIPLY'
        effective_density.location = (-960, -180)
        links.new(group_in.outputs[density_socket], effective_density.inputs[0])
        links.new(weight, effective_density.inputs[1])

        if selection_method == SELECTION_METHOD_EVERY_NTH:
            HairCardService._add_input(node_group, 'Jitter', 'NodeSocketFloat', 0.15, (0.0, 1.0))

            index_node = nodes.new('GeometryNodeInputIndex')
            index_node.location = (-1400, 150)

            density_clamped = nodes.new('ShaderNodeClamp')
            density_clamped.location = (-960, 150)
            links.new(effective_density.outputs[0], density_clamped.inputs[0])
            density_clamped.inputs[1].default_value = 0.001  # Min
            density_clamped.inputs[2].default_value = 1.0  # Max

            inv_density = nodes.new('ShaderNodeMath')
            inv_density.operation = 'DIVIDE'
            inv_density.location = (-780, 150)
            inv_density.inputs[0].default_value = 1.0
            links.new(density_clamped.outputs[0], inv_density.inputs[1])

            step = nodes.new('ShaderNodeMath')
            step.operation = 'ROUND'
            step.location = (-600, 150)
            links.new(inv_density.outputs[0], step.inputs[0])

            index_mod = nodes.new('ShaderNodeMath')
            index_mod.operation = 'MODULO'
            index_mod.location = (-420, 150)
            links.new(index_node.outputs['Index'], index_mod.inputs[0])
            links.new(step.outputs[0], index_mod.inputs[1])

            on_grid = nodes.new('FunctionNodeCompare')
            on_grid.data_type = 'FLOAT'
            on_grid.operation = 'LESS_THAN'
            on_grid.location = (-240, 150)
            links.new(index_mod.outputs[0], on_grid.inputs[0])
            on_grid.inputs[1].default_value = 1.0

            # Extra random inclusion on top of the grid, so the pattern is not repetetive
            jitter_mul = nodes.new('ShaderNodeMath')
            jitter_mul.operation = 'MULTIPLY'
            jitter_mul.location = (-420, 20)
            links.new(group_in.outputs['Jitter'], jitter_mul.inputs[0])
            links.new(effective_density.outputs[0], jitter_mul.inputs[1])

            jitter_extra = nodes.new('FunctionNodeCompare')
            jitter_extra.data_type = 'FLOAT'
            jitter_extra.operation = 'LESS_THAN'
            jitter_extra.location = (-240, 20)
            links.new(HairCardService._enabled_socket(random_value.outputs, "Value"), jitter_extra.inputs[0])
            links.new(jitter_mul.outputs[0], jitter_extra.inputs[1])

            keep = nodes.new('FunctionNodeBooleanMath')
            keep.operation = 'OR'
            keep.location = (-60, 100)
            links.new(on_grid.outputs['Result'], keep.inputs[0])
            links.new(jitter_extra.outputs['Result'], keep.inputs[1])

            delete_selection = nodes.new('FunctionNodeBooleanMath')
            delete_selection.operation = 'NOT'
            delete_selection.location = (120, 100)
            links.new(keep.outputs[0], delete_selection.inputs[0])
            return delete_selection.outputs[0]

        if selection_method == SELECTION_METHOD_POISSON and basemesh is not None:
            HairCardService._add_input(node_group, 'Poisson radius', 'NodeSocketFloat', 0.02, (0.001, 0.2))

            scalp_info = nodes.new('GeometryNodeObjectInfo')
            scalp_info.location = (-1400, 420)
            scalp_info.inputs['Object'].default_value = basemesh
            scalp_info.transform_space = 'RELATIVE'

            distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
            distribute.distribute_method = 'POISSON'  # also enables the Density Max/Factor sockets below
            distribute.location = (-1180, 420)
            links.new(scalp_info.outputs['Geometry'], distribute.inputs['Mesh'])
            distribute.inputs['Density Max'].default_value = 6000.0
            links.new(effective_density.outputs[0], distribute.inputs['Density Factor'])
            links.new(group_in.outputs['Seed'], distribute.inputs['Seed'])

            root_position = HairCardService._strand_root_position(node_group, (-960, 420))

            proximity = nodes.new('GeometryNodeProximity')
            proximity.target_element = 'POINTS'
            proximity.location = (-780, 420)
            links.new(distribute.outputs['Points'], proximity.inputs['Geometry'])
            links.new(root_position, proximity.inputs['Sample Position'])

            near_scalp_sample = nodes.new('FunctionNodeCompare')
            near_scalp_sample.data_type = 'FLOAT'
            near_scalp_sample.operation = 'LESS_THAN'
            near_scalp_sample.location = (-600, 420)
            links.new(proximity.outputs['Distance'], near_scalp_sample.inputs[0])
            links.new(group_in.outputs['Poisson radius'], near_scalp_sample.inputs[1])

            delete_selection = nodes.new('FunctionNodeBooleanMath')
            delete_selection.operation = 'NOT'
            delete_selection.location = (-420, 420)
            links.new(near_scalp_sample.outputs['Result'], delete_selection.inputs[0])
            return delete_selection.outputs[0]

        # Default / fallback: independent random draw per strand, weighted by the vertex group
        compare = nodes.new('FunctionNodeCompare')
        compare.data_type = 'FLOAT'
        compare.operation = 'GREATER_THAN'
        compare.location = (-600, -300)
        links.new(HairCardService._enabled_socket(random_value.outputs, "Value"), compare.inputs[0])
        links.new(effective_density.outputs[0], compare.inputs[1])
        return compare.outputs['Result']

    @staticmethod
    def _build_cluster_blend(node_group, geometry_socket, location):
        """Blend each kept strand points towards the points of its nearest neighbouring strand.

        A pairwise blend with the nearest strand from the other half of the strand pool.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        HairCardService._add_input(node_group, 'Cluster strength', 'NodeSocketFloat', 0.0, (0.0, 1.0))

        def parity(loc):
            """Split strands into evens and odds.

            The nearest point is taken from the other group, so it cannot be a point of this strand.
            """
            curve_of_point = nodes.new('GeometryNodeCurveOfPoint')
            curve_of_point.location = (loc[0] - 180, loc[1])
            bucket = nodes.new('ShaderNodeMath')
            bucket.operation = 'MODULO'
            bucket.location = loc
            links.new(curve_of_point.outputs['Curve Index'], bucket.inputs[0])
            bucket.inputs[1].default_value = 2.0
            return bucket.outputs[0]

        def as_int(value_socket, loc):
            to_int = nodes.new('FunctionNodeFloatToInt')
            to_int.rounding_mode = 'FLOOR'
            to_int.location = loc
            links.new(value_socket, to_int.inputs[0])
            return to_int.outputs[0]

        # Proximity cannot read curve geometry, so the strands are handed over as point cloud.
        # The parity is captured on the point domain to survive the conversion.
        own_parity = as_int(parity((location[0] - 700, location[1] - 100)), (location[0] - 540, location[1] - 100))

        capture = nodes.new('GeometryNodeCaptureAttribute')
        capture.domain = 'POINT'
        capture.location = (location[0] - 360, location[1] - 100)
        capture.capture_items.new('INT', "strand_parity")
        links.new(geometry_socket, capture.inputs[0])
        links.new(own_parity, HairCardService._enabled_socket(capture.inputs, "strand_parity"))

        strand_points = nodes.new('GeometryNodeCurveToPoints')
        strand_points.mode = 'EVALUATED'
        strand_points.location = (location[0] - 160, location[1] - 100)
        links.new(capture.outputs[0], strand_points.inputs['Curve'])

        other_parity = nodes.new('ShaderNodeMath')
        other_parity.operation = 'SUBTRACT'
        other_parity.location = (location[0] - 360, location[1] - 260)
        other_parity.inputs[0].default_value = 1.0
        links.new(parity((location[0] - 540, location[1] - 260)), other_parity.inputs[1])

        position = nodes.new('GeometryNodeInputPosition')
        position.location = (location[0] - 160, location[1] + 40)

        proximity = nodes.new('GeometryNodeProximity')
        proximity.target_element = 'POINTS'
        proximity.location = (location[0] + 260, location[1] - 40)
        links.new(strand_points.outputs['Points'], proximity.inputs['Geometry'])
        links.new(HairCardService._enabled_socket(capture.outputs, "strand_parity"), proximity.inputs['Group ID'])
        links.new(position.outputs['Position'], proximity.inputs['Sample Position'])
        links.new(as_int(other_parity.outputs[0], (location[0] - 160, location[1] - 260)),
                  proximity.inputs['Sample Group ID'])

        # No partner strand to pull towards - keep the point where it is
        effective_strength = nodes.new('ShaderNodeMath')
        effective_strength.operation = 'MULTIPLY'
        effective_strength.location = (location[0] + 440, location[1] + 120)
        links.new(group_in.outputs['Cluster strength'], effective_strength.inputs[0])
        links.new(proximity.outputs['Is Valid'], effective_strength.inputs[1])

        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'VECTOR'
        mix.location = (location[0] + 440, location[1] - 40)
        # inputs[0] is scalar Factor. inputs[1] is disabled unless factor_mode is 'NON_UNIFORM'
        links.new(effective_strength.outputs[0], mix.inputs[0])  # Factor (scalar)
        links.new(position.outputs['Position'], mix.inputs[4])  # A (vector variant)
        links.new(proximity.outputs['Position'], mix.inputs[5])  # B (vector variant)

        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (location[0] + 620, location[1] - 40)
        links.new(capture.outputs[0], set_position.inputs['Geometry'])
        links.new(mix.outputs[1], set_position.inputs['Position'])  # Result (vector variant)

        return set_position.outputs['Geometry']

    @staticmethod
    def _build_offset(node_group, geometry_socket, basemesh, location):
        """Push every point away from the scalp by the live "Offset" input.

        The direction is basemesh surface normal at the nearest point. Without basemesh it falls back to curve normal.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        HairCardService._add_input(node_group, 'Offset', 'NodeSocketFloat', 0.0, (0.0, 0.1))

        if basemesh is not None:
            scalp_info = nodes.new('GeometryNodeObjectInfo')
            scalp_info.location = (location[0] - 540, location[1] - 160)
            scalp_info.inputs['Object'].default_value = basemesh
            scalp_info.transform_space = 'RELATIVE'

            scalp_normal = nodes.new('GeometryNodeInputNormal')
            scalp_normal.location = (location[0] - 540, location[1] - 320)

            position = nodes.new('GeometryNodeInputPosition')
            position.location = (location[0] - 540, location[1] - 400)

            sample_scalp = nodes.new('GeometryNodeSampleNearestSurface')
            sample_scalp.data_type = 'FLOAT_VECTOR'
            sample_scalp.location = (location[0] - 360, location[1] - 220)
            links.new(scalp_info.outputs['Geometry'], sample_scalp.inputs['Mesh'])
            links.new(scalp_normal.outputs['Normal'], sample_scalp.inputs['Value'])
            links.new(position.outputs['Position'], sample_scalp.inputs['Sample Position'])
            direction = sample_scalp.outputs['Value']
        else:
            curve_normal = nodes.new('GeometryNodeInputNormal')
            curve_normal.location = (location[0] - 360, location[1] - 220)
            direction = curve_normal.outputs['Normal']

        normalize = nodes.new('ShaderNodeVectorMath')
        normalize.operation = 'NORMALIZE'
        normalize.location = (location[0] - 180, location[1] - 220)
        links.new(direction, normalize.inputs[0])

        offset_vec = nodes.new('ShaderNodeVectorMath')
        offset_vec.operation = 'SCALE'
        offset_vec.location = (location[0] - 180, location[1] - 120)
        links.new(normalize.outputs[0], offset_vec.inputs[0])
        links.new(group_in.outputs['Offset'], offset_vec.inputs['Scale'])

        offset_pos = nodes.new('GeometryNodeSetPosition')
        offset_pos.location = location
        links.new(geometry_socket, offset_pos.inputs['Geometry'])
        links.new(offset_vec.outputs[0], offset_pos.inputs['Offset'])
        return offset_pos.outputs['Geometry']

    @staticmethod
    def _capture_per_curve_random_vector(node_group, geometry_socket, location):
        """One random 0..1 vector per curve (constant along all of a strand points).

        Returns (geometry_output_socket, vector_attribute_output_socket).
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        index_node = nodes.new('GeometryNodeInputIndex')
        index_node.location = (location[0] - 200, location[1] - 60)

        random_value = nodes.new('FunctionNodeRandomValue')
        random_value.data_type = 'FLOAT_VECTOR'
        random_value.location = (location[0], location[1] - 60)
        links.new(group_in.outputs['Seed'], HairCardService._enabled_socket(random_value.inputs, "Seed"))
        links.new(index_node.outputs['Index'], HairCardService._enabled_socket(random_value.inputs, "ID"))

        capture = nodes.new('GeometryNodeCaptureAttribute')
        capture.domain = 'CURVE'
        capture.location = (location[0] + 200, location[1])
        capture.capture_items.new('VECTOR', "per_curve_random")
        links.new(geometry_socket, capture.inputs[0])
        links.new(HairCardService._enabled_socket(random_value.outputs, "Value"), HairCardService._enabled_socket(capture.inputs, "per_curve_random"))
        return capture.outputs[0], HairCardService._enabled_socket(capture.outputs, "per_curve_random")

    @staticmethod
    def build_tiles_node_group(group_name, selection_method, basemesh):
        node_group = HairCardService._new_group(group_name)
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        group_out = next(n for n in nodes if n.bl_idname == 'NodeGroupOutput')
        group_in.location = (-2200, 0)
        group_out.location = (1400, 0)

        delete_selection = HairCardService._build_strand_selection(node_group, selection_method, basemesh)

        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'CURVE'
        delete.location = (-800, 0)
        links.new(group_in.outputs['Geometry'], delete.inputs['Geometry'])
        links.new(delete_selection, delete.inputs['Selection'])

        blended = HairCardService._build_cluster_blend(node_group, delete.outputs['Geometry'], (-600, -700))

        HairCardService._add_input(node_group, 'Segments', 'NodeSocketInt', 8, (2, 64))
        resample = nodes.new('GeometryNodeResampleCurve')
        resample.location = (-360, 0)
        links.new(blended, resample.inputs['Curve'])
        links.new(group_in.outputs['Segments'], resample.inputs['Count'])

        offset_geometry = HairCardService._build_offset(node_group, resample.outputs['Curve'], basemesh, (0, 0))

        HairCardService._add_input(node_group, 'Card width', 'NodeSocketFloat', 0.03, (0.001, 0.5))
        HairCardService._add_input(node_group, 'Card length', 'NodeSocketFloat', 0.03, (0.001, 0.5))
        HairCardService._add_input(node_group, 'Width random', 'NodeSocketFloat', 0.0, (0.0, 1.0))
        HairCardService._add_input(node_group, 'Length random', 'NodeSocketFloat', 0.0, (0.0, 1.0))
        HairCardService._add_input(node_group, 'Tilt random', 'NodeSocketFloat', 0.0, (0.0, 1.0))
        HairCardService._add_input(node_group, 'Scale', 'NodeSocketFloat', 1.0, (0.01, 5.0))

        points_geometry, variation_vector = HairCardService._capture_per_curve_random_vector(node_group, offset_geometry, (-360, 500))
        separate_rand = nodes.new('ShaderNodeSeparateXYZ')
        separate_rand.location = (-160, 500)
        links.new(variation_vector, separate_rand.inputs[0])

        def _signed_jitter(component_socket, amount_socket, loc):
            signed = nodes.new('ShaderNodeMath')
            signed.operation = 'SUBTRACT'
            signed.location = loc
            links.new(component_socket, signed.inputs[0])
            signed.inputs[1].default_value = 0.5
            scaled = nodes.new('ShaderNodeMath')
            scaled.operation = 'MULTIPLY'
            scaled.location = (loc[0] + 160, loc[1])
            links.new(signed.outputs[0], scaled.inputs[0])
            links.new(amount_socket, scaled.inputs[1])
            factor = nodes.new('ShaderNodeMath')
            factor.operation = 'ADD'
            factor.location = (loc[0] + 320, loc[1])
            factor.inputs[0].default_value = 1.0
            links.new(scaled.outputs[0], factor.inputs[1])
            return factor.outputs[0]

        width_factor = _signed_jitter(separate_rand.outputs[0], group_in.outputs['Width random'], (60, 620))
        length_factor = _signed_jitter(separate_rand.outputs[1], group_in.outputs['Length random'], (60, 480))
        tilt_factor = _signed_jitter(separate_rand.outputs[2], group_in.outputs['Tilt random'], (60, 340))

        # Grid is a fixed 1x1 quad, sizing happens in Instance on Points Scale.
        grid = nodes.new('GeometryNodeMeshGrid')
        grid.inputs['Vertices X'].default_value = 2
        grid.inputs['Vertices Y'].default_value = 2
        grid.inputs['Size X'].default_value = 1.0
        grid.inputs['Size Y'].default_value = 1.0
        grid.location = (620, 550)

        # Tile UVs come from the Grid node: U across the quad, V along the strand
        tile_uv = nodes.new('GeometryNodeStoreNamedAttribute')
        tile_uv.data_type = 'FLOAT2'
        tile_uv.domain = 'CORNER'
        tile_uv.inputs['Name'].default_value = CARDS_UV_MAP
        tile_uv.location = (800, 700)
        links.new(grid.outputs['Mesh'], tile_uv.inputs['Geometry'])
        links.new(grid.outputs['UV Map'], tile_uv.inputs['Value'])

        width_final = nodes.new('ShaderNodeMath')
        width_final.operation = 'MULTIPLY'
        width_final.location = (420, 620)
        links.new(group_in.outputs['Card width'], width_final.inputs[0])
        links.new(width_factor, width_final.inputs[1])

        length_final = nodes.new('ShaderNodeMath')
        length_final.operation = 'MULTIPLY'
        length_final.location = (420, 480)
        links.new(group_in.outputs['Card length'], length_final.inputs[0])
        links.new(length_factor, length_final.inputs[1])

        width_scaled = nodes.new('ShaderNodeMath')
        width_scaled.operation = 'MULTIPLY'
        width_scaled.location = (600, 620)
        links.new(width_final.outputs[0], width_scaled.inputs[0])
        links.new(group_in.outputs['Scale'], width_scaled.inputs[1])

        length_scaled = nodes.new('ShaderNodeMath')
        length_scaled.operation = 'MULTIPLY'
        length_scaled.location = (600, 480)
        links.new(length_final.outputs[0], length_scaled.inputs[0])
        links.new(group_in.outputs['Scale'], length_scaled.inputs[1])

        card_scale = nodes.new('ShaderNodeCombineXYZ')
        card_scale.location = (800, 550)
        links.new(width_scaled.outputs[0], card_scale.inputs['X'])
        links.new(length_scaled.outputs[0], card_scale.inputs['Y'])
        links.new(group_in.outputs['Scale'], card_scale.inputs['Z'])

        tangent = nodes.new('GeometryNodeInputTangent')
        tangent.location = (0, 200)
        normal2 = nodes.new('GeometryNodeInputNormal')
        normal2.location = (0, 100)

        # Tilt: rotation of the card around its strand by up to +/- 90 degrees. tilt_factor is 1.0 +/- amount/2
        tilt_signed = nodes.new('ShaderNodeMath')
        tilt_signed.operation = 'SUBTRACT'
        tilt_signed.location = (240, 340)
        links.new(tilt_factor, tilt_signed.inputs[0])
        tilt_signed.inputs[1].default_value = 1.0

        tilt_radians = nodes.new('ShaderNodeMath')
        tilt_radians.operation = 'MULTIPLY'
        tilt_radians.location = (420, 340)
        links.new(tilt_signed.outputs[0], tilt_radians.inputs[0])
        tilt_radians.inputs[1].default_value = math.pi

        tilt_rotation = nodes.new('FunctionNodeAxisAngleToRotation')
        tilt_rotation.location = (240, 200)
        links.new(tangent.outputs['Tangent'], tilt_rotation.inputs['Axis'])
        links.new(tilt_radians.outputs[0], tilt_rotation.inputs['Angle'])

        tilted_axis = nodes.new('FunctionNodeRotateVector')
        tilted_axis.location = (440, 200)
        links.new(normal2.outputs['Normal'], tilted_axis.inputs['Vector'])
        links.new(tilt_rotation.outputs['Rotation'], tilted_axis.inputs['Rotation'])

        align_length = nodes.new('FunctionNodeAlignRotationToVector')
        align_length.axis = 'Y'
        align_length.pivot_axis = 'AUTO'
        align_length.location = (640, 380)
        links.new(tangent.outputs['Tangent'], align_length.inputs['Vector'])

        align_face = nodes.new('FunctionNodeAlignRotationToVector')
        align_face.axis = 'Z'
        align_face.pivot_axis = 'Y'
        align_face.location = (820, 380)
        links.new(align_length.outputs['Rotation'], align_face.inputs['Rotation'])
        links.new(tilted_axis.outputs['Vector'], align_face.inputs['Vector'])

        instance = nodes.new('GeometryNodeInstanceOnPoints')
        instance.location = (1000, 0)
        links.new(points_geometry, instance.inputs['Points'])
        links.new(tile_uv.outputs['Geometry'], instance.inputs['Instance'])
        links.new(align_face.outputs['Rotation'], instance.inputs['Rotation'])
        links.new(card_scale.outputs['Vector'], instance.inputs['Scale'])

        realize = nodes.new('GeometryNodeRealizeInstances')
        realize.location = (1200, 0)
        links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
        links.new(realize.outputs['Geometry'], group_out.inputs['Geometry'])

        return node_group

    @staticmethod
    def _build_tip_extension(node_group, curve_socket, location):
        """Push the last point of every curve out along its own tangent. Returns the curve socket.

        Extending the card past the strand tip gives the bake somewhere to put the last bit of hair.
        Blender 5.1 has no Extend Curves node - the endpoint is moved along its tangent instead.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        x, y = location

        HairCardService._add_input(node_group, 'Extend tip', 'NodeSocketFloat', 0.0, (0.0, 0.1))

        endpoint = nodes.new('GeometryNodeCurveEndpointSelection')
        endpoint.location = (x, y + 120)
        endpoint.inputs['Start Size'].default_value = 0
        endpoint.inputs['End Size'].default_value = 1

        tangent = nodes.new('GeometryNodeInputTangent')
        tangent.location = (x, y - 60)

        offset = nodes.new('ShaderNodeVectorMath')
        offset.operation = 'SCALE'
        offset.location = (x + 180, y - 60)
        links.new(tangent.outputs['Tangent'], offset.inputs[0])
        links.new(group_in.outputs['Extend tip'], offset.inputs['Scale'])

        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (x + 360, y)
        links.new(curve_socket, set_position.inputs['Geometry'])
        links.new(endpoint.outputs['Selection'], set_position.inputs['Selection'])
        links.new(offset.outputs['Vector'], set_position.inputs['Offset'])
        return set_position.outputs['Geometry']

    @staticmethod
    def _build_ribbon_shape(node_group, curve_socket, basemesh, base_width_socket=None,
                            location=(0, 0), profile_steps=16):
        """Turn a set of curves into taperable, twistable ribbon cards with hair-aligned UVs.

        Shared by RIBBON (one card per strand) and CLUSTER_RIBBON (one card per cluster).
        Returns the mesh output socket.

        ``base_width_socket`` optionally replaces the flat "Card width" input with a per-curve width.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        x, y = location

        HairCardService._add_input(node_group, 'Profile steps', 'NodeSocketInt', profile_steps, (2, 64))
        resample = nodes.new('GeometryNodeResampleCurve')
        resample.location = (x - 360, y)
        links.new(curve_socket, resample.inputs['Curve'])
        links.new(group_in.outputs['Profile steps'], resample.inputs['Count'])

        extended = HairCardService._build_tip_extension(node_group, resample.outputs['Curve'], (x - 360, y - 300))
        offset_geometry = HairCardService._build_offset(node_group, extended, basemesh, (x, y))

        # Taper: the ribbon narrows towards the tip according to "Taper" (0 = uniform, 1 = to a point)
        if base_width_socket is None:
            HairCardService._add_input(node_group, 'Card width', 'NodeSocketFloat', 0.03, (0.001, 0.5))
        HairCardService._add_input(node_group, 'Taper', 'NodeSocketFloat', 0.3, (0.0, 1.0))
        spline_param = nodes.new('GeometryNodeSplineParameter')
        spline_param.location = (x, y + 260)

        taper_amount = nodes.new('ShaderNodeMath')
        taper_amount.operation = 'MULTIPLY'
        taper_amount.location = (x + 180, y + 260)
        links.new(spline_param.outputs['Factor'], taper_amount.inputs[0])
        links.new(group_in.outputs['Taper'], taper_amount.inputs[1])

        taper_factor = nodes.new('ShaderNodeMath')
        taper_factor.operation = 'SUBTRACT'
        taper_factor.location = (x + 360, y + 260)
        taper_factor.inputs[0].default_value = 1.0
        links.new(taper_amount.outputs[0], taper_factor.inputs[1])

        # Width of the ribbon at this point along the strand.
        ribbon_width = nodes.new('ShaderNodeMath')
        ribbon_width.operation = 'MULTIPLY'
        ribbon_width.location = (x + 540, y + 200)
        links.new(base_width_socket or group_in.outputs['Card width'], ribbon_width.inputs[0])
        links.new(taper_factor.outputs[0], ribbon_width.inputs[1])

        # Twist: a progressive rotation of the ribbon along strand
        HairCardService._add_input(node_group, 'Twist', 'NodeSocketFloat', 0.0, (-4.0, 4.0))
        twist_turns = nodes.new('ShaderNodeMath')
        twist_turns.operation = 'MULTIPLY'
        twist_turns.location = (x + 180, y - 140)
        links.new(group_in.outputs['Twist'], twist_turns.inputs[0])
        twist_turns.inputs[1].default_value = 2.0 * math.pi

        twist_angle = nodes.new('ShaderNodeMath')
        twist_angle.operation = 'MULTIPLY'
        twist_angle.location = (x + 360, y - 140)
        links.new(spline_param.outputs['Factor'], twist_angle.inputs[0])
        links.new(twist_turns.outputs[0], twist_angle.inputs[1])

        set_tilt = nodes.new('GeometryNodeSetCurveTilt')
        set_tilt.location = (x + 900, y)
        links.new(offset_geometry, set_tilt.inputs['Curve'])
        links.new(twist_angle.outputs[0], set_tilt.inputs['Tilt'])

        # UVs: V along the strand, U across the ribbon, the same as tiles and cluster boxes (the atlas packs cards that way).
        # Curve to Mesh carries point attributes of both inputs (V on curve, U on profile).
        store_along = nodes.new('GeometryNodeStoreNamedAttribute')
        store_along.data_type = 'FLOAT'
        store_along.domain = 'POINT'
        store_along.inputs['Name'].default_value = _CARD_V_ATTRIBUTE
        store_along.location = (x + 1080, y)
        links.new(set_tilt.outputs['Curve'], store_along.inputs['Geometry'])
        links.new(spline_param.outputs['Factor'], store_along.inputs['Value'])

        # Unit-long profile, so Scale is card width in metres
        profile = nodes.new('GeometryNodeCurvePrimitiveLine')
        profile.location = (x + 720, y - 320)
        profile.inputs['Start'].default_value = (-0.5, 0.0, 0.0)
        profile.inputs['End'].default_value = (0.5, 0.0, 0.0)

        profile_param = nodes.new('GeometryNodeSplineParameter')
        profile_param.location = (x + 720, y - 460)

        store_across = nodes.new('GeometryNodeStoreNamedAttribute')
        store_across.data_type = 'FLOAT'
        store_across.domain = 'POINT'
        store_across.inputs['Name'].default_value = _CARD_U_ATTRIBUTE
        store_across.location = (x + 900, y - 320)
        links.new(profile.outputs['Curve'], store_across.inputs['Geometry'])
        links.new(profile_param.outputs['Factor'], store_across.inputs['Value'])

        curve_to_mesh = nodes.new('GeometryNodeCurveToMesh')
        curve_to_mesh.location = (x + 1260, y - 100)
        links.new(store_across.outputs['Geometry'], curve_to_mesh.inputs['Profile Curve'])
        # Unit-long profile, so this factor is the card width in metres.
        # 4.2 has no Scale input and uses radius instead with a fraction of milimeter
        scale_input = curve_to_mesh.inputs.get('Scale')
        if scale_input is not None:
            links.new(store_along.outputs['Geometry'], curve_to_mesh.inputs['Curve'])
            links.new(ribbon_width.outputs[0], scale_input)
        else:
            set_radius = nodes.new('GeometryNodeSetCurveRadius')
            set_radius.location = (x + 1080, y + 160)
            links.new(store_along.outputs['Geometry'], set_radius.inputs['Curve'])
            links.new(ribbon_width.outputs[0], set_radius.inputs['Radius'])
            links.new(set_radius.outputs['Curve'], curve_to_mesh.inputs['Curve'])

        return HairCardService._store_card_uvs(node_group, curve_to_mesh.outputs['Mesh'], (x + 1500, y))

    @staticmethod
    def _store_card_uvs(node_group, mesh_socket, location):
        """Combine the scratch U/V attributes left by _build_ribbon_shape() into UV map."""
        nodes = node_group.nodes
        links = node_group.links

        read_u = nodes.new('GeometryNodeInputNamedAttribute')
        read_u.data_type = 'FLOAT'
        read_u.inputs['Name'].default_value = _CARD_U_ATTRIBUTE
        read_u.location = (location[0] - 360, location[1] - 200)

        read_v = nodes.new('GeometryNodeInputNamedAttribute')
        read_v.data_type = 'FLOAT'
        read_v.inputs['Name'].default_value = _CARD_V_ATTRIBUTE
        read_v.location = (location[0] - 360, location[1] - 340)

        uv = nodes.new('ShaderNodeCombineXYZ')
        uv.location = (location[0] - 180, location[1] - 260)
        links.new(read_u.outputs['Attribute'], uv.inputs['X'])
        links.new(read_v.outputs['Attribute'], uv.inputs['Y'])

        store_uv = nodes.new('GeometryNodeStoreNamedAttribute')
        store_uv.data_type = 'FLOAT2'
        store_uv.domain = 'CORNER'
        store_uv.inputs['Name'].default_value = CARDS_UV_MAP
        store_uv.location = location
        links.new(mesh_socket, store_uv.inputs['Geometry'])
        links.new(uv.outputs['Vector'], store_uv.inputs['Value'])

        # Remove scratch attributes
        geometry = store_uv.outputs['Geometry']
        for index, name in enumerate((_CARD_U_ATTRIBUTE, _CARD_V_ATTRIBUTE)):
            remove = nodes.new('GeometryNodeRemoveAttribute')
            remove.location = (location[0] + 180 + index * 180, location[1])
            remove.inputs['Name'].default_value = name
            links.new(geometry, remove.inputs['Geometry'])
            geometry = remove.outputs['Geometry']
        return geometry

    @staticmethod
    def build_ribbon_node_group(group_name, selection_method, basemesh):
        node_group = HairCardService._new_group(group_name)
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        group_out = next(n for n in nodes if n.bl_idname == 'NodeGroupOutput')
        group_in.location = (-2000, 0)
        group_out.location = (2100, 0)

        delete_selection = HairCardService._build_strand_selection(node_group, selection_method, basemesh)

        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'CURVE'
        delete.location = (-800, 0)
        links.new(group_in.outputs['Geometry'], delete.inputs['Geometry'])
        links.new(delete_selection, delete.inputs['Selection'])

        blended = HairCardService._build_cluster_blend(node_group, delete.outputs['Geometry'], (-600, -500))

        links.new(HairCardService._build_ribbon_shape(node_group, blended, basemesh), group_out.inputs['Geometry'])
        return node_group

    @staticmethod
    def build_cluster_ribbon_node_group(group_name, basemesh):
        """Shape the pre-averaged cluster poly-lines from build_cluster_ribbon_mesh() into ribbon cards.

        No strand selection here, the input is already one poly-line per cluster (bundle).
        "Width from cluster" scales each card by the cluster thickness.
        """
        node_group = HairCardService._new_group(group_name)
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        group_out = next(n for n in nodes if n.bl_idname == 'NodeGroupOutput')
        group_in.location = (-1200, 0)
        group_out.location = (2100, 0)

        to_curve = nodes.new('GeometryNodeMeshToCurve')
        to_curve.location = (-1000, 0)
        links.new(group_in.outputs['Geometry'], to_curve.inputs['Mesh'])

        HairCardService._add_input(node_group, 'Card width', 'NodeSocketFloat', 0.03, (0.001, 0.5))
        HairCardService._add_input(node_group, 'Width from cluster', 'NodeSocketFloat', 0.6, (0.0, 1.0))

        measured = nodes.new('GeometryNodeInputNamedAttribute')
        measured.data_type = 'FLOAT'
        measured.inputs['Name'].default_value = CLUSTER_WIDTH_ATTRIBUTE
        measured.location = (-1000, -300)

        measured_width = nodes.new('ShaderNodeMath')
        measured_width.operation = 'MULTIPLY'
        measured_width.location = (-820, -300)
        links.new(measured.outputs['Attribute'], measured_width.inputs[0])
        measured_width.inputs[1].default_value = 2.0  # stored as a half width

        base_width = nodes.new('ShaderNodeMix')
        base_width.data_type = 'FLOAT'
        base_width.location = (-640, -300)
        links.new(group_in.outputs['Width from cluster'], base_width.inputs[0])  # Factor
        links.new(group_in.outputs['Card width'], base_width.inputs[2])  # A (float variant)
        links.new(measured_width.outputs[0], base_width.inputs[3])  # B (float variant)

        # Fewer profile steps than plain ribbon - the input is already a smooth resampled average
        mesh = HairCardService._build_ribbon_shape(node_group, to_curve.outputs['Curve'], basemesh,
                                   base_width_socket=base_width.outputs[0],
                                   profile_steps=CLUSTER_RIBBON_PROFILE_STEPS)
        links.new(mesh, group_out.inputs['Geometry'])
        return node_group

    @staticmethod
    def _build_shell_hug(node_group, shell_socket, curves_socket, location):
        """Pull every shell vertex towards the nearest actual hair point by the "Hug strands" amount.

        0: Shell is just raw isosurface inflated by the strand radius 
        1: Shell sits on the outermost strands

        Vertices with no hair near them keep their position, since Is Valid gates the blend.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        HairCardService._add_input(node_group, 'Hug strands', 'NodeSocketFloat', 0.7, (0.0, 1.0))

        # Proximity cannot read curve geometry, so the strands are handed over as a point cloud
        strand_points = nodes.new('GeometryNodeCurveToPoints')
        strand_points.mode = 'EVALUATED'
        strand_points.location = (location[0] - 360, location[1])
        links.new(curves_socket, strand_points.inputs['Curve'])

        position = nodes.new('GeometryNodeInputPosition')
        position.location = (location[0] - 360, location[1] - 160)

        proximity = nodes.new('GeometryNodeProximity')
        proximity.target_element = 'POINTS'
        proximity.location = (location[0] - 160, location[1])
        links.new(strand_points.outputs['Points'], proximity.inputs['Geometry'])
        links.new(position.outputs['Position'], proximity.inputs['Sample Position'])

        strength = nodes.new('ShaderNodeMath')
        strength.operation = 'MULTIPLY'
        strength.location = (location[0] + 20, location[1] + 140)
        links.new(group_in.outputs['Hug strands'], strength.inputs[0])
        links.new(proximity.outputs['Is Valid'], strength.inputs[1])

        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'VECTOR'
        mix.location = (location[0] + 20, location[1])
        links.new(strength.outputs[0], mix.inputs[0])  # Factor (scalar)
        links.new(position.outputs['Position'], mix.inputs[4])  # A (vector variant)
        links.new(proximity.outputs['Position'], mix.inputs[5])  # B (vector variant)

        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (location[0] + 220, location[1])
        links.new(shell_socket, set_position.inputs['Geometry'])
        links.new(mix.outputs[1], set_position.inputs['Position'])  # Result (vector variant)
        return set_position.outputs['Geometry']

    @staticmethod
    def _build_shell_base(node_group, basemesh):
        """Thin the strands, turn them into a volume and back into a smoothed mesh shell.

        Points to Volume puts a sphere of "Strand radius" around every sampled strand point, so the hull is inflated by that radius.
        "Strand samples" allows a smaller radius without beading
        "Hug strands" pulls the shell onto the hair.
        Smoothing keeps the hugging from creating creases.
        """
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)

        delete_selection = HairCardService._build_strand_selection(
            node_group, SELECTION_METHOD_RANDOM, basemesh,
            density_socket='Volume density', density_default=0.05)
        delete = nodes.new('GeometryNodeDeleteGeometry')
        delete.domain = 'CURVE'
        delete.location = (-800, 0)
        links.new(group_in.outputs['Geometry'], delete.inputs['Geometry'])
        links.new(delete_selection, delete.inputs['Selection'])

        HairCardService._add_input(node_group, 'Strand samples', 'NodeSocketInt', 32, (2, 128))
        resample = nodes.new('GeometryNodeResampleCurve')
        resample.location = (-600, 0)
        links.new(group_in.outputs['Strand samples'], resample.inputs['Count'])
        links.new(delete.outputs['Geometry'], resample.inputs['Curve'])

        HairCardService._add_input(node_group, 'Voxel size', 'NodeSocketFloat', 0.008, (0.001, 0.05))
        HairCardService._add_input(node_group, 'Strand radius', 'NodeSocketFloat', 0.015, (0.001, 0.05))
        to_volume = nodes.new('GeometryNodePointsToVolume')
        to_volume.location = (-360, 0)
        HairCardService._use_voxel_size(to_volume)
        links.new(resample.outputs['Curve'], to_volume.inputs['Points'])
        links.new(group_in.outputs['Voxel size'], to_volume.inputs['Voxel Size'])
        links.new(group_in.outputs['Strand radius'], to_volume.inputs['Radius'])

        HairCardService._add_input(node_group, 'Adaptivity', 'NodeSocketFloat', 0.3, (0.0, 1.0))
        to_mesh = nodes.new('GeometryNodeVolumeToMesh')
        to_mesh.location = (-160, 0)
        HairCardService._use_voxel_size(to_mesh)
        links.new(to_volume.outputs['Volume'], to_mesh.inputs['Volume'])
        links.new(group_in.outputs['Voxel size'], to_mesh.inputs['Voxel Size'])
        links.new(group_in.outputs['Adaptivity'], to_mesh.inputs['Adaptivity'])

        hugged = HairCardService._build_shell_hug(node_group, to_mesh.outputs['Mesh'], resample.outputs['Curve'], (300, -420))

        HairCardService._add_input(node_group, 'Smooth iterations', 'NodeSocketInt', 2, (0, 5))
        index_switch = nodes.new('GeometryNodeIndexSwitch')
        index_switch.data_type = 'GEOMETRY'
        index_switch.location = (600, 0)
        links.new(group_in.outputs['Smooth iterations'], index_switch.inputs['Index'])

        stage_geometry = hugged
        links.new(stage_geometry, index_switch.inputs[1])  # stage 0 = no smoothing
        for iteration in range(1, 6):
            if len(index_switch.index_switch_items) < iteration + 1:
                index_switch.index_switch_items.new()
            blur = nodes.new('GeometryNodeBlurAttribute')
            blur.data_type = 'FLOAT_VECTOR'
            blur.location = (60 + iteration * 80, 200 + iteration * 40)
            position = nodes.new('GeometryNodeInputPosition')
            position.location = (blur.location[0] - 140, blur.location[1])
            links.new(position.outputs['Position'], blur.inputs[0])
            blur.inputs[1].default_value = 1  # Iterations (single blur pass per stage, chained)
            set_pos = nodes.new('GeometryNodeSetPosition')
            set_pos.location = (blur.location[0] + 140, blur.location[1])
            links.new(stage_geometry, set_pos.inputs['Geometry'])
            links.new(blur.outputs[0], set_pos.inputs['Position'])
            stage_geometry = set_pos.outputs['Geometry']
            links.new(stage_geometry, index_switch.inputs[iteration + 1])

        return index_switch.outputs['Output']

    @staticmethod
    def build_shell_node_group(group_name, basemesh=None):
        node_group = HairCardService._new_group(group_name)
        nodes = node_group.nodes
        links = node_group.links
        group_out = next(n for n in nodes if n.bl_idname == 'NodeGroupOutput')
        group_out.location = (1400, 0)

        shell_geometry = HairCardService._build_shell_base(node_group, basemesh)
        links.new(shell_geometry, group_out.inputs['Geometry'])
        return node_group

    @staticmethod
    def _kmeans_roots(roots, cluster_count, seed, iterations=12, restarts=None):
        """K-means over strand root positions, seeded for reproducibility.

        Starts from k-means++ centres (each next centre is picked with a probability growing with its squared distance
        from the centres picked so far) and keeps the best of a few runs.
        """
        import numpy as np

        rng = np.random.RandomState(seed)
        cluster_count = min(cluster_count, len(roots))
        if restarts is None:
            restarts = 3 if len(roots) * cluster_count <= _KMEANS_RESTART_BUDGET else 1

        def assign(centers):
            """Nearest centre per root and the distance to it, in chunks to keep the distance matrix small."""
            out = np.empty(len(roots), dtype=np.int64)
            nearest = np.empty(len(roots), dtype=np.float64)
            for start in range(0, len(roots), 4096):
                block = roots[start:start + 4096]
                distances = np.linalg.norm(block[:, None, :] - centers[None, :, :], axis=2)
                out[start:start + 4096] = np.argmin(distances, axis=1)
                nearest[start:start + 4096] = distances.min(axis=1)
            return out, nearest

        def starting_centers():
            centers = np.empty((cluster_count, roots.shape[1]), dtype=np.float64)
            centers[0] = roots[rng.randint(0, len(roots))]
            closest = np.linalg.norm(roots - centers[0], axis=1) ** 2
            for index in range(1, cluster_count):
                total = closest.sum()
                # Every root already on centre (duplicate roots)
                pick = rng.randint(0, len(roots)) if total <= 0.0 else rng.choice(len(roots), p=closest / total)
                centers[index] = roots[pick]
                closest = np.minimum(closest, np.linalg.norm(roots - centers[index], axis=1) ** 2)
            return centers

        best = None
        for _run in range(max(1, restarts)):
            centers = starting_centers()
            for _ in range(iterations):
                assignments, _nearest = assign(centers)
                for cluster_index in range(cluster_count):
                    members = roots[assignments == cluster_index]
                    if len(members) > 0:
                        centers[cluster_index] = members.mean(axis=0)
                    else:
                        # Re-seed empty clusters from a random strand
                        centers[cluster_index] = roots[rng.randint(0, len(roots))]
            assignments, nearest = assign(centers)
            spread = float((nearest ** 2).sum())
            if best is None or spread < best[0]:
                best = (spread, assignments)
        return best[1], cluster_count

    @staticmethod
    def _evaluated_curves(hair_obj, depsgraph=None):
        """The hair curves as the viewport shows them (with the grooming stack applied).

        Falls back to the raw data if the evaluated object carries no curves.
        """
        if depsgraph is None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        try:
            evaluated = hair_obj.evaluated_get(depsgraph)
        except Exception:
            return hair_obj.data
        data = getattr(evaluated, "data", None)
        if isinstance(data, bpy.types.Curves) and len(data.curves) > 0:
            return data
        return hair_obj.data

    @staticmethod
    def _read_clustered_strands(hair_obj, cluster_count, min_strands, seed, depsgraph):
        """Reads the evaluated groom into numpy and groups strands into clusters by their roots.

        Returns None if there is not enough hair to form a single cluster, otherwise a dict with the flat point positions,
        per-curve point ranges, roots, tips, the cluster assignment and the cluster count.
        """
        import numpy as np

        curves = HairCardService._evaluated_curves(hair_obj, depsgraph)
        curve_count = len(curves.curves)
        if curve_count == 0 or curve_count < min_strands:
            return None

        flat_positions = np.empty(len(curves.points) * 3, dtype=np.float64)
        curves.points.foreach_get('position', flat_positions)
        positions = flat_positions.reshape(-1, 3)

        first_index = np.empty(curve_count, dtype=np.int64)
        point_count = np.empty(curve_count, dtype=np.int64)
        curves.curves.foreach_get('first_point_index', first_index)
        curves.curves.foreach_get('points_length', point_count)

        roots = positions[first_index]
        tips = positions[first_index + point_count - 1]
        assignments, actual_cluster_count = HairCardService._kmeans_roots(roots, cluster_count, seed)

        return {
            "positions": positions,
            "first_index": first_index,
            "point_count": point_count,
            "roots": roots,
            "tips": tips,
            "assignments": assignments,
            "cluster_count": actual_cluster_count,
            }

    @staticmethod
    def _bundle_members(clustered, cluster_index, min_strands):
        """Indices of the strands in one cluster strided down to a sane number if they are too many, None if too few."""
        import numpy as np

        members = np.nonzero(clustered["assignments"] == cluster_index)[0]
        if len(members) < min_strands:
            return None
        if len(members) > _MAX_MEMBERS_PER_BUNDLE:
            stride = len(members) // _MAX_MEMBERS_PER_BUNDLE
            members = members[::stride][:_MAX_MEMBERS_PER_BUNDLE]
        return members

    @staticmethod
    def build_cluster_ribbon_mesh(hair_obj, cluster_count, min_strands, seed, samples, depsgraph=None):
        """Build one averaged poly-line per cluster of nearby strands as a base for ribbon card.

        Member strands are resampled onto a common 0..1 parameter before being averaged.
        Each cluster also records how far its strands spread out at root, so the node group can use it for card width.

        Returns bpy.types.Mesh (mesh of edge chains), or None if no cluster qualified.
        """
        import numpy as np

        clustered = HairCardService._read_clustered_strands(hair_obj, cluster_count, min_strands, seed, depsgraph)
        if clustered is None:
            return None

        positions = clustered["positions"]
        first_index = clustered["first_index"]
        point_count = clustered["point_count"]
        roots = clustered["roots"]

        samples = max(2, int(samples))
        target = np.linspace(0.0, 1.0, samples)

        averaged = []
        half_widths = []
        for cluster_index in range(clustered["cluster_count"]):
            members = HairCardService._bundle_members(clustered, cluster_index, min_strands)
            if members is None:
                continue

            accumulator = np.zeros((samples, 3), dtype=np.float64)
            used = 0
            for member in members:
                start = first_index[member]
                count = point_count[member]
                if count < 2:
                    continue
                strand = positions[start:start + count]
                # Resample by arc length, so points bunched up at the root do not drag the average towards the scalp
                steps = np.linalg.norm(np.diff(strand, axis=0), axis=1)
                travelled = np.concatenate(([0.0], np.cumsum(steps)))
                if travelled[-1] <= 0.0:
                    continue
                parameter = travelled / travelled[-1]
                for axis in range(3):
                    accumulator[:, axis] += np.interp(target, parameter, strand[:, axis])
                used += 1

            if used == 0:
                continue
            averaged.append(accumulator / used)

            member_roots = roots[members]
            spread = member_roots - member_roots.mean(axis=0)
            half_widths.append(float(np.sqrt((spread ** 2).sum(axis=1).mean())))

        if not averaged:
            return None

        vertices = np.concatenate(averaged, axis=0)
        edges = []
        for bundle in range(len(averaged)):
            base = bundle * samples
            edges.extend((base + step, base + step + 1) for step in range(samples - 1))

        mesh = bpy.data.meshes.new(f"{hair_obj.name}_cluster_ribbons")
        mesh.from_pydata([tuple(v) for v in vertices], edges, [])
        mesh.update()

        # Stored per point because Mesh to Curve keeps point attributes
        width_attribute = mesh.attributes.new(CLUSTER_WIDTH_ATTRIBUTE, 'FLOAT', 'POINT')
        width_attribute.data.foreach_set(
            'value', np.repeat(np.array(half_widths, dtype=np.float32), samples))

        return mesh

    @staticmethod
    def build_cluster_box_mesh(hair_obj, cluster_count, min_strands, seed, depsgraph=None):
        """Build one oriented quad per cluster of nearby strands.

        Strand roots are grouped with k-means
        PCA over the member points gives the card axes: the longest is the length (following root-tip direction), the next is the width and the flattest is the face normal.
        The result is a static mesh, that only changes on "Regenerate".

        Returns a bpy.types.Mesh, or None if there were not enough strands to form a single cluster.
        """
        import numpy as np

        clustered = HairCardService._read_clustered_strands(hair_obj, cluster_count, min_strands, seed, depsgraph)
        if clustered is None:
            return None

        positions = clustered["positions"]
        first_index = clustered["first_index"]
        point_count = clustered["point_count"]
        roots = clustered["roots"]
        tips = clustered["tips"]
        actual_cluster_count = clustered["cluster_count"]

        verts = []
        faces = []
        uvs = []

        for cluster_index in range(actual_cluster_count):
            member_curve_indices = HairCardService._bundle_members(clustered, cluster_index, min_strands)
            if member_curve_indices is None:
                continue

            member_point_ranges = [
                (first_index[i], first_index[i] + point_count[i]) for i in member_curve_indices
                ]
            member_points = np.concatenate([positions[start:end] for start, end in member_point_ranges], axis=0)
            if len(member_points) < 3:
                continue

            centroid = member_points.mean(axis=0)
            centered = member_points - centroid
            covariance = (centered.T @ centered) / len(centered)
            eigvals, eigvecs = np.linalg.eigh(covariance)
            # eigh() returns ascending eigenvalues - the last column is the length axis, the first the flattest one (card normal)
            length_axis = eigvecs[:, 2]
            width_axis = eigvecs[:, 1]
            normal_axis = eigvecs[:, 0]

            flow = (tips[member_curve_indices] - roots[member_curve_indices]).mean(axis=0)
            if np.dot(length_axis, flow) < 0:
                length_axis = -length_axis

            length_proj = centered @ length_axis
            width_proj = centered @ width_axis
            length_center = (length_proj.max() + length_proj.min()) / 2.0
            width_center = (width_proj.max() + width_proj.min()) / 2.0
            half_length = max((length_proj.max() - length_proj.min()) / 2.0, 1e-5)
            half_width = max((width_proj.max() - width_proj.min()) / 2.0, 1e-5)

            card_center = centroid + length_center * length_axis + width_center * width_axis

            # Wind the corners so that the face normal matches normal_axis
            winding_normal = np.cross(length_axis, width_axis)
            corner_order = ((-1, -1), (1, -1), (1, 1), (-1, 1))
            if np.dot(winding_normal, normal_axis) < 0:
                corner_order = tuple(reversed(corner_order))

            base_index = len(verts)
            for length_sign, width_sign in corner_order:
                corner = card_center + length_sign * half_length * length_axis + width_sign * half_width * width_axis
                verts.append(tuple(corner))
                # V along the cluster length, U across its width
                uvs.append(((width_sign + 1) / 2.0, (length_sign + 1) / 2.0))
            faces.append((base_index, base_index + 1, base_index + 2, base_index + 3))

        if not faces:
            return None

        mesh = bpy.data.meshes.new(f"{hair_obj.name}_cluster_boxes")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        uv_layer = mesh.uv_layers.new(name="UVMap")
        for loop in mesh.loops:
            uv_layer.data[loop.index].uv = uvs[loop.vertex_index]

        return mesh

    @staticmethod
    @contextmanager
    def _evaluated_surface(surface_obj, depsgraph=None):
        """The body mesh as it appears on screen (hidden helpers, applied morphs etc.), for the duration of the block."""
        if depsgraph is None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = surface_obj.evaluated_get(depsgraph)
        try:
            yield evaluated.to_mesh()
        finally:
            evaluated.to_mesh_clear()

    @staticmethod
    def _body_face_indices(surface_obj, mesh):
        """The faces of ``mesh`` that are actual body surface (None if can't be determined)."""
        criteria = []
        for modifier in surface_obj.modifiers:
            if modifier.type != 'MASK' or not modifier.vertex_group:
                continue
            group = surface_obj.vertex_groups.get(modifier.vertex_group)
            if group is not None:
                criteria.append((group.index, modifier.invert_vertex_group))
        if not criteria:
            return None

        allowed = None
        for group_index, inverted in criteria:
            member = [any(group.group == group_index for group in vertex.groups)
                      for vertex in mesh.vertices]
            # Normal mask keeps face only if all its corners belong to the group, inverted drops it if any is
            kept = {polygon.index for polygon in mesh.polygons
                    if (not any(member[i] for i in polygon.vertices) if inverted
                        else all(member[i] for i in polygon.vertices))}
            allowed = kept if allowed is None else (allowed & kept)
        return allowed

    @staticmethod
    def _fur_bearing_faces_in(mesh, surface_obj, hair_obj, face_dilation, depsgraph=None):
        """Which faces of an already opened evaluated body mesh the hair asset grows out of."""
        import numpy as np
        from mathutils.bvhtree import BVHTree

        curves = HairCardService._evaluated_curves(hair_obj, depsgraph)
        if len(curves.curves) == 0:
            return set()

        positions = np.empty(len(curves.points) * 3, dtype=np.float64)
        curves.points.foreach_get('position', positions)
        positions = positions.reshape(-1, 3)
        first_index = np.empty(len(curves.curves), dtype=np.int64)
        curves.curves.foreach_get('first_point_index', first_index)
        roots = positions[first_index]
        if len(roots) > _MAX_ROOT_SAMPLES:
            roots = roots[::len(roots) // _MAX_ROOT_SAMPLES]

        allowed = HairCardService._body_face_indices(surface_obj, mesh)

        # Roots and mesh are in different local spaces
        to_surface_local = surface_obj.matrix_world.inverted() @ hair_obj.matrix_world
        tree = BVHTree.FromPolygons([vertex.co for vertex in mesh.vertices],
                                    [tuple(polygon.vertices) for polygon in mesh.polygons],
                                    all_triangles=False, epsilon=0.0)
        faces = set()
        for root in roots:
            _location, _normal, index, _distance = tree.find_nearest(to_surface_local @ Vector(tuple(root)))
            if index is not None:
                faces.add(index)
        if allowed is not None:
            faces &= allowed

        for _ring in range(max(0, int(face_dilation))):
            faces = HairCardService._grow_face_set(mesh, faces)
            if allowed is not None:
                faces &= allowed
        return faces

    @staticmethod
    def _fur_bearing_faces(surface_obj, hair_obj, face_dilation, depsgraph=None):
        """Indices of the evaluated body faces the hair asset grows out of.

        Used only for counting and measuring as indices are only valid for the evaluated mesh.
        """
        with HairCardService._evaluated_surface(surface_obj, depsgraph) as mesh:
            return HairCardService._fur_bearing_faces_in(mesh, surface_obj, hair_obj, face_dilation, depsgraph)

    @staticmethod
    def _grow_face_set(mesh, faces):
        """The given faces plus every face sharing a vertex with them."""
        wanted_vertices = set()
        for index in faces:
            wanted_vertices.update(mesh.polygons[index].vertices)
        grown = set(faces)
        for polygon in mesh.polygons:
            if polygon.index in grown:
                continue
            if wanted_vertices.intersection(polygon.vertices):
                grown.add(polygon.index)
        return grown

    @staticmethod
    def build_body_shell_mesh(surface_obj, hair_obj, face_dilation, depsgraph=None):
        """A mesh holding just the body faces the asset grows from, with its UVs renormalised.

        Cut out of the body as it currently appears (_evaluated_surface).
        Body UV layout is kept, but normalised uniformly onto patch bounding box, so patch uses whole texture.

        Returns a bpy.types.Mesh, or None if the asset does not appear to grow from this surface.
        """
        import bmesh

        with HairCardService._evaluated_surface(surface_obj, depsgraph) as surface_mesh:
            faces = HairCardService._fur_bearing_faces_in(surface_mesh, surface_obj, hair_obj, face_dilation, depsgraph)
            if not faces:
                return None

            mesh = None
            bm = bmesh.new()
            try:
                bm.from_mesh(surface_mesh)
                bm.faces.ensure_lookup_table()
                doomed = [face for face in bm.faces if face.index not in faces]
                if doomed:
                    bmesh.ops.delete(bm, geom=doomed, context='FACES')
                if not bm.faces:
                    return None

                # Shape key layers of evaluated mesh are dropped, shell follows the body through Surface Deform
                shape_layers = bm.verts.layers.shape
                for name in list(shape_layers.keys()):
                    shape_layers.remove(shape_layers[name])

                uv_layer = bm.loops.layers.uv[0] if bm.loops.layers.uv else None
                if uv_layer is not None:
                    coordinates = [loop[uv_layer].uv for face in bm.faces for loop in face.loops]
                    min_u = min(uv.x for uv in coordinates)
                    min_v = min(uv.y for uv in coordinates)
                    extent = max(max(uv.x for uv in coordinates) - min_u,
                                 max(uv.y for uv in coordinates) - min_v)
                    if extent > 1e-6:
                        for uv in coordinates:
                            uv.x = (uv.x - min_u) / extent
                            uv.y = (uv.y - min_v) / extent

                mesh = bpy.data.meshes.new(f"{hair_obj.name}_body_shell")
                bm.to_mesh(mesh)
            finally:
                bm.free()

        mesh.update()
        return mesh

    @staticmethod
    def hair_extent_above_surface(surface_obj, hair_obj, depsgraph=None, samples=4000):
        """How far out of the body the hair reaches, in metres, or 0.0 if it cannot be measured.

        Used to start the body shell bake rays far enough out to capture the whole length of the fur.
        Points sampled for speed.
        """
        import numpy as np
        from mathutils.bvhtree import BVHTree

        curves = HairCardService._evaluated_curves(hair_obj, depsgraph)
        if len(curves.curves) == 0:
            return 0.0

        positions = np.empty(len(curves.points) * 3, dtype=np.float64)
        curves.points.foreach_get('position', positions)
        positions = positions.reshape(-1, 3)
        if len(positions) > samples:
            positions = positions[::len(positions) // samples]

        with HairCardService._evaluated_surface(surface_obj, depsgraph) as mesh:
            tree = BVHTree.FromPolygons([vertex.co for vertex in mesh.vertices],
                                        [tuple(polygon.vertices) for polygon in mesh.polygons],
                                        all_triangles=False, epsilon=0.0)
            to_surface_local = surface_obj.matrix_world.inverted() @ hair_obj.matrix_world
            furthest = 0.0
            for position in positions:
                _location, _normal, index, distance = tree.find_nearest(
                    to_surface_local @ Vector(tuple(position)))
                if index is not None and distance is not None:
                    furthest = max(furthest, distance)
        return float(furthest)

    @staticmethod
    @contextmanager
    def body_held_at_rest_pose(rig):
        """Hold the character in its rest pose for the duration of the block.

        ``surfacedeform_bind`` silently refuses to bind (``is_bound`` stays False) while the armature is posed,
        and a shell cut from a posed body would store the posed shape as its rest shape.

        A rig of None, or one already at rest, makes this a no-op.
        """
        if rig is None or rig.data.pose_position == 'REST':
            yield
            return
        previous = rig.data.pose_position
        rig.data.pose_position = 'REST'
        try:
            bpy.context.view_layer.update()
            yield
        finally:
            rig.data.pose_position = previous
            bpy.context.view_layer.update()

    @staticmethod
    def weight_body_shell_to_rig(shell_obj, surface_obj, rig):
        """Give shell the bone weights of the body, so that it exports as skinned geometry.

        The shell vertices are body vertices, so the body weights apply verbatim and are already in the mesh.
        Only the vertex group names are missing, they are recreated in the surface object order.

        Only works for a shell cut after the rig was added, MPFB loads the bone weights onto the body together with the rig.
        """
        from .rigservice import RigService

        if rig is None:
            return False

        existing = {group.name for group in shell_obj.vertex_groups}
        for group in surface_obj.vertex_groups:
            if group.name not in existing:
                shell_obj.vertex_groups.new(name=group.name)

        # Same call used in clothes path. move_to_top puts the armature ahead of the Surface Deform added next
        RigService.ensure_armature_modifier(shell_obj, rig)
        return True

    @staticmethod
    def body_shell_is_weighted_to(shell_obj, rig):
        """Whether this shell would deform with the given rig on its own."""
        if shell_obj is None or rig is None:
            return False
        return any(modifier.type == 'ARMATURE' and modifier.object == rig
                   for modifier in shell_obj.modifiers)

    @staticmethod
    def bind_body_shell_to_body(context, shell_obj, surface_obj):
        """Tie the shell back to the body surface it was cut from. Returns whether succeeded.

        Surface Deform binds against the evaluated body, so the shell follows shape keys, targets and the armature.

        It has to be placed after armature modifier (armature only carries export weights).
        """
        from .objectservice import ObjectService

        follow = shell_obj.modifiers.new(name=BODY_SHELL_FOLLOW_MODIFIER_NAME, type='SURFACE_DEFORM')
        follow.target = surface_obj
        try:
            with context.temp_override(object=shell_obj, active_object=shell_obj,
                                       selected_objects=[shell_obj],
                                       selected_editable_objects=[shell_obj]):
                bpy.ops.object.surfacedeform_bind(modifier=follow.name)
        except Exception:
            ObjectService.deselect_and_deactivate_all()
            ObjectService.activate_blender_object(shell_obj)
            try:
                bpy.ops.object.surfacedeform_bind(modifier=follow.name)
            except Exception:
                pass
        if not follow.is_bound:
            # Unbound Surface Deform does nothing, so its removed. Shell stays static
            shell_obj.modifiers.remove(follow)
            return False
        return True

    @staticmethod
    def store_shell_edge_fade(mesh, width_in_rings):
        """Write a 0..1 weight per vertex: 0 on the patch border, 1 once ``width_in_rings`` faces in.

        The shell is a patch with a hard border, this lets the baked shader fade out on the rim of the shell.

        Returns True if fade weight was written. A closed patch (no border) or a width of zero leaves the mesh untouched.
        """
        import bmesh

        width = max(0, int(width_in_rings))
        if width == 0:
            return False

        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()

            # A border edge has one face in the patch, its vertices are the outer rim
            frontier = {vertex.index for edge in bm.edges if len(edge.link_faces) == 1
                        for vertex in edge.verts}
            if not frontier or len(frontier) == len(bm.verts):
                return False

            # BFS over edges - distance in face rings
            distance = {index: 0 for index in frontier}
            current = frontier
            for ring in range(1, width + 1):
                nxt = set()
                for index in current:
                    for edge in bm.verts[index].link_edges:
                        other = edge.other_vert(bm.verts[index]).index
                        if other not in distance:
                            distance[other] = ring
                            nxt.add(other)
                if not nxt:
                    break
                current = nxt

            attribute = mesh.attributes.get(SHELL_EDGE_FADE_ATTRIBUTE)
            if attribute is None:
                attribute = mesh.attributes.new(SHELL_EDGE_FADE_ATTRIBUTE, 'FLOAT', 'POINT')
            for index in range(len(mesh.vertices)):
                # Vertices the search never reached are further in than the fade width (opaque), the rest ramps linearly to zero
                attribute.data[index].value = min(1.0, distance.get(index, width) / float(width))
            mesh.update()
            return True
        finally:
            bm.free()

    @staticmethod
    def build_body_shell_node_group(group_name):
        """Float the duplicated body faces off the skin, along a smoothed normal.

        Normals are blurred first, so the offset does not self-intersect on concave parts of the body (e.g. armpit, behind the ear).
        """
        node_group = HairCardService._new_group(group_name)
        nodes = node_group.nodes
        links = node_group.links
        group_in = HairCardService._group_input_node(node_group)
        group_out = next(n for n in nodes if n.bl_idname == 'NodeGroupOutput')
        group_in.location = (-800, 0)
        group_out.location = (400, 0)

        HairCardService._add_input(node_group, 'Height', 'NodeSocketFloat', 0.006, (0.0, 0.2))
        HairCardService._add_input(node_group, 'Normal smoothing', 'NodeSocketInt', 3, (0, 20))

        normal = nodes.new('GeometryNodeInputNormal')
        normal.location = (-600, -200)

        blur = nodes.new('GeometryNodeBlurAttribute')
        blur.data_type = 'FLOAT_VECTOR'
        blur.location = (-420, -200)
        links.new(normal.outputs['Normal'], blur.inputs[0])
        links.new(group_in.outputs['Normal smoothing'], blur.inputs[1])

        normalize = nodes.new('ShaderNodeVectorMath')
        normalize.operation = 'NORMALIZE'
        normalize.location = (-240, -200)
        links.new(blur.outputs[0], normalize.inputs[0])

        offset = nodes.new('ShaderNodeVectorMath')
        offset.operation = 'SCALE'
        offset.location = (-60, -200)
        links.new(normalize.outputs[0], offset.inputs[0])
        links.new(group_in.outputs['Height'], offset.inputs['Scale'])

        set_position = nodes.new('GeometryNodeSetPosition')
        set_position.location = (180, 0)
        links.new(group_in.outputs['Geometry'], set_position.inputs['Geometry'])
        links.new(offset.outputs[0], set_position.inputs['Offset'])

        links.new(set_position.outputs['Geometry'], group_out.inputs['Geometry'])
        return node_group
