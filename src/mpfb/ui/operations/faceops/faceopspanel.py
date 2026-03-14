"""UI panel for facial shape key operations and Lip Sync integration."""

import os, bpy
from .... import ClassManager
from ....services import LogService
from ....services import ObjectService
from ....services import SceneConfigSet
from ....services import SystemService
from ....services import UiService
from ...abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("faceops.faceopspanel")

_LOC = os.path.dirname(__file__)
FACEOPS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
FACEOPS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(FACEOPS_PROPERTIES_DIR, prefix="FAOP_")


class MPFB_PT_FaceOpsPanel(Abstract_Panel):
    """UI panel for loading facial shape key packs and configuring Lip Sync integration."""

    bl_label = "Face operations"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def _shape_key_packs(self, scene, layout):
        box = self.create_box(layout, "Facial shape key packs")
        FACEOPS_PROPERTIES.draw_properties(scene, box, [
            "visemes01",
            "visemes02",
            "faceunits01"
            ])
        box.operator("mpfb.load_face_shape_keys")

    def _lip_sync(self, basemesh, layout):
        box = self.create_box(layout, "Lip Sync shape keys")

        if not SystemService.check_for_lipsync():
            box.label(text="Lip Sync addon is not enabled", icon="ERROR")
            return

        has_visemes02 = (
            basemesh.data.shape_keys is not None
            and "viseme_sil" in basemesh.data.shape_keys.key_blocks
        )
        if not has_visemes02:
            box.label(text="Load visemes02 to enable Lip Sync configuration", icon="INFO")
            return

        if not hasattr(basemesh, "lipsync2d_props") or not basemesh.lipsync2d_props.lip_sync_2d_initialized:
            box.label(text="Initialise Lip Sync on this object first (use the Lip Sync panel)", icon="INFO")
            return

        box.operator("mpfb.configure_lip_sync")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object)
        if basemesh is None:
            return

        self._shape_key_packs(scene, layout)
        self._lip_sync(basemesh, layout)


ClassManager.add_class(MPFB_PT_FaceOpsPanel)
