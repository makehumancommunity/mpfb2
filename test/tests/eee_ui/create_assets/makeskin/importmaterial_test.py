"""Tests for the MakeSkin ImportMaterial operator."""

import bpy
from .... import ObjectService, dynamic_import
from ..._helpers import HumanFixture

MPFB_OT_ImportMaterialOperator = dynamic_import("mpfb.ui.create_assets.makeskin.operators", "MPFB_OT_ImportMaterialOperator")


def test_import_material_is_registered():
    assert bpy.ops.mpfb.import_makeskin_material is not None
    assert MPFB_OT_ImportMaterialOperator is not None


def test_import_material_poll_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_ImportMaterialOperator.poll(bpy.context)
