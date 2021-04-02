
from mpfb.services.logservice import LogService
_LOG = LogService.get_logger("ui.init")
_LOG.trace("initializing ui module")

# Model
from mpfb.ui.newhuman import *

# Imports
from mpfb.ui.importer import *
from mpfb.ui.importerpresets import *

# Rigging
from mpfb.ui.rigify import *
from mpfb.ui.righelpers import *

# Materials
from mpfb.ui.enhancedsettings import *
from mpfb.ui.eyesettings import *
from mpfb.ui.makeskin import *

# Clothes
from mpfb.ui.loadclothes import *

# Targets
from mpfb.ui.maketarget import *

# Old
#from .clothespanel import MPFB_PT_Clothes_Panel
#from .materialspanel import MPFB_PT_Materials_Panel
#from .targetspanel import MPFB_PT_Targets_Panel

# Developer
from mpfb.ui.loglevels import *
from mpfb.ui.savenodes import *

__all__ = [
    "MPFB_PT_Importer_Panel",
    "MPFB_PT_Importer_Presets_Panel",
    #"MPFB_PT_Materials_Panel",
    #"MPFB_PT_Targets_Panel",
    #"MPFB_PT_Clothes_Panel",
    "MPFB_PT_Save_Nodes_Panel",
    "MPFB_PT_RigHelpersPanel",
    "MPFB_PT_Enhanced_Settings_Panel",
    "MPFB_PT_Eye_Settings_Panel",
    "MPFB_PT_MakeSkin_Panel",
    "MPFB_PT_MakeTarget_Panel",
    "MPFB_PT_Load_Clothes_Panel",
    "MPFB_PT_Log_Levels_Panel"
    ]
