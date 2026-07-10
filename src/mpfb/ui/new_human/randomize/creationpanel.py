"""File containing the creation settings sub-panel of the randomize panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from .randomizeproperties import RANDOMIZE_PROPERTIES

_LOG = LogService.get_logger("ui.new_human.randomize.creationpanel")


class MPFB_PT_Randomize_Creation_Panel(Abstract_Panel):
    """Creation settings and the create button."""

    bl_label = "Creation settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = set()
    bl_parent_id = "MPFB_PT_Randomize_Panel"
    bl_order = 9

    def draw(self, context):
        _LOG.enter()
        scene = context.scene
        layout = self.layout
        # The rig is added right after the human is created, before the body parts, so they
        # are rigged as they attach. The Rigify pair mirrors the from-save-file panel.
        rig_box = layout.box()
        rig_box.label(text="Rig")
        RANDOMIZE_PROPERTIES.draw_properties(scene, rig_box, [
            "rig",
            "auto_generate_rigify",
            "meta_rig_action"
            ])
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, [
            "scale_factor",
            "detailed_helpers",
            "extra_vertex_groups",
            "mask_helpers"
            ])
        # The "new random seed" checkbox sits next to the create button so its effect on the
        # seed field after each creation is discoverable.
        RANDOMIZE_PROPERTIES.draw_properties(scene, layout, ["new_random_seed"])
        layout.operator('mpfb.create_random_human')


ClassManager.add_class(MPFB_PT_Randomize_Creation_Panel)
