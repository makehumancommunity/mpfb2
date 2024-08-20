import bpy, os
from pytest import approx
from .. import dynamic_import
from .. import LocationService


def test_mhmat_texture_keys():
    """MHMAT texture keys"""
    MHMAT_KEYS = dynamic_import("mpfb.entities.material.mhmatkeys", "MHMAT_KEYS")
    MHMAT_NAME_TO_KEY = dynamic_import("mpfb.entities.material.mhmatkeys", "MHMAT_NAME_TO_KEY")
    assert MHMAT_KEYS

    texture_keys = [
        "diffuseTexture",
        "bumpmapTexture",
        "normalmapTexture",
        "displacementmapTexture",
        "specularmapTexture",
        "transmissionmapTexture",
        "opacitymapTexture",
        "roughnessmapTexture",
        "metallicmapTexture",
        "aomapTexture",
        "emissionColorMapTexture",
        "emissionStrengthMapTexture",
        "subsurfaceColorMapTexture",
        "subsurfaceStrengthMapTexture"
        ]

    known_keys = []

    for key in MHMAT_KEYS:
        known_keys.append(key.key_name)

    for key in texture_keys:
        assert key in known_keys
        assert key.lower() in MHMAT_NAME_TO_KEY


def test_load_mhmat_file():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "notextures.mhmat")
    assert os.path.exists(matfile)
    MhMaterial = dynamic_import("mpfb.entities.material.mhmaterial", "MhMaterial")
    mhmat = MhMaterial()
    assert mhmat
    mhmat.populate_from_mhmat(matfile)
    col = mhmat.get_value("diffusecolor", True)
    assert col
    assert col[0] > 0.4
    assert col[0] < 0.6

