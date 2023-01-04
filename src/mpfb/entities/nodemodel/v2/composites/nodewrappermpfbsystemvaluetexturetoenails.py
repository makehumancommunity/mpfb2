import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureToenails(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_toenails.jpg", "IsToenails", "NodeWrapperMpfbSystemValueTextureToenails")

NodeWrapperMpfbSystemValueTextureToenails = _NodeWrapperMpfbSystemValueTextureToenails()
