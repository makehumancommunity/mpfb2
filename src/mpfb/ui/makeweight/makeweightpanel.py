"""File containing main UI for makeweight"""

import bpy, os
from mpfb import ClassManager
from ...services import LogService
from ...services import ObjectService
from ...services import UiService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel

_LOC = os.path.dirname(__file__)
MAKEWEIGHT_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKEWEIGHT_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKEWEIGHT_PROPERTIES_DIR, prefix="MW_")

_LOG = LogService.get_logger("makeweight.makeweightpanel")

def _populate_groups(self, context):
    _LOG.enter()
    blender_object = None
    if isinstance(context, bpy.types.Object):
        blender_object = context
    else:
        blender_object = context.active_object

    _LOG.dump("blender_object", blender_object)

    if blender_object is None:
        return []

    group_names = []
    for group in blender_object.vertex_groups:
        if not str(group.name).startswith("joint-"):
            group_names.append(group.name)

    group_names.sort()

    _LOG.dump("Group names", group_names)

    groups = []

    i = 0
    for name in group_names:
        groups.append((name, name, name, i))
        i = i + 1

    _LOG.dump("Groups", groups)

    return groups

_GROUPS_LIST_PROP = {
    "type": "enum",
    "name": "vertex_group",
    "description": "Vertex groups currently existing on the selected object",
    "label": "Vertex group",
    "default": None
}

MAKEWEIGHT_PROPERTIES.add_property(_GROUPS_LIST_PROP, _populate_groups)

class MPFB_PT_MakeWeight_Panel(Abstract_Panel):
    """MakeWeight main panel."""

    bl_label = "MakeWeight"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _operations(self, scene, layout):
        box = self._create_box(layout, "Vertex groups", "TOOL_SETTINGS")
        MAKEWEIGHT_PROPERTIES.draw_properties(scene, box, ["vertex_group"])
        box.operator('mpfb.truncate_weights')

    def _load_save(self, scene, layout):
        box = self._create_box(layout, "Load and save", "TOOL_SETTINGS")
        box.operator('mpfb.import_makeweight_weight')
        box.operator('mpfb.save_makeweight_weight')

    def _symmetrize_weight(self, scene, layout):
        box = self._create_box(layout, "Symmetrize", "TOOL_SETTINGS")
        box.operator('mpfb.symmetrize_makeweight_left')
        box.operator('mpfb.symmetrize_makeweight_right')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object
        if blender_object is None:
            return

        self._load_save(scene, layout)
        self._operations(scene, layout)
        self._symmetrize_weight(scene, layout)

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if ObjectService.object_is_basemesh(context.active_object):
            return True
        if ObjectService.object_is_skeleton(context.active_object):
            return True
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        if rig:
            return True
        return False

ClassManager.add_class(MPFB_PT_MakeWeight_Panel)


