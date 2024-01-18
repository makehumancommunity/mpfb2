import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb.entities.objectproperties import HumanObjectProperties

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
    """HumanService.prune_shapekeys()"""
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

def test_target_fingerprinting():
    """TargetService.get_target_stack_fingerprint()"""
    obj = HumanService.create_human()
    assert obj is not None

    fingerprint_before = TargetService.get_target_stack_fingerprint(obj)
    assert fingerprint_before is not None

    TargetService.reapply_macro_details(obj, remove_zero_weight_targets=True)
    fingerprint_inbetween = TargetService.get_target_stack_fingerprint(obj)
    assert fingerprint_inbetween is not None
    assert fingerprint_before == fingerprint_inbetween

    HumanObjectProperties.set_value("weight", 0.75, entity_reference=obj)
    TargetService.reapply_macro_details(obj, remove_zero_weight_targets=True)

    fingerprint_after = TargetService.get_target_stack_fingerprint(obj)
    assert fingerprint_after is not None
    assert fingerprint_before != fingerprint_after

