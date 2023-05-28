"""Asset library subpanels"""

import bpy, math
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.assetservice import AssetService, ASSET_LIBRARY_SECTIONS
from mpfb.services.humanservice import HumanService
from mpfb.services.objectservice import ObjectService
from mpfb.ui.assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES
from mpfb.services.uiservice import UiService
from mpfb.ui.assetspanel import FILTER_PROPERTIES

_LOG = LogService.get_logger("assetlibrary.assetlibrarypanel")

_NOASSETS = [
    "No assets in this section.",
    "Maybe set MH user data preference",
    "or install assets in MPFB user data"
    ]


class _Abstract_Asset_Library_Panel(bpy.types.Panel):
    """Asset library panel"""

    bl_label = "SHOULD BE OVERRIDDEN"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Assets_Panel"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    basemesh = None
    asset_subdir = "-"
    asset_type = "mhclo"
    skin_overrides = False
    eye_overrides = False
    object_type = "Clothes"
    equipped = []

    def _draw_section(self, scene, layout):
        _LOG.enter()
        tot_width = bpy.context.region.width
        cols = max(1, math.floor(tot_width / 256))
        _LOG.debug("Number of UI columns to use", cols)

        items = AssetService.get_asset_list(self.asset_subdir, self.asset_type)
        allnames = list(items.keys())
        if len(allnames) < 1:
            for line in _NOASSETS:
                layout.label(text=line)
            return
        allnames.sort()

        filter_term = str(FILTER_PROPERTIES.get_value("filter", entity_reference=scene)).strip().lower()
        pack_term = str(FILTER_PROPERTIES.get_value("packname", entity_reference=scene)).strip().lower()

        pack_assets = []
        if pack_term:
            pack_assets = AssetService.get_asset_names_in_pack_pattern(pack_term)
            _LOG.debug("pack_assets", pack_assets)

        names = []
        for name in allnames:
            acceptable = True
            original_name = items[name]["name_without_ext"]
            if filter_term:
                if not filter_term in str(name).lower() and not filter_term in original_name:
                    _LOG.trace(name + " not acceptable, does not match ", filter_term)
                    acceptable = False
            if pack_term:
                if not original_name in pack_assets:
                    acceptable = False
            if acceptable:
                names.append(name)

        if len(names) < 1:
            layout.label(text="No matching assets.")
            layout.label(text="Maybe change filter?")
            return

        grid = layout.grid_flow(columns=cols, even_columns=True, even_rows=False)

        for name in names:
            box = grid.box()
            box.label(text=name)
            asset = items[name]
            is_equipped = False
            for child in self.equipped:
                if child in asset["fragment"]:
                    is_equipped = True
                    break
            _LOG.debug("Now checking asset", asset)
            _LOG.dump("Asset is equipped", is_equipped)

            if "thumb" in asset and not asset["thumb"] is None:
                box.template_icon(icon_value=asset["thumb"].icon_id, scale=6.0)
            operator = None
            if self.asset_type == "mhclo":
                if is_equipped:
                    operator = box.operator("mpfb.unload_library_clothes")
                else:
                    operator = box.operator("mpfb.load_library_clothes")
            if self.asset_type == "proxy":
                operator = box.operator("mpfb.load_library_proxy")
            if self.asset_type == "mhmat":
                if self.skin_overrides:
                    operator = box.operator("mpfb.load_library_skin")
            if not operator is None:
                if not is_equipped:
                    operator.filepath = asset["full_path"]
                else:
                    operator.filepath = asset["fragment"]
                if hasattr(operator, "object_type") and self.object_type:
                    operator.object_type = self.object_type
                if hasattr(operator, "material_type"):
                    procedural_eyes = ASSET_SETTINGS_PROPERTIES.get_value("procedural_eyes", entity_reference=scene)
                    _LOG.dump("Eye settings, eye_overrides, procedural_eyes", (self.eye_overrides, procedural_eyes))
                    if self.eye_overrides and procedural_eyes:
                        operator.material_type = "PROCEDURAL_EYES"
                    else:
                        operator.material_type = "MAKESKIN"
                    _LOG.debug("Operator material type is now", operator.material_type)
                else:
                    _LOG.debug("Operator does not have a material type")


    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        if context.object:
            if ObjectService.object_is_basemesh(context.object):
                self.basemesh = context.object
            else:
                self.basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Basemesh")
            _LOG.debug("basemesh", self.basemesh)

        if self.basemesh and self.asset_type in ["mhclo", "proxy"]:
            self.equipped = HumanService.get_asset_sources_of_equipped_mesh_assets(self.basemesh)
            _LOG.debug("Equipped assets", self.equipped)

        self._draw_section(scene, layout)


for _definition in ASSET_LIBRARY_SECTIONS:
    _LOG.dump("Definition", _definition)
    _sub_panel = type("MPFB_PT_Asset_Library_Panel_" + _definition["asset_subdir"], (_Abstract_Asset_Library_Panel,), _definition)
    _LOG.dump("sub_panel", _sub_panel)
    ClassManager.add_class(_sub_panel)
