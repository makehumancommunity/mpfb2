import bpy, os, shutil
import pytest
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import LocationService
from .. import RigService
from .. import SystemService
from .. import UiService
from .. import dynamic_import
from ._helpers import MockOperatorBase

MPFB_OT_CreateHumanOperator = dynamic_import("mpfb.ui.new_human.newhuman.operators.createhuman", "MPFB_OT_CreateHumanOperator")
MPFB_OT_HumanFromMHMOperator = dynamic_import("mpfb.ui.new_human.newhuman.operators.humanfrommhm", "MPFB_OT_HumanFromMHMOperator")
MPFB_OT_HumanFromPresetsOperator = dynamic_import("mpfb.ui.new_human.newhuman.operators.humanfrompresets", "MPFB_OT_HumanFromPresetsOperator")

def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.create_human is not None
    assert bpy.ops.mpfb.human_from_mhm is not None
    assert bpy.ops.mpfb.human_from_presets is not None

def test_create_human_defaults():
    ObjectService.deselect_and_deactivate_all()
    mockself = MockOperatorBase()
    MPFB_OT_CreateHumanOperator.hardened_execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    basemesh = bpy.context.view_layer.objects.active
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.delete_object(basemesh)

def test_create_human_from_mhm():
    ObjectService.deselect_and_deactivate_all()
    assert not bpy.context.view_layer.objects.active
    testdata = LocationService.get_mpfb_test("testdata")
    mhm_file = os.path.join(testdata, "testchar.mhm")
    assert os.path.exists(mhm_file)
    mockself = MockOperatorBase(filepath=mhm_file)
    MPFB_OT_HumanFromMHMOperator.hardened_execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    active_obj = bpy.context.view_layer.objects.active
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active_obj)
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.delete_object(basemesh)

def test_create_human_from_preset():
    ObjectService.deselect_and_deactivate_all()
    assert not bpy.context.view_layer.objects.active
    testdata = LocationService.get_mpfb_test("testdata")
    src_preset_file = os.path.join(testdata, "human.unit_test_sample.json")
    assert os.path.exists(src_preset_file)

    randname = ObjectService.random_name()
    config = LocationService.get_user_config()
    name = "human." + randname + ".json"

    dst_preset_file = os.path.join(config, name)
    shutil.copyfile(src_preset_file, dst_preset_file)
    assert os.path.exists(dst_preset_file)

    UiService.rebuild_importer_presets_panel_list()
    PRESETS_HUMAN_PROPERTIES = dynamic_import("mpfb.ui.new_human.newhuman.frompresetspanel", "PRESETS_HUMAN_PROPERTIES")
    assert(PRESETS_HUMAN_PROPERTIES)

    PRESETS_HUMAN_PROPERTIES.set_value("available_presets", randname, entity_reference=bpy.context.scene)

    mockself = MockOperatorBase()
    MPFB_OT_HumanFromPresetsOperator.hardened_execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    active_obj = bpy.context.view_layer.objects.active
    basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active_obj)
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.delete_object(basemesh)

    os.remove(dst_preset_file)


def test_create_human_from_preset_with_rigify_auto_generate():
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    ObjectService.deselect_and_deactivate_all()
    assert not bpy.context.view_layer.objects.active
    testdata = LocationService.get_mpfb_test("testdata")
    src_preset_file = os.path.join(testdata, "human.unit_test_sample.json")
    assert os.path.exists(src_preset_file)

    randname = ObjectService.random_name()
    config = LocationService.get_user_config()
    name = "human." + randname + ".json"

    dst_preset_file = os.path.join(config, name)
    shutil.copyfile(src_preset_file, dst_preset_file)
    assert os.path.exists(dst_preset_file)

    UiService.rebuild_importer_presets_panel_list()
    PRESETS_HUMAN_PROPERTIES = dynamic_import("mpfb.ui.new_human.newhuman.frompresetspanel", "PRESETS_HUMAN_PROPERTIES")
    assert PRESETS_HUMAN_PROPERTIES

    PRESETS_HUMAN_PROPERTIES.set_value("available_presets", randname, entity_reference=bpy.context.scene)
    PRESETS_HUMAN_PROPERTIES.set_value("override_rig", "rigify.human_toes", entity_reference=bpy.context.scene)
    PRESETS_HUMAN_PROPERTIES.set_value("auto_generate_rigify", True, entity_reference=bpy.context.scene)
    PRESETS_HUMAN_PROPERTIES.set_value("keep_meta_rig_on_load", False, entity_reference=bpy.context.scene)

    try:
        mockself = MockOperatorBase()
        MPFB_OT_HumanFromPresetsOperator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        active_obj = bpy.context.view_layer.objects.active
        assert active_obj is not None
        assert active_obj.type == "ARMATURE"

        rig_type = RigService.identify_rig(active_obj)
        assert not rig_type.startswith("rigify."), \
            f"Active rig should be a generated rigify rig, got {rig_type}"

        leftover = [o for o in bpy.data.objects if o.name.endswith(".metarig")]
        assert not leftover, f"Meta rig should have been deleted, found: {[o.name for o in leftover]}"

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active_obj)
        if basemesh is not None:
            ObjectService.delete_object(basemesh)
    finally:
        # Reset to default to not affect other tests
        PRESETS_HUMAN_PROPERTIES.set_value("override_rig", "PRESET", entity_reference=bpy.context.scene)
        if os.path.exists(dst_preset_file):
            os.remove(dst_preset_file)
