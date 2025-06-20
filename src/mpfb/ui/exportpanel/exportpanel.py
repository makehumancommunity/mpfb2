# ------------------------------------------------------------------------------
# MPFB2 Extension by Klecer
# Author:       Tomáš Klecer
# Date:         13.5.2025
# University:   Brno University of Technology
# Supervisor:   Ing. Tomáš Chlubna, Ph.D.
# Description:  UI panel for Unreal Engine 5 exporter module
# ------------------------------------------------------------------------------
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel
import bpy,os,json
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("ui.exportpanel")
_LOC = os.path.dirname(__file__)

HAIR_PROPERTIES_DIR = os.path.join(_LOC, "../haireditorpanel/properties")
HAIR_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(HAIR_PROPERTIES_DIR, prefix="HAI_")

class MPFB_PT_Export_Panel(Abstract_Panel):
    bl_label = "Export"
    bl_category = UiService.get_value("EXPORTCATEGORY")

    # Box with operator responsible for setting up scene for export
    def _rescale_ue5(self, scene, layout):
        box = self._create_box(layout, "Setup objects for Export")
        box.label(text="Rescale mesh and armature to work correctly UE5 mannequin and setup export settings")
        box.operator("mpfb.rescale_ue5", text="Setup")

    # Box with export options and export operator
    def _export_ue5(self, scene, layout):
        box = self._create_box(layout, "Export to UE5")
        box.label(text="WARNING: Make sure material is baked, ue5 rig is applied and there are no unbaked card assets!")

        if hasattr(bpy.types.Scene, f"join_hair_cards"):
            box.prop(scene, f"join_hair_cards", text="Join hair cards with mesh")
        if hasattr(bpy.types.Scene, f"join_hair_assets"):
            box.prop(scene, f"join_hair_assets", text="Merge hair assets together")

        if hasattr(bpy.types.Scene, "export_object_name"):
            box.prop(scene, "export_object_name", text="Export Object Name")
        if hasattr(bpy.types.Scene, "export_save_path"):
            box.prop(scene, "export_save_path", text="Export Save Path")


        export_op = box.operator("mpfb.export_ue5")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if hasattr(bpy.types.Scene, f"mesh_rescaled_for_export"):
            self._export_ue5(scene, layout)
        else:
            self._rescale_ue5(scene, layout)


ClassManager.add_class(MPFB_PT_Export_Panel)