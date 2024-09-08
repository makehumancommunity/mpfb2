import bpy, os

from .. import AssetService
from .. import LocationService


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


def test_list_mhclo_assets():
    mhclo_assets = AssetService.list_mhclo_assets()
    assert mhclo_assets, "The list of mhclo assets should not be empty"
    assert len(mhclo_assets), "The list of mhclo assets should not be empty"


def test_find_asset_absolute_path():
    path_fragment = "shoes01/shoes01.mhclo"
    absolute_path = AssetService.find_asset_absolute_path(path_fragment)

    assert absolute_path is not None, "The absolute path should not be None"
    assert os.path.isabs(absolute_path), "The path should be an absolute path"
    assert os.path.exists(absolute_path), f"The path {absolute_path} should exist"


def test_asset_lists():
    AssetService.update_all_asset_lists()  # Largely to make sure it does not crash
    alist = AssetService.get_asset_list()
    assert alist, "The asset list should not be empty"
    assert len(alist) > 0, "The asset list should not be empty"

