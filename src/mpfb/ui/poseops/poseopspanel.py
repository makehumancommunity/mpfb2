import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import SceneConfigSet
from ...services import UiService
from ...services import MaterialService
from ..abstractpanel import Abstract_Panel

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

        objtype = ObjectService.get_object_type(context.object)

        if objtype != "Skeleton":
            return

        self._apply_pose(scene, layout)
        self._copy_pose(scene, layout)

ClassManager.add_class(MPFB_PT_PoseopsPanel)
