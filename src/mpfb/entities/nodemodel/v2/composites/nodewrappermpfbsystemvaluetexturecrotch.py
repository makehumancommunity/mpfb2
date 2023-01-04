import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureCrotch(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_crotch.jpg", "IsCrotch", "NodeWrapperMpfbSystemValueTextureCrotch")

NodeWrapperMpfbSystemValueTextureCrotch = _NodeWrapperMpfbSystemValueTextureCrotch()
