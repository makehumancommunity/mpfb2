"""Tests for the Standard Rig panel and its scene-property registration."""

import bpy
import pytest
from .... import dynamic_import, HumanService, ObjectService, RigService, SystemService
from ..._helpers import HumanFixture, HumanWithRigFixture

STANDARD_RIG_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "STANDARD_RIG_PROPERTIES"
)
SETUP_HELPERS_PROPERTIES = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "SETUP_HELPERS_PROPERTIES"
)
MPFB_PT_Standard_Rig_Panel = dynamic_import(
    "mpfb.ui.rigging.standardrig.standardrigpanel", "MPFB_PT_Standard_Rig_Panel"
)


def test_standard_rig_panel_is_registered():
    assert hasattr(bpy.types, "MPFB_PT_Standard_Rig_Panel")
    assert MPFB_PT_Standard_Rig_Panel is not None


def test_standard_rig_properties_not_none():
    assert STANDARD_RIG_PROPERTIES is not None
    assert SETUP_HELPERS_PROPERTIES is not None


def test_standard_rig_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_ADR_standard_rig")
    assert hasattr(bpy.types.Scene, "MPFB_ADR_import_weights")


def test_rig_helpers_scene_properties_are_registered():
    assert hasattr(bpy.types.Scene, "MPFB_SIK_arm_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_leg_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_finger_helpers_type")
    assert hasattr(bpy.types.Scene, "MPFB_SIK_eye_ik")


# The panel's gate in MPFB_PT_Standard_Rig_Panel.draw() is:
#   if rig_type in ("default", "default_no_toes"): _draw_helpers(...)
# These tests verify that the rig-identification values produced by the
# fixtures match (or fail to match) that gate. Constructing a real bpy panel
# instance from Python is not supported (bpy_struct.__new__ rejects it), so we
# pin the contract at the identify_rig level instead.


def test_identify_rig_default_matches_helpers_gate():
    """The default-rig fixture must identify as a value the helpers gate accepts."""
    with HumanWithRigFixture() as fixture:
        rig_type = RigService.identify_rig(fixture.rig)
        assert rig_type in ("default", "default_no_toes"), \
            f"HumanWithRigFixture expected to produce a default rig, got {rig_type}"


def test_identify_rig_generated_rigify_excluded_from_helpers_gate():
    """A generated rigify rig must NOT identify as a value the helpers gate accepts."""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")
    with HumanFixture() as fixture:
        meta_rig = HumanService.add_builtin_rig(fixture.basemesh, "rigify.human")
        assert meta_rig is not None
        generated = RigService.generate_rigify_rig(meta_rig, meta_rig_action="delete")
        assert generated is not None
        rig_type = RigService.identify_rig(generated)
        assert rig_type not in ("default", "default_no_toes"), \
            f"Generated rigify must not match the default-rig helpers gate, got {rig_type}"
        assert rig_type.startswith("rigify_generated."), \
            f"Expected rigify_generated.* identification, got {rig_type}"


def test_identify_rig_rigify_metarig_excluded_from_helpers_gate():
    """A rigify meta rig must NOT identify as a value the helpers gate accepts."""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")
    with HumanFixture() as fixture:
        meta_rig = HumanService.add_builtin_rig(fixture.basemesh, "rigify.human")
        assert meta_rig is not None
        rig_type = RigService.identify_rig(meta_rig)
        assert rig_type not in ("default", "default_no_toes"), \
            f"Rigify meta rig must not match the default-rig helpers gate, got {rig_type}"
        assert rig_type.startswith("rigify."), \
            f"Expected rigify.* identification, got {rig_type}"
