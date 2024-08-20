import bpy, os

from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService


def test_uiservice_exists():
    assert UiService is not None, "UiService could not be imported"


def test_internal_state():
    # Set a known value
    UiService.set_value("test_key", "test_value")

    # Retrieve the value
    value = UiService.get_value("test_key")

    # Assert that the retrieved value matches the set value
    assert value == "test_value", f"Expected 'test_value', but got {value}"
