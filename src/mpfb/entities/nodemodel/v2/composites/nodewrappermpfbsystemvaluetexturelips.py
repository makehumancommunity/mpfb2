import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureLips(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_lips.jpg", "IsLips", "NodeWrapperMpfbSystemValueTextureLips")

NodeWrapperMpfbSystemValueTextureLips = _NodeWrapperMpfbSystemValueTextureLips()
