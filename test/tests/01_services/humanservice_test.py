import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.locationservice import LocationService

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
