"""This file contains the AI panel."""

from ... import ClassManager
from ...services import LogService
from ...services import UiService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel
import bpy, os

_LOG = LogService.get_logger("ui.aipanel")

_LOC = os.path.dirname(__file__)
AI_PROPERTIES_DIR = os.path.join(_LOC, "properties")
AI_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(AI_PROPERTIES_DIR, prefix="AI_")

class MPFB_PT_Ai_Panel(Abstract_Panel):
    """UI for various AI-related functions."""
    bl_label = "OpenPose"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _visible_bones(self, scene, layout):
        box = self._create_box(layout, "Rig add visible bones")
        props = [
            "bone_size",
            "joint_size"
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.openpose_visible_bones")

    def _visible_bones_scene(self, scene, layout):
        box = self._create_box(layout, "Visible bones scene settings")
        props = [
            "background",
            "view",
            "render",
            "color",
            "hide"
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.openpose_scene_settings")

    def _mode(self, scene, layout):
        box = self._create_box(layout, "JSON Projection mode")
        props = [
            "mode",
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)

    def _parts(self, scene, layout):
        box = self._create_box(layout, "JSON OpenPose structures")
        props = [
            #"bodyformat",
            "hands",
            #"face",
            #"use2d",
            #"use3d"
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)

    def _confidence(self, scene, layout):
        box = self._create_box(layout, "JSON Confidence levels")
        props = [
            "highconfidence",
            "mediumconfidence",
            "lowconfidence",
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)

    def _camera(self, scene, layout):
        box = self._create_box(layout, "JSON Export")
        box.operator("mpfb.save_openpose")

    def _bounds(self, scene, layout):
        box = self._create_box(layout, "JSON Bounding box")
        props = [
            "minx",
            "maxx",
            "minz",
            "maxz"
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)
        box.operator("mpfb.boundingbox")

    def _xz(self, scene, layout):
        box = self._create_box(layout, "JSON Export")
        props = [
            "resx",
            "resy"
            ]
        AI_PROPERTIES.draw_properties(scene, box, props)

        box.operator("mpfb.save_openpose")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene
        mode = AI_PROPERTIES.get_value("mode", entity_reference=scene)

        self._visible_bones(scene, layout)
        self._visible_bones_scene(scene, layout)
        self._mode(scene, layout)
        self._parts(scene, layout)
        self._confidence(scene, layout)
        if mode != "XZ":
            self._camera(scene, layout)
        else:
            self._bounds(scene, layout)
            self._xz(scene, layout)

ClassManager.add_class(MPFB_PT_Ai_Panel)

