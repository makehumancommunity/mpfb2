"""Tests for assetlibrary panel and scene-property registration."""

import bpy
from ... import dynamic_import

ASSET_SETTINGS_PROPERTIES = dynamic_import("mpfb.ui.assetlibrary.assetsettingspanel", "ASSET_SETTINGS_PROPERTIES")
ALTMAT_PROPERTIES = dynamic_import("mpfb.ui.assetlibrary.alternativematerialpanel", "ALTMAT_PROPERTIES")


def test_asset_settings_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_Asset_Settings_Panel')


def test_alternative_material_panel_is_registered():
    assert hasattr(bpy.types, 'MPFB_PT_Alternative_Material_Panel')


def test_asset_settings_properties_are_registered():
    assert ASSET_SETTINGS_PROPERTIES is not None
    assert hasattr(bpy.types.Scene, 'MPFB_ASLS_fit_to_body')
    assert hasattr(bpy.types.Scene, 'MPFB_ASLS_set_up_rigging')
    assert hasattr(bpy.types.Scene, 'MPFB_ASLS_skin_type')
    assert hasattr(bpy.types.Scene, 'MPFB_ASLS_mask_base_mesh')
    assert hasattr(bpy.types.Scene, 'MPFB_ASLS_delete_group')


def test_altmat_properties_are_registered():
    assert ALTMAT_PROPERTIES is not None
    assert hasattr(bpy.types.Scene, 'MPFB_ALTM_available_materials')
