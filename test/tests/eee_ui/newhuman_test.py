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
    PRESETS_HUMAN_PROPERTIES.set_value("meta_rig_action", "delete", entity_reference=bpy.context.scene)

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
        PRESETS_HUMAN_PROPERTIES.set_value("meta_rig_action", "hide", entity_reference=bpy.context.scene)
        if os.path.exists(dst_preset_file):
            os.remove(dst_preset_file)


def test_create_human_from_preset_with_rigify_hide_meta_rig():
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
    PRESETS_HUMAN_PROPERTIES.set_value("meta_rig_action", "hide", entity_reference=bpy.context.scene)

    try:
        mockself = MockOperatorBase()
        MPFB_OT_HumanFromPresetsOperator.hardened_execute(mockself, bpy.context)
        mockself.mock_report.assert_no_errors()

        # In the hide path, both the generated rig and the meta rig should be present.
        # The meta rig is the armature that is NOT the active object (which is the generated rig)
        # and whose `data.rigify_target_rig` points at the generated rig.
        active_obj = bpy.context.view_layer.objects.active
        assert active_obj is not None and active_obj.type == "ARMATURE"
        meta_rigs = [
            o for o in bpy.data.objects
            if o.type == "ARMATURE"
            and o is not active_obj
            and getattr(o.data, "rigify_target_rig", None) is active_obj
        ]
        assert meta_rigs, (
            "Meta rig should remain in the scene when meta_rig_action=hide; "
            f"armatures in scene: {[o.name for o in bpy.data.objects if o.type == 'ARMATURE']}"
        )
        for mr in meta_rigs:
            assert mr.hide_viewport, f"Meta rig {mr.name} should have hide_viewport=True"
            assert mr.hide_render, f"Meta rig {mr.name} should have hide_render=True"

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(active_obj)
        if basemesh is not None:
            ObjectService.delete_object(basemesh)
    finally:
        PRESETS_HUMAN_PROPERTIES.set_value("override_rig", "PRESET", entity_reference=bpy.context.scene)
        PRESETS_HUMAN_PROPERTIES.set_value("meta_rig_action", "hide", entity_reference=bpy.context.scene)
        if os.path.exists(dst_preset_file):
            os.remove(dst_preset_file)
