"""This is the root panel for the asset library."""

import bpy
from bpy.props import StringProperty
from ... import ClassManager
from ...services import LogService
from ...services import UiService
from ...services import AssetService
from ..abstractpanel import Abstract_Panel
from ..mpfboperator import MpfbOperator
from ..systemassets import get_system_assets_status, get_system_assets_lines, STATUS_OK
from ...services import SceneConfigSet

_LOG = LogService.get_logger("ui.assetspanel")

_UPDATING_TAG_INPUT = False


def get_selected_tags(scene) -> list[str]:
    """Return the normalized list of currently selected tag filters on the scene."""
    if scene is None:
        return []
    raw = str(FILTER_PROPERTIES.get_value("selected_tags", entity_reference=scene) or "")
    return AssetService.normalize_tags(raw)


def set_selected_tags(scene, tags: list[str]) -> None:
    """Persist selected tag filters on the scene."""
    normalized = AssetService.normalize_tags(tags)
    FILTER_PROPERTIES.set_value("selected_tags", ", ".join(normalized), entity_reference=scene)


def _search_tags(scene, _context, edit_text: str) -> list[str]:
    """Return co-occurring tags matching the current autocomplete text."""
    candidates = AssetService.get_cooccurring_tags(get_selected_tags(scene))
    needle = edit_text.strip().lower()
    if needle:
        return [t for t in candidates if needle in t]
    return candidates


def _on_tag_input_changed(scene, _context) -> None:
    """Add picked/entered tag to selected_tags and clear the autocomplete input box."""
    global _UPDATING_TAG_INPUT
    if _UPDATING_TAG_INPUT:
        return
    raw = str(getattr(scene, "MPFB_APAS_tag_input", "") or "").strip().lower()
    if not raw:
        return

    selected = get_selected_tags(scene)
    available = set(AssetService.get_cooccurring_tags(selected))
    if raw not in available:
        return

    _UPDATING_TAG_INPUT = True
    try:
        selected.append(raw)
        set_selected_tags(scene, selected)
        scene.MPFB_APAS_tag_input = ""
    finally:
        _UPDATING_TAG_INPUT = False


FILTER_PROPERTIES = SceneConfigSet([
    {
    "type": "string",
    "name": "filter",
    "description": "Only list assets with this term in the title",
    "label": "Title must contain",
    "default": ""
    },
    {
    "type": "string",
    "name": "selected_tags",
    "description": "Comma-separated list of active tag filters",
    "label": "Selected tags",
    "default": ""
    },
    {
    "type": "string",
    "name": "packname",
    "description": "Only list assets belonging to an asset pack matching this name",
    "label": "Pack name must contain",
    "default": ""
    },
    {
    "type": "boolean",
    "name": "only_equipped",
    "description": "Only show assets which are currently equipped",
    "label": "Only equipped",
    "default": False
    }
    ], 'APAS_')

bpy.types.Scene.MPFB_APAS_tag_input = StringProperty(
    name="Tags",
    description="Type to search tags and select one to add it to the filter",
    default="",
    search=_search_tags,
    update=_on_tag_input_changed,
)


class MPFB_OT_Remove_Tag_Filter_Operator(MpfbOperator):
    """Remove a tag from the active asset library tag filter"""
    bl_idname = "mpfb.remove_tag_filter"
    bl_label = "Remove tag"
    bl_options = {'REGISTER'}

    tag: StringProperty(options={'HIDDEN'})

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        selected = get_selected_tags(context.scene)
        target = self.tag.strip().lower()
        set_selected_tags(context.scene, [t for t in selected if t != target])
        return {'FINISHED'}


class MPFB_OT_Clear_Tag_Filters_Operator(MpfbOperator):
    """Clear all active tag filters"""
    bl_idname = "mpfb.clear_tag_filters"
    bl_label = "Clear tags"
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        set_selected_tags(context.scene, [])
        return {'FINISHED'}


class MPFB_PT_Assets_Panel(Abstract_Panel):
    bl_label = "Apply assets"
    bl_category = UiService.get_value("MATERIALSCATEGORY")
    bl_order = 40

    def system_assets(self, layout):
        status = get_system_assets_status()
        if status == STATUS_OK:
            return
        box = layout.box()
        box.label(text="NOTE ABOUT SYSTEM ASSETS")
        box.label(text="")
        for line in get_system_assets_lines(status):
            box.label(text=line)

    def _draw_tag_filter(self, context, box):
        if not AssetService.get_all_asset_tags():
            return

        scene = context.scene
        selected = get_selected_tags(scene)

        row = box.row(align=True)
        row.prop(scene, "MPFB_APAS_tag_input", text="Tags", icon="TAG")
        if selected:
            row.operator("mpfb.clear_tag_filters", text="", icon="X")
            flow = box.grid_flow(columns=2, even_columns=False, even_rows=False)
            for tag in selected:
                op = flow.operator("mpfb.remove_tag_filter", text=tag, icon="X")
                op.tag = tag

    def draw(self, context):
        _LOG.enter()
        layout = self.layout

        self.system_assets(layout)

        box = layout.box()
        box.label(text="Filter")
        FILTER_PROPERTIES.draw_properties(context.scene, box, ["filter"])
        self._draw_tag_filter(context, box)

        show_props = []
        if AssetService.get_pack_names():
            _LOG.debug("There is pack metadata")
            show_props.append("packname")
        else:
            _LOG.debug("There is no pack metadata")
        show_props.append("only_equipped")
        FILTER_PROPERTIES.draw_properties(context.scene, box, show_props)


ClassManager.add_class(MPFB_OT_Remove_Tag_Filter_Operator)
ClassManager.add_class(MPFB_OT_Clear_Tag_Filters_Operator)
ClassManager.add_class(MPFB_PT_Assets_Panel)
