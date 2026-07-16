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


def test_alternative_materials_for_asset():
    materials = AssetService.alternative_materials_for_asset("low-poly/low-poly.mhclo", "eyes")

    assert materials, "The eyes should have alternative materials"
    for material in materials:
        assert os.path.isabs(material), f"The path {material} should be an absolute path"
        assert os.path.exists(material), f"The path {material} should exist"

    basenames = [os.path.basename(material) for material in materials]
    assert "brown.mhmat" in basenames, "The bundled brown eyes material should be listed"
    assert len(basenames) == len(set(basenames)), "The same material should not be listed twice"
    assert materials == sorted(materials), "The materials should be sorted"


def test_alternative_materials_for_nonexisting_asset():
    """A fragment which cannot be resolved should give an empty list rather than crash."""
    assert AssetService.alternative_materials_for_asset("no_such_asset/no_such_asset.mhclo", "clothes") == []
    assert AssetService.alternative_materials_for_asset(None, "clothes") == []
    assert AssetService.alternative_materials_for_asset("", "clothes") == []


def test_get_placeholder_thumbnail():
    # Note that icon_id is 0 when running headless, as blender only allocates icon ids when there is a UI
    placeholder = AssetService.get_placeholder_thumbnail()
    assert placeholder is not None, "The bundled placeholder thumbnail should be loadable"
    assert tuple(placeholder.image_size) == (128, 128), "The placeholder image should have been loaded"
    assert AssetService.get_placeholder_thumbnail() is placeholder, "The placeholder should only be loaded once"


def test_alternative_material_tiles_have_thumbs():
    """The eyes materials all have a thumb of their own next to the mhmat."""
    tiles = AssetService.alternative_material_tiles_for_asset("low-poly/low-poly.mhclo", "eyes")

    assert tiles, "The eyes should have alternative material tiles"

    by_name = {tile["name_without_ext"]: tile for tile in tiles}
    assert "brown" in by_name, "The bundled brown eyes material should have a tile"

    brown = by_name["brown"]
    assert brown["label"] == "Brown", "The label should be a capitalized version of the name"
    assert brown["fragment"] == "materials/brown.mhmat", "The fragment should be relative to the asset root"
    assert brown["thumb_path"] is not None, "The brown material has a thumb of its own"
    assert os.path.exists(brown["thumb_path"]), "The thumb path should exist"
    assert brown["thumb"] is not None, "The thumb should have been loaded"


def test_alternative_material_tiles_fall_back_to_placeholder():
    """The fedora mhmat has no thumb of its own, as the thumb is named after the mhclo."""
    tiles = AssetService.alternative_material_tiles_for_asset("fedora01/fedora01.mhclo", "clothes")

    assert tiles, "The fedora should have alternative material tiles"

    by_name = {tile["name_without_ext"]: tile for tile in tiles}
    assert "fedora" in by_name, "The fedora material should have a tile"

    fedora = by_name["fedora"]
    assert fedora["thumb_path"] is None, "The fedora material does not have a thumb of its own"
    assert fedora["thumb"] is not None, "A material without a thumb should still get the placeholder"
    assert fedora["thumb"] == AssetService.get_placeholder_thumbnail(), "The placeholder should have been used"


def test_alternative_material_cache_is_invalidated():
    AssetService.alternative_materials_for_asset("low-poly/low-poly.mhclo", "eyes")
    AssetService.alternative_material_tiles_for_asset("low-poly/low-poly.mhclo", "eyes")

    AssetService.invalidate_alternative_materials_cache()  # Largely to make sure it does not crash

    materials = AssetService.alternative_materials_for_asset("low-poly/low-poly.mhclo", "eyes")
    assert materials, "The materials should be rescanned after the cache was invalidated"


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

