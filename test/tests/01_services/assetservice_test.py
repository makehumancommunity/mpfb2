import bpy, os

from mpfb.services.assetservice import AssetService
from mpfb.services.locationservice import LocationService


def test_assetservice_exists():
    assert AssetService is not None, "AssetService could not be imported"


def test_system_assets_pack_is_installed():
    assert AssetService.have_any_pack_meta_data() == True, "At least one pack metadata file"
    assert AssetService.system_assets_pack_is_installed() == True, "makehuman_system_assets should be installed in order to run the tests"


def test_get_available_data_roots():
    data_roots = AssetService.get_available_data_roots()
    assert isinstance(data_roots, list), "get_available_data_roots should return a list"

    for root in data_roots:
        assert os.path.exists(root), f"Data root path {root} should exist"
        assert os.path.isdir(root), f"Data root path {root} should be a directory"

    # Additional checks to ensure specific data roots are included
    user_data = LocationService.get_user_data()
    mpfb_data = LocationService.get_mpfb_data()

    expected_roots = [mpfb_data, user_data]
    for expected_root in expected_roots:
        if expected_root and os.path.exists(expected_root):
            assert expected_root in data_roots, f"Expected data root {expected_root} should be in the list of data roots"


def test_get_asset_names_in_pack():

    pack_name = "makehuman_system_assets"
    asset_names = AssetService.get_asset_names_in_pack(pack_name)

    assert isinstance(asset_names, list), "get_asset_names_in_pack should return a list"
    assert len(asset_names) > 0, "The list of asset names should not be empty"

    for name in asset_names:
        assert isinstance(name, str), f"Asset name {name} should be a string"
        assert name, "Asset name should not be an empty string"

    # Additional check to ensure specific assets are included (if known)
    expected_assets = ["afro01", "eyebrow001"]  # Replace with actual expected asset names
    for expected_asset in expected_assets:
        assert expected_asset in asset_names, f"Expected asset {expected_asset} should be in the list of asset names"
