import bpy, os
from pytest import approx
from mpfb.services.locationservice import LocationService

def test_mhmat_texture_keys():
    """MHMAT texture keys"""
    from mpfb.entities.material.mhmatkeys import MHMAT_KEYS, MHMAT_NAME_TO_KEY
    assert MHMAT_KEYS
    
    texture_keys = [
        "diffuseTexture",
        "bumpmapTexture",
        "normalmapTexture",
        "displacementmapTexture",
        "specularmapTexture",
        "transmissionmapTexture",
        "transparencymapTexture",
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
        
def test_mhmat_alias_keys():
    """MHMAT alias keys"""
    from mpfb.entities.material.mhmatkeys import MHMAT_KEYS, MHMAT_NAME_TO_KEY
    assert MHMAT_KEYS
    
    alias_keys = [
        "diffusemapTexture",
        "albedoTexture",
        "albedoMapTexture",
        "basecolorTexture",
        "basecolorMapTexture",
        "opacityTexture",
        "opacityMapTexture",
        "emissiveTexture",
        "emissionTexture",
        "sssTexture",
        "sssMapTexture"    
        ]

    known_keys = []
    
    for key in MHMAT_KEYS:
        known_keys.append(key.key_name)
        
    for key in alias_keys:
        assert key.lower() in MHMAT_NAME_TO_KEY
        
def test_load_mhmat_file():
    td = LocationService.get_mpfb_test("testdata")
    matfile = os.path.join(td, "materials", "notextures.mhmat")
    assert os.path.exists(matfile)
    from mpfb.entities.material.mhmaterial import MhMaterial
    mhmat = MhMaterial()
    assert mhmat
    mhmat.populate_from_mhmat(matfile)
    col = mhmat.get_value("diffusecolor", True)
    assert col
    assert col[0] > 0.4
    assert col[0] < 0.6

    
    