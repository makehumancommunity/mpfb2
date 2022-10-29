from mpfb.services.logservice import LogService
from .abstractsystemvaluetexture import MpfbAbstractSystemValueTexture

import bpy, os

_LOG = LogService.get_logger("nodemodel.systemvaluetexturetoenails")
_GROUP_NAME = "MpfbSystemValueTextureToenails"
_IMAGE_FILE_NAME = "mpfb_toenails.jpg"

class MpfbSystemValueTextureToenails(MpfbAbstractSystemValueTexture):
    def __init__(self):
        _LOG.trace("Constructing system image for ", _IMAGE_FILE_NAME)
        MpfbAbstractSystemValueTexture.__init__(self, _GROUP_NAME, _IMAGE_FILE_NAME)

