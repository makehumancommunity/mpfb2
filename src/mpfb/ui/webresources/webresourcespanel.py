"""This file contains the web resources panel."""

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.ui.abstractpanel import Abstract_Panel

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

        self._url(layout, "Project home", "https://github.com/makehumancommunity/mpfb2")
        self._url(layout, "Documentation", "https://github.com/makehumancommunity/mpfb2/blob/master/docs/README.md")
        self._url(layout, "Get support", "http://www.makehumancommunity.org/forum/")
        self._url(layout, "Report a bug", "https://github.com/makehumancommunity/mpfb2/issues")
        self._url(layout, "Asset packs", "http://download.tuxfamily.org/makehuman/asset_packs/index.html")


ClassManager.add_class(MPFB_PT_Web_Resources_Panel)

