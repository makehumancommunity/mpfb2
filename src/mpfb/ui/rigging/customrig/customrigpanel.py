"""Custom rig sub-panel: add a rig the user built or imported (e.g. via MakeRig)."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ....services import ObjectService
from ....services import SceneConfigSet
from ...abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("customrig.customrigpanel")


def _populate_custom_rigs(self, context):
    from ....services import AssetService  # pylint: disable=C0415
    return AssetService.get_custom_rigs_enum_items()


_CUSTOM_RIG_PROP = {
    "type": "enum",
    "name": "custom_rig",
    "description": "Select a custom rig from user data",
    "label": "Custom rig",
    "default": None
}

_IMPORT_WEIGHTS_CUSTOM_PROP = {
    "type": "boolean",
    "name": "import_weights_custom",
    "description": "Also import weights (if available) and set up the corresponding vertex groups",
    "label": "Import weights",
    "default": True
}

CUSTOM_RIG_PROPERTIES = SceneConfigSet([], prefix="ADR_")
CUSTOM_RIG_PROPERTIES.add_property(_CUSTOM_RIG_PROP, _populate_custom_rigs)
CUSTOM_RIG_PROPERTIES.add_property(_IMPORT_WEIGHTS_CUSTOM_PROP)


class MPFB_PT_Custom_Rig_Panel(Abstract_Panel):
    """Add a custom rig from the user library (MakeRig output or third-party)."""

    bl_label = "Custom rig"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    def _add_custom_rig(self, scene, layout):
        from ....services import AssetService  # pylint: disable=C0415
        box = self.create_box(layout, "Add custom rig")
        box.label(text="For rigs you built yourself")
        box.label(text="or imported from elsewhere.")
        if not AssetService.get_custom_rigs():
            box.label(text="No custom rigs found in user data")
            box.label(text="Use MakeRig to create and save a rig to library")
            return
        CUSTOM_RIG_PROPERTIES.draw_properties(scene, box, ["custom_rig", "import_weights_custom"])
        box.operator('mpfb.add_custom_rig')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if context.active_object is None:
            _LOG.debug("There is no active object")
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if armature_object:
            layout.label(text="Not applicable for the current state.")
            return

        self._add_custom_rig(scene, layout)


ClassManager.add_class(MPFB_PT_Custom_Rig_Panel)
