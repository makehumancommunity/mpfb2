import bpy, os, json
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import ExportService
from .. import TargetService
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


def test_exportervice_exists():
    """ExportService"""
    assert ExportService is not None, "ExportService can be imported"

def create_sample_human():
    """Character to use in tests"""
    name = ObjectService.random_name()
    deserialization_settings = HumanService.get_default_deserialization_settings()
    human_info = HUMAN_PRESET_DICT.copy()
    human_info["name"] = name
    basemesh = HumanService.deserialize_from_dict(human_info, deserialization_settings)
    return basemesh

def remove_character_copy(character_copy):
    """Remove a character copy from the scene"""
    if character_copy is None:
        return
    if character_copy.parent is None:
        obj = character_copy
    else:
        obj = character_copy.parent

    for child in ObjectService.get_list_of_children(obj):
        ObjectService.delete_object(child)
    ObjectService.delete_object(obj)

def test_create_character_copy():
    """ExportService.create_character_copy()"""
    basemesh = create_sample_human()
    character_copy = ExportService.create_character_copy(basemesh)
    assert character_copy is not None, "Character copy created successfully"
    remove_character_copy(character_copy)

# def bake_shapekeys_modifiers_remove_helpers(basemesh, bake_shapekeys=True, bake_masks=False, bake_subdiv=False, remove_helpers=True, also_proxy=True):

def test_bake_shapekeys_and_modifiers():
    """ExportService.bake_shapekeys_modifiers_remove_helpers()"""
    basemesh = create_sample_human()
    character_copy = ExportService.create_character_copy(basemesh)
    new_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(character_copy)

    has_mask_modifier = False
    has_subdiv_modifier = False

    for modifier in new_basemesh.modifiers:
        #print(modifier)
        if modifier.type == 'MASK':
            has_mask_modifier = True
        elif modifier.type == 'SUBSURF':
            has_subdiv_modifier = True

    assert has_mask_modifier
    assert has_subdiv_modifier
    assert TargetService.has_any_shapekey(new_basemesh)

    ExportService.bake_shapekeys_modifiers_remove_helpers(
        new_basemesh,
        bake_shapekeys=True,
        bake_masks=True,
        bake_subdiv=True,
        remove_helpers=False,
        also_proxy=False)

    has_mask_modifier = False
    has_subdiv_modifier = False

    for modifier in new_basemesh.modifiers:
        print(modifier)
        if modifier.type == 'MASK':
            has_mask_modifier = True
        elif modifier.type == 'SUBSURF':
            has_subdiv_modifier = True

    assert not has_mask_modifier
    assert not has_subdiv_modifier
    assert not TargetService.has_any_shapekey(new_basemesh)

    remove_character_copy(character_copy)