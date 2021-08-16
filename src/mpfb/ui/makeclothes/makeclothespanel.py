"""File containing main UI for makeclothes"""

import os, bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.objectservice import ObjectService
from mpfb.ui.makeclothes import MakeClothesObjectProperties
from mpfb.ui.abstractpanel import Abstract_Panel

_LOC = os.path.dirname(__file__)
MAKECLOTHES_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKECLOTHES_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKECLOTHES_PROPERTIES_DIR, prefix="MC_")

_LOG = LogService.get_logger("makeclothes.makeclothespanel")

def _populate_groups(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    blender_object = context.active_object
    if ObjectService.object_is_basemesh(blender_object):
        groups = []
        names = ["body"]
        for vgroup in blender_object.vertex_groups:
            name = vgroup.name
            if "helper" in name or name in ["scalp", "fingernails", "toenails", "ears", "lips", "HelperGeometry", "Left", "Mid", "Right"]:
                names.append(name)
        names.sort()
        for name in names:
            groups.append((name, name, name))
        return groups
    return []

_GROUPS_LIST_PROP = {
    "type": "enum",
    "name": "available_groups",
    "description": "These are the vertex groups which can be extracted to clothes",
    "label": "Extract group",
    "default": None
}
MAKECLOTHES_PROPERTIES.add_property(_GROUPS_LIST_PROP, _populate_groups)

class MPFB_PT_MakeClothes_Panel(Abstract_Panel):
    """MakeClothes main panel."""

    bl_label = "MakeClothes"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _setup_clothes(self, scene, layout, blender_object):
        box = self._create_box(layout, "Set up clothes", "TOOL_SETTINGS")
        if ObjectService.object_is_basemesh(blender_object):
            props = ["available_groups"]
            MAKECLOTHES_PROPERTIES.draw_properties(scene, box, props)
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

        if not blender_object:
            return

        if blender_object:
            self._setup_clothes(scene, layout, blender_object)

        if blender_object.type == "MESH":
            self._write_clothes(blender_object, scene, layout)


ClassManager.add_class(MPFB_PT_MakeClothes_Panel)


