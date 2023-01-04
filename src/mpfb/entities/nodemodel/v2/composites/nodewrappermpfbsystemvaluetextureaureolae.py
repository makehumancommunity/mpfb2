import bpy, json

from .nodewrappermpfbsystemvaluetexture import NodeWrapperMpfbSystemValueTexture

class _NodeWrapperMpfbSystemValueTextureAureolae(NodeWrapperMpfbSystemValueTexture):
    def __init__(self):
        print("\n\n--- YYY ---\n")
        NodeWrapperMpfbSystemValueTexture.__init__(self, "mpfb_aureolae.jpg", "IsAureolae", "NodeWrapperMpfbSystemValueTextureAureolae")

NodeWrapperMpfbSystemValueTextureAureolae = _NodeWrapperMpfbSystemValueTextureAureolae()
