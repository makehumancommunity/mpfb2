"""File containing main UI for makerig"""

import bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("makepose.makeposepanel")

class MPFB_PT_MakeRig_Panel(Abstract_Panel):
    """MakeRig main panel."""

    bl_label = "MakeRig"
    bl_category = UiService.get_value("RIGCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def draw(self, context):
        _LOG.enter()

ClassManager.add_class(MPFB_PT_MakeRig_Panel)


