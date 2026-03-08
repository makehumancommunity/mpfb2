from ..services import LogService
from ..services import SystemService

_LOG = LogService.get_logger("ui.init")
_LOG.trace("initializing ui module")

UI_DUMMY_VALUE = None  # To be able to import something independent of blender version

if SystemService.is_blender_version_at_least():

    # Top level panels
    from .newpanel import *
    from .presetspanel import *
    from .model import *
    from .rigpanel import *
    from .assetspanel import *
    from .operationspanel import *
    from .createpanel import *
    from .systempanel import *
    from .developer import *
    from .haireditorpanel import *

    # New human panels
    from .newhuman import *
    from .importer import *
    from .importerpresets import *

    # Create assets panels
    from .create_assets import *

    # Rig panels
    from .rigging import *

    # Presets
    from .presets import *

    # Assets
    from .assetlibrary import *
    from .loadclothes import *

    # Operations
    from .operations import *

    # System
    from .system import *

    __all__ = [
        "MPFB_PT_New_Panel",
        "MPFB_PT_Create_Panel",
        "MPFB_PT_Add_Rig_Panel",
        "MPFB_PT_Importer_Panel",
        "MPFB_PT_Importer_Presets_Panel",
        "MPFB_PT_Presets_Panel",
        # "MPFB_PT_Targets_Panel",
        # "MPFB_PT_Clothes_Panel",
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
