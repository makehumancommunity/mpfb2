"""Tests for the ImporterPresets SaveNewPresets operator."""

import bpy
from ... import dynamic_import
from .._helpers import MockOperatorBase

MPFB_OT_SaveNewImporterPresetsOperator = dynamic_import(
    "mpfb.ui.new_human.importerpresets.operators.savenewpresets",
    "MPFB_OT_SaveNewImporterPresetsOperator"
)


def test_save_new_importer_presets_is_registered():
    assert bpy.ops.mpfb.importerpresets_save_new_importer_presets is not None
    assert MPFB_OT_SaveNewImporterPresetsOperator is not None


def test_save_new_importer_presets_blank_name_reports_error():
    mock = MockOperatorBase()
    result = MPFB_OT_SaveNewImporterPresetsOperator.hardened_execute(mock, bpy.context)
    assert result == {'FINISHED'}
    mock.mock_report.assert_reported('ERROR', 'name')
