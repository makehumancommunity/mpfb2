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