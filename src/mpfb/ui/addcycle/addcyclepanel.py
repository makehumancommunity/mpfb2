"""File containing UI for adding a walk cycle"""

import os, bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.uiservice import UiService
from mpfb.services.objectservice import ObjectService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("addcycle.addcyclepanel")

_WC = os.listdir(LocationService.get_mpfb_data("walkcycles"))

_LOC = os.path.dirname(__file__)
ADD_CYCLE_PROPERTIES_DIR = os.path.join(_LOC, "properties")
ADD_CYCLE_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(ADD_CYCLE_PROPERTIES_DIR, prefix="AWC_")

def _populate_settings(self, context):
    global _WC
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    cycles = []
    for wc in _WC:
        cycles.append((wc, wc, wc))
    return cycles

_SETTINGS_LIST_PROP = {
    "type": "enum",
    "name": "available_cycles",
    "description": "These are the currently available walk cycles",
    "label": "Walk cycle",
    "default": None
}
ADD_CYCLE_PROPERTIES.add_property(_SETTINGS_LIST_PROP, _populate_settings)

class MPFB_PT_Add_Cycle_Panel(Abstract_Panel):
    """Functionality for adding/setting walk cycle"""

    bl_label = "Add walk cycle"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"

    def _load_cycle(self, scene, layout):
        box = self._create_box(layout, "Load walk cycle", "TOOL_SETTINGS")
        box.label(text='This is all very experimental.')
        box.label(text='The only supported rig is')
        box.label(text='"default_no_toes".')
        props = ["available_cycles", "iterations"]
        ADD_CYCLE_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.load_walk_cycle')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if context.active_object is None:
            _LOG.debug("There is no active object")
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")
        _LOG.debug("Armature object", armature_object)

        if armature_object is None:
            _LOG.debug("There is no armature object")
            return

        self._load_cycle(scene, layout)

ClassManager.add_class(MPFB_PT_Add_Cycle_Panel)
