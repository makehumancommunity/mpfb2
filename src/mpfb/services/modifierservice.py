"""This module contains utility functions for working with modifiers."""

import bpy
from typing import Any
from .logservice import LogService

_LOG = LogService.get_logger("services.modifierservice")


class ModifierService:
    """ModifierService contains various functions for working with modifiers, such as creating a new modifier,
    finding a modifier, and moving a modifier to the top of the stack and so forth."""

    def __init__(self):
        raise RuntimeError("You should not instance ModifierService. Use its static methods instead.")

    @staticmethod
    def move_modifier_to_top(blender_object: bpy.types.Object, modifier_name: str) -> None:
        """Move a modifier to the top of the stack"""
        if not modifier_name or modifier_name not in blender_object.modifiers:
            return
        with bpy.context.temp_override(object=blender_object):
            while blender_object.modifiers.find(modifier_name) != 0:
                bpy.ops.object.modifier_move_up(modifier=modifier_name)

    @staticmethod
    def create_modifier(blender_object: bpy.types.Object, modifier_name: str, modifier_type: str, move_to_top: bool = False) -> Any:
        """Create a new modifier for blender_object, of the given type. Optionally place it in the top of the stack."""
        if not blender_object:
            raise ValueError('Tried to call create_modifier for None object')
        if not modifier_type:
            raise ValueError('Tried to call create_modifier with an empty modifier type')
        if not modifier_name:
            raise ValueError('Tried to call create_modifier with an empty modifier name')
        modifier = blender_object.modifiers.new(modifier_name, modifier_type)  # type: ignore[arg-type]
        if move_to_top:
            ModifierService.move_modifier_to_top(blender_object, modifier_name)
        return modifier

    @staticmethod
    def create_armature_modifier(blender_object: bpy.types.Object, armature_object: bpy.types.Object, modifier_name: str, show_in_editmode: bool = True, show_on_cage: bool = True, move_to_top: bool = True) -> Any:
        """Create an armature modifier for an object. Optionally place it in the top of the stack."""
        modifier = ModifierService.create_modifier(blender_object, modifier_name, 'ARMATURE', move_to_top=move_to_top)
        modifier.object = armature_object
        modifier.show_in_editmode = show_in_editmode
        modifier.show_on_cage = show_on_cage
        return modifier

    @staticmethod
    def create_mask_modifier(blender_object: bpy.types.Object, modifier_name: str, vertex_group: str, show_in_editmode: bool = True, show_on_cage: bool = True, move_to_top: bool = False) -> Any:
        """Create a mask modifier for blender_object, for the given vertex group. Optionally place it in the top of the stack."""
        modifier = ModifierService.create_modifier(blender_object, modifier_name, 'MASK', move_to_top=move_to_top)
        modifier.vertex_group = vertex_group
        modifier.show_in_editmode = show_in_editmode
        modifier.show_on_cage = show_on_cage
        return modifier

    @staticmethod
    def create_subsurf_modifier(blender_object: bpy.types.Object, modifier_name: str, levels: int = 0, render_levels: int = 1, show_in_editmode: bool = True, move_to_top: bool = False) -> Any:
        """Create a subdiv modifier for blender_object. Optionally place it in the top of the stack."""
        modifier = ModifierService.create_modifier(blender_object, modifier_name, 'SUBSURF', move_to_top=move_to_top)
        modifier.levels = levels
        modifier.render_levels = render_levels
        modifier.show_in_editmode = show_in_editmode
        return modifier

    @staticmethod
    def find_modifiers_of_type(blender_object: bpy.types.Object, modifier_type: str) -> list[bpy.types.Modifier]:
        """Return a list with all modifiers with a given type for the given object."""
        modifiers = []
        if not blender_object or not modifier_type:
            return modifiers
        for modifier in blender_object.modifiers:
            if modifier.type == modifier_type:
                modifiers.append(modifier)
        return modifiers

    @staticmethod
    def find_modifier(blender_object: bpy.types.Object, modifier_type: str, modifier_name: str | None = None) -> bpy.types.Modifier | None:
        """Return a modifier of the given type, optionally also limited by name"""
        if not blender_object:
            return None
        modifiers = ModifierService.find_modifiers_of_type(blender_object, modifier_type)
        if not modifiers or len(modifiers) < 1:
            return None
        for modifier in modifiers:
            if modifier_name:
                if modifier.name == modifier_name:
                    return modifier
            else:
                return modifier
        return None
