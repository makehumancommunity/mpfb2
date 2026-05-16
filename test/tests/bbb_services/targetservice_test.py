import bpy, os
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import LocationService
from .. import TargetService


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


def test_expression_name_to_shapekey_name():
    """TargetService.expression_name_to_shapekey_name() prepends the !ex- prefix."""
    assert TargetService.expression_name_to_shapekey_name("browDownLeft") == "!ex-browDownLeft"
    assert TargetService.expression_name_to_shapekey_name("jawOpen") == "!ex-jawOpen"


def test_shapekey_name_to_expression_name_strips_prefix():
    """TargetService.shapekey_name_to_expression_name() strips !ex- and returns the bare name."""
    assert TargetService.shapekey_name_to_expression_name("!ex-jawOpen") == "jawOpen"
    assert TargetService.shapekey_name_to_expression_name("!ex-mouthSmileLeft") == "mouthSmileLeft"


def test_shapekey_name_to_expression_name_returns_none_for_non_expression():
    """TargetService.shapekey_name_to_expression_name() returns None for non-expression names."""
    assert TargetService.shapekey_name_to_expression_name("Basis") is None
    assert TargetService.shapekey_name_to_expression_name("$md-foo") is None
    assert TargetService.shapekey_name_to_expression_name("hip-waist-up") is None
    assert TargetService.shapekey_name_to_expression_name("") is None
    assert TargetService.shapekey_name_to_expression_name(None) is None


def test_expression_naming_helpers_round_trip():
    """expression_name_to_shapekey_name/shapekey_name_to_expression_name are inverses."""
    for name in ["browInnerUp", "cheekPuff", "tongueOut", "eyeWideRight"]:
        sk = TargetService.expression_name_to_shapekey_name(name)
        assert TargetService.shapekey_name_to_expression_name(sk) == name
