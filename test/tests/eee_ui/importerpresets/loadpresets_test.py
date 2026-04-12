"""Tests for the ImporterPresets LoadPresets operator."""

import bpy
from ... import dynamic_import

MPFB_OT_LoadImporterPresetsOperator = dynamic_import(
    "mpfb.ui.new_human.importerpresets.operators.loadpresets",
    "MPFB_OT_LoadImporterPresetsOperator"
)


def test_load_importer_presets_is_registered():
    assert bpy.ops.mpfb.importerpresets_load_importer_presets is not None
    assert MPFB_OT_LoadImporterPresetsOperator is not None
