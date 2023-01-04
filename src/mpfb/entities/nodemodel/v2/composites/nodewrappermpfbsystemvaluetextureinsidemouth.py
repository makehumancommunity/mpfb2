import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureInsideMouth(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_inside-mouth.jpg", "IsInsideMouth", "NodeWrapperMpfbSystemValueTextureInsideMouth")

NodeWrapperMpfbSystemValueTextureInsideMouth = _NodeWrapperMpfbSystemValueTextureInsideMouth()
