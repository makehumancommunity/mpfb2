import bpy, os
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import RigService
from .. import MaterialService
from .. import LocationService

HUMAN_PRESET_DICT = {
        "clothes": [
            "female_casualsuit01/female_casualsuit01.mhclo"
        ],
        "color_adjustments": {},
        "eyebrows": "eyebrow001/eyebrow001.mhclo",
        "eyelashes": "eyelashes01/eyelashes01.mhclo",
        "eyes": "high-poly/high-poly.mhclo",
        "eyes_material_settings": {},
        "eyes_material_type": "PROCEDURAL_EYES",
        "hair": "long01/long01.mhclo",
        "phenotype": {
            "age": 0.5,
            "cupsize": 0.550000011920929,
            "firmness": 0.550000011920929,
            "gender": 0.0,
            "height": 0.5,
            "muscle": 0.5,
            "proportions": 0.5,
            "race": {
                "african": 0.0,
                "asian": 0.0,
                "caucasian": 1.0
            },
            "weight": 0.5
        },
        "proxy": "",
        "rig": "default",
        "skin_material_settings": {},
        "skin_material_type": "ENHANCED_SSS",
        "skin_mhmat": "middleage_caucasian_female/middleage_caucasian_female.mhmat",
        "targets": [
            {
                "target": "head-age-decr",
                "value": 1.0
            }
        ],
        "teeth": "",
        "tongue": ""
    }


def _create_human_with_rig():
    deserialization_settings = HumanService.get_default_deserialization_settings()
    basemesh = HumanService.deserialize_from_dict(HUMAN_PRESET_DICT, deserialization_settings)
    assert basemesh
    rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
    assert rig
    return (basemesh, rig)


def test_rigservice_exists():
    """RigService"""
    assert RigService is not None, "RigService can be imported"


def test_identify_rig():
    """RigService.identify_rig()"""
    (basemesh, rig) = _create_human_with_rig()
    assert RigService.identify_rig(rig) == "default", "Expected 'default' rig type"
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_identify_rig():
    """RigService.identify_rig()"""
    (basemesh, rig) = _create_human_with_rig()
    RigService.refit_existing_armature(rig, basemesh)  # Just to ensure it doesn't raise an error'
    assert rig
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)

def test_add_path_object_to_bone():
    """RigService.add_path_object_to_bone()"""
    (basemesh, rig) = _create_human_with_rig()
    curve_object = RigService.add_path_object_to_bone(rig, "spine05")

