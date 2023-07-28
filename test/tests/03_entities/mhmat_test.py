import bpy, os
from pytest import approx

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