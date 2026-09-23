"""Tests for MPFB_OT_Unload_Library_Proxy_Operator."""

import bpy
import os
from .... import ObjectService, LocationService, HumanService, dynamic_import
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Unload_Library_Proxy_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.unloadlibraryproxy",
    "MPFB_OT_Unload_Library_Proxy_Operator"
)
MPFB_OT_Load_Library_Proxy_Operator = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.operators.loadlibraryproxy",
    "MPFB_OT_Load_Library_Proxy_Operator"
)
ASSET_SETTINGS_PROPERTIES = dynamic_import(
    "mpfb.ui.apply_assets.assetlibrary.assetsettingspanel",
    "ASSET_SETTINGS_PROPERTIES"
)

GeneralObjectProperties = dynamic_import(
    "mpfb.entities.objectproperties",
    "GeneralObjectProperties"
)


def _load_proxy(mask_base_mesh=False):
    """Equip the testdata proxy on the currently active basemesh and return its asset source."""
    testdata = LocationService.get_mpfb_test("testdata")
    socks = os.path.join(testdata, "better_socks_low.mhclo")
    scene = bpy.context.scene
    ASSET_SETTINGS_PROPERTIES.set_value("set_up_rigging", False, entity_reference=scene)
    ASSET_SETTINGS_PROPERTIES.set_value("fit_to_body", True, entity_reference=scene)
    ASSET_SETTINGS_PROPERTIES.set_value("delete_group", False, entity_reference=scene)
    ASSET_SETTINGS_PROPERTIES.set_value("interpolate_weights", False, entity_reference=scene)
    ASSET_SETTINGS_PROPERTIES.set_value("mask_base_mesh", mask_base_mesh, entity_reference=scene)
    load_self = MockOperatorBase(filepath=socks, object_type="Proxymeshes")
    MPFB_OT_Load_Library_Proxy_Operator.hardened_execute(load_self, bpy.context)
    load_self.mock_report.assert_no_errors()


def test_operator_is_registered():
    assert bpy.ops.mpfb.unload_library_proxy is not None
    assert MPFB_OT_Unload_Library_Proxy_Operator is not None


def test_errors_when_no_matching_asset():
    with HumanFixture() as fixture:
        mockself = MockOperatorBase(filepath="nonexistent/dummy.proxy")
        result = MPFB_OT_Unload_Library_Proxy_Operator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_reported('ERROR', 'Could not find asset')


def test_unload_proxy_successfully():
    with HumanFixture() as fixture:
        _load_proxy()

        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Proxymeshes")
        assert proxy is not None, "Proxy must be loaded before unload test"

        source = GeneralObjectProperties.get_value("asset_source", entity_reference=proxy)
        assert source, "Loaded proxy must have an asset_source property"

        ObjectService.activate_blender_object(fixture.basemesh)
        unload_self = MockOperatorBase(filepath=source)
        result = MPFB_OT_Unload_Library_Proxy_Operator.hardened_execute(unload_self, bpy.context)
        assert result == {'FINISHED'}
        unload_self.mock_report.assert_no_errors()

        remaining = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Proxymeshes")
        assert remaining is None, "Proxy should have been removed"


def test_equipped_source_matches_fragment_used_by_panel():
    """The asset source stored on load is what the panel hands back as filepath when unequipping."""
    with HumanFixture() as fixture:
        _load_proxy()
        ObjectService.activate_blender_object(fixture.basemesh)

        equipped = HumanService.get_asset_sources_of_equipped_mesh_assets(fixture.basemesh)
        assert len(equipped) == 1, "The loaded proxy should show up as an equipped mesh asset"

        unload_self = MockOperatorBase(filepath=equipped[0])
        result = MPFB_OT_Unload_Library_Proxy_Operator.hardened_execute(unload_self, bpy.context)
        assert result == {'FINISHED'}
        unload_self.mock_report.assert_no_errors()

        assert HumanService.get_asset_sources_of_equipped_mesh_assets(fixture.basemesh) == []


def test_unload_proxy_removes_base_mesh_mask():
    with HumanFixture() as fixture:
        _load_proxy(mask_base_mesh=True)

        masks = [mod for mod in fixture.basemesh.modifiers if mod.name == "Hide base mesh"]
        assert len(masks) == 1, "Loading with mask_base_mesh should add a mask modifier"

        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(fixture.basemesh, "Proxymeshes")
        source = GeneralObjectProperties.get_value("asset_source", entity_reference=proxy)

        ObjectService.activate_blender_object(fixture.basemesh)
        unload_self = MockOperatorBase(filepath=source)
        MPFB_OT_Unload_Library_Proxy_Operator.hardened_execute(unload_self, bpy.context)
        unload_self.mock_report.assert_no_errors()

        masks = [mod for mod in fixture.basemesh.modifiers if mod.name == "Hide base mesh"]
        assert not masks, "The base mesh mask should have been removed together with the proxy"
