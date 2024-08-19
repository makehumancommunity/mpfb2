"""File containing main UI for maketarget"""

import bpy
from mpfb import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import UiService
from ...services import TargetService
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.ui.maketarget import MakeTargetObjectProperties

_LOG = LogService.get_logger("maketarget.maketargetpanel")


class MPFB_PT_MakeTarget_Panel(Abstract_Panel):
    """MakeTarget main panel."""

    bl_label = "MakeTarget"
    bl_category = UiService.get_value("TARGETSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _initialize_target(self, blender_object, layout):
        box = self._create_box(layout, "Initialize", "TOOL_SETTINGS")
        props = ["name"]
        MakeTargetObjectProperties.draw_properties(blender_object, box, props)
        box.operator('mpfb.create_maketarget_target')
        box.operator('mpfb.import_maketarget_target')
        box.operator('mpfb.import_maketarget_ptarget')

    def _save_target(self, scene, layout):
        box = self._create_box(layout, "Save as file", "TOOL_SETTINGS")
        box.operator('mpfb.write_maketarget_target')
        box.operator('mpfb.write_maketarget_ptarget')

        box = self._create_box(layout, "Save to library", "TOOL_SETTINGS")
        box.operator('mpfb.write_library_target')

    def _symmetrize_target(self, scene, layout):
        box = self._create_box(layout, "Symmetrize", "TOOL_SETTINGS")
        box.operator('mpfb.symmetrize_maketarget_left')
        box.operator('mpfb.symmetrize_maketarget_right')

    def _debug_target(self, scene, layout):
        box = self._create_box(layout, "Debug", "TOOL_SETTINGS")
        box.operator('mpfb.print_maketarget_target')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object
        if blender_object is None:
            return

        object_type = ObjectService.get_object_type(blender_object)

        if object_type and not object_type == "Skeleton":
            expected_name = MakeTargetObjectProperties.get_value("name", entity_reference=blender_object)
            if not blender_object.data.shape_keys or not TargetService.has_target(blender_object, expected_name):
                self._initialize_target(blender_object, layout)
            else:
                self._save_target(scene, layout)
                if object_type == "Basemesh":
                    self._symmetrize_target(scene, layout)
                self._debug_target(scene, layout)


ClassManager.add_class(MPFB_PT_MakeTarget_Panel)

