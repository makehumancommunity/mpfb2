from mpfb.services.logservice import LogService
from mpfb.services.systemservice import SystemService

_LOG = LogService.get_logger("ui.init")
_LOG.trace("initializing ui module")

if SystemService.is_blender_version_at_least():

    # Top level panels
    from mpfb.ui.newpanel import *
    from mpfb.ui.presetspanel import *
    from mpfb.ui.model import *
    from mpfb.ui.rigpanel import *
    from mpfb.ui.assetspanel import *
    from mpfb.ui.operationspanel import *
    from mpfb.ui.createpanel import *
    from mpfb.ui.systempanel import *
    from mpfb.ui.developer import *
    from mpfb.ui.exportpanel import *
    from mpfb.ui.skineditorpanel import *
    from mpfb.ui.haireditorpanel import *

    # New human panels
    from mpfb.ui.newhuman import *
    from mpfb.ui.importer import *
    from mpfb.ui.importerpresets import *

    # Create assets panels
    from mpfb.ui.makeskin import *
    from mpfb.ui.maketarget import *
    from mpfb.ui.makeclothes import *
    from mpfb.ui.makeweight import *
    from mpfb.ui.makepose import *
    from mpfb.ui.makerig import *

    # Rig panels
    from mpfb.ui.addrig import *
    from mpfb.ui.rigify import *
    from mpfb.ui.righelpers import *
    from mpfb.ui.applypose import *
    from mpfb.ui.addcycle import *

    # Presets
    from mpfb.ui.humanpresets import *
    from mpfb.ui.enhancedsettings import *
    from mpfb.ui.eyesettings import *

    # Assets
    from mpfb.ui.assetlibrary import *
    from mpfb.ui.loadclothes import *

    # Operations
    from mpfb.ui.animops import *
    from mpfb.ui.basemeshops import *
    from mpfb.ui.poseops import *
    from mpfb.ui.sculpt import *
    from mpfb.ui.matops import *
    from mpfb.ui.boneops import *
    from mpfb.ui.ai import *

    # System
    from mpfb.ui.webresources import *
    from mpfb.ui.dirresources import *

    __all__ = [
        "MPFB_PT_New_Panel",
        "MPFB_PT_Create_Panel",
        "MPFB_PT_Add_Rig_Panel",
        "MPFB_PT_Importer_Panel",
        "MPFB_PT_Importer_Presets_Panel",
        "MPFB_PT_Presets_Panel",
        #"MPFB_PT_Targets_Panel",
        #"MPFB_PT_Clothes_Panel",
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
        "MPFB_PT_Export_Panel",
        "MPFB_PT_Skin_Editor_Panel",
        "MPFB_PT_Hair_Editor_Panel",
        "MPFB_PT_Ai_Panel"
        ]
else:
    from mpfb.ui.versionpanel import *
    __all__ = [
        "MPFB_PT_Version_Panel"
        ]