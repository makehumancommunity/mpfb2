import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.rigservice import RigService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("sculpt.sculptpanel")

_LOC = os.path.dirname(__file__)
SCULPT_PROPERTIES_DIR = os.path.join(_LOC, "properties")
SCULPT_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SCULPT_PROPERTIES_DIR, prefix="SCL_")

class MPFB_PT_SculptPanel(Abstract_Panel):
    bl_label = "Bake for sculpt"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        props = [
            "delete_helpers",
            "remove_delete",
            "delete_proxies",
            #"normal_material",
            #"setup_multires",
            "enter_sculpt"
            ]

        SCULPT_PROPERTIES.draw_properties(scene, layout, props)
        layout.operator("mpfb.setup_sculpt")

        armature_object = context.object


ClassManager.add_class(MPFB_PT_SculptPanel)
