from mpfb.services.logservice import LogService
from .abstractsystemvaluetexture import MpfbAbstractSystemValueTexture

import bpy, os

_LOG = LogService.get_logger("nodemodel.systemvaluetexturecrotch")
_GROUP_NAME = "MpfbSystemValueTextureCrotch"
_IMAGE_FILE_NAME = "mpfb_crotch.jpg"

class MpfbSystemValueTextureCrotch(MpfbAbstractSystemValueTexture):
    def __init__(self):
        _LOG.trace("Constructing system image for ", _IMAGE_FILE_NAME)
        MpfbAbstractSystemValueTexture.__init__(self, _GROUP_NAME, _IMAGE_FILE_NAME)

