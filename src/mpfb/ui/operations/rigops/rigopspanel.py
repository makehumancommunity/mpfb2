# Part of the legacy "convert to rigify" workflow. This workflow is discouraged
# in new projects; it remains supported only because it is the only viable
# rigify path for characters imported from MakeHuman. For new characters, use
# the modern workflow on the Rigging panel (Add rigify metarig + Generate).

"""UI for the legacy "convert to rigify" workflow, hosted under Operations."""

from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import UiService
from ....services import SceneConfigSet
from ....services import SystemService
from ...abstractpanel import Abstract_Panel
import bpy, os

_LOG = LogService.get_logger("ui.rigopspanel")

_LOC = os.path.dirname(__file__)
RIGIFY_PROPERTIES_DIR = os.path.join(_LOC, "properties")
RIGIFY_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(RIGIFY_PROPERTIES_DIR, prefix="RF_")

class MPFB_PT_Rig_Operations_Panel(Abstract_Panel):
    """The rig operations panel, hosting the legacy convert-to-rigify workflow."""

    bl_label = "Rig operations"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        if ObjectService.object_is_skeleton(context.active_object):
            scene = context.scene
            if not SystemService.check_for_rigify():
                layout.label(text="Rigify is not enabled")
            else:
                layout.label(text="Legacy work flow.", icon="INFO")
                RIGIFY_PROPERTIES.draw_properties(scene, layout, ["name", "produce", "meta_rig_action"])
                layout.operator("mpfb.convert_to_rigify")

ClassManager.add_class(MPFB_PT_Rig_Operations_Panel)
