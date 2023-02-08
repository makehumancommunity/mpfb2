import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureEars(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_ears.jpg", "NodeWrapperMpfbSystemValueTextureEars")

NodeWrapperMpfbSystemValueTextureEars = _NodeWrapperMpfbSystemValueTextureEars()
