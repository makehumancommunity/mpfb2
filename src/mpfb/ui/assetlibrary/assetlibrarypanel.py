"""Asset library subpanels"""

import bpy, os, json
from bpy.props import FloatProperty
from mpfb import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.assetservice import AssetService, ASSET_LIBRARY_SECTIONS

_LOG = LogService.get_logger("assetlibrary.assetlibrarypanel")
_LOG.set_level(LogService.DUMP)

_NOASSETS = [
    "No assets in this section.",
    "Maybe set MH user data preference",
    "or install assets in MPFB user data"
    ]


class _Abstract_Asset_Library_Panel(bpy.types.Panel):
    """Asset library panel."""

    bl_label = "SHOULD BE OVERRIDDEN"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Assets_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    asset_subdir = "-"
    asset_type = "mhclo"
    skin_overrides = False
    eye_overrides = False
    object_type = "Clothes"

    def _draw_section(self, scene, layout):
        _LOG.enter()
        items = AssetService.get_asset_list(self.asset_subdir, self.asset_type)
        names = list(items.keys())
        if len(names) < 1:
            for line in _NOASSETS:
                layout.label(text=line)
            return
        names.sort()
        for name in names:
            box = layout.box()
            box.label(text=name)
            asset = items[name]
            _LOG.debug("Asset", asset)
            if "thumb" in asset and not asset["thumb"] is None:
                box.template_icon(icon_value=asset["thumb"].icon_id, scale=6.0)
            op = None
            if self.asset_type == "mhclo":
                op = box.operator("mpfb.load_library_clothes")
            if self.asset_type == "proxy":
                op = box.operator("mpfb.load_library_proxy")
            if self.asset_type == "mhmat":
                if self.skin_overrides:
                    op = box.operator("mpfb.load_library_skin")
            if not op is None:
                op.filepath = asset["full_path"]
                if hasattr(op, "object_type") and self.object_type:
                    op.object_type = self.object_type

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

#===============================================================================
#         if not context.object:
#             return
#
#         if not ObjectService.object_is_basemesh(context.object):
#             return
#
#         basemesh = context.object
#===============================================================================

        self._draw_section(scene, layout)


for _definition in ASSET_LIBRARY_SECTIONS:
    _LOG.dump("Definition", _definition)
    _sub_panel = type("MPFB_PT_Asset_Library_Panel_" + _definition["asset_subdir"], (_Abstract_Asset_Library_Panel,), _definition)
    _LOG.debug("sub_panel", _sub_panel)
    ClassManager.add_class(_sub_panel)
