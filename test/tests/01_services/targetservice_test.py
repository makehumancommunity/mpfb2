import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService

def test_targetservice_exists():
    """TargetService"""
    assert TargetService is not None, "TargetService can be imported"

def test_shapekey_is_target_common():
    """HumanService.shapekey_is_target() -- common cases"""
    for name in ["Basis", "", False, None, "yadayada"]:
        assert not TargetService.shapekey_is_target(name)

    for name in ["hip-waist-up", "l-foot-scale-incr", "$md-yadayada"]:
        assert TargetService.shapekey_is_target(name)

def test_shapekey_is_target_human():
    """HumanService.shapekey_is_target() -- loaded targets"""
    obj = HumanService.create_human()
    assert obj is not None
    for shapekey in obj.data.shape_keys.key_blocks:
        if shapekey.name != "Basis":
            assert TargetService.shapekey_is_target(shapekey.name)
        else:
            assert not TargetService.shapekey_is_target(shapekey.name)

def test_prune_shapekeys():
    """HumanService.shapekey_is_target() -- loaded targets"""
    obj = HumanService.create_human()
    assert obj is not None

    ObjectService.activate_blender_object(obj, deselect_all=True)

    shapekey_names = []

    for shapekey in obj.data.shape_keys.key_blocks:
        shapekey_names.append(shapekey.name)

    test_shapekey_name = shapekey_names[2]
    TargetService.prune_shapekeys(obj)

    assert test_shapekey_name in obj.data.shape_keys.key_blocks
    assert "Basis" in obj.data.shape_keys.key_blocks

    obj.data.shape_keys.key_blocks[test_shapekey_name].value = 0.0000
    TargetService.prune_shapekeys(obj)

    assert not test_shapekey_name in obj.data.shape_keys.key_blocks
    assert "Basis" in obj.data.shape_keys.key_blocks

    TargetService.create_shape_key(obj, "yadayada")
    obj.data.shape_keys.key_blocks["yadayada"].value = 0.0000

    TargetService.prune_shapekeys(obj)

    assert "yadayada" in obj.data.shape_keys.key_blocks
