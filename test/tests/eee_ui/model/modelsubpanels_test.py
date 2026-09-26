"""Tests for the dynamically generated target sliders in the Model sub panels.

The _modelsubpanels module does all of its work while being imported, and dynamic_import only finds
modules which are already loaded. The module can therefore not be re-imported against a fabricated
asset root, which means "drop an overly long target file and check that the import survives" cannot
be tested directly. Instead the filtering logic is exercised as a function over fabricated section
data, plus an invariant check over the sections the running addon actually built.
"""

import bpy
from pathlib import Path
from ... import dynamic_import, UiService

_drop_categories_with_unusable_identifiers = dynamic_import(
    "mpfb.ui.model._modelsubpanels", "_drop_categories_with_unusable_identifiers"
)
_category_identifier = dynamic_import("mpfb.ui.model._modelsubpanels", "_category_identifier")
_category_identifiers = dynamic_import("mpfb.ui.model._modelsubpanels", "_category_identifiers")
_sections = dynamic_import("mpfb.ui.model._modelsubpanels", "_sections")
_SORTED_CATEGORIES = dynamic_import("mpfb.ui.model._modelsubpanels", "_SORTED_CATEGORIES")


def _category(name, sided=False, full_path=None):
    """Build a category dict shaped like the ones the custom and user target sources produce."""
    return {
        "has_left_and_right": sided,
        "label": name.replace("_", " "),
        "name": name,
        "targets": [name + ".target"],
        "full_path": full_path if full_path is not None else Path("/tmp/" + name + ".target"),
        }


def test_category_identifier_matches_the_documented_format():
    # The panels and the registration loop must derive exactly the same string
    assert _category_identifier("custom", "a-b") == UiService.as_valid_identifier("custom.a-b")
    assert _category_identifier("custom", "a-b", "left") == UiService.as_valid_identifier("custom.l-a-b")
    assert _category_identifier("custom", "a-b", "right") == UiService.as_valid_identifier("custom.r-a-b")


def test_sided_categories_yield_two_identifiers_and_unsided_one():
    sided = _category_identifiers("custom", _category("x", sided=True))
    unsided = _category_identifiers("custom", _category("x"))
    assert len(sided) == 2, "A sided category registers a left and a right property"
    assert len(unsided) == 1, "An unsided category registers a single property"
    assert unsided[0] not in sided, "The unsided identifier is never registered for a sided category"


def test_categories_which_fit_are_left_untouched():
    sections = {"custom": {"categories": [_category("alpha"), _category("beta"), _category("gamma")]}}
    dropped = _drop_categories_with_unusable_identifiers(sections)
    assert dropped == [], "Nothing should be dropped when all names fit"
    names = [cat["name"] for cat in sections["custom"]["categories"]]
    assert names == ["alpha", "beta", "gamma"], "Order and content must be preserved"


def test_overly_long_category_is_dropped_and_reported():
    long_name = "l" * 100
    sections = {"custom": {"categories": [_category("alpha"), _category(long_name)]}}
    dropped = _drop_categories_with_unusable_identifiers(sections)
    assert len(dropped) == 1, "Exactly the one overly long category should have been dropped"
    section_name, category, identifier = dropped[0]
    assert section_name == "custom"
    assert str(category["full_path"]).endswith(long_name + ".target"), "The full path must be reported"
    assert len(identifier) > UiService.MAX_IDENTIFIER_LENGTH
    assert [cat["name"] for cat in sections["custom"]["categories"]] == ["alpha"]


def test_dropping_keeps_the_remaining_indices_consistent():
    # The getter and setter factories close over a position in this list, so a dropped category in the
    # middle must not leave a hole or shift the wrong entries
    sections = {"custom": {"categories": [_category("short_a"), _category("L" * 100), _category("short_b")]}}
    _drop_categories_with_unusable_identifiers(sections)
    categories = sections["custom"]["categories"]
    assert len(categories) == 2
    assert categories[0]["name"] == "short_a"
    assert categories[1]["name"] == "short_b", "The category after the dropped one must move up"


def test_category_is_only_measured_against_the_identifiers_it_registers():
    # "custom." + 56 characters is exactly 63, but "custom.l-" + 56 characters is 65
    name = "z" * 56
    sections = {"custom": {"categories": [_category(name), _category(name, sided=True)]}}
    dropped = _drop_categories_with_unusable_identifiers(sections)
    assert len(dropped) == 1, "Only the sided variant should overflow"
    assert dropped[0][1]["has_left_and_right"], "The dropped category should be the sided one"
    assert not sections["custom"]["categories"][0]["has_left_and_right"]


def test_filtering_tolerates_categories_without_a_full_path():
    # Categories coming from the bundled target.json have no full_path key
    sections = {"stock": {"categories": [{"has_left_and_right": False, "name": "n" * 100, "label": "n"}]}}
    dropped = _drop_categories_with_unusable_identifiers(sections)
    assert len(dropped) == 1, "A category without a full_path should still be dropped, not raise"
    assert sections["stock"]["categories"] == []


def test_filtering_tolerates_empty_and_missing_category_lists():
    sections = {"empty": {"categories": []}, "missing": {}}
    dropped = _drop_categories_with_unusable_identifiers(sections)
    assert dropped == []
    assert sections["empty"]["categories"] == []
    assert sections["missing"]["categories"] == []


def test_every_registered_slider_identifier_fits_and_exists():
    """The actual regression guard, checked against the sections the running addon built.

    If registration had aborted because of an overly long identifier, the addon would not have loaded
    and this test would never run at all.
    """
    for section_name in _sections:
        for category in _sections[section_name]["categories"]:
            for identifier in _category_identifiers(section_name, category):
                assert len(identifier) <= UiService.MAX_IDENTIFIER_LENGTH, \
                    "Too long identifier survived filtering: " + identifier
                assert hasattr(bpy.types.Scene, identifier), \
                    "Slider was not registered: " + identifier


def test_sections_without_categories_still_get_a_panel():
    # The bundled "measure" section ships with no categories at all, so empty sections are an existing
    # and harmless condition. Filtering every category out of a section produces the same situation.
    assert "measure" in _sections, "Expected the bundled measure section to exist"
    assert _SORTED_CATEGORIES["measure"] == []
    assert hasattr(bpy.types, "MPFB_PT_Model_Sub_Panel_measure"), "An empty section should still register"


def test_macro_targets_are_not_part_of_the_model_sub_panel_sections():
    # Macro details are driven by _macrosubpanel, which uses a fixed prefix rather than file names, so
    # they can never be affected by the identifier length filtering
    for section_name in _sections:
        assert "macrodetails" not in str(section_name), \
            "Macro details should not be a model sub panel section"
