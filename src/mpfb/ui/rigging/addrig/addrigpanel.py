"""File containing main UI for modeling humans"""

import os
from .... import ClassManager
from ....services import LogService
from ....services import RigService
from ....services import UiService
from ....services import ObjectService
from ....services import SceneConfigSet
from ....services import SystemService
from ...abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("addrig.addrigpanel")

_LOC = os.path.dirname(__file__)
ADD_RIG_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ADD_RIG_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ADD_RIG_PROPERTIES_DIR, prefix="ADR_")


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

ADD_RIG_PROPERTIES.add_property(_CUSTOM_RIG_PROP, _populate_custom_rigs)
ADD_RIG_PROPERTIES.add_property(_IMPORT_WEIGHTS_CUSTOM_PROP)

class MPFB_PT_Add_Rig_Panel(Abstract_Panel):
    """Functionality for adding/setting rig"""

    bl_label = "Add rig"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"

    def _standard_rig(self, scene, layout):
        box = self.create_box(layout, "Add standard rig")
        props = [
            "standard_rig",
            "import_weights"
            ]
        ADD_RIG_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.add_standard_rig')

    def _add_rigify_rig(self, scene, layout):
        box = self.create_box(layout, "Add rigify rig")
        if not SystemService.check_for_rigify():
            box.label(text="Rigify is not enabled")
        else:
            props = [
                "rigify_rig",
                "import_weights_rigify"
                ]
            ADD_RIG_PROPERTIES.draw_properties(scene, box, props)
            box.operator('mpfb.add_rigify_rig')

    def _generate_rigify_rig(self, scene, layout):
        box = self.create_box(layout, "Generate rigify rig")
        if not SystemService.check_for_rigify():
            box.label(text="Rigify is not enabled")
        else:
            props = [
                "name",
                "delete_after_generate",
                ]
            ADD_RIG_PROPERTIES.draw_properties(scene, box, props)
            box.operator('mpfb.generate_rigify_rig')

    def _add_custom_rig(self, scene, layout):
        from ....services import AssetService  # pylint: disable=C0415
        box = self.create_box(layout, "Add custom rig")
        if not AssetService.get_custom_rigs():
            box.label(text="No custom rigs found in user data")
            box.label(text="Use MakeRig to create and save a rig to library")
        else:
            ADD_RIG_PROPERTIES.draw_properties(scene, box, ["custom_rig", "import_weights_custom"])
            box.operator('mpfb.add_custom_rig')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if context.active_object is None:
            _LOG.debug("There is no active object")
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        _LOG.debug("Armature object", armature_object)

        if not armature_object:
            self._standard_rig(scene, layout)
            self._add_rigify_rig(scene, layout)
            self._add_custom_rig(scene, layout)
        elif ObjectService.object_is_any_skeleton(context.active_object):
            rig_type = RigService.identify_rig(context.active_object)
            if rig_type.startswith("rigify."):
                self._generate_rigify_rig(scene, layout)

ClassManager.add_class(MPFB_PT_Add_Rig_Panel)
