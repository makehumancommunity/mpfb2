import bpy, os
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import MaterialService
from .. import LocationService


def test_humanservice_exists():
    """HumanService"""
    assert HumanService is not None, "HumanService can be imported"


def test_create_human_defaults():
    """HumanService.create_human() -- defaults"""
    obj = HumanService.create_human()
    assert obj is not None
    assert getattr(obj, 'MPFB_GEN_object_type') == "Basemesh"
    assert getattr(obj, 'MPFB_GEN_scale_factor') == approx(0.1)
    ObjectService.delete_object(obj)


def test_add_mhclo_asset_without_rig():
    """HumanService.add_mhclo_asset() -- without rig"""
    testdata = LocationService.get_mpfb_test("testdata")
    mhclo_file = os.path.join(testdata, "better_socks_low.mhclo")
    assert os.path.exists(mhclo_file)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    clothes = HumanService.add_mhclo_asset(mhclo_file, basemesh, set_up_rigging=False, interpolate_weights=False, import_subrig=False, import_weights=False)
    assert clothes is not None
    assert clothes.parent == basemesh
    ObjectService.delete_object(clothes)
    ObjectService.delete_object(basemesh)


def test_add_mhclo_asset_with_rig():
    """HumanService.add_mhclo_asset() -- with rig"""
    testdata = LocationService.get_mpfb_test("testdata")
    mhclo_file = os.path.join(testdata, "better_socks_low.mhclo")
    assert os.path.exists(mhclo_file)
    basemesh = HumanService.create_human()
    assert basemesh is not None
    rig = HumanService.add_builtin_rig(basemesh, "default")
    assert rig is not None
    clothes = HumanService.add_mhclo_asset(mhclo_file, basemesh, set_up_rigging=True, interpolate_weights=False, import_subrig=False, import_weights=True)
    assert clothes is not None
    assert clothes.parent == rig
    ObjectService.delete_object(clothes)
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_add_builtin_rig_standard():
    """HumanService.add_builtin_rig() -- standard rig"""
    basemesh = HumanService.create_human()
    assert basemesh is not None
    rig = HumanService.add_builtin_rig(basemesh, "default")
    assert rig is not None
    assert basemesh.parent == rig
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_serialize_v2_skin():
    """HumanService.serialize_to_json_string() -- v2 skin"""
    basemesh = HumanService.create_human()
    assert basemesh is not None
    human_info = HumanService._create_default_human_info_dict()
    assert human_info
    assert human_info["skin_material_type"] == "NONE"
    assert len(human_info["skin_material_settings"].keys()) == 0

    name = ObjectService.random_name()
    MaterialService.create_v2_skin_material(name, basemesh)

    HumanService._populate_human_info_with_skin_info(human_info, basemesh)

    assert human_info["skin_material_type"] == "LAYERED"
    assert len(human_info["skin_material_settings"].keys()) > 0
    assert "color" in human_info["skin_material_settings"]
    assert "DiffuseTextureStrength" in human_info["skin_material_settings"]["color"]

    ObjectService.delete_object(basemesh)


def test_deserialize_from_dict():
    """HumanService.deserialize_from_dict()"""
    name = ObjectService.random_name()

    human_info = HumanService._create_default_human_info_dict()
    human_info["name"] = name

    deser = HumanService.get_default_deserialization_settings()

    basemesh = HumanService.deserialize_from_dict(human_info, deser)
    assert basemesh
    assert basemesh.name == name + ".body"

    ObjectService.delete_object(basemesh)


def test_deserialize_from_mhm():
    """HumanService.deserialize_from_mhm()"""
    deser = HumanService.get_default_deserialization_settings()
    deser["clothes_deep_search"] = False
    deser["bodypart_deep_search"] = False

    testdata = LocationService.get_mpfb_test("testdata")
    mhm_file = os.path.join(testdata, "testchar.mhm")

    assert os.path.exists(mhm_file)

    basemesh = HumanService.deserialize_from_mhm(mhm_file, deser)
    assert basemesh
    assert basemesh.name == "testchar.body"

    ObjectService.delete_object(basemesh)


def test_serialize_to_json_string():
    """HumanService.serialize_to_json_string()"""
    obj = HumanService.create_human()
    assert obj is not None

    name = ObjectService.random_name()
    obj.name = name + ".body"

    jstr = HumanService.serialize_to_json_string(obj)
    assert jstr
    assert "eyebrows" in jstr

    ObjectService.delete_object(obj)

