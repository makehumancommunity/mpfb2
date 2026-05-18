"""Rigify rig sub-panel: add meta rig and generate rigify rig (recommended workflow)."""

import os
from .... import ClassManager
from ....services import LogService
from ....services import RigService
from ....services import UiService
from ....services import ObjectService
from ....services import SceneConfigSet
from ....services import SystemService
from ...abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("rigifyrig.rigifyrigpanel")

_LOC = os.path.dirname(__file__)
RIGIFY_RIG_PROPERTIES_DIR = os.path.join(_LOC, "properties")
RIGIFY_RIG_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(RIGIFY_RIG_PROPERTIES_DIR, prefix="ADR_")


class MPFB_PT_Rigify_Rig_Panel(Abstract_Panel):
    """Add a rigify meta rig and then generate the final rigify rig from it."""

    bl_label = "Rigify rig"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"
    bl_options = set()

    def _rigify_not_enabled(self, layout):
        box = self.create_box(layout, "Rigify not enabled")
        box.label(text="Enable the Rigify addon in")
        box.label(text="Blender preferences > Add-ons")
        box.label(text="to use this workflow.")

    def _add_rigify_rig(self, scene, layout):
        box = self.create_box(layout, "Add rigify meta rig")
        box.label(text="Recommended workflow for")
        box.label(text="rigify-based characters.")
        props = [
            "rigify_rig",
            "import_weights_rigify",
            "name",
            "auto_generate",
            ]
        RIGIFY_RIG_PROPERTIES.draw_properties(scene, box, props)
        keep_row = box.row()
        keep_row.enabled = bool(RIGIFY_RIG_PROPERTIES.get_value("auto_generate", entity_reference=scene))
        RIGIFY_RIG_PROPERTIES.draw_properties(scene, keep_row, ["keep_meta_rig"])
        box.operator('mpfb.add_rigify_rig')

    def _generate_rigify_rig(self, scene, layout):
        box = self.create_box(layout, "Generate rigify rig")
        props = [
            "name",
            "delete_after_generate",
            ]
        RIGIFY_RIG_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.generate_rigify_rig')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if not SystemService.check_for_rigify():
            self._rigify_not_enabled(layout)
            return

        if context.active_object is None:
            _LOG.debug("There is no active object")
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        _LOG.debug("Armature object", armature_object)

        if not armature_object:
            self._add_rigify_rig(scene, layout)
            return

        if ObjectService.object_is_any_skeleton(context.active_object):
            rig_type = RigService.identify_rig(context.active_object)
            if rig_type and rig_type.startswith("rigify."):
                self._generate_rigify_rig(scene, layout)
                return

        layout.label(text="Not applicable for the current rig.")


ClassManager.add_class(MPFB_PT_Rigify_Rig_Panel)
