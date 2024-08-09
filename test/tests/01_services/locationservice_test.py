import bpy, os

from mpfb.services.locationservice import LocationService


def test_locationservice_exists():
    assert LocationService is not None, "LocationService can be imported"


def test_mpfb_root():
    assert os.path.exists(LocationService.get_mpfb_root()), "MPFB root directory should exist"
    assert os.path.exists(LocationService.get_mpfb_root("data")), "MPFB root directory should contain a data subdir"


def test_get_user_home():
    user_home = LocationService.get_user_home()
    assert user_home is not None, "User home directory path should not be None"
    assert os.path.exists(user_home), "User home directory exists"

    # Test with a sub_path
    sub_path = "test_subdir"
    user_home_with_subpath = LocationService.get_user_home(sub_path)
    expected_path = os.path.join(user_home, sub_path)
    assert user_home_with_subpath == expected_path, f"User home directory with sub_path should be {expected_path}"
