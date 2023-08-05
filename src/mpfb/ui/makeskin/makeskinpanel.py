"""File containing main UI for makeskin"""

import os, bpy
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.ui.makeskin import MakeSkinObjectProperties
from mpfb.ui.abstractpanel import Abstract_Panel

_LOC = os.path.dirname(__file__)
MAKESKIN_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKESKIN_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKESKIN_PROPERTIES_DIR, prefix="MS_")

_LOG = LogService.get_logger("makeskin.makeskinpanel")

class MPFB_PT_MakeSkin_Panel(Abstract_Panel):
    """MakeSkin main panel."""

    bl_label = "MakeSkin"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _create_material(self, scene, layout):
        box = self._create_box(layout, "Create empty material", "TOOL_SETTINGS")
        props = [
            #"overwrite",
            #"create_node_visualization"
            "create_diffuse",
            "create_normalmap",
            "create_bumpmap",
            "create_aomap",
            "create_displacementmap",
            "create_emissionColorMap",
            "create_emissionStrengthMap",
            "create_metallicmap",
            "create_opacitymap",
            "create_roughnessmap",
            "create_specularmap",
            "create_subsurfaceColorMap",
            "create_subsurfaceStrengthMap",
            "create_transmissionmap",
            "resolution"
            ]
        MAKESKIN_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.create_makeskin_material')

    def _import_material(self, layout):
        box = self._create_box(layout, "Import", "MATERIAL_DATA")
        box.operator('mpfb.import_makeskin_material')

    def _save_material(self, blender_object, layout):
        box = self._create_box(layout, "Write material", "MATERIAL_DATA")
        props = [
            "name",
            "description",
            "tag",
            "license",
            "author",
            "homepage",
            "backface_culling",
            "cast_shadows",
            "receive_shadows",
            "alpha_to_coverage",
            "shadeless",
            "wireframe",
            "transparent",
            "depthless",
            "sss_enable",
            "auto_blend",
            "textures",
            "use_litsphere",
            "litsphere"
            ]
        MakeSkinObjectProperties.draw_properties(blender_object, box, props)
        box.operator('mpfb.write_makeskin_to_library')
        box.operator('mpfb.write_makeskin_material')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object
        if blender_object is None:
            return

        if blender_object.type == "MESH":
            self._create_material(scene, layout)
            self._import_material(layout)
            self._save_material(blender_object, layout)


ClassManager.add_class(MPFB_PT_MakeSkin_Panel)


