import bpy, os
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import ClothesService
from .. import MaterialService
from .. import LocationService


def test_clothesservice_exists():
    """ClothesService"""
    assert ClothesService is not None, "ClothesService can be imported"

# This is basically a placeholder test file. Eventually clothes creation should be tested here, but all
# clothes loading and fitting is implicitly called by the humanservice_test file.
