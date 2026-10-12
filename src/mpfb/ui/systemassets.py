"""This file contains helpers for reporting on the state of the makehuman system assets. Both the
"Apply assets" panel and the "Start here" panel need to say the same thing about this, so the
wording is kept here rather than in either panel."""

from ..services import LogService
from ..services import AssetService

_LOG = LogService.get_logger("ui.systemassets")

STATUS_MISSING = "MISSING"
STATUS_OUTDATED = "OUTDATED"
STATUS_OK = "OK"

_MISSING_LINES = [
    "It seems the makehuman system assets",
    "have not been installed. You will",
    "likely want these before trying to load",
    "any assets"
    ]

_OUTDATED_LINES = [
    "While the makehuman system assets",
    "are installed, it seems you are using",
    "a rather old version. You might want",
    "to download and reinstall the latest",
    "version of the makehuman system assets",
    "if you encounter problems."
    ]


def get_system_assets_status():
    """Figure out if the makehuman system assets are installed, and if so whether they are recent
    enough. This is called from panel draw methods, so it must never raise. If the state cannot be
    determined we claim everything is fine, as a wrong warning is worse than no warning."""
    try:
        (has_sys_assets, modern_sys_assets) = AssetService.check_if_modern_makehuman_system_assets_installed()
    except Exception as exception:  # pylint: disable=W0703
        _LOG.debug("Could not check the system assets status", exception)
        return STATUS_OK
    _LOG.debug("has_sys_assets", (has_sys_assets, modern_sys_assets))
    if not has_sys_assets:
        return STATUS_MISSING
    if not modern_sys_assets:
        return STATUS_OUTDATED
    return STATUS_OK


def get_system_assets_lines(status):
    """Return the lines to display for a given system assets status. The lines are pre-broken to
    fit a narrow sidebar, as blender does not wrap label texts. An empty list is returned when
    there is nothing to say."""
    if status == STATUS_MISSING:
        return list(_MISSING_LINES)
    if status == STATUS_OUTDATED:
        return list(_OUTDATED_LINES)
    return []
