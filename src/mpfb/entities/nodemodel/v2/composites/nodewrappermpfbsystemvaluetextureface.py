import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureFace(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_face.jpg", "NodeWrapperMpfbSystemValueTextureFace")

NodeWrapperMpfbSystemValueTextureFace = _NodeWrapperMpfbSystemValueTextureFace()
