"""Tests for the MakeClothes LegacyImport operator."""

import bpy
from .... import dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_LegacyImportOperator = dynamic_import("mpfb.ui.create_assets.makeclothes.operators", "MPFB_OT_LegacyImportOperator")


def test_legacy_import_is_registered():
    assert bpy.ops.mpfb.legacy_makeclothes_import is not None
    assert MPFB_OT_LegacyImportOperator is not None


def test_legacy_import_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_LegacyImportOperator.poll(bpy.context)
