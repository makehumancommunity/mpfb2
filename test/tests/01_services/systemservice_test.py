import bpy, os
from pytest import approx
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.services.locationservice import LocationService
from mpfb.services.systemservice import SystemService

def test_systemservice_exists():
    """SystemService"""
    assert SystemService is not None, "SystemService can be imported"

def test_normalize_path_separators():
    """normalize_path_separators"""
    assert SystemService.normalize_path_separators("d:\\yada\\yada") == "d:/yada/yada"
    assert SystemService.normalize_path_separators("d:/yada/yada") == "d:/yada/yada"
    assert SystemService.normalize_path_separators(None) == ""

def test_string_contains_path_segment():
    """string_contains_path_segment"""
    assert SystemService.string_contains_path_segment("d:\\ugga\\bugga", "ugga")
    assert SystemService.string_contains_path_segment("d:\\ugga\\bugga", "bugga")
    assert not SystemService.string_contains_path_segment("d:\\ugga\\bugga", "uggabugga")
    assert not SystemService.string_contains_path_segment("", "")
    assert not SystemService.string_contains_path_segment("d:\\Ugga\\Bugga", "ugga", case_insensitive=False)
    assert SystemService.string_contains_path_segment("d:\\Ugga\\Bugga", "ugga")

def test_is_blender_version_at_least():
    """is_blender_version_at_least"""
    assert SystemService.is_blender_version_at_least([2, 80, 0])
    assert SystemService.is_blender_version_at_least([3, 0, 0])
    assert SystemService.is_blender_version_at_least(list(bpy.app.version))
    assert not SystemService.is_blender_version_at_least([300, 0, 0])

def test_check_for_obj_importer():
    """check_for_obj_importer"""
    assert SystemService.check_for_obj_importer()
