"""Operator for copying the selected detail section's settings to every section."""

from .....services import LogService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, DETAIL_SECTIONS
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.applydetailtoall")

# The five per-section settings copied by this operator (the suffix of each detail property).
_DETAIL_SETTINGS = ["min", "max", "include", "exclude", "deviation"]


class MPFB_OT_Randomize_Detail_Apply_All_Operator(MpfbOperator):
    """Copy the currently shown section's detail settings to every section"""
    bl_idname = "mpfb.randomize_detail_apply_all"
    bl_label = "Apply to all sections"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()
        scene = context.scene

        source_section = RANDOMIZE_PROPERTIES.get_value("details_section", entity_reference=scene)
        if not source_section:
            return {'FINISHED'}

        # Read the shown section's settings, then write them to every section (including the shown
        # one, which is a harmless no-op). Sections can afterwards be re-adjusted individually.
        values = {}
        for setting in _DETAIL_SETTINGS:
            values[setting] = RANDOMIZE_PROPERTIES.get_value("detail_" + source_section + "_" + setting, entity_reference=scene)

        for section_name in DETAIL_SECTIONS:
            for setting in _DETAIL_SETTINGS:
                RANDOMIZE_PROPERTIES.set_value("detail_" + section_name + "_" + setting, values[setting], entity_reference=scene)

        self.report({'INFO'}, "Copied the " + str(source_section) + " settings to all sections")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Randomize_Detail_Apply_All_Operator)
