"""This file contains the start here panel."""

from ... import ClassManager
from ... import get_preference
from ...services import LogService
from ...services import UiService
from ..abstractpanel import Abstract_Panel
from ..systemassets import get_system_assets_status, STATUS_OK
from ..weburls import URL_DOCUMENTATION, URL_FAQ, URL_FORUM, URL_ISSUE_TRACKER, URL_SYSTEM_ASSETS
from ..weburls import URL_GETTING_STARTED_GUIDE, URL_GETTING_STARTED_VIDEO, URL_VIDEO_CHANNEL, URL_ASSET_PACKS

_LOG = LogService.get_logger("start_here.startherepanel")

class MPFB_PT_Start_Here_Panel(Abstract_Panel):
    """UI with a short introduction for users who are new to MPFB."""
    bl_label = "Start here"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = set()  # Abstract_Panel sets DEFAULT_CLOSED, but this panel should be open
    bl_order = 0

    @classmethod
    def poll(cls, context):
        # This runs on every redraw, so keep it cheap and never let it raise. If the preference
        # cannot be read for some reason, show the panel rather than hide it.
        try:
            show_panel = get_preference("mpfb_show_start_here")
        except Exception as exception:  # pylint: disable=W0703
            _LOG.debug("Could not read the start here preference", exception)
            return True
        return show_panel is None or bool(show_panel)

    def _url(self, layout, label, url):
        weblink = layout.operator("mpfb.web_resource", text=label)
        weblink.url = url

    def _what_this_is(self, layout):
        box = self.create_box(layout, "ABOUT:")
        box.label(text="MPFB is a human character")
        box.label(text="modeler. Characters and")
        box.label(text="assets are free to use,")
        box.label(text="also commercially")
        box.label(text="")
        box.label(text="The buttons below will open")
        box.label(text="a web browser at a specific")
        box.label(text="address. If the browser does")
        box.label(text="not show, make sure it is not.")
        box.label(text="minimized.")

    def _first_step(self, layout):
        box = self.create_box(layout, "FIRST STEPS")
        box.operator("mpfb.create_random_human", text="Create random human")
        box.operator("mpfb.create_human", text="Create default human")
        box.label(text="For all options, see the panel")
        box.label(text="\"New human\" below.")

    def _tutorials(self, layout):
        box = self.create_box(layout, "GUIDES AND DOCS:")
        self._url(box, "Getting started guide", URL_GETTING_STARTED_GUIDE)
        self._url(box, "Getting started video tutorial", URL_GETTING_STARTED_VIDEO)
        self._url(box, "Video tutorial channel", URL_VIDEO_CHANNEL)
        self._url(box, "Documentation", URL_DOCUMENTATION)
        self._url(box, "FAQ", URL_FAQ)

    def _assets(self, layout):
        box = self.create_box(layout, "GETTING ASSETS:")
        self._url(box, "All asset packs", URL_ASSET_PACKS)

    def _dismiss(self, layout):
        box = self.create_box(layout, "DISMISS:")
        box.operator("mpfb.dismiss_start_here")
        box.label(text="To get it back, see Blender")
        box.label(text="Preferences -> Add-ons -> MPFB.")

    def _asset_library(self, layout):
        status = get_system_assets_status()

        if status == STATUS_OK:
            return

        box = self.create_box(layout, "SYSTEM ASSETS:")

        box.label(text="It seems the system")
        box.label(text="asset pack is not")
        box.label(text="installed. Chances are")
        box.label(text="you want to download ")
        box.label(text="and install this before")
        box.label(text="continuing.")

        self._url(box, "Get system assets", URL_SYSTEM_ASSETS)
        box.operator("mpfb.load_pack", text="Install pack from zip")

    def _getting_help(self, layout):
        box = self.create_box(layout, "GETTING HELP:")
        self._url(box, "Visit the forum", URL_FORUM)
        self._url(box, "Open a ticket", URL_ISSUE_TRACKER)

    def draw(self, context):
        _LOG.enter()
        layout = self.layout

        self._what_this_is(layout)
        self._asset_library(layout)
        self._assets(layout)
        self._first_step(layout)
        self._tutorials(layout)
        self._getting_help(layout)
        self._dismiss(layout)

ClassManager.add_class(MPFB_PT_Start_Here_Panel)
