"""File containing main UI for the expressions library panel."""

from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import UiService
from ....services.faceservice import FaceService
from ...abstractpanel import Abstract_Panel
from . import ExpressionsLibraryProperties, _EXPRESSION_PROP_MAP

_LOG = LogService.get_logger("useexpression.useexpressionpanel")


class MPFB_PT_ExpressionsLibrary_Panel(Abstract_Panel):
    """Apply saved expressions on a character via a flat list of [0,1] sliders."""

    bl_label = "Expressions library"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Assets_Panel"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        return ObjectService.find_object_of_type_amongst_nearest_relatives(
            context.active_object, "Basemesh"
        ) is not None

    def _draw_pack_hint(self, layout):
        box = self._create_box(layout, "Asset pack required", "ERROR")
        box.label(text="The faceunits01 asset pack is not installed.")
        box.label(text="Expressions cannot be applied until it is installed.")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        ExpressionsLibraryProperties.draw_properties(scene, layout, ["auto_refit", "only_show_applied", "filter"])

        if not FaceService.is_faceunits01_installed():
            self._draw_pack_hint(layout)
            return

        only_applied = ExpressionsLibraryProperties.get_value("only_show_applied", entity_reference=scene)
        filter_text = ExpressionsLibraryProperties.get_value("filter", entity_reference=scene) or ""
        filter_lc = str(filter_text).lower().strip()

        ordered = sorted(_EXPRESSION_PROP_MAP.items(), key=lambda kv: kv[1]["label"].lower())

        for identifier, entry in ordered:
            label = entry["label"]
            if filter_lc and filter_lc not in label.lower():
                continue
            try:
                weight = float(getattr(scene, identifier, 0.0))
            except (TypeError, ValueError):
                weight = 0.0
            if only_applied and weight <= 0.001:
                continue
            box = layout.box()
            box.label(text=label)
            box.alert = weight > 0.001
            box.prop(scene, identifier, text="Value:")


ClassManager.add_class(MPFB_PT_ExpressionsLibrary_Panel)
