import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureEyelids(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_eyelids.jpg", "NodeWrapperMpfbSystemValueTextureEyelids")

NodeWrapperMpfbSystemValueTextureEyelids = _NodeWrapperMpfbSystemValueTextureEyelids()
