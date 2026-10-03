import os
from .. import dynamic_import
from .. import LocationService

Mhclo = dynamic_import("mpfb.entities.clothes.mhclo", "Mhclo")

_MINIMAL_MHCLO = """# This is a minimal clothes file written by a unit test
basemesh hm08

name unit_test_asset
obj_file unit_test_asset.obj
{material_line}
"""


def _write_minimal_mhclo(dest_dir, material_line):
    """Write a minimal mhclo (metadata only, no vertex data) and return its path."""
    path = os.path.join(str(dest_dir), "unit_test_asset.mhclo")
    with open(path, "w", encoding="utf8") as handle:
        handle.write(_MINIMAL_MHCLO.format(material_line=material_line))
    return path


def test_mhclo_entity_exists():
    """Mhclo -- a fresh instance has neither a material nor a missing material"""
    assert Mhclo
    mhclo = Mhclo()
    assert mhclo is not None
    assert mhclo.material is None
    # Must be set in __init__ rather than only in load(), since ClothesService builds Mhclo
    # objects which are never loaded from a file
    assert mhclo.missing_material is None


def test_load_sets_material_when_mhmat_exists():
    """Mhclo.load() -- an existing material file is resolved to an absolute path"""
    testdata = LocationService.get_mpfb_test("testdata")
    mhclo_file = os.path.join(testdata, "better_socks_low.mhclo")
    assert os.path.exists(mhclo_file)
    mhclo = Mhclo()
    mhclo.load(mhclo_file)
    assert mhclo.material is not None
    assert str(mhclo.material).endswith("better_socks_low.mhmat")
    assert os.path.exists(mhclo.material)
    assert mhclo.missing_material is None
    # Guard against the material check breaking the rest of the parsing
    assert mhclo.obj_file is not None
    assert mhclo.verts


def test_load_with_missing_mhmat_leaves_material_unset(tmp_path):
    """Mhclo.load() -- a non-existent material file is recorded rather than raising"""
    mhclo_file = _write_minimal_mhclo(tmp_path, "material no_such_material.mhmat")
    mhclo = Mhclo()
    mhclo.load(mhclo_file)
    assert mhclo.material is None
    assert mhclo.missing_material == os.path.join(os.path.realpath(str(tmp_path)), "no_such_material.mhmat")
    # The rest of the metadata should still have been parsed
    assert mhclo.name == "unit_test_asset"


def test_load_without_material_line(tmp_path):
    """Mhclo.load() -- no material line at all is distinguishable from a broken reference"""
    mhclo_file = _write_minimal_mhclo(tmp_path, "")
    mhclo = Mhclo()
    mhclo.load(mhclo_file)
    assert mhclo.material is None
    assert mhclo.missing_material is None


def test_load_only_metadata_detects_missing_mhmat(tmp_path):
    """Mhclo.load() -- a non-existent material file is also detected for metadata only loads"""
    mhclo_file = _write_minimal_mhclo(tmp_path, "material no_such_material.mhmat")
    mhclo = Mhclo()
    mhclo.load(mhclo_file, only_metadata=True)
    assert mhclo.material is None
    assert mhclo.missing_material == os.path.join(os.path.realpath(str(tmp_path)), "no_such_material.mhmat")
