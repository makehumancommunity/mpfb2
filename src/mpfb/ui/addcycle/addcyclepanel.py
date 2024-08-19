"""File containing deprecated UI for adding a walk cycle"""

import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import UiService
from ...services import ObjectService
from ...services import SceneConfigSet
from ..abstractpanel import Abstract_Panel


class MPFB_PT_Add_Cycle_Panel(Abstract_Panel):
    """Deprecated functionality for adding/setting walk cycle"""

    bl_label = "Add walk cycle"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_parent_id = "MPFB_PT_Rig_Panel"

    def _load_cycle(self, scene, layout):
        box = self._create_box(layout, "Load walk cycle", "TOOL_SETTINGS")
        box.label(text=' ')
        box.label(text='DEPRECATED in favor of')
        box.label(text='mixamo functionality')
        box.label(text=' ')
        box.label(text='(and it never worked')
        box.label(text='particularly well in')
        box.label(text='the first place)')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if context.active_object is None:
            return

        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(context.active_object, "Skeleton")

        if armature_object is None:
            return

        self._load_cycle(scene, layout)

ClassManager.add_class(MPFB_PT_Add_Cycle_Panel)
