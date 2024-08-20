import bpy, os
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import LocationService
from .. import ModifierService
from .. import dynamic_import
MPFB_OT_Load_Clothes_Operator = dynamic_import("mpfb.ui.loadclothes.operators", "MPFB_OT_Load_Clothes_Operator")


class MockSelf:
    filepath = ""

    def report(self, reporttype, reportmessage):
        rep = next(iter(reporttype))
        print(str(rep) + " -- " + str(reportmessage))
        if rep == 'ERROR':
            raise ValueError(reportmessage)


def test_operators_exist():
    """Operators are not none"""
    assert bpy.ops.mpfb.load_clothes is not None
    assert MPFB_OT_Load_Clothes_Operator is not None


def test_load_clothes_without_rig():
    basemesh = HumanService.create_human()
    assert basemesh is not None
    assert ObjectService.object_is_basemesh(basemesh)
    ObjectService.activate_blender_object(basemesh)
    LOAD_CLOTHES_PROPERTIES = dynamic_import("mpfb.ui.loadclothes.loadclothespanel", "LOAD_CLOTHES_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("delete_group", True, entity_reference=bpy.context.scene)
    ASSET_SETTINGS_PROPERTIES.set_value("specific_delete_group", True, entity_reference=bpy.context.scene)
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    mockself = MockSelf()
    mockself.filepath = socks
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
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
    LOAD_CLOTHES_PROPERTIES = dynamic_import("mpfb.ui.loadclothes.loadclothespanel", "LOAD_CLOTHES_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", True, entity_reference=bpy.context.scene)
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    mockself = MockSelf()
    mockself.filepath = socks
    MPFB_OT_Load_Clothes_Operator.execute(mockself, bpy.context)
    print(bpy.context.view_layer.objects.active)
    clothes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Clothes")
    assert clothes is not None, "Was able to find clothes"
    assert clothes.parent == rig
    modifier = ModifierService.find_modifier(basemesh, 'ARMATURE')
    assert modifier is not None, "There is an armature modifier"
    ObjectService.delete_object(clothes)
