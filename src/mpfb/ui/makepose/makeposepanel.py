"""File containing main UI for makepose"""

import bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.ui.makepose import MakePoseProperties

_LOG = LogService.get_logger("makepose.makeposepanel")

class MPFB_PT_MakePose_Panel(Abstract_Panel):
    """MakePose main panel."""

    bl_label = "MakePose"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

#===============================================================================
#     def _initialize_pose(self, blender_object, layout):
#         box = self._create_box(layout, "Initialize", "TOOL_SETTINGS")
#         props = ["name"]
#         MakePoseObjectProperties.draw_properties(blender_object, box, props)
#         box.operator('mpfb.create_makepose_pose')
#         box.operator('mpfb.import_makepose_pose')
#
#     def _save_pose(self, scene, layout):
#         box = self._create_box(layout, "Save pose", "TOOL_SETTINGS")
#         box.operator('mpfb.write_makepose_pose')
#
#     def _symmetrize_pose(self, scene, layout):
#         box = self._create_box(layout, "Symmetrize", "TOOL_SETTINGS")
#         box.operator('mpfb.symmetrize_makepose_left')
#         box.operator('mpfb.symmetrize_makepose_right')
#
#     def _debug_pose(self, scene, layout):
#         box = self._create_box(layout, "Debug", "TOOL_SETTINGS")
#         box.operator('mpfb.print_makepose_pose')
#===============================================================================

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object
        if blender_object is None:
            return

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        if object_type != "Skeleton":
            return

        props = ["name", "pose_type", "roottrans", "iktrans", "fktrans", "overwrite"]
        MakePoseProperties.draw_properties(scene, layout, props)
        layout.operator('mpfb.save_pose')



ClassManager.add_class(MPFB_PT_MakePose_Panel)


