"""
Module with logic regarding staging characters for export.

In many cases, external applications will have difficulties managing blender logic such as shape keys, materials, modifiers
and animations. This module provides a set of tools to create character copies where such logic is baked, transformed or
otherwise managed.
"""

import bpy
from .logservice import LogService
from .targetservice import TargetService
from .objectservice import ObjectService
from .clothesservice import ClothesService
from ..entities.clothes.mhclo import Mhclo

_LOG = LogService.get_logger("services.exportservice")
_LOG.set_level(LogService.DEBUG)

MICROSOFT_VISEMES = [
    "aa_02",
    "aa_ah_ax_01",
    "ao_03",
    "aw_09",
    "ay_11",
    "d_t_n_19",
    "er_05",
    "ey_eh_uh_04",
    "f_v_18",
    "h_12",
    "k_g_ng_20",
    "l_14",
    "ow_08",
    "oy_10",
    "p_b_m_21",
    "r_13",
    "sh_ch_jh_zh_16",
    "sil_00",
    "s_z_15",
    "th_dh_17",
    "w_uw_07",
    "y_iy_ih_ix_06"
    ]

META_VISEMES = [
    "viseme_aa",
    "viseme_CH",
    "viseme_DD",
    "viseme_E",
    "viseme_FF",
    "viseme_I",
    "viseme_kk",
    "viseme_nn",
    "viseme_O",
    "viseme_PP",
    "viseme_RR",
    "viseme_sil",
    "viseme_SS",
    "viseme_TH",
    "viseme_U"
    ]

# TODO: List arkit face units here

# If no vert was shifted more than this in a shape key, assume the shape key is not significant enough to be interpolated.
SIGNIFICANT_SHIFT_MINIMUM = 0.0001

class ExportService:
    """The ExportService class serves as a utility class for staging characters for export.

    Note that this class is designed to be used without instantiation. All methods are static methods that can be called directly."""

    def __init__(self):
        raise RuntimeError("You should not instance ExportService. Use its static methods instead.")

    @staticmethod
    def create_character_copy(source_object, name_suffix="_export_copy", place_in_collection=None):
        """
        Creates a deep copy of the given character, including any rig or child meshes connected to it.

        Args:
        - source_object (bpy.types.Object): The source object to create a copy of. This is usually the basemesh or the rig
        - name_suffix (str): A suffix to append to created objects' names.
        - place_in_collection (bpy.types.Collection, optional): The collection where the character copy should be placed. If not provided, the copy will be placed in the default collection.

        Returns:
        - bpy.types.Object: The created character copy.
        """

        _LOG.enter()

        _LOG.debug("source_object", source_object)

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(source_object)
        if not basemesh:
            _LOG.error("No basemesh related to the given object", source_object)
            raise ValueError("No basemesh related to the given object")

        _LOG.debug("Basemesh", basemesh)

        root_object = basemesh
        if basemesh.parent:
            root_object = basemesh.parent

        _LOG.debug("Root object", root_object)

        children = ObjectService.get_list_of_children(root_object)

        _LOG.debug("Children", children)

        new_root = ObjectService.duplicate_blender_object(root_object, collection=place_in_collection)
        new_root.name = root_object.name + name_suffix

        for child in children:
            _LOG.debug("Child", child)
            name = child.name + name_suffix
            duplicated_child = ObjectService.duplicate_blender_object(child, collection=place_in_collection, parent=new_root)
            duplicated_child.name = name
            if new_root.type == 'ARMATURE':
                # We need to make sure that any armature modifier on the child is pointed to the new root
                modifier = duplicated_child.modifiers.get("Armature") # Assuming there's only one armature modifier
                if modifier:
                    modifier.object = new_root

        return new_root

    @staticmethod
    def load_targets(basemesh, load_microsoft_visemes=True, load_meta_visemes=False, load_arkit_faceunits=False):
        """Bulk load targets, if installed. Will raise exception if target asset pack is not installed."""
        _LOG.enter()

        target_stack = []

        if load_microsoft_visemes:
            for target in MICROSOFT_VISEMES:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if load_meta_visemes:
            for target in META_VISEMES:
                _LOG.debug("Adding target", target)
                target_stack.append(
                    {
                        "target": target,
                        "value": 0.0
                    })

        if len(target_stack) > 0:
            TargetService.bulk_load_targets(basemesh, target_stack)

    @staticmethod
    def interpolate_targets(basemesh):
        """Interpolate viseme and faceunit shape keys from the basemesh to child meshes.

        For each child mesh that has an associated MHCLO file, this method transfers all non-modelling
        shape keys from the basemesh using the MHCLO vertex correspondence data.

        Args:
            basemesh (bpy.types.Object): The basemesh object whose shape keys will be interpolated to children.
        """
        _LOG.enter()

        if not basemesh.data.shape_keys or not basemesh.data.shape_keys.key_blocks:
            _LOG.debug("No shape keys on basemesh, nothing to interpolate")
            return

        # Temporarily disable all modifiers on the basemesh. Store their state so they can be restored in the end of the function
        modifier_states = {}
        for modifier in basemesh.modifiers:
            _LOG.debug("Disabling modifier", (modifier.name, modifier.show_viewport))
            modifier_states[modifier.name] = modifier.show_viewport
            modifier.show_viewport = False

        root_object = basemesh
        if basemesh.parent:
            root_object = basemesh.parent

        children = ObjectService.get_list_of_children(root_object)
        _LOG.debug("Children to interpolate to", children)

        all_relevant_shapekey_names = list(MICROSOFT_VISEMES)
        all_relevant_shapekey_names.extend(list(META_VISEMES))
        # TODO: Extend to handle faceunit shape keys as well as viseme shape keys

        shape_keys_to_interpolate = []
        for key_block in basemesh.data.shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue
            if key_block.name not in all_relevant_shapekey_names:
                continue
            shape_keys_to_interpolate.append(key_block)

        if not shape_keys_to_interpolate:
            _LOG.debug("No viseme/faceunit shape keys found to interpolate")
            return

        _LOG.debug("Shape keys to interpolate", [sk.name for sk in shape_keys_to_interpolate])

        basis_coords = [v.co.copy() for v in basemesh.data.vertices]

        for child in children:
            if child == basemesh or child.type != 'MESH':
                continue

            mhclo_path = ClothesService.find_clothes_absolute_path(child)
            if not mhclo_path:
                _LOG.debug("No MHCLO path for child, skipping", child.name)
                continue

            _LOG.debug("Interpolating shape keys to", child.name)

            mhclo = Mhclo()
            mhclo.load(mhclo_path)

            if not child.data.shape_keys:
                child.shape_key_add(name="Basis", from_mix=False)

            for source_key in shape_keys_to_interpolate:
                if source_key.name in child.data.shape_keys.key_blocks:
                    _LOG.debug("Shape key already exists on child, skipping", (child.name, source_key.name))
                    continue

                # First, calculate all interpolated offsets to check if any are significant
                significant_changes = []
                for child_vert_idx in mhclo.verts:
                    if child_vert_idx >= len(child.data.vertices):
                        break
                    mapping = mhclo.verts[child_vert_idx]
                    v0, v1, v2 = mapping["verts"]
                    w0, w1, w2 = mapping["weights"]

                    if v0 >= len(source_key.data) or v1 >= len(source_key.data) or v2 >= len(source_key.data):
                        continue

                    offset0 = source_key.data[v0].co - basis_coords[v0]
                    offset1 = source_key.data[v1].co - basis_coords[v1]
                    offset2 = source_key.data[v2].co - basis_coords[v2]

                    interpolated_offset = offset0 * w0 + offset1 * w1 + offset2 * w2

                    # Check if this offset is significant
                    if interpolated_offset.length > SIGNIFICANT_SHIFT_MINIMUM:
                        significant_changes.append((child_vert_idx, interpolated_offset))

                # Only create the shape key if there are significant changes
                if not significant_changes:
                    _LOG.debug("No significant changes for shape key, skipping", (child.name, source_key.name))
                    continue

                new_key = child.shape_key_add(name=source_key.name, from_mix=False)
                new_key.value = source_key.value

                # Apply the significant changes
                for child_vert_idx, interpolated_offset in significant_changes:
                    new_key.data[child_vert_idx].co = child.data.vertices[child_vert_idx].co + interpolated_offset

                _LOG.debug("Interpolated shape key to child", (source_key.name, child.name))

        # Restore the modifier states
        for modifier in basemesh.modifiers:
            if modifier.name in modifier_states:
                modifier.show_viewport = modifier_states[modifier.name]

    @staticmethod
    def bake_modifiers_remove_helpers(basemesh, bake_masks=False, bake_subdiv=False, remove_helpers=True, also_proxy=True):
        """Bakes modifiers and optionally remove helpers.

        Args:
        - basemesh (bpy.types.Object): The object to bake shape keys, masks, and subdivision modifiers for.
        - bake_masks (bool): Whether to bake masks.
        - bake_subdiv (bool): Whether to bake subdivision modifiers.
        - remove_helpers (bool): Whether to remove helper geometry
        - also_proxy (bool): Whether to also bake on the body proxy if it exists.
        """

        _LOG.enter()

        has_sk = TargetService.has_any_shapekey(basemesh)

        helpers_removed_by_modifier = False

        bpy.context.view_layer.objects.active = basemesh

        if (bake_masks or bake_subdiv) and has_sk:
            # Pre-adjust SUBSURF levels to render_levels so duplicates inherit the right level
            for modifier in basemesh.modifiers:
                if modifier.type == 'SUBSURF' and bake_subdiv:
                    modifier.levels = modifier.render_levels

            # Collect modifiers to apply (in order)
            mods_to_apply = []
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and bake_masks:
                    if modifier.vertex_group == "body" and not modifier.invert_vertex_group:
                        helpers_removed_by_modifier = True
                        mods_to_apply.append(modifier.name)
                    elif modifier.vertex_group == "body" and modifier.invert_vertex_group:
                        pass  # handled in cleanup loop below
                    else:
                        mods_to_apply.append(modifier.name)
                elif modifier.type == 'SUBSURF' and bake_subdiv and modifier.levels > 0:
                    mods_to_apply.append(modifier.name)

            ExportService._apply_modifiers_keep_shapekeys(basemesh, mods_to_apply)

            # Cleanup: remove all bake-related modifiers from basemesh object
            # (applied ones had their effect baked into mesh data; unapplied ones are discarded)
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and bake_masks:
                    basemesh.modifiers.remove(modifier)
                elif modifier.type == 'SUBSURF' and bake_subdiv:
                    basemesh.modifiers.remove(modifier)
        else:
            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and bake_masks:
                    if modifier.vertex_group == "body" and not modifier.invert_vertex_group:
                        # This is the modifier that hides helper geometry
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
                        helpers_removed_by_modifier = True
                    else:
                        if modifier.vertex_group == "body" and modifier.invert_vertex_group:
                            # This is the modifier that hides the body if there is a proxy. It does not make much
                            # sense to keep this if we're baking masks, but it doesn't make sense to bake it either
                            basemesh.modifiers.remove(modifier)
                        else:
                            # This is probably a clothes delete group
                            bpy.ops.object.modifier_apply(modifier=modifier.name)
                else:
                    if modifier.type == 'SUBSURF' and bake_subdiv:
                        modifier.levels = modifier.render_levels
                        if modifier.levels == 0:
                            basemesh.modifiers.remove(modifier)
                        else:
                            bpy.ops.object.modifier_apply(modifier=modifier.name)

        if remove_helpers and not helpers_removed_by_modifier:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            ExportService._delete_vertex_group(basemesh, "HelperGeometry")
            ExportService._delete_vertex_group(basemesh, "JointCubes")

            for modifier in basemesh.modifiers:
                if modifier.type == 'MASK' and modifier.vertex_group == 'body' and not modifier.invert_vertex_group:
                    basemesh.modifiers.remove(modifier)

            if has_sk:
                TargetService.reapply_all_details(basemesh)

            basemesh.select_set(True)
            ObjectService.activate_blender_object(basemesh)

            for group in basemesh.vertex_groups:
                _LOG.trace("group name", group.name)
                if group.name.startswith("helper-") or group.name.startswith("joint-") or group.name in ["Mid", "Left", "Right"]:
                    basemesh.vertex_groups.remove(group)

        root_obj = basemesh
        if basemesh.parent is not None:
            root_obj = basemesh.parent

        ObjectService.activate_blender_object(root_obj, deselect_all=True)

        if also_proxy:
            proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")
            _LOG.debug("Proxy", proxy)
            if proxy is None:
                _LOG.debug("Requested to bake modifiers on proxy, but proxy not found.")
                return

            # Pre-adjust SUBSURF levels on proxy before collecting mods
            for modifier in proxy.modifiers:
                if modifier.type == 'SUBSURF' and bake_subdiv:
                    modifier.levels = modifier.render_levels

            proxy_mods_to_apply = []
            for modifier in proxy.modifiers:
                if modifier.type == 'MASK' and bake_masks:
                    proxy_mods_to_apply.append(modifier.name)
                elif modifier.type == 'SUBSURF' and bake_subdiv and modifier.levels > 0:
                    proxy_mods_to_apply.append(modifier.name)

            _LOG.debug("Proxy modifiers to apply", proxy_mods_to_apply)

            if len(proxy_mods_to_apply) < 1:
                _LOG.debug("No modifiers to bake on proxy.")
                return

            ObjectService.activate_blender_object(proxy, deselect_all=True)

            for mod_name in proxy_mods_to_apply:
                if mod_name in proxy.modifiers:
                    _LOG.debug("Baking proxy modifier", mod_name)
                    bpy.ops.object.modifier_apply(modifier=mod_name)

        ObjectService.activate_blender_object(root_obj, deselect_all=True)

    @staticmethod
    def _apply_modifiers_keep_shapekeys(basemesh, modifier_names_to_apply):
        """Apply modifiers to basemesh while preserving shape keys.

        Uses the copy-bake-apply-delta strategy: for each shape key, a temporary duplicate
        is baked and modified; the resulting vertex deltas vs a modified Basis mesh become
        the new shape key data on the final mesh.

        Args:
            basemesh (bpy.types.Object): The object to apply modifiers on.
            modifier_names_to_apply (list): Ordered list of modifier names to apply.
        """
        _LOG.enter()

        if not modifier_names_to_apply:
            return

        # Just in case, although this will probably never happen here
        if not TargetService.has_any_shapekey(basemesh):
            bpy.context.view_layer.objects.active = basemesh
            basemesh.select_set(True)
            for mod_name in modifier_names_to_apply:
                bpy.ops.object.modifier_apply(modifier=mod_name)
            return

        # Snapshot shape key metadata (skip Basis)
        original_sk_data = [
            {"name": kb.name, "value": kb.value}
            for kb in basemesh.data.shape_keys.key_blocks
            if kb.name != "Basis"
        ]

        _LOG.dump("Shape keys to preserve", [sk["name"] for sk in original_sk_data])

        bpy.ops.object.select_all(action='DESELECT')
        export_basis_obj = ObjectService.duplicate_blender_object(basemesh)
        bpy.context.view_layer.objects.active = export_basis_obj
        export_basis_obj.select_set(True)

        for kb in export_basis_obj.data.shape_keys.key_blocks:
            kb.value = 0.0

        TargetService.bake_targets(export_basis_obj)

        bpy.context.view_layer.objects.active = export_basis_obj
        export_basis_obj.select_set(True)
        for mod_name in modifier_names_to_apply:
            if mod_name in export_basis_obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod_name)

        n_verts = len(export_basis_obj.data.vertices)
        export_basis_coords = [0.0] * (n_verts * 3)
        export_basis_obj.data.vertices.foreach_get('co', export_basis_coords)

        _LOG.debug("export_basis vertex count", n_verts)

        # Per-key loop: build delta data for each shape key
        new_sk_deltas = []

        for sk_info in original_sk_data:
            sk_name = sk_info["name"]
            sk_value = sk_info["value"]

            bpy.ops.object.select_all(action='DESELECT')
            temp_obj = ObjectService.duplicate_blender_object(basemesh)
            bpy.context.view_layer.objects.active = temp_obj
            temp_obj.select_set(True)
            _LOG.debug("Created new temporary object", temp_obj.name)

            # Set only this key to 1.0
            for kb in temp_obj.data.shape_keys.key_blocks:
                if kb.name == sk_name:
                    kb.value = 1.0
                else:
                    kb.value = 0.0

            TargetService.bake_targets(temp_obj)

            bpy.context.view_layer.objects.active = temp_obj
            temp_obj.select_set(True)
            for mod_name in modifier_names_to_apply:
                if mod_name in temp_obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier=mod_name)

            if len(temp_obj.data.vertices) != n_verts:
                _LOG.warning("Vertex count mismatch for shape key, skipping", (sk_name, len(temp_obj.data.vertices), n_verts))
                bpy.data.objects.remove(temp_obj, do_unlink=True)
                continue

            temp_coords = [0.0] * (n_verts * 3)
            temp_obj.data.vertices.foreach_get('co', temp_coords)

            significant_deltas = []
            min_sq = SIGNIFICANT_SHIFT_MINIMUM * SIGNIFICANT_SHIFT_MINIMUM
            for i in range(n_verts):
                dx = temp_coords[i * 3] - export_basis_coords[i * 3]
                dy = temp_coords[i * 3 + 1] - export_basis_coords[i * 3 + 1]
                dz = temp_coords[i * 3 + 2] - export_basis_coords[i * 3 + 2]
                if dx * dx + dy * dy + dz * dz > min_sq:
                    significant_deltas.append((i, dx, dy, dz))

            _LOG.debug("About to remove object", temp_obj.name)
            bpy.data.objects.remove(temp_obj, do_unlink=True)

            _LOG.debug("Shape key deltas", (sk_name, len(significant_deltas)))
            new_sk_deltas.append((sk_name, sk_value, significant_deltas))

        # Swap mesh data: replace basemesh.data with export_basis_obj.data
        old_mesh_data = basemesh.data
        basemesh.data = export_basis_obj.data
        bpy.data.objects.remove(export_basis_obj, do_unlink=True)
        bpy.data.meshes.remove(old_mesh_data)

        # Reconstruct shape keys from stored deltas
        if new_sk_deltas:
            basemesh.shape_key_add(name="Basis", from_mix=False)
            basis_key = basemesh.data.shape_keys.key_blocks["Basis"]

            basis_coords = [0.0] * (n_verts * 3)
            basemesh.data.vertices.foreach_get('co', basis_coords)

            for sk_name, sk_value, deltas in new_sk_deltas:
                new_key = basemesh.shape_key_add(name=sk_name, from_mix=False)
                new_key.value = sk_value
                new_key.relative_key = basis_key

                if deltas:
                    key_coords = list(basis_coords)
                    for idx, dx, dy, dz in deltas:
                        key_coords[idx * 3] = basis_coords[idx * 3] + dx
                        key_coords[idx * 3 + 1] = basis_coords[idx * 3 + 1] + dy
                        key_coords[idx * 3 + 2] = basis_coords[idx * 3 + 2] + dz
                    new_key.data.foreach_set('co', key_coords)


    @staticmethod
    def _delete_vertex_group(blender_object, vgroup_name):

        context = bpy.context

        _LOG.debug("Deleting vertex groups", (blender_object, vgroup_name))
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = blender_object
        blender_object.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        group_idx = None
        for group in blender_object.vertex_groups:
            _LOG.dump("group name", group.name)
            if vgroup_name in group.name:
                group_idx = group.index
        _LOG.dump("group index", group_idx)

        for vertex in blender_object.data.vertices:
            vertex.select = False
            for group in vertex.groups:
                if group.group == group_idx:
                    vertex.select = True
            _LOG.dump("Vertex index, selected", (vertex.index, vertex.select))

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        blender_object.select_set(False)

        # Re-query the vertex group after mesh topology changes
        group_to_remove = None
        for group in blender_object.vertex_groups:
            if vgroup_name in group.name:
                group_to_remove = group
                break

        if group_to_remove:
            _LOG.debug("Deleting vertex group", group_to_remove)
            blender_object.vertex_groups.remove(group_to_remove)
