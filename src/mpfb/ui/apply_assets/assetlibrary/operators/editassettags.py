"""Operator for editing custom user tags on an asset library item."""

import bpy
from bpy.props import StringProperty
from ..... import ClassManager
from .....services import LogService, AssetService
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.editassettags")


class MPFB_OT_Edit_Asset_Tags_Operator(MpfbOperator):
    """Add or edit custom user tags for this asset"""
    bl_idname = "mpfb.edit_asset_tags"
    bl_label = "Edit asset tags"
    bl_options = {'REGISTER'}

    asset_subdir: StringProperty(options={'HIDDEN'})
    asset_fragment: StringProperty(options={'HIDDEN'})
    asset_label: StringProperty(options={'HIDDEN'})
    tags: StringProperty(
        name="User tags",
        description="Comma-separated custom tags for this asset (e.g. favorite, work, winter)",
        default="",
    )

    def get_logger(self):
        return _LOG

    def invoke(self, context, _event):
        existing = AssetService.get_user_tags_for_asset(self.asset_subdir, self.asset_fragment)
        self.tags = ", ".join(existing)
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, _context):
        layout = self.layout
        if self.asset_label:
            layout.label(text=f"Asset: {self.asset_label}")
        file_tags = self._find_file_tags()
        if file_tags:
            layout.label(text="Built-in tags: " + ", ".join(file_tags))
        layout.prop(self, "tags")

    def _find_file_tags(self) -> list[str]:
        if not self.asset_subdir or not self.asset_fragment:
            return []
        items = AssetService.get_asset_list(self.asset_subdir, self._guess_asset_type())
        for item in items.values():
            if item.get("fragment") == self.asset_fragment:
                return item.get("file_tags", [])
        return []

    def _guess_asset_type(self) -> str:
        from .....services.assetservice import ASSET_LIBRARY_SECTIONS  # pylint: disable=C0415
        for section in ASSET_LIBRARY_SECTIONS:
            if section["asset_subdir"] == self.asset_subdir:
                return section["asset_type"]
        return "mhclo"

    def hardened_execute(self, _context):
        if not self.asset_subdir or not self.asset_fragment:
            self.report({'ERROR'}, "Missing asset reference")
            return {'CANCELLED'}

        saved = AssetService.set_user_tags_for_asset(self.asset_subdir, self.asset_fragment, self.tags)
        if saved:
            self.report({'INFO'}, f"Saved user tags: {', '.join(saved)}")
        else:
            self.report({'INFO'}, "Cleared custom user tags")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Edit_Asset_Tags_Operator)
