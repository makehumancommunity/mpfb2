import bpy, os, pytest

from .. import ObjectService
from .. import ModifierService


def test_modifierservice_exists():
    """ModifierService"""
    assert ModifierService is not None, "ModifierService can be imported"


def test_create_modifier():
    """ModifierService.create_modifier()"""
    obj = ObjectService.create_blender_object_with_mesh()
    with pytest.raises(ValueError):
        modifier = ModifierService.create_modifier(None, "a", "SUBSURF")
    with pytest.raises(ValueError):
        modifier = ModifierService.create_modifier(obj, "", "SUBSURF")
    with pytest.raises(ValueError):
        modifier = ModifierService.create_modifier(obj, "a", "")
    modifier1 = ModifierService.create_modifier(obj, 'modifier1', 'SUBSURF')
    assert modifier1.name == "modifier1"
    assert obj.modifiers.find(modifier1.name) == 0
    modifier2 = ModifierService.create_modifier(obj, 'modifier2', 'SUBSURF')
    assert modifier2.name == "modifier2"
    assert obj.modifiers.find(modifier2.name) > 0
    modifier3 = ModifierService.create_modifier(obj, 'modifier3', 'SUBSURF', move_to_top=True)
    assert modifier3.name == "modifier3"
    assert obj.modifiers.find(modifier3.name) == 0

# TODO: Test create mask modifier


def test_create_subsurf_modifier():
    """ModifierService.create_subsurf_modifier()"""
    obj = ObjectService.create_blender_object_with_mesh()
    with pytest.raises(ValueError):
        modifier = ModifierService.create_subsurf_modifier(None, "a")
    with pytest.raises(ValueError):
        modifier = ModifierService.create_subsurf_modifier(obj, "")
    modifier = ModifierService.create_subsurf_modifier(obj, 'modifier1', levels=2, render_levels=2, show_in_editmode=False)
    assert modifier.name == "modifier1"
    assert obj.modifiers.find(modifier.name) == 0
    assert modifier.levels == 2
    assert modifier.render_levels == 2
    assert not modifier.show_in_editmode


def test_find_modifiers_of_type():
    """ModifierService.find_modifiers_of_type()"""
    obj = ObjectService.create_blender_object_with_mesh()
    modifier1 = ModifierService.create_modifier(obj, 'modifier1', 'SUBSURF')
    modifier2 = ModifierService.create_modifier(obj, 'modifier2', 'SUBSURF')
    modifier3 = ModifierService.create_modifier(obj, 'modifier3', 'MASK')
    modifiers = ModifierService.find_modifiers_of_type(obj, 'SUBSURF')
    assert modifiers is not None
    assert len(modifiers) == 2
    assert modifier1 in modifiers
    modifiers = ModifierService.find_modifiers_of_type(None, None)
    assert modifiers is not None
    assert len(modifiers) == 0


def test_find_modifier():
    """ModifierService.find_modifiers_of_type()"""
    obj = ObjectService.create_blender_object_with_mesh()
    modifier = ModifierService.find_modifier(obj, 'SUBSURF')
    assert modifier is None

    modifier1 = ModifierService.create_modifier(obj, 'modifier1', 'SUBSURF')
    modifier2 = ModifierService.create_modifier(obj, 'modifier2', 'SUBSURF')
    modifier3 = ModifierService.create_modifier(obj, 'modifier3', 'MASK')

    modifier = ModifierService.find_modifier(obj, 'SUBSURF')
    assert modifier is not None
    assert modifier.name == "modifier1"

    modifier = ModifierService.find_modifier(obj, 'SUBSURF', "modifier2")
    assert modifier is not None
    assert modifier.name == "modifier2"

    modifier = ModifierService.find_modifier(None, 'SUBSURF', "modifier2")
    assert modifier is None

    modifier = ModifierService.find_modifier(obj, 'SUBSURF', "yadayada")
    assert modifier is None
