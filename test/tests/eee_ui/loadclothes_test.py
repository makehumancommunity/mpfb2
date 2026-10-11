import bpy, os, shutil
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import LocationService
from .. import ModifierService
from .. import MaterialService
from .. import dynamic_import
from ._helpers import MockOperatorBase, HumanFixture
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

# --- Helpers for the tests below -------------------------------------------------------------

_ASSET_SETTINGS_KEYS = [
    "fit_to_body", "delete_group", "specific_delete_group", "set_up_rigging",
    "interpolate_weights", "makeclothes_metadata", "clothes_type", "eyes_type",
    ]


class _ScenePropertyGuard:
    """Restores the scene properties that these tests change, so they do not leak into other tests."""

    def __init__(self):
        self.asset_settings = dynamic_import("mpfb.ui.apply_assets.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
        self.load_clothes = dynamic_import("mpfb.ui.apply_assets.loadclothes.loadclothespanel", "LOAD_CLOTHES_PROPERTIES")
        self._saved = {}

    def __enter__(self):
        scene = bpy.context.scene
        for key in _ASSET_SETTINGS_KEYS:
            self._saved[key] = self.asset_settings.get_value(key, entity_reference=scene)
        self._saved["object_type"] = self.load_clothes.get_value("object_type", entity_reference=scene)
        return self

    def __exit__(self, *args):
        scene = bpy.context.scene
        for key in _ASSET_SETTINGS_KEYS:
            self.asset_settings.set_value(key, self._saved[key], entity_reference=scene)
        self.load_clothes.set_value("object_type", self._saved["object_type"], entity_reference=scene)

    def set_asset_settings(self, **kwargs):
        scene = bpy.context.scene
        for key, value in kwargs.items():
            self.asset_settings.set_value(key, value, entity_reference=scene)

    def set_object_type(self, value):
        self.load_clothes.set_value("object_type", value, entity_reference=bpy.context.scene)


def _load_socks():
    """Drives MPFB_OT_Load_Clothes_Operator on the test mhclo, returning (mockself, clothes_object)."""
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    mockself = MockOperatorBase(filepath=socks)
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
    clothes = None
    for obj in bpy.data.objects:
        if "better_socks_low" in obj.name:
            clothes = obj
    return mockself, clothes


def _material_names(blender_object):
    return [slot.material.name for slot in blender_object.material_slots if slot.material]


# --- Bug: material_type was read from a non-existing scene key, so it was always None ---------

def test_material_type_is_read_from_an_existing_property():
    """The material setting the operator reads must actually exist, otherwise it silently reads None"""
    scene = bpy.context.scene
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.apply_assets.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    assert ASSET_SETTINGS_PROPERTIES.get_value("clothes_type", entity_reference=scene) is not None, \
        "clothes_type is the source of truth for clothes materials and must resolve"
    assert ASSET_SETTINGS_PROPERTIES.get_value("eyes_type", entity_reference=scene) is not None, \
        "eyes_type is the source of truth for eyes materials and must resolve"
    assert ASSET_SETTINGS_PROPERTIES.get_value("material_type", entity_reference=scene) is None, \
        "there is deliberately no material_type property; the operator must not read one"


def test_makeskin_material_is_applied_when_not_fitting_to_body():
    """With fit_to_body off, the MakeSkin material from the mhclo still has to be applied"""
    with HumanFixture(), _ScenePropertyGuard() as guard:
        guard.set_object_type("Clothes")
        guard.set_asset_settings(
            fit_to_body=False, delete_group=False, specific_delete_group=False,
            set_up_rigging=False, interpolate_weights=False, makeclothes_metadata=False,
            clothes_type="MAKESKIN", eyes_type="GAMEENGINE")
        mockself, clothes = _load_socks()
        mockself.mock_report.assert_no_errors()
        assert clothes is not None, "Was able to find clothes"
        materials = _material_names(clothes)
        assert materials, "A material was applied to the clothes"
        assert any("better_socks_low" in name for name in materials), \
            f"The mhclo's own material was applied, got {materials}"


def test_eyes_material_setting_is_used_for_eyes_sub_type():
    """When the sub type is Eyes, the eyes_type setting decides the material, not clothes_type"""
    with HumanFixture(), _ScenePropertyGuard() as guard:
        guard.set_object_type("Eyes")
        guard.set_asset_settings(
            fit_to_body=False, delete_group=False, specific_delete_group=False,
            set_up_rigging=False, interpolate_weights=False, makeclothes_metadata=False,
            clothes_type="GAMEENGINE", eyes_type="MAKESKIN")
        mockself, clothes = _load_socks()
        mockself.mock_report.assert_no_errors()
        assert clothes is not None, "Was able to find the loaded mesh"
        materials = _material_names(clothes)
        assert materials, "eyes_type was honored, so a MakeSkin material was applied"
        assert any("better_socks_low" in name for name in materials), \
            f"The mhclo's own material was applied, got {materials}"


# --- Bug: NameError when makeclothes_metadata was enabled together with fit_to_body -----------

def test_makeclothes_metadata_with_fit_to_body():
    """Enabling MakeClothes metadata together with fit to body must not raise NameError"""
    with HumanFixture(), _ScenePropertyGuard() as guard:
        guard.set_object_type("Clothes")
        guard.set_asset_settings(
            fit_to_body=True, delete_group=False, specific_delete_group=False,
            set_up_rigging=False, interpolate_weights=False, makeclothes_metadata=True,
            clothes_type="MAKESKIN", eyes_type="MAKESKIN")
        mockself, clothes = _load_socks()
        mockself.mock_report.assert_no_errors()
        assert clothes is not None, "Was able to find clothes"
        MakeClothesObjectProperties = dynamic_import("mpfb.ui.create_assets.makeclothes", "MakeClothesObjectProperties")
        assert MakeClothesObjectProperties.get_value("name", entity_reference=clothes) == "better_socks_low", \
            "The MakeClothes metadata was taken from the mhclo"
        assert MakeClothesObjectProperties.get_value("delete_group", entity_reference=clothes) == "Delete.better_socks_low", \
            "The delete group name was recorded in the metadata"


def test_makeclothes_metadata_without_fit_to_body():
    """MakeClothes metadata is also set when the mesh is loaded without being fitted"""
    with HumanFixture(), _ScenePropertyGuard() as guard:
        guard.set_object_type("Clothes")
        guard.set_asset_settings(
            fit_to_body=False, delete_group=False, specific_delete_group=False,
            set_up_rigging=False, interpolate_weights=False, makeclothes_metadata=True,
            clothes_type="MAKESKIN", eyes_type="MAKESKIN")
        mockself, clothes = _load_socks()
        mockself.mock_report.assert_no_errors()
        assert clothes is not None, "Was able to find clothes"
        MakeClothesObjectProperties = dynamic_import("mpfb.ui.create_assets.makeclothes", "MakeClothesObjectProperties")
        assert MakeClothesObjectProperties.get_value("name", entity_reference=clothes) == "better_socks_low", \
            "The MakeClothes metadata was taken from the mhclo"
        assert MakeClothesObjectProperties.get_value("delete_group", entity_reference=clothes) == "Delete", \
            "The default delete group name was recorded in the metadata"
