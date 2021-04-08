"""File containing main UI for makeclothes"""

import os, bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.ui.makeclothes import MakeClothesObjectProperties

_LOC = os.path.dirname(__file__)
MAKECLOTHES_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKECLOTHES_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKECLOTHES_PROPERTIES_DIR, prefix="MC_")

_LOG = LogService.get_logger("makeclothes.makeclothespanel")

class MPFB_PT_MakeClothes_Panel(bpy.types.Panel):
    """MakeClothes main panel."""

    bl_label = "MakeClothes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _setup_clothes(self, scene, layout):
        box = self._create_box(layout, "Set up clothes", "TOOL_SETTINGS")
        box.operator('mpfb.extract_makeclothes_clothes')
        box.operator('mpfb.mark_makeclothes_clothes')

    def _write_clothes(self, blender_object, scene, layout):
        box = self._create_box(layout, "Write clothes", "MATERIAL_DATA")

        props = [
            "overwrite"
            ]
        MAKECLOTHES_PROPERTIES.draw_properties(scene, box, props)

        props = [
            "name",
            "description",
            "tag",
            "license",
            "author",
            "homepage"
            ]
        MakeClothesObjectProperties.draw_properties(blender_object, box, props)

        box.operator('mpfb.write_makeclothes_clothes')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object

        #self._setup_clothes(scene, layout)

        if blender_object is None:
            return

        #if blender_object.type == "MESH":
        #    self._write_clothes(blender_object, scene, layout)


ClassManager.add_class(MPFB_PT_MakeClothes_Panel)


