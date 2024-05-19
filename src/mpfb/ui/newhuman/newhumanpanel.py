"""File containing main UI for creating new humans"""

import bpy, os
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.sceneconfigset import SceneConfigSet

_LOG = LogService.get_logger("newhuman.newhumanpanel")

_LOC = os.path.dirname(__file__)
NEW_HUMAN_PROPERTIES_DIR = os.path.join(_LOC, "properties")
NEW_HUMAN_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(NEW_HUMAN_PROPERTIES_DIR, prefix="NH_")


class MPFB_PT_NewHuman_Panel(bpy.types.Panel):
    """Create human from scratch main panel."""

    bl_label = "From scratch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_New_Panel"

    def _create_box(self, layout, box_text):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text)
        return box

    def _create(self, scene, layout):
        box = self._create_box(layout, "Create")
        NEW_HUMAN_PROPERTIES.draw_properties(scene, box, [
            "scale_factor",
            "detailed_helpers",
            "extra_vertex_groups",
            "mask_helpers",
            "preselect_group"
            ])
        box.operator('mpfb.create_human')

    def _phenotype(self, scene, layout):
        box = self._create_box(layout, "Phenotype")
        NEW_HUMAN_PROPERTIES.draw_properties(scene, box, [
            "phenotype_gender",
            "phenotype_age",
            "phenotype_muscle",
            "phenotype_weight",
            "phenotype_height",
            "phenotype_proportions",
            "phenotype_race",
            "add_phenotype",
            "phenotype_influence"
            ])

    def _breast(self, scene, layout):
        box = self._create_box(layout, "Breast")
        NEW_HUMAN_PROPERTIES.draw_properties(scene, box, [
            "phenotype_breastsize",
            "phenotype_breastfirmness",
            "add_breast",
            "breast_influence"
            ])

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        self._phenotype(scene, layout)
        self._breast(scene, layout)
        self._create(scene, layout)


ClassManager.add_class(MPFB_PT_NewHuman_Panel)

