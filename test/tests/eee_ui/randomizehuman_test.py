import bpy
from pytest import approx
from .. import ObjectService
from .. import TargetService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_Create_Random_Human_Operator = dynamic_import("mpfb.ui.new_human.randomize.operators.createrandomhuman", "MPFB_OT_Create_Random_Human_Operator")
RANDOMIZE_PROPERTIES = dynamic_import("mpfb.ui.new_human.randomize.randomizeproperties", "RANDOMIZE_PROPERTIES")


def _flatten_macro(macro):
    """Flatten a macro info dict (including the nested race weights) to a plain name -> value dict."""
    flat = {}
    for key, value in macro.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                flat[key + "." + subkey] = subvalue
        else:
            flat[key] = value
    return flat


def _create_and_read(seed):
    RANDOMIZE_PROPERTIES.set_value("seed", seed, entity_reference=bpy.context.scene)
    ObjectService.deselect_and_deactivate_all()
    mockself = MockOperatorBase()
    MPFB_OT_Create_Random_Human_Operator.hardened_execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    basemesh = bpy.context.view_layer.objects.active
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    macro = TargetService.get_macro_info_dict_from_basemesh(basemesh)
    ObjectService.delete_object(basemesh)
    return macro


def test_operator_exists():
    assert bpy.ops.mpfb.create_random_human is not None


def test_create_random_human_defaults():
    RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)
    ObjectService.deselect_and_deactivate_all()
    mockself = MockOperatorBase()
    MPFB_OT_Create_Random_Human_Operator.hardened_execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    basemesh = bpy.context.view_layer.objects.active
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.delete_object(basemesh)


def test_same_seed_produces_identical_human():
    try:
        first = _flatten_macro(_create_and_read(4242))
        second = _flatten_macro(_create_and_read(4242))
        assert first.keys() == second.keys()
        for key in first:
            assert first[key] == approx(second[key], abs=1e-4), "Attribute " + key + " differs between identical seeds"
    finally:
        RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)


def test_default_settings_respect_bounds():
    try:
        macro = _create_and_read(777)
        # With the default spec the scalar attributes are drawn around neutral 0.5 with a
        # 0.5 deviation, so they span the full 0.0-1.0 range. A small tolerance is added for
        # shape-key read-back rounding.
        for name in ["muscle", "weight", "height", "proportions"]:
            assert macro[name] >= 0.0 - 1e-3
            assert macro[name] <= 1.0 + 1e-3
        # Gender is discrete by default, so it is either fully female or fully male.
        assert macro["gender"] == approx(0.0, abs=1e-3) or macro["gender"] == approx(1.0, abs=1e-3)
        # Race weights are normalized to sum to ~1.
        race_sum = macro["race"]["asian"] + macro["race"]["caucasian"] + macro["race"]["african"]
        assert race_sum == approx(1.0, abs=1e-3)
    finally:
        RANDOMIZE_PROPERTIES.set_value("seed", 0, entity_reference=bpy.context.scene)
