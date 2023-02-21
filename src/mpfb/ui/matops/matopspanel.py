import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("matops.matopspanel")

_LOC = os.path.dirname(__file__)
MATOPS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MATOPS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MATOPS_PROPERTIES_DIR, prefix="MATO_")

class MPFB_PT_MatopsPanel(Abstract_Panel):
    bl_label = "Material"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _adjust(self, scene, layout):
        box = self.create_box(layout, "Adjust material")
        box.operator("mpfb.set_normalmap")

    def _experimental(self, scene, layout):
        box = self.create_box(layout, "Experimental")
        MATOPS_PROPERTIES.draw_properties(scene, box, ["recreate_groups", "reuse_textures"])
        box.operator("mpfb.create_v2_skin")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        objtype = ObjectService.get_object_type(context.object)

        if not objtype or objtype == "Skeleton":
            return

        #material = MaterialService.get_material(context.object)
        #_LOG.dump("Material", (material, MaterialService.identify_material(material)))

        self._adjust(scene, layout)
        self._experimental(scene, layout)


ClassManager.add_class(MPFB_PT_MatopsPanel)
