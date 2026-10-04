import bpy, os, shutil
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import LocationService
from .. import ModifierService
from .. import MaterialService
from .. import dynamic_import
from ._helpers import MockOperatorBase
MPFB_OT_Load_Clothes_Operator = dynamic_import("mpfb.ui.apply_assets.loadclothes.operators", "MPFB_OT_Load_Clothes_Operator")


def _write_broken_mhclo(dest_dir):
    """Copy the socks fixture into dest_dir, with its material line pointed at a nonexistent file."""
    testdata = LocationService.get_mpfb_test("testdata")
    shutil.copy(os.path.join(testdata, "better_socks_low.obj"), str(dest_dir))
    with open(os.path.join(testdata, "better_socks_low.mhclo"), "r", encoding="utf8") as handle:
        content = handle.read()
    assert "material better_socks_low.mhmat" in content
    content = content.replace("material better_socks_low.mhmat", "material no_such_material.mhmat")
    broken = os.path.join(str(dest_dir), "broken_material.mhclo")
    with open(broken, "w", encoding="utf8") as handle:
        handle.write(content)
    return broken


def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.load_clothes is not None
    assert MPFB_OT_Load_Clothes_Operator is not None


def test_load_clothes_without_rig():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.activate_blender_object(basemesh)
    LOAD_CLOTHES_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.loadclothes.loadclothespanel", "LOAD_CLOTHES_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("delete_group", True, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("specific_delete_group", True, entity_reference=bpy.context.scene)
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    mockself = MockOperatorBase(filepath=socks)
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    print(bpy.context.view_layer.objects.active)
    clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes")
    assert clothes is not None, "Was able to find clothes"
    assert "better_socks_low" in clothes.name, "Clothes have the correct name"
    modifier = ModifierService.find_modifier(basemesh, 'MASK')
    assert modifier is not None, "There is a delete group"
    ObjectService.delete_object(clothes)


def test_load_clothes_with_rig():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.activate_blender_object(basemesh)
    HumanService.add_builtin_rig(basemesh, "default")
    rig = basemesh.parent
    ObjectService.activate_blender_object(rig)
    LOAD_CLOTHES_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.loadclothes.loadclothespanel", "LOAD_CLOTHES_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", True, entity_reference=bpy.context.scene)
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    mockself = MockOperatorBase(filepath=socks)
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    print(bpy.context.view_layer.objects.active)
    clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes")
    assert clothes is not None, "Was able to find clothes"
    assert clothes.parent == rig
    modifier = ModifierService.find_modifier(basemesh, 'ARMATURE')
    assert modifier is not None, "There is an armature modifier"
    ObjectService.delete_object(clothes)


def test_load_clothes_warns_on_missing_material(tmp_path):
    """The operator warns, rather than crashing, when the mhclo points at a missing mhmat"""
    broken = _write_broken_mhclo(tmp_path)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    ObjectService.activate_blender_object(basemesh)
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    # fit_to_body must be pinned, since the other tests in this file leave it at whatever they found.
    # False forces the branch where the operator loads the mhclo itself.
    ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", False, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=bpy.context.scene)
    # Note: this operator reads a "material_type" scene property which does not exist, so it always
    # resolves to None. That is a separate pre-existing bug; the missing material warning is not
    # gated on the material type, so it is reported regardless.
    mockself = MockOperatorBase(filepath=broken)
    # Before issue 420 was fixed, this raised FileNotFoundError
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
    mockself.mock_report.assert_no_errors()
    mockself.mock_report.assert_reported('WARNING', "no_such_material.mhmat")
    clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes")
    assert clothes is not None, "Clothes should have been loaded despite the missing material"
    assert not MaterialService.has_materials(clothes), "A missing material should mean no material at all"
    ObjectService.delete_object(clothes)
    ObjectService.delete_object(basemesh)
