import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("poseops.poseopspanel")

_LOC = os.path.dirname(__file__)
POP_PROPERTIES_DIR = os.path.join(_LOC, "properties")
POP_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(POP_PROPERTIES_DIR, prefix="POP_")

class MPFB_PT_PoseopsPanel(Abstract_Panel):
    bl_label = "Poses"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _apply_pose(self, scene, layout):
        box = self._create_box(layout, "Apply pose")
        box.operator("mpfb.apply_pose")

    def _copy_pose(self, scene, layout):
        box = self._create_box(layout, "Copy pose")
        POP_PROPERTIES.draw_properties(scene, box, ["only_rotation"])
        box.operator("mpfb.copy_pose")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        from mpfb.entities.objectproperties import GeneralObjectProperties

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if objtype != "Skeleton":
            return

        self._apply_pose(scene, layout)
        self._copy_pose(scene, layout)

ClassManager.add_class(MPFB_PT_PoseopsPanel)
