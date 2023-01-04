import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureFingernails(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_fingernails.jpg", "NodeWrapperMpfbSystemValueTextureFingernails")

NodeWrapperMpfbSystemValueTextureFingernails = _NodeWrapperMpfbSystemValueTextureFingernails()
