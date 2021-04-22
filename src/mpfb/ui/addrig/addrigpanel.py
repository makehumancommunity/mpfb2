"""File containing main UI for modeling humans"""

import os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("addrig.addrigpanel")

_LOC = os.path.dirname(__file__)
ADD_RIG_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ADD_RIG_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ADD_RIG_PROPERTIES_DIR, prefix="ADR_")

class MPFB_PT_Add_Rig_Panel(Abstract_Panel):
    """Functionality for adding/setting rig"""

    bl_label = "Add rig"
    bl_category = UiService.get_value("MODELCATEGORY")

    def _standard_rig(self, scene, layout):
        box = self.create_box(layout, "Add standard rig")
        props = [
            "standard_rig",
            "import_weights"
            ]
        ADD_RIG_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.add_standard_rig')

    def _rigify_rig(self, scene, layout):
        box = self.create_box(layout, "Add rigify rig")
        props = [
            "import_weights_rigify",
            "generate",
            "delete_after_generate"
            ]
        ADD_RIG_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.add_rigify_rig')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene
        self._standard_rig(scene, layout)
        self._rigify_rig(scene, layout)

ClassManager.add_class(MPFB_PT_Add_Rig_Panel)
