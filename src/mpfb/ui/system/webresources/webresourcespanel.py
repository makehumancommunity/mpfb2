"""This file contains the web resources panel."""

from .... import ClassManager
from ....services import LogService
from ....services import UiService
from ...abstractpanel import Abstract_Panel
from ...weburls import URL_HOMEPAGE, URL_SOURCE_CODE, URL_DOCUMENTATION, URL_FORUM, URL_ISSUE_TRACKER, URL_ASSET_PACKS

_LOG = LogService.get_logger("webresources.webresourcespanel")

class MPFB_PT_Web_Resources_Panel(Abstract_Panel):
    """UI for opening web links."""
    bl_label = "Web resources"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_System_Panel"

    def _url(self, layout, label, url):
        weblink = layout.operator("mpfb.web_resource", text=label)
        weblink.url = url

    def draw(self, context):
        _LOG.enter()
        layout = self.layout

        self._url(layout, "Project homepage", URL_HOMEPAGE)
        self._url(layout, "Source code", URL_SOURCE_CODE)
        self._url(layout, "Documentation", URL_DOCUMENTATION)
        self._url(layout, "Get support", URL_FORUM)
        self._url(layout, "Report a bug", URL_ISSUE_TRACKER)
        self._url(layout, "Asset packs", URL_ASSET_PACKS)

ClassManager.add_class(MPFB_PT_Web_Resources_Panel)

