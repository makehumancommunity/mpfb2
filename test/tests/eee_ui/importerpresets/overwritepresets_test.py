"""Tests for the ImporterPresets OverwritePresets operator."""

import bpy
from ... import dynamic_import

MPFB_OT_OverwriteImporterPresetsOperator = dynamic_import(
    "mpfb.ui.importerpresets.operators.overwritepresets",
    "MPFB_OT_OverwriteImporterPresetsOperator"
)


def test_overwrite_importer_presets_is_registered():
    assert bpy.ops.mpfb.importerpresets_overwrite_importer_presets is not None
    assert MPFB_OT_OverwriteImporterPresetsOperator is not None
