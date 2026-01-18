"""UI for creating an export copy.

An "export copy" is a deep copy of a character, including the basemesh and any rig and child meshes connected to it.
Various operations can be applied to this, to make it more palatable for applications other than Blender."""

import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import SceneConfigSet
from ...services import UiService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("matops.exportopspanel")

_LOC = os.path.dirname(__file__)
EXPORTOPS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
EXPORTOPS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(EXPORTOPS_PROPERTIES_DIR, prefix="EXPO_")


class MPFB_PT_ExportOpsPanel(Abstract_Panel):
    """UI for creating an export copy."""

    bl_label = "Export copy"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _basemesh(self, scene, layout):
        box = self.create_box(layout, "Basemesh")
        EXPORTOPS_PROPERTIES.draw_properties(scene, box, [
            "mask_modifiers",
            "subdiv_modifiers",
            "bake_shapekeys",
            "delete_helpers",
            "remove_basemesh"
            ])
        #box.operator("mpfb.remove_makeup")

    def _visemes(self, scene, layout):
        box = self.create_box(layout, "Visemes and faceunits")
        EXPORTOPS_PROPERTIES.draw_properties(scene, box, [
            "visemes_meta",
            "visemes_microsoft",
            "faceunits_arkit",
            "interpolate"
            ])
        #box.operator("mpfb.remove_makeup")

    def _create(self, scene, layout):
        box = self.create_box(layout, "Create copy")
        EXPORTOPS_PROPERTIES.draw_properties(scene, box, [
        #    "visemes_meta",
        #    "visemes_microsoft",
        #    "faceunits_arkit",
            "suffix",
            "collection"
            ])
        box.operator("mpfb.export_copy")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            return

        self._basemesh(scene, layout)
        self._visemes(scene, layout)
        self._create(scene, layout)


ClassManager.add_class(MPFB_PT_ExportOpsPanel)
