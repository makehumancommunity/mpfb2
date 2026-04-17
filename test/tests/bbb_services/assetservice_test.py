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

def test_bad_mac_pack():
    """Test AssetService.check_asset_pack_zip for detecting zip files corrupted by mac"""
    testdata = LocationService.get_mpfb_test("testdata")
    mac_corrupted_zip = os.path.abspath(os.path.join(testdata, "packs", "mac_corrupted.zip"))
    assert os.path.exists(mac_corrupted_zip), f"The path {mac_corrupted_zip} should exist"
    assert AssetService.check_asset_pack_zip(mac_corrupted_zip) == "MACOS", "A corrupted zip file should be detected"

def test_too_deep_pack():
    """Test AssetService.check_asset_pack_zip for detecting zip files with one dir level too many"""
    testdata = LocationService.get_mpfb_test("testdata")
    too_deep_cc0 = os.path.abspath(os.path.join(testdata, "packs", "too_deep_cc0.zip"))
    assert os.path.exists(too_deep_cc0), f"The path {too_deep_cc0} should exist"
    too_deep_ccby = os.path.abspath(os.path.join(testdata, "packs", "too_deep_ccby.zip"))
    assert os.path.exists(too_deep_ccby), f"The path {too_deep_ccby} should exist"
    assert AssetService.check_asset_pack_zip(too_deep_cc0) == "STRUCTURE", "A zip with too deep structure (cc0) should be detected"
    assert AssetService.check_asset_pack_zip(too_deep_ccby) == "STRUCTURE", "A zip with too deep structure (cc0) should be detected"

def test_no_packs_pack():
    """Test AssetService.check_asset_pack_zip for detecting zip files with no packs directory"""
    testdata = LocationService.get_mpfb_test("testdata")
    no_packs = os.path.abspath(os.path.join(testdata, "packs", "no_packs.zip"))
    assert os.path.exists(no_packs), f"The path {no_packs} should exist"
    assert AssetService.check_asset_pack_zip(no_packs) == "NO_PACKS", "A zip file with no packs dir should be detected"

def test_valid_pack():
    """Test AssetService.check_asset_pack_zip returns None for a valid zip"""
    testdata = LocationService.get_mpfb_test("testdata")
    valid_zip = os.path.abspath(os.path.join(testdata, "packs", "valid.zip"))
    assert os.path.exists(valid_zip), f"The path {valid_zip} should exist"
    assert AssetService.check_asset_pack_zip(valid_zip) is None, "A valid zip should return None"

def test_fix_too_deep_pack():
    """Test AssetService.fix_and_extract_asset_pack_zip handles a one-level-too-deep zip"""
    import tempfile
    testdata = LocationService.get_mpfb_test("testdata")
    too_deep_cc0 = os.path.abspath(os.path.join(testdata, "packs", "too_deep_cc0.zip"))
    with tempfile.TemporaryDirectory() as tmp:
        result = AssetService.fix_and_extract_asset_pack_zip(too_deep_cc0, tmp)
        assert result is None, f"fix_and_extract should succeed, got: {result}"
        assert os.path.isdir(os.path.join(tmp, "packs")), "packs/ should exist in target after fix"

def test_fix_mac_corrupted_pack():
    """Test AssetService.fix_and_extract_asset_pack_zip handles a Safari-repackaged zip"""
    import tempfile
    testdata = LocationService.get_mpfb_test("testdata")
    mac_zip = os.path.abspath(os.path.join(testdata, "packs", "mac_corrupted.zip"))
    with tempfile.TemporaryDirectory() as tmp:
        result = AssetService.fix_and_extract_asset_pack_zip(mac_zip, tmp)
        assert result is None, f"fix_and_extract should succeed on mac zip, got: {result}"
        assert os.path.isdir(os.path.join(tmp, "packs")), "packs/ should exist after fixing mac zip"

def test_fix_no_packs_fails():
    """Test AssetService.fix_and_extract_asset_pack_zip fails gracefully when zip has no packs dir"""
    import tempfile
    testdata = LocationService.get_mpfb_test("testdata")
    no_packs = os.path.abspath(os.path.join(testdata, "packs", "no_packs.zip"))
    with tempfile.TemporaryDirectory() as tmp:
        result = AssetService.fix_and_extract_asset_pack_zip(no_packs, tmp)
        assert result is not None, "fix_and_extract should fail for a zip with no packs dir"

