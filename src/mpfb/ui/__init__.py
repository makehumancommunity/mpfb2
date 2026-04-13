"""This is the root directory of the UI layer."""

from ..services import LogService
from ..services import SystemService

_LOG = LogService.get_logger("ui.init")
_LOG.trace("initializing ui module")

UI_DUMMY_VALUE = None  # To be able to import something independent of blender version

if SystemService.is_blender_version_at_least():

    # Meta classes. These are used by most panels and operators.
    from .abstractpanel import Abstract_Panel
    from .mpfboperator import MpfbOperator
    from .mpfbcontext import MpfbContext, ContextFocusObject, ContextResolveEffort
    from .pollstrategy import pollstrategy, PollStrategy

    # Special cases in the UI layer. These contain specific complex logic which makes them
    # unsuitable to arrange in the same manner as the rest of the UI layer.
    from .model import *
    from .developer import *
    from .haireditorpanel import *

    # Most of the UI layer follows a common pattern: A top level directory matching a main panel
    # in the ui, with subdirectories matching subpanels.
    from .new_human import *
    from .create_assets import *
    from .rigging import *
    from .presets import *
    from .apply_assets import *
    from .operations import *
    from .system import *

    __all__ = [
        "Abstract_Panel",
        "MpfbOperator",
        "MpfbContext",
        "ContextFocusObject",
        "ContextResolveEffort",
        "pollstrategy",
        "PollStrategy",
        "MPFB_PT_New_Panel",
        "MPFB_PT_Create_Panel",
        "MPFB_PT_Add_Rig_Panel",
        "MPFB_PT_Importer_Panel",
        "MPFB_PT_Importer_Presets_Panel",
        "MPFB_PT_Presets_Panel",
        "MPFB_PT_Save_Nodes_Panel",
        "MPFB_PT_RigHelpersPanel",
        "MPFB_PT_Enhanced_Settings_Panel",
        "MPFB_PT_Eye_Settings_Panel",
        "MPFB_PT_MakeSkin_Panel",
        "MPFB_PT_MakeTarget_Panel",
        "MPFB_PT_Load_Clothes_Panel",
        "MPFB_PT_MakeClothes_Panel",
        "MPFB_PT_Operations_Panel",
        "MPFB_PT_Devloper_Panel",
        "MPFB_PT_Hair_Editor_Panel",
        "MPFB_PT_Ai_Panel",
        "UI_DUMMY_VALUE"
        ]
else:
    from .versionpanel import *
    __all__ = [
        "MPFB_PT_Version_Panel",
        "UI_DUMMY_VALUE"
        ]
