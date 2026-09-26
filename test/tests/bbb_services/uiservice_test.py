import bpy, os

from .. import UiService
from .. import LocationService


def test_uiservice_exists():
    assert UiService is not None, "UiService could not be imported"


def test_internal_state():
    # Set a known value
    UiService.set_value("test_key", "test_value")

    # Retrieve the value
    value = UiService.get_value("test_key")

    # Assert that the retrieved value matches the set value
    assert value == "test_value", f"Expected 'test_value', but got {value}"


def test_max_identifier_length_matches_blenders_limit():
    # Blender's MAX_IDPROP_NAME is 64 and the check is "id_len >= 64", so 63 is the largest usable length
    assert UiService.MAX_IDENTIFIER_LENGTH == 63, "Expected the blender identifier limit to be 63"


def test_as_valid_identifier_preserves_length():
    # is_valid_identifier_length() measures the sanitized string, which is only equivalent to measuring
    # the raw string because sanitizing substitutes characters one by one
    raw = "a/b.c-d e" * 11
    assert len(UiService.as_valid_identifier(raw)) == len(raw), "Sanitizing must not change the length"


def test_as_valid_identifier_does_not_truncate():
    # Backwards compatibility: existing callers must keep getting the full string back
    raw = "x" * 100
    assert UiService.as_valid_identifier(raw) == raw, "Sanitizing must not truncate"


def test_is_valid_identifier_length_accepts_names_which_fit():
    assert UiService.is_valid_identifier_length("torso.stomach-pregnant-decr-incr")
    assert UiService.is_valid_identifier_length("y" * 63), "63 characters should be accepted"


def test_is_valid_identifier_length_rejects_names_which_do_not_fit():
    assert not UiService.is_valid_identifier_length("y" * 64), "64 characters should be rejected"
    assert not UiService.is_valid_identifier_length("y" * 100)


def test_is_valid_identifier_length_counts_section_and_side_prefixes():
    # A name can fit when unsided and still overflow once the "l-" side prefix is added
    name = "z" * 56
    assert UiService.is_valid_identifier_length("custom." + name), "Should fit at exactly 63 characters"
    assert not UiService.is_valid_identifier_length("custom.l-" + name), "Side prefix should push it over"
