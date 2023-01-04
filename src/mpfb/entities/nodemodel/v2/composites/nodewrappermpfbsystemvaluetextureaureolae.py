import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureAureolae(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_aureolae.jpg", "NodeWrapperMpfbSystemValueTextureAureolae")

NodeWrapperMpfbSystemValueTextureAureolae = _NodeWrapperMpfbSystemValueTextureAureolae()
