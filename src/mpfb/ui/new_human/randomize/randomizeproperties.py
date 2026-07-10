"""Shared properties, spec translation and draw helpers for the randomize panels.

This module holds everything the randomize sub-panels and operators have in common: the
scene property config set (including the per-attribute properties generated in code), the
preset list cache, the translation between the scene properties and a randomization spec,
and the draw helpers shared by the macrodetail and breast sub-panels. The panels themselves
live in one file each (randomizepanel.py, presetspanel.py, ...); the operators import the
config set and the translators from here.
"""

import os, re
from typing import TYPE_CHECKING
from ....services import LogService
from ....services import LocationService
from ....services import SceneConfigSet
from ....services import RandomizationService

if TYPE_CHECKING:
    import bpy

_LOG = LogService.get_logger("ui.new_human.randomize.randomizeproperties")

_LOC: str = os.path.dirname(__file__)
RANDOMIZE_PROPERTIES_DIR: str = os.path.join(_LOC, "properties")
RANDOMIZE_PROPERTIES: SceneConfigSet = SceneConfigSet.from_definitions_in_json_directory(RANDOMIZE_PROPERTIES_DIR, prefix="RAND_")

# The scalar phenotype attributes which have an include/neutral/deviation triple, together
# with the label shown in the UI and the box they are grouped under. The grouping mirrors the
# existing phenotype subpanel (see ui/model/_macrosubpanel.py). Race is handled separately as
# it only has an include toggle.
_ATTRIBUTE_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Macrodetails", [
        ("gender", "Gender"),
        ("age", "Age"),
        ("muscle", "Muscle"),
        ("weight", "Weight"),
        ("height", "Height"),
        ("proportions", "Proportions"),
        ]),
    ("Breast shape", [
        ("cupsize", "Cup size"),
        ("firmness", "Firmness"),
        ]),
    ]

_SCALAR_ATTRIBUTES: list[str] = [name for _group, attributes in _ATTRIBUTE_GROUPS for name, _label in attributes]

# The attributes with a discrete mode, mapped to the label shown for each of their values. In
# discrete mode the panel shows one "Allow value" checkbox per value instead of the
# neutral/deviation sliders. The value names and their order come from RandomizationService 
# so they cannot drift out of sync with the sampling code.
_DISCRETE_LABELS: dict[str, dict[str, str]] = {
    "gender": {"female": "Female", "male": "Male"},
    "age": {"baby": "Baby", "child": "Child", "young": "Young", "middleage": "Middle age", "old": "Old"},
    "race": {"asian": "Asian", "caucasian": "Caucasian", "african": "African"},
    }

# The ordered (value name, label) pairs for each discrete attribute, built from the canonical
# value names in RandomizationService and the labels above.
_DISCRETE_VALUES: dict[str, list[tuple[str, str]]] = {
    attribute: [(value_name, _DISCRETE_LABELS[attribute][value_name])
                for value_name in RandomizationService.get_discrete_value_names(attribute)]
    for attribute in _DISCRETE_LABELS
    }

# The per-attribute scene properties are generated here rather than as individual JSON files,
# following the precedent of ui/model/_macrosubpanel.py. Each scalar attribute gets an include
# toggle, a neutral override and a max deviation.
for _group_name, _attributes in _ATTRIBUTE_GROUPS:
    for _attribute_name, _attribute_label in _attributes:
        RANDOMIZE_PROPERTIES.add_property({
            "type": "boolean",
            "name": _attribute_name + "_include",
            "description": "Include " + _attribute_label.lower() + " in the randomization. When unchecked, it is set to its neutral value instead",
            "label": "Randomize " + _attribute_label.lower(),
            "default": True
            })
        RANDOMIZE_PROPERTIES.add_property({
            "type": "float",
            "name": _attribute_name + "_neutral",
            "description": "The value the " + _attribute_label.lower() + " distribution is centered on",
            "label": _attribute_label + " neutral",
            "default": 0.5,
            "min": 0.0,
            "max": 1.0
            })
        RANDOMIZE_PROPERTIES.add_property({
            "type": "float",
            "name": _attribute_name + "_deviation",
            "description": "The maximum distance from the neutral value that the " + _attribute_label.lower() + " may deviate",
            "label": _attribute_label + " max deviation",
            "default": 0.5,
            "min": 0.0,
            "max": 1.0
            })

RANDOMIZE_PROPERTIES.add_property({
    "type": "boolean",
    "name": "race_include",
    "description": "Include race in the randomization. When unchecked, a mix of all races is used instead (33% of each race).",
    "label": "Randomize race",
    "default": True
    })

# The per-value "allow" toggles for the discrete attributes, generated in a loop over the value
# table above. In discrete mode a value is only eligible to be picked when its toggle is on;
# with none of an attribute's values allowed, the attribute is treated as excluded.
for _discrete_attribute, _values in _DISCRETE_VALUES.items():
    for _value_name, _value_label in _values:
        RANDOMIZE_PROPERTIES.add_property({
            "type": "boolean",
            "name": _discrete_attribute + "_allow_" + _value_name,
            "description": "Allow the discrete value \"" + _value_label + "\" to be picked when randomizing",
            "label": "Allow \"" + _value_label + "\"",
            "default": True
            })

# The bodypart types which are randomized from an asset pool and get a pack/include/exclude
# filter set. Hair is included (it shares the three filters) but its enable toggle is a JSON
# property (hair_randomize) since it carries extra hair-only settings. Eyes are not here at
# all, being a drop-down rather than a randomized pool.
_FILTERED_BODYPART_TYPES: list[str] = ["hair", "eyebrows", "eyelashes", "teeth", "tongue"]

# The plain bodypart types get a generated enable toggle in addition to the three filters.
_PLAIN_BODYPART_TYPES: list[str] = RandomizationService.get_plain_bodypart_types()

# The plain bodypart types paired with the label shown for their box in the panel.
_PLAIN_BODYPART_LABELS: list[tuple[str, str]] = [
    ("eyebrows", "Eyebrows"),
    ("eyelashes", "Eyelashes"),
    ("teeth", "Teeth"),
    ("tongue", "Tongue"),
    ]

# The near-identical per-type filter properties (enable for the plain types, plus pack, include
# and exclude for every filtered type) are generated in a loop rather than as one JSON file
# each, mirroring the per-attribute phenotype properties above.
for _bodypart in _PLAIN_BODYPART_TYPES:
    RANDOMIZE_PROPERTIES.add_property({
        "type": "boolean",
        "name": _bodypart + "_enable",
        "description": "Attach a randomly picked " + _bodypart + " asset to the created human. When off, none is added",
        "label": "Randomize " + _bodypart,
        "default": True
        })
for _bodypart in _FILTERED_BODYPART_TYPES:
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": _bodypart + "_pack",
        "description": "Only pick " + _bodypart + " belonging to an asset pack whose name contains this string. Leave empty to allow all packs",
        "label": "Asset pack name filter",
        "default": ""
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": _bodypart + "_include",
        "description": "Only pick " + _bodypart + " whose name contains at least one of these comma-separated keywords. Leave empty to allow all",
        "label": "Name must contain",
        "default": ""
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": _bodypart + "_exclude",
        "description": "Never pick " + _bodypart + " whose name contains any of these comma-separated keywords",
        "label": "Name must not contain",
        "default": ""
        })

# The eight clothes slots, paired with the label shown for their box in the panel. The slot
# names and their defaults are canonical in RandomizationService; only the display labels live
# here. The list is in body order (head to feet), which is how the panel lays the boxes out.
_CLOTHES_SLOTS: list[str] = RandomizationService.get_clothes_slots()
_CLOTHES_SLOT_LABELS: list[tuple[str, str]] = [
    ("head", "Head"),
    ("full_body", "Full body"),
    ("upper_body", "Upper body"),
    ("lower_body", "Lower body"),
    ("hands", "Hands"),
    ("feet", "Feet"),
    ("underwear", "Underwear"),
    ("accessories", "Accessories"),
    ]

# Each slot gets eight near-identical properties, generated in a loop rather than as JSON files.
# The "_open" toggle is UI state only (whether the slot's box is expanded) and is not part of
# the spec; the other seven map to the slot's spec section. Per-slot defaults (enablement,
# chance, keyword lists) come from RandomizationService so they cannot drift out of sync.
for _slot in _CLOTHES_SLOTS:
    _slot_default = RandomizationService.get_default_clothes_asset_spec(_slot)
    RANDOMIZE_PROPERTIES.add_property({
        "type": "boolean",
        "name": "clothes_" + _slot + "_open",
        "description": "Expand this slot to show its filters",
        "label": "",
        "default": False,
        "subtype": "panel_toggle"
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "boolean",
        "name": "clothes_" + _slot + "_enable",
        "description": "Attach a randomly picked garment to this slot. When off, this slot is skipped",
        "label": "Randomize",
        "default": _slot_default["enabled"]
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "int",
        "name": "clothes_" + _slot + "_chance",
        "description": "The percent chance, per character, that this slot produces a garment",
        "label": "Chance (%)",
        "default": _slot_default["chance"],
        "min": 0,
        "max": 100
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": "clothes_" + _slot + "_pack",
        "description": "Only pick garments belonging to an asset pack whose name contains this string. Leave empty to allow all packs",
        "label": "Asset pack name filter",
        "default": _slot_default["pack"]
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": "clothes_" + _slot + "_include_any",
        "description": "Pick garments whose name contains at least one of these comma-separated keywords, regardless of gender",
        "label": "Name must contain (any)",
        "default": _slot_default["include_any"]
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": "clothes_" + _slot + "_include_female",
        "description": "Additional keywords used only for female characters (unioned with the common list)",
        "label": "Name must contain (female)",
        "default": _slot_default["include_female"]
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": "clothes_" + _slot + "_include_male",
        "description": "Additional keywords used only for male characters (unioned with the common list)",
        "label": "Name must contain (male)",
        "default": _slot_default["include_male"]
        })
    RANDOMIZE_PROPERTIES.add_property({
        "type": "string",
        "name": "clothes_" + _slot + "_exclude",
        "description": "Never pick garments whose name contains any of these comma-separated keywords",
        "label": "Name must not contain",
        "default": _slot_default["exclude"]
        })

# The list of saved randomization presets is cached so that the enum property below keeps
# references to the option strings alive (see the equivalent handling in HumanService).
_EXISTING_PRESETS: list[str] | None = None


def rebuild_preset_list() -> None:
    """Rescan the user config directory for randomization presets and cache their names."""
    _LOG.enter()
    global _EXISTING_PRESETS  # pylint: disable=W0603
    confdir = LocationService.get_user_config()
    presets = []
    for filename in os.listdir(confdir):
        match = re.search(r'^randomization\.(.*)\.json$', filename)
        if match and match.group(1):
            presets.append(match.group(1))
    presets.sort()
    _EXISTING_PRESETS = presets


def _populate_presets(self, context: "bpy.types.Context") -> list[tuple[str, str, str]]:
    _LOG.enter()
    if _EXISTING_PRESETS is None:
        rebuild_preset_list()
    return [(name, name, name) for name in _EXISTING_PRESETS]


RANDOMIZE_PROPERTIES.add_property({
    "type": "enum",
    "name": "available_presets",
    "description": "Saved randomization presets",
    "label": "Available presets",
    "default": 0
    }, _populate_presets)


def _populate_rig(self, context: "bpy.types.Context") -> list[tuple[str, str, str]]:
    """Build the rig drop-down items.

    Same language and contents as the new-human-from-save-file panel's rig override, except
    the "From preset" entry is omitted (there is no preset to defer to). The built-in and
    Rigify entries are hardcoded; the custom rigs come from AssetService.
    """
    from ....services import AssetService  # pylint: disable=C0415
    items = [
        ("NONE", "No rig", "Do not add a rig"),
        ("default", "Default", "Use the default rig"),
        ("default_no_toes", "Default (no toes)", "Use the default_no_toes rig"),
        ("game_engine", "Game engine", "Use the game_engine rig"),
        ("game_engine_with_breast", "Game engine (with breast)", "Use the game_engine_with_breast rig"),
        ("cmu_mb", "CMU MB", "Use the cmu_mb rig"),
        ("mixamo", "Mixamo", "Use the mixamo rig"),
        ("mixamo_unity", "Mixamo (unity extensions)", "The Mixamo rig with extra bones for unity"),
        ("rigify.human_toes", "Rigify default metarig", "Use the default rigify metarig"),
        ("rigify.human", "Rigify metarig without toes", "Use the default rigify metarig without toes"),
        ("openpose", "OpenPose", "Use the OpenPose BODY_25 rig (without hands)"),
        ]
    for custom_rig in AssetService.get_custom_rigs():
        items.append(("custom." + custom_rig["name"], "Custom: " + custom_rig["name"], "Use custom rig " + custom_rig["name"]))
    return items


RANDOMIZE_PROPERTIES.add_property({
    "type": "enum",
    "name": "rig",
    "description": "What rig to add to the created human. The rig is added before the body parts, so they are rigged as they are attached",
    "label": "Rig",
    "default": 1
    }, _populate_rig)


def scene_to_spec(scene: "bpy.types.Scene") -> dict:
    """Build a randomization spec dict from the current scene property values.

    The result has the shape produced by RandomizationService.get_default_phenotype_spec()
    plus a "creation" section holding the duplicated creation settings, and is what gets
    saved as a preset.
    """
    _LOG.enter()
    spec = RandomizationService.get_default_phenotype_spec()

    phenotype = spec["phenotype"]
    phenotype["distribution"] = RANDOMIZE_PROPERTIES.get_value("distribution", entity_reference=scene)
    phenotype["discrete_race"] = RANDOMIZE_PROPERTIES.get_value("discrete_race", entity_reference=scene)
    phenotype["discrete_gender"] = RANDOMIZE_PROPERTIES.get_value("discrete_gender", entity_reference=scene)
    phenotype["discrete_age"] = RANDOMIZE_PROPERTIES.get_value("discrete_age", entity_reference=scene)
    phenotype["breast_gender_cutoff"] = RANDOMIZE_PROPERTIES.get_value("breast_gender_cutoff", entity_reference=scene)
    phenotype["breast_age_cutoff"] = RANDOMIZE_PROPERTIES.get_value("breast_age_cutoff", entity_reference=scene)

    attributes = phenotype["attributes"]
    for name in _SCALAR_ATTRIBUTES:
        attributes[name] = {
            "include": RANDOMIZE_PROPERTIES.get_value(name + "_include", entity_reference=scene),
            "neutral": RANDOMIZE_PROPERTIES.get_value(name + "_neutral", entity_reference=scene),
            "deviation": RANDOMIZE_PROPERTIES.get_value(name + "_deviation", entity_reference=scene)
            }
    attributes["race"] = {"include": RANDOMIZE_PROPERTIES.get_value("race_include", entity_reference=scene)}

    # The allowed value lists for the discrete attributes are collected from their per-value
    # toggles, preserving the value order defined in _DISCRETE_VALUES.
    for discrete_attribute, values in _DISCRETE_VALUES.items():
        attributes[discrete_attribute]["allowed"] = [
            value_name for value_name, _label in values
            if RANDOMIZE_PROPERTIES.get_value(discrete_attribute + "_allow_" + value_name, entity_reference=scene)
            ]

    spec["creation"] = {
        "scale_factor": RANDOMIZE_PROPERTIES.get_value("scale_factor", entity_reference=scene),
        "detailed_helpers": RANDOMIZE_PROPERTIES.get_value("detailed_helpers", entity_reference=scene),
        "extra_vertex_groups": RANDOMIZE_PROPERTIES.get_value("extra_vertex_groups", entity_reference=scene),
        "mask_helpers": RANDOMIZE_PROPERTIES.get_value("mask_helpers", entity_reference=scene),
        "rig": RANDOMIZE_PROPERTIES.get_value("rig", entity_reference=scene),
        "auto_generate_rigify": RANDOMIZE_PROPERTIES.get_value("auto_generate_rigify", entity_reference=scene),
        "meta_rig_action": RANDOMIZE_PROPERTIES.get_value("meta_rig_action", entity_reference=scene)
        }

    # The assets.skin section is filled from the skin sub-panel's properties. The default spec
    # already carries a skin subsection, so only its values are overwritten here.
    skin = spec["assets"]["skin"]
    skin["enabled"] = RANDOMIZE_PROPERTIES.get_value("randomize_skin", entity_reference=scene)
    skin["match_gender"] = RANDOMIZE_PROPERTIES.get_value("match_gender", entity_reference=scene)
    skin["match_age"] = RANDOMIZE_PROPERTIES.get_value("match_age", entity_reference=scene)
    skin["match_race"] = RANDOMIZE_PROPERTIES.get_value("match_race", entity_reference=scene)
    skin["fallback"] = RANDOMIZE_PROPERTIES.get_value("skin_fallback", entity_reference=scene)
    skin["pack"] = RANDOMIZE_PROPERTIES.get_value("skin_pack", entity_reference=scene)
    skin["include"] = RANDOMIZE_PROPERTIES.get_value("skin_include", entity_reference=scene)
    skin["exclude"] = RANDOMIZE_PROPERTIES.get_value("skin_exclude", entity_reference=scene)
    skin["skin_type"] = RANDOMIZE_PROPERTIES.get_value("skin_type", entity_reference=scene)
    skin["material_instances"] = RANDOMIZE_PROPERTIES.get_value("skin_material_instances", entity_reference=scene)

    # The bodypart sections. The default spec already carries every subsection, so only their
    # values are overwritten here. The shared asset material applies to all bodyparts but eyes.
    assets = spec["assets"]
    assets["asset_material_type"] = RANDOMIZE_PROPERTIES.get_value("asset_material_type", entity_reference=scene)

    eyes = assets["eyes"]
    eyes["mode"] = RANDOMIZE_PROPERTIES.get_value("eyes_mode", entity_reference=scene)
    eyes["material_type"] = RANDOMIZE_PROPERTIES.get_value("eyes_material_type", entity_reference=scene)
    eyes["randomize_alt_materials"] = RANDOMIZE_PROPERTIES.get_value("eyes_randomize_alt_materials", entity_reference=scene)

    hair = assets["hair"]
    hair["enabled"] = RANDOMIZE_PROPERTIES.get_value("hair_randomize", entity_reference=scene)
    hair["match_gender"] = RANDOMIZE_PROPERTIES.get_value("hair_match_gender", entity_reference=scene)
    hair["fallback"] = RANDOMIZE_PROPERTIES.get_value("hair_fallback", entity_reference=scene)
    hair["pack"] = RANDOMIZE_PROPERTIES.get_value("hair_pack", entity_reference=scene)
    hair["include"] = RANDOMIZE_PROPERTIES.get_value("hair_include", entity_reference=scene)
    hair["exclude"] = RANDOMIZE_PROPERTIES.get_value("hair_exclude", entity_reference=scene)
    hair["randomize_alt_materials"] = RANDOMIZE_PROPERTIES.get_value("hair_randomize_alt_materials", entity_reference=scene)

    for bodypart in _PLAIN_BODYPART_TYPES:
        section = assets[bodypart]
        section["enabled"] = RANDOMIZE_PROPERTIES.get_value(bodypart + "_enable", entity_reference=scene)
        section["pack"] = RANDOMIZE_PROPERTIES.get_value(bodypart + "_pack", entity_reference=scene)
        section["include"] = RANDOMIZE_PROPERTIES.get_value(bodypart + "_include", entity_reference=scene)
        section["exclude"] = RANDOMIZE_PROPERTIES.get_value(bodypart + "_exclude", entity_reference=scene)

    # The assets.clothes section: one subsection per slot. The default spec already carries
    # every slot, so only their values are overwritten here. The "_open" toggle is UI state and
    # is deliberately not written to the spec.
    clothes = assets["clothes"]
    for slot in _CLOTHES_SLOTS:
        slot_section = clothes[slot]
        prefix = "clothes_" + slot + "_"
        slot_section["enabled"] = RANDOMIZE_PROPERTIES.get_value(prefix + "enable", entity_reference=scene)
        slot_section["chance"] = RANDOMIZE_PROPERTIES.get_value(prefix + "chance", entity_reference=scene)
        slot_section["pack"] = RANDOMIZE_PROPERTIES.get_value(prefix + "pack", entity_reference=scene)
        slot_section["include_any"] = RANDOMIZE_PROPERTIES.get_value(prefix + "include_any", entity_reference=scene)
        slot_section["include_female"] = RANDOMIZE_PROPERTIES.get_value(prefix + "include_female", entity_reference=scene)
        slot_section["include_male"] = RANDOMIZE_PROPERTIES.get_value(prefix + "include_male", entity_reference=scene)
        slot_section["exclude"] = RANDOMIZE_PROPERTIES.get_value(prefix + "exclude", entity_reference=scene)
    return spec


def spec_to_scene(spec: dict, scene: "bpy.types.Scene") -> None:
    """Populate the scene properties from a loaded randomization spec dict.

    Missing keys fall back to the built-in defaults, so presets written by earlier versions
    or by later sub-features can still be loaded.
    """
    _LOG.enter()
    default = RandomizationService.get_default_phenotype_spec()["phenotype"]
    phenotype = spec.get("phenotype", default)

    RANDOMIZE_PROPERTIES.set_value("distribution", phenotype.get("distribution", default["distribution"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("discrete_race", phenotype.get("discrete_race", False), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("discrete_gender", phenotype.get("discrete_gender", True), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("discrete_age", phenotype.get("discrete_age", True), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("breast_gender_cutoff", phenotype.get("breast_gender_cutoff", default["breast_gender_cutoff"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("breast_age_cutoff", phenotype.get("breast_age_cutoff", default["breast_age_cutoff"]), entity_reference=scene)

    attributes = phenotype.get("attributes", {})
    for name in _SCALAR_ATTRIBUTES:
        cfg = attributes.get(name, {})
        RANDOMIZE_PROPERTIES.set_value(name + "_include", cfg.get("include", True), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(name + "_neutral", cfg.get("neutral", 0.5), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(name + "_deviation", cfg.get("deviation", 0.5), entity_reference=scene)
    race_cfg = attributes.get("race", {})
    RANDOMIZE_PROPERTIES.set_value("race_include", race_cfg.get("include", True), entity_reference=scene)

    # Restore the per-value toggles for the discrete attributes. A missing "allowed" list (an
    # older preset) defaults every value to allowed.
    for discrete_attribute, values in _DISCRETE_VALUES.items():
        allowed = attributes.get(discrete_attribute, {}).get("allowed")
        for value_name, _label in values:
            is_allowed = True if allowed is None else value_name in allowed
            RANDOMIZE_PROPERTIES.set_value(discrete_attribute + "_allow_" + value_name, is_allowed, entity_reference=scene)

    creation = spec.get("creation", {})
    RANDOMIZE_PROPERTIES.set_value("scale_factor", creation.get("scale_factor", "METER"), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("detailed_helpers", creation.get("detailed_helpers", True), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("extra_vertex_groups", creation.get("extra_vertex_groups", True), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("mask_helpers", creation.get("mask_helpers", True), entity_reference=scene)
    # A preset without a rig key loads as "No rig", so an old preset keeps producing the
    # unrigged character it did before.
    RANDOMIZE_PROPERTIES.set_value("rig", creation.get("rig", "NONE"), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("auto_generate_rigify", creation.get("auto_generate_rigify", True), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("meta_rig_action", creation.get("meta_rig_action", "hide"), entity_reference=scene)

    # The assets.skin section. A preset written before this section existed has no "assets"
    # key; skin randomization is then set to disabled so the old preset keeps producing what
    # it did before (a default material). The remaining skin controls fall back to the
    # built-in skin defaults.
    default_skin = RandomizationService.get_default_skin_asset_spec()
    skin = (spec.get("assets") or {}).get("skin", {})
    RANDOMIZE_PROPERTIES.set_value("randomize_skin", skin.get("enabled", False), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("match_gender", skin.get("match_gender", default_skin["match_gender"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("match_age", skin.get("match_age", default_skin["match_age"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("match_race", skin.get("match_race", default_skin["match_race"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_fallback", skin.get("fallback", default_skin["fallback"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_pack", skin.get("pack", default_skin["pack"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_include", skin.get("include", default_skin["include"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_exclude", skin.get("exclude", default_skin["exclude"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_type", skin.get("skin_type", default_skin["skin_type"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("skin_material_instances", skin.get("material_instances", default_skin["material_instances"]), entity_reference=scene)

    # The bodypart sections. As with skin, a preset written before these sections existed has
    # no subsection for a given type; that type is then set to disabled (eyes to "do not add")
    # so the old preset keeps producing exactly what it did before. The remaining controls fall
    # back to the built-in bodypart defaults.
    assets = spec.get("assets") or {}
    RANDOMIZE_PROPERTIES.set_value("asset_material_type", assets.get("asset_material_type", "MAKESKIN"), entity_reference=scene)

    default_eyes = RandomizationService.get_default_bodypart_asset_spec("eyes")
    eyes = assets.get("eyes", {})
    RANDOMIZE_PROPERTIES.set_value("eyes_mode", eyes.get("mode", "DONOTADD"), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("eyes_material_type", eyes.get("material_type", default_eyes["material_type"]), entity_reference=scene)
    eyes_alt = eyes.get("randomize_alt_materials", default_eyes["randomize_alt_materials"])
    RANDOMIZE_PROPERTIES.set_value("eyes_randomize_alt_materials", eyes_alt, entity_reference=scene)

    default_hair = RandomizationService.get_default_bodypart_asset_spec("hair")
    hair = assets.get("hair", {})
    RANDOMIZE_PROPERTIES.set_value("hair_randomize", hair.get("enabled", False), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("hair_match_gender", hair.get("match_gender", default_hair["match_gender"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("hair_fallback", hair.get("fallback", default_hair["fallback"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("hair_pack", hair.get("pack", default_hair["pack"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("hair_include", hair.get("include", default_hair["include"]), entity_reference=scene)
    RANDOMIZE_PROPERTIES.set_value("hair_exclude", hair.get("exclude", default_hair["exclude"]), entity_reference=scene)
    hair_alt = hair.get("randomize_alt_materials", default_hair["randomize_alt_materials"])
    RANDOMIZE_PROPERTIES.set_value("hair_randomize_alt_materials", hair_alt, entity_reference=scene)

    for bodypart in _PLAIN_BODYPART_TYPES:
        default_bodypart = RandomizationService.get_default_bodypart_asset_spec(bodypart)
        section = assets.get(bodypart, {})
        RANDOMIZE_PROPERTIES.set_value(bodypart + "_enable", section.get("enabled", False), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(bodypart + "_pack", section.get("pack", default_bodypart["pack"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(bodypart + "_include", section.get("include", default_bodypart["include"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(bodypart + "_exclude", section.get("exclude", default_bodypart["exclude"]), entity_reference=scene)

    # The assets.clothes section. As with the bodyparts, a preset written before this section
    # existed has no "clothes" key (or is missing a given slot); that slot is then set to
    # disabled so the old preset keeps producing exactly what it did before. The remaining slot
    # controls fall back to the built-in clothes defaults. The "_open" toggles are UI state and
    # are left at their default.
    clothes = assets.get("clothes") or {}
    for slot in _CLOTHES_SLOTS:
        default_slot = RandomizationService.get_default_clothes_asset_spec(slot)
        slot_section = clothes.get(slot, {})
        prefix = "clothes_" + slot + "_"
        RANDOMIZE_PROPERTIES.set_value(prefix + "enable", slot_section.get("enabled", False), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "chance", slot_section.get("chance", default_slot["chance"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "pack", slot_section.get("pack", default_slot["pack"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "include_any", slot_section.get("include_any", default_slot["include_any"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "include_female", slot_section.get("include_female", default_slot["include_female"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "include_male", slot_section.get("include_male", default_slot["include_male"]), entity_reference=scene)
        RANDOMIZE_PROPERTIES.set_value(prefix + "exclude", slot_section.get("exclude", default_slot["exclude"]), entity_reference=scene)


# The scalar attributes which have a discrete mode, mapped to the scene property toggling it.
# When the toggle is on the attribute shows its "allow value" toggles instead of the
# neutral/deviation sliders. Race has its own box (draw_race_box) rather than a slider box.
_DISCRETE_MODE_TOGGLES: dict[str, str] = {
    "gender": "discrete_gender",
    "age": "discrete_age",
    }


def draw_allow_toggles(scene: "bpy.types.Scene", layout: "bpy.types.UILayout", attribute_name: str) -> None:
    """Draw the per-value "allow" toggles for one discrete attribute."""
    RANDOMIZE_PROPERTIES.draw_properties(scene, layout, [
        attribute_name + "_allow_" + value_name for value_name, _label in _DISCRETE_VALUES[attribute_name]
        ])


def _draw_scalar_box(scene: "bpy.types.Scene", layout: "bpy.types.UILayout", attribute_name: str, attribute_label: str) -> None:
    """Draw one scalar attribute's settings into its own labelled box.

    Every attribute has an include toggle. Gender and age additionally have a "Discrete"
    toggle and, when it is on, show the per-value "allow" toggles instead of the
    neutral/deviation sliders (which are meaningless in discrete mode). The other scalars
    are always continuous.
    """
    box = layout.box()
    box.label(text=attribute_label + " settings")
    RANDOMIZE_PROPERTIES.draw_properties(scene, box, [attribute_name + "_include"])
    discrete_toggle = _DISCRETE_MODE_TOGGLES.get(attribute_name)
    if discrete_toggle is not None:
        RANDOMIZE_PROPERTIES.draw_properties(scene, box, [discrete_toggle])
        if RANDOMIZE_PROPERTIES.get_value(discrete_toggle, entity_reference=scene):
            draw_allow_toggles(scene, box, attribute_name)
            return
    RANDOMIZE_PROPERTIES.draw_properties(scene, box, [
        attribute_name + "_neutral",
        attribute_name + "_deviation"
        ])


def draw_attribute_group(scene: "bpy.types.Scene", layout: "bpy.types.UILayout", attributes: list[tuple[str, str]]) -> None:
    """Draw a labelled settings box for each scalar attribute in the group."""
    for attribute_name, attribute_label in attributes:
        _draw_scalar_box(scene, layout, attribute_name, attribute_label)


def draw_race_box(scene: "bpy.types.Scene", layout: "bpy.types.UILayout") -> None:
    """Draw the race settings into their own labelled box.

    Race has an include toggle and a "Discrete race" toggle. In discrete mode it shows one
    "allow value" toggle per race; in continuous mode there is nothing else to configure
    (the three weights are randomized and normalized automatically).
    """
    box = layout.box()
    box.label(text="Race settings")
    RANDOMIZE_PROPERTIES.draw_properties(scene, box, ["race_include", "discrete_race"])
    if RANDOMIZE_PROPERTIES.get_value("discrete_race", entity_reference=scene):
        draw_allow_toggles(scene, box, "race")


def draw_breast_cutoffs_box(scene: "bpy.types.Scene", layout: "bpy.types.UILayout") -> None:
    """Draw the breast constraint cutoffs into their own labelled box.

    Breasts (cup size and firmness) are only randomized for characters below the gender cutoff
    and at or above the age cutoff; the two sliders let the user tune those bounds.
    """
    box = layout.box()
    box.label(text="Cutoffs")
    RANDOMIZE_PROPERTIES.draw_properties(scene, box, ["breast_gender_cutoff", "breast_age_cutoff"])


def _draw_bodypart_filters(scene: "bpy.types.Scene", box: "bpy.types.UILayout", bodypart: str) -> None:
    """Draw the pack / include / exclude filters for one bodypart type into its box."""
    RANDOMIZE_PROPERTIES.draw_properties(scene, box, [
        bodypart + "_pack",
        bodypart + "_include",
        bodypart + "_exclude"
        ])


def draw_bodyparts(scene: "bpy.types.Scene", layout: "bpy.types.UILayout") -> None:
    """Draw the body parts panel: a shared material enum, then one box per bodypart type.

    Eyes and hair carry extra settings, so they get their own hand-written boxes; the plain
    types (eyebrows, eyelashes, teeth, tongue) get a uniform enable-plus-filters box each.
    """
    RANDOMIZE_PROPERTIES.draw_properties(scene, layout, ["asset_material_type"])

    eyes_box = layout.box()
    eyes_box.label(text="Eyes")
    RANDOMIZE_PROPERTIES.draw_properties(scene, eyes_box, [
        "eyes_mode",
        "eyes_material_type",
        "eyes_randomize_alt_materials"
        ])

    hair_box = layout.box()
    hair_box.label(text="Hair")
    RANDOMIZE_PROPERTIES.draw_properties(scene, hair_box, [
        "hair_randomize",
        "hair_match_gender",
        "hair_fallback"
        ])
    _draw_bodypart_filters(scene, hair_box, "hair")
    RANDOMIZE_PROPERTIES.draw_properties(scene, hair_box, ["hair_randomize_alt_materials"])

    for bodypart, label in _PLAIN_BODYPART_LABELS:
        box = layout.box()
        box.label(text=label)
        RANDOMIZE_PROPERTIES.draw_properties(scene, box, [bodypart + "_enable"])
        _draw_bodypart_filters(scene, box, bodypart)


def draw_clothes(scene: "bpy.types.Scene", layout: "bpy.types.UILayout") -> None:
    """Draw the clothes panel: a shared material enum, then one collapsible box per slot.

    Each slot's box always shows a header row (an expand toggle, the enable checkbox and the
    chance slider); its filter fields (pack and the four keyword lists) are only drawn when the
    slot is expanded. Eight always-open boxes would make the panel very tall, so the filters
    fold away by default.
    """
    RANDOMIZE_PROPERTIES.draw_properties(scene, layout, ["asset_material_type"])

    for slot, label in _CLOTHES_SLOT_LABELS:
        box = layout.box()
        header = box.row()
        header.label(text=label)
        RANDOMIZE_PROPERTIES.draw_properties(scene, header, [
            "clothes_" + slot + "_open",
            "clothes_" + slot + "_enable",
            "clothes_" + slot + "_chance"
            ])
        if RANDOMIZE_PROPERTIES.get_value("clothes_" + slot + "_open", entity_reference=scene):
            RANDOMIZE_PROPERTIES.draw_properties(scene, box, [
                "clothes_" + slot + "_pack",
                "clothes_" + slot + "_include_any",
                "clothes_" + slot + "_include_female",
                "clothes_" + slot + "_include_male",
                "clothes_" + slot + "_exclude"
                ])
