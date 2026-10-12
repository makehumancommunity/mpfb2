"""Tests for the MakeUp WriteInk operator."""

import bpy
import os
import json
from .... import dynamic_import, ObjectService, LocationService
from ..._helpers import MockOperatorBase, HumanFixture, BasemeshWithMakeSkinFixture

MPFB_OT_WriteInkOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.writeink", "MPFB_OT_WriteInkOperator")
MPFB_OT_CreateInkOperator = dynamic_import("mpfb.ui.create_assets.makeup.operators.createink", "MPFB_OT_CreateInkOperator")
MAKEUP_PROPERTIES = dynamic_import("mpfb.ui.create_assets.makeup.makeuppanel", "MAKEUP_PROPERTIES")


def test_write_ink_layer_is_registered():
    assert bpy.ops.mpfb.write_ink_layer is not None
    assert MPFB_OT_WriteInkOperator is not None


def test_write_ink_layer_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_WriteInkOperator.poll(bpy.context)


def test_write_ink_layer_poll_true_with_active_mesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_WriteInkOperator.poll(bpy.context)


def test_write_ink_layer_errors_without_ink_layer_name():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("ink_layer_name", "", entity_reference=bpy.context.scene)
        mockself = MockOperatorBase()
        result = MPFB_OT_WriteInkOperator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        mockself.mock_report.assert_reported('ERROR', "ink layer name")


def test_write_ink_layer_errors_not_basemesh():
    with HumanFixture() as fixture:
        MAKEUP_PROPERTIES.set_value("ink_layer_name", "test_ink", entity_reference=bpy.context.scene)
        # The basemesh IS a basemesh, but has no material
        mockself = MockOperatorBase()
        result = MPFB_OT_WriteInkOperator.hardened_execute(mockself, bpy.context)
        assert result == {'CANCELLED'}
        # Should report error about no materials or no MakeSkin material
        assert len(mockself.mock_report.reports) > 0


def test_write_ink_layer_with_full_body_focus(request):
    # Regression test for issue 415: an ink layer using the full body focus (ie the
    # basemesh's default UV map, no specialized UV) must be writable to the library.
    with BasemeshWithMakeSkinFixture() as fixture:
        scene = bpy.context.scene

        # Create an ink layer using the full body focus, including an image to write.
        MAKEUP_PROPERTIES.set_value("focus_name", "NONE", entity_reference=scene)
        MAKEUP_PROPERTIES.set_value("create_ink", True, entity_reference=scene)
        MAKEUP_PROPERTIES.set_value("resolution", "1024", entity_reference=scene)
        create_result = MPFB_OT_CreateInkOperator.hardened_execute(MockOperatorBase(), bpy.context)
        assert create_result == {'FINISHED'}

        ink_name = "issue415_full_body_ink"
        MAKEUP_PROPERTIES.set_value("ink_layer_name", ink_name, entity_reference=scene)
        MAKEUP_PROPERTIES.set_value("layer_number", "1", entity_reference=scene)

        inkpath = LocationService.get_user_data("ink_layers")
        ink_json = os.path.join(inkpath, ink_name + ".json")
        ink_png = os.path.join(inkpath, ink_name + ".png")

        def _cleanup():
            for path in (ink_json, ink_png):
                if os.path.exists(path):
                    os.remove(path)
        request.addfinalizer(_cleanup)

        mockself = MockOperatorBase()
        result = MPFB_OT_WriteInkOperator.hardened_execute(mockself, bpy.context)
        assert result == {'FINISHED'}
        mockself.mock_report.assert_no_errors()

        assert os.path.exists(ink_json)
        assert os.path.exists(ink_png)

        with open(ink_json, "r", encoding="utf-8") as json_file:
            ink_info = json.load(json_file)
        # An empty focus signals the full body focus, matching what load_ink_layer expects.
        assert ink_info["focus"] == ""
