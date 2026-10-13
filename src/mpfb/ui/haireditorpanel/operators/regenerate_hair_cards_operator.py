# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         1.9.2026
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  operator for rebuilding a hair cards after changing mode/placement settings
# ------------------------------------------------------------------------------
from ....services.logservice import LogService
from ....services.objectservice import ObjectService
from .... import ClassManager
from ...mpfboperator import MpfbOperator
from ...pollstrategy import pollstrategy, PollStrategy
from ..hairproperties import HAIR_PROPERTIES, FUR_PROPERTIES, CARDS_MODIFIER_NAME, CARDS_OBJECT_SUFFIX, \
    create_cards_properties, snapshot_cards_properties, remember_cards_settings, get_cards_flag, \
    get_cards_mode
from .generate_hair_cards_operator import build_cards_for_asset

import bpy

_LOG = LogService.get_logger("haireditorpanel.regenerate_hair_cards_operator")


@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_RegenerateHairCards_Operator(MpfbOperator):
    """Rebuilds the cards of an asset, picking up mode/placement changes which need a full rebuild"""
    bl_idname = "mpfb.regenerate_hair_cards_operator"
    bl_label = "Regenerate cards"
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

        properties = FUR_PROPERTIES if self.is_fur else HAIR_PROPERTIES
        kind = "fur" if self.is_fur else "hair"

        if not get_cards_flag(properties, basemesh, self.hair_asset, kind, "generated"):
            self.report({'ERROR'}, "Cards have not been generated yet for this asset")
            return {'CANCELLED'}
        if get_cards_flag(properties, basemesh, self.hair_asset, kind, "baked"):
            self.report({'ERROR'}, "Cards have already been baked; unbake first")
            return {'CANCELLED'}

        hair_obj = None
        old_card_obj = None
        card_name = f"{self.hair_asset}{CARDS_OBJECT_SUFFIX}"
        for child in ObjectService.get_list_of_children(basemesh):
            if child.name == self.hair_asset:
                hair_obj = child
            if child.name == card_name:
                old_card_obj = child

        if hair_obj is None:
            self.report({'ERROR'}, f"Hair object '{self.hair_asset}' not found amongst the children of the basemesh")
            return {'CANCELLED'}

        # Placement/shape values live in the node group which is about to be removed, so they are saved here and restored after.
        # They are merged into the remembered settings, because a snapshot only has the sockets of the current mode.
        preserved_values = remember_cards_settings(
            basemesh, self.hair_asset,
            snapshot_cards_properties(properties, basemesh, self.hair_asset))

        # Build the replacement first, so a failed rebuild does not leave the asset without cards (and without undo)
        temporary_name = f"{card_name}_rebuilding"
        try:
            card_obj, used_generator = build_cards_for_asset(
                context, basemesh, hair_obj, temporary_name, self.is_fur, properties, self.hair_asset)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            _LOG.error("Could not rebuild the cards", e)
            self.report({'ERROR'}, f"Could not rebuild the cards: {e}; the previous cards were kept")
            return {'CANCELLED'}

        if old_card_obj is not None:
            old_node_group = None
            modifier = old_card_obj.modifiers.get(CARDS_MODIFIER_NAME)
            if modifier is not None:
                old_node_group = modifier.node_group
            old_data = old_card_obj.data
            bpy.data.objects.remove(old_card_obj, do_unlink=True)

            if old_node_group is not None and old_node_group.users == 0:
                bpy.data.node_groups.remove(old_node_group)
            if old_data is not None and old_data.users == 0:
                if isinstance(old_data, bpy.types.Mesh):
                    bpy.data.meshes.remove(old_data)
                elif isinstance(old_data, bpy.types.Curves):
                    bpy.data.hair_curves.remove(old_data)

        card_obj.name = card_name
        new_modifier = card_obj.modifiers.get(CARDS_MODIFIER_NAME)
        if new_modifier is not None and new_modifier.node_group is not None:
            # Built under the temporary name, delete_hair_operator expects this one
            new_modifier.node_group.name = f"{card_name}_{CARDS_MODIFIER_NAME}"

        if used_generator:
            create_cards_properties(properties, basemesh, self.hair_asset,
                                    values=preserved_values,
                                    mode=get_cards_mode(properties, basemesh, self.hair_asset))

        ObjectService.deselect_and_deactivate_all()
        ObjectService.activate_blender_object(basemesh)

        self.report({'INFO'}, f"Regenerated hair cards: {card_obj.name}")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_RegenerateHairCards_Operator)
