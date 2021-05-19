from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("ui.init")
_LOG.trace("initializing ui module")

# Top level panels
from mpfb.ui.newpanel import *
from mpfb.ui.model import *
from mpfb.ui.assetspanel import *
#from mpfb.ui.materialspanel import *
from mpfb.ui.presetspanel import *
from mpfb.ui.rigpanel import *
from mpfb.ui.createpanel import *
from mpfb.ui.systempanel import *

# New human panels
from mpfb.ui.newhuman import *
from mpfb.ui.importer import *
from mpfb.ui.importerpresets import *

# Create assets panels
from mpfb.ui.makeskin import *
from mpfb.ui.maketarget import *
from mpfb.ui.makeclothes import *

# Rig panels
from mpfb.ui.addrig import *
from mpfb.ui.rigify import *
from mpfb.ui.righelpers import *

# Presets
from mpfb.ui.humanpresets import *
from mpfb.ui.enhancedsettings import *
from mpfb.ui.eyesettings import *

# Assets
from mpfb.ui.assetlibrary import *
from mpfb.ui.loadclothes import *

# System
from mpfb.ui.webresources import *
from mpfb.ui.dirresources import *

# Targets

# Old
#from .clothespanel import MPFB_PT_Clothes_Panel
#from .materialspanel import MPFB_PT_Materials_Panel
#from .targetspanel import MPFB_PT_Targets_Panel

# Developer
from mpfb.ui.developer import *

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
    "MPFB_PT_Devloper_Panel"
    ]
