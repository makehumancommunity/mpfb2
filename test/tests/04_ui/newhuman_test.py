import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.locationservice import LocationService

def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.create_human is not None
    assert bpy.ops.mpfb.human_from_mhm is not None
    assert bpy.ops.mpfb.human_from_presets is not None

def test_create_human_defaults():
    bpy.ops.mpfb.create_human()
    basemesh = bpy.context.view_layer.objects.active
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.delete_object(basemesh)