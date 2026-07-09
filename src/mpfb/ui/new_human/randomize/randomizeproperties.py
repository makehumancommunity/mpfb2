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
    "age": {"baby": "Baby", "child": "Child", "young": "Young", "old": "Old"},
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
        "mask_helpers": RANDOMIZE_PROPERTIES.get_value("mask_helpers", entity_reference=scene)
        }
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
    RANDOMIZE_PROPERTIES.set_value("discrete_age", phenotype.get("discrete_age", False), entity_reference=scene)

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
