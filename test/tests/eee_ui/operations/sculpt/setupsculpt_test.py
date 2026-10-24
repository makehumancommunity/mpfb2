"""Tests for the Sculpt Setup Sculpt operator."""

from types import SimpleNamespace

import bpy
from .... import dynamic_import, ObjectService
from ..._helpers import MockOperatorBase, HumanFixture

MPFB_OT_Setup_Sculpt_Operator = dynamic_import(
    "mpfb.ui.operations.sculpt.operators.setupsculpt",
    "MPFB_OT_Setup_Sculpt_Operator"
)
SCULPT_PROPERTIES = dynamic_import("mpfb.ui.operations.sculpt.sculptpanel", "SCULPT_PROPERTIES")


def test_setup_sculpt_is_registered():
    assert bpy.ops.mpfb.setup_sculpt is not None
    assert MPFB_OT_Setup_Sculpt_Operator is not None


def test_setup_sculpt_poll_false_no_active_object():
    ObjectService.deselect_and_deactivate_all()
    assert not MPFB_OT_Setup_Sculpt_Operator.poll(bpy.context)


def test_setup_sculpt_poll_true_with_basemesh():
    with HumanFixture() as fixture:
        assert MPFB_OT_Setup_Sculpt_Operator.poll(bpy.context)


def test_setup_sculpt_executes_with_basemesh_origin_strategy():
    with HumanFixture() as fixture:
        # Use ORIGIN strategy — safest: no copies are made, no armature needed
        SCULPT_PROPERTIES.set_value("sculpt_strategy", "ORIGIN", entity_reference=bpy.context.scene)
        # Operator uses self._handle_bm() etc — requires real operator instance via bpy.ops
        result = bpy.ops.mpfb.setup_sculpt()
        assert result == {'FINISHED'}


def test_set_if_available_prefers_the_first_existing_path():
    scene = SimpleNamespace(render=SimpleNamespace(bake=SimpleNamespace(use_multires=True), use_bake_multires=True))
    assert MPFB_OT_Setup_Sculpt_Operator._set_if_available(
        scene, ["render.bake.use_multires", "render.use_bake_multires"], False)
    assert scene.render.bake.use_multires is False
    # The legacy name must be left alone once the current one has been set
    assert scene.render.use_bake_multires is True


def test_set_if_available_falls_back_to_the_legacy_path():
    scene = SimpleNamespace(render=SimpleNamespace(use_bake_multires=True))
    assert MPFB_OT_Setup_Sculpt_Operator._set_if_available(
        scene, ["render.bake.use_multires", "render.use_bake_multires"], False)
    assert scene.render.use_bake_multires is False


def test_set_if_available_is_silent_when_no_path_exists():
    scene = SimpleNamespace(render=SimpleNamespace())
    assert not MPFB_OT_Setup_Sculpt_Operator._set_if_available(
        scene, ["render.bake.use_multires", "render.use_bake_multires"], False)
    assert not hasattr(scene.render, "use_bake_multires")


def test_set_if_available_is_silent_when_an_intermediate_object_is_missing():
    scene = SimpleNamespace()
    assert not MPFB_OT_Setup_Sculpt_Operator._set_if_available(scene, ["cycles.bake_type"], 'NORMAL')


def test_adjust_bake_settings_survives_a_scene_without_any_bake_properties():
    MPFB_OT_Setup_Sculpt_Operator._adjust_bake_settings(
        SimpleNamespace(render=SimpleNamespace(bake=SimpleNamespace())))


def test_setup_sculpt_adjusts_bake_settings_with_destcopy_strategy():
    with HumanFixture() as fixture:
        scene = bpy.context.scene
        SCULPT_PROPERTIES.set_value("sculpt_strategy", "DESTCOPY", entity_reference=scene)
        SCULPT_PROPERTIES.set_value("adjust_settings", True, entity_reference=scene)

        result = bpy.ops.mpfb.setup_sculpt()
        assert result == {'FINISHED'}

        assert scene.render.bake.use_selected_to_active is True
        assert round(scene.render.bake.cage_extrusion, 5) == 0.01
        assert round(scene.render.bake.max_ray_distance, 5) == 0.1

        if hasattr(scene, "cycles"):
            assert scene.cycles.bake_type == 'NORMAL'
            assert scene.cycles.samples == 8
            assert scene.cycles.use_denoising is False

        # The property which caused the reported crash. It only exists on recent blender versions.
        if hasattr(scene.render.bake, "use_multires"):
            assert scene.render.bake.use_multires is False
        else:
            assert scene.render.use_bake_multires is False

        # The operator ends in sculpt mode, which would leak into following tests
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        SCULPT_PROPERTIES.set_value("sculpt_strategy", "SOURCEDESTCOPY", entity_reference=scene)
