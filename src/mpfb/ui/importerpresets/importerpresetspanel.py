import os, bpy
from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.sceneconfigset import SceneConfigSet
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("ui.importerpresets")

_LOC = os.path.dirname(__file__)
IMPORTER_PRESETS_PROPERTIES_DIR = os.path.join(_LOC, "properties")
IMPORTER_PRESETS_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(IMPORTER_PRESETS_PROPERTIES_DIR, prefix="IP_")


def _populate_presets(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    available_presets = UiService.get_importer_presets_panel_list()
    if available_presets is None:
        available_presets = []
    return available_presets


_PRESETS_LIST_PROP = {
    "type": "enum",
    "name": "available_presets",
    "description": "Available presets",
    "label": "Available presets",
    "default": 0
}
IMPORTER_PRESETS_PROPERTIES.add_property(_PRESETS_LIST_PROP, _populate_presets)


class MPFB_PT_Importer_Presets_Panel(Abstract_Panel):
    bl_label = "Importer Presets"
    bl_category = UiService.get_value("IMPORTERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_New_Panel"

    def _create_box(self, layout, box_text, box_icon=None):
        _LOG.enter()
        box = layout.box()
        box.label(text=box_text, icon=box_icon)
        return box

    def _load_save_box(self, scene, layout):
        _LOG.enter()
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, ["available_presets"])
        layout.operator('mpfb.importerpresets_load_importer_presets')
        layout.operator('mpfb.importerpresets_overwrite_importer_presets')
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, ["name"])
        layout.operator('mpfb.importerpresets_save_new_importer_presets')

    def _what_box(self, scene, layout):
        _LOG.enter()
        props = [
            "import_body",
            "import_body_proxy",
            "import_body_parts",
            "import_clothes",
            "import_rig",
            "rig_as_parent"
            ]
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, props)

    def _general_box(self, scene, layout):
        _LOG.enter()
        props = [
            "scale_factor",
            "feet_on_ground",
            "create_collection",
            "collections_as_children",
            "prefix_object_names"
            ]
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, props)

    def _mesh_and_groups_box(self, scene, layout):
        _LOG.enter()
        props = [
            "mask_base_mesh",
            "add_subdiv_modifier",
            "subdiv_levels",
            "handle_helpers",
            "detailed_helpers",
            "extra_vertex_groups"
            ]
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, props)

    def _materials_box(self, scene, layout):
        _LOG.enter()
        props = [
            "skin_material_type",
            "material_named_from_object",
            "prefix_material_names",
            "material_creation_policy",
            "material_instances",
            "procedural_eyes",
            "fix_bad_roughness"
            ]
        IMPORTER_PRESETS_PROPERTIES.draw_properties(scene, layout, props)

    def _network_box(self, scene, layout):
        pass

    def draw(self, context):
        _LOG.enter()

        default_json = LocationService.get_user_config("importer_presets.default.json")
        if not os.path.exists(default_json):
            _LOG.warn("The default importer presets do not exist. Will create these.")
            excludes = ["available_presets", "name"]
            IMPORTER_PRESETS_PROPERTIES.serialize_to_json(default_json, entity_reference=context, exclude_keys=excludes)
        else:
            _LOG.trace("Default presets exist")

        if UiService.get_importer_presets_panel_list() is None:
            UiService.rebuild_importer_presets_panel_list()

        layout = self.layout
        scene = context.scene

        self._load_save_box(scene, self._create_box(layout, "Load/save presets", "MODIFIER"))
        self._what_box(scene, self._create_box(layout, "What to import", "MODIFIER"))
        self._general_box(scene, self._create_box(layout, "General", "MODIFIER"))
        self._mesh_and_groups_box(scene, self._create_box(layout, "Mesh and vGroups", "MODIFIER"))
        self._materials_box(scene, self._create_box(layout, "Materials", "MODIFIER"))
        self._network_box(scene, self._create_box(layout, "Network", "MODIFIER"))


ClassManager.add_class(MPFB_PT_Importer_Presets_Panel)
