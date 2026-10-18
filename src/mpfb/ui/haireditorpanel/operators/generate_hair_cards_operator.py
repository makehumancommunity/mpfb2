# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         7.5.2025  - updated 6.10.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for loading card asset or generating it
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import (HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_MODIFIER_NAME,
                              CARDS_OBJECT_SUFFIX, create_cards_properties,
                              create_cards_bake_properties, create_cards_config_properties,
                              set_cards_flag, get_cards_mode,
                              get_cards_selection_method, read_cards_settings,
                              get_bake_target, resolve_body_surface)
from .. import cardgenerators as cg

import bpy

_LOG = LogService.get_logger("haireditorpanel.generate_hair_cards_operator")


def build_cards_for_asset(context, basemesh, hair_obj, card_name, is_fur, properties, asset_name):
    """Build the card object for one hair/fur asset, according to its current mode.

    Returns (card_obj, used_generator), where used_generator is False when the card object is a finished
    mesh without a generator node group (cluster boxes).
    """
    target = get_bake_target(properties, basemesh, asset_name)

    if target == cg.BAKE_TARGET_BODY_SHELL:
        # The shell is copied off the body, so cards_mode does not apply. It uses the card object slot
        surface_obj = resolve_body_surface(basemesh)
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")

        # The shell has to be built in rest pose, Surface Deform will not bind otherwise
        with cg.body_held_at_rest_pose(rig):
            mesh = cg.build_body_shell_mesh(
                surface_obj, hair_obj,
                int(properties.get_value(f"{asset_name}_cards_body_face_dilation", 1, entity_reference=basemesh)),
                depsgraph=context.evaluated_depsgraph_get())
            if mesh is None:
                raise ValueError(
                    "Could not work out which body faces this asset grows from, so there is no shell to build")

            card_obj = bpy.data.objects.new(card_name, mesh)
            context.collection.objects.link(card_obj)
            # The faces were copied in the surface object local space, so the shell needs its world transform
            card_obj.parent = basemesh
            card_obj.matrix_parent_inverse = basemesh.matrix_world.inverted()
            card_obj.matrix_basis = surface_obj.matrix_world.copy()

            # Modifier order: armature, Surface Deform, then the height offset (works on deformed normals)
            if not cg.weight_body_shell_to_rig(card_obj, surface_obj, rig):
                _LOG.debug("No rig on this character, so the body shell is not weighted", card_name)
            if not cg.bind_body_shell_to_body(context, card_obj, surface_obj):
                _LOG.warn("Could not bind the body shell to the body, it will not follow later "
                          "reshaping", card_name)

            modifier = card_obj.modifiers.new(name=CARDS_MODIFIER_NAME, type='NODES')
            modifier.node_group = cg.build_body_shell_node_group(f"{card_name}_{CARDS_MODIFIER_NAME}")
        return card_obj, True

    mode = get_cards_mode(properties, basemesh, asset_name)

    # Cards are always generated, the hand modelled ones in the asset pack (<asset>_cards) are no longer loaded
    # User can now create own card mesh using Custom Mesh target

    if mode in cg.CLUSTER_MODES:
        cluster_settings = (
            int(properties.get_value(f"{asset_name}_cards_cluster_count", 40, entity_reference=basemesh)),
            int(properties.get_value(f"{asset_name}_cards_cluster_min_strands", 3, entity_reference=basemesh)),
            int(properties.get_value(f"{asset_name}_cards_cluster_seed", 0, entity_reference=basemesh)),
            )
        depsgraph = context.evaluated_depsgraph_get()

        if mode == cg.CARDS_MODE_CLUSTER_BOX:
            data = cg.build_cluster_box_mesh(hair_obj, *cluster_settings, depsgraph=depsgraph)
        else:
            samples = int(properties.get_value(
                f"{asset_name}_cards_cluster_samples", 24, entity_reference=basemesh))
            data = cg.build_cluster_ribbon_mesh(hair_obj, *cluster_settings, samples, depsgraph=depsgraph)

        if data is None:
            raise ValueError("Not enough strands to form any cluster card with the current settings")

        card_obj = bpy.data.objects.new(card_name, data)
        context.collection.objects.link(card_obj)
        card_obj.parent = basemesh
        # The geometry is in the hair object local space, so the card object needs its transform too
        card_obj.matrix_parent_inverse = hair_obj.matrix_parent_inverse.copy()
        card_obj.matrix_basis = hair_obj.matrix_basis.copy()

        # Cluster boxes are a finished mesh, ribbons are shaped by a node group
        if mode == cg.CARDS_MODE_CLUSTER_BOX:
            return card_obj, False

        modifier = card_obj.modifiers.new(name=CARDS_MODIFIER_NAME, type='NODES')
        modifier.node_group = cg.build_cluster_ribbon_node_group(
            f"{card_name}_{CARDS_MODIFIER_NAME}", basemesh)
        return card_obj, True

    selection_method = get_cards_selection_method(properties, basemesh, asset_name)
    group_name = f"{card_name}_{CARDS_MODIFIER_NAME}"

    if mode == cg.CARDS_MODE_RIBBON:
        node_group = cg.build_ribbon_node_group(group_name, selection_method, basemesh)
    elif mode == cg.CARDS_MODE_SHELL:
        node_group = cg.build_shell_node_group(group_name, basemesh)
    else:
        node_group = cg.build_tiles_node_group(group_name, selection_method, basemesh)

    card_obj = hair_obj.copy()
    card_obj.data = hair_obj.data.copy()
    card_obj.name = card_name
    context.collection.objects.link(card_obj)

    modifier = card_obj.modifiers.new(name=CARDS_MODIFIER_NAME, type='NODES')
    modifier.node_group = node_group

    # Copy of the hair object, so it takes the hair parent inverse to stay on the hair
    card_obj.parent = basemesh
    card_obj.matrix_parent_inverse = hair_obj.matrix_parent_inverse.copy()

    return card_obj, True


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_GenerateHairCards_Operator(MpfbOperator):
    """Converts curve based hair to card object"""
    bl_idname = "mpfb.generate_hair_cards_operator"
    bl_label = "Generate hair cards"
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

        hair_obj = None
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == self.hair_asset:
                hair_obj = child
                break
        if hair_obj is None:
            self.report({'ERROR'}, f"Hair object '{self.hair_asset}' not found amongst the children of the basemesh")
            return {'CANCELLED'}

        card_name = f"{self.hair_asset}{CARDS_OBJECT_SUFFIX}"
        if card_name in bpy.data.objects:
            self.report({'ERROR'}, f"An object named '{card_name}' already exists")
            return {'CANCELLED'}

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"

        create_cards_config_properties(properties, basemesh, self.hair_asset)

        try:
            card_obj, used_generator = build_cards_for_asset(
                context, basemesh, hair_obj, card_name, self.is_fur, properties, self.hair_asset)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        if used_generator:
            # Pick up settings remembered from previous cards of this asset
            create_cards_properties(properties, basemesh, self.hair_asset,
                                    values=read_cards_settings(basemesh, self.hair_asset),
                                    mode=get_cards_mode(properties, basemesh, self.hair_asset))
        else:
            self.report({'INFO'}, f"Imported cards for '{self.hair_asset}'. You might need to manually align them to fit correctly.")

        create_cards_bake_properties(properties, basemesh, self.hair_asset)
        set_cards_flag(properties, basemesh, self.hair_asset, kind, "generated", True)

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Created hair cards: {card_obj.name}")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_GenerateHairCards_Operator)
