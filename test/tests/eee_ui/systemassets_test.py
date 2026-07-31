import pytest
from .. import dynamic_import

get_system_assets_status = dynamic_import("mpfb.ui.systemassets", "get_system_assets_status")
get_system_assets_lines = dynamic_import("mpfb.ui.systemassets", "get_system_assets_lines")
STATUS_MISSING = dynamic_import("mpfb.ui.systemassets", "STATUS_MISSING")
STATUS_OUTDATED = dynamic_import("mpfb.ui.systemassets", "STATUS_OUTDATED")
STATUS_OK = dynamic_import("mpfb.ui.systemassets", "STATUS_OK")

def test_status_is_one_of_the_known_values():
    assert get_system_assets_status() in [STATUS_MISSING, STATUS_OUTDATED, STATUS_OK]

def test_ok_has_nothing_to_say():
    assert get_system_assets_lines(STATUS_OK) == []

def test_missing_and_outdated_say_different_things():
    missing = get_system_assets_lines(STATUS_MISSING)
    outdated = get_system_assets_lines(STATUS_OUTDATED)
    assert len(missing) > 0
    assert len(outdated) > 0
    assert missing != outdated

def test_lines_fit_in_a_narrow_sidebar():
    """Blender does not wrap label texts, so the lines have to be pre-broken"""
    for status in [STATUS_MISSING, STATUS_OUTDATED]:
        for line in get_system_assets_lines(status):
            assert len(line) <= 40, "Too long line for status " + status + ": " + line

def test_returned_lines_are_copies():
    """A caller must not be able to modify the module level lists"""
    lines = get_system_assets_lines(STATUS_MISSING)
    lines.append("bogus")
    assert "bogus" not in get_system_assets_lines(STATUS_MISSING)
