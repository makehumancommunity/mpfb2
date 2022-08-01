import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("basemeshops.basemeshopspanel")

#_LOC = os.path.dirname(__file__)
#SCULPT_PROPERTIES_DIR = os.path.join(_LOC, "properties")
#SCULPT_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SCULPT_PROPERTIES_DIR, prefix="SCL_")

class MPFB_PT_BasemeshOpsPanel(Abstract_Panel):
    bl_label = "Basemesh"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        from mpfb.entities.objectproperties import GeneralObjectProperties

        objtype = GeneralObjectProperties.get_value("object_type", entity_reference=context.object)

        if objtype != "Basemesh":
            return

        layout.operator("mpfb.bake_shapekeys")
        layout.operator("mpfb.delete_helpers")


ClassManager.add_class(MPFB_PT_BasemeshOpsPanel)
