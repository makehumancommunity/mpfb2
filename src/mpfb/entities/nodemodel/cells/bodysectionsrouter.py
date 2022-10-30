from mpfb.services.logservice import LogService
from .cell import Cell

import bpy

_LOG = LogService.get_logger("nodemodel.bodysectionsrouter")
_GROUP_NAME = "MpfbBodySectionsRouter"

class MpfbBodySectionsRouter(Cell):
    def __init__(self):
        _LOG.trace("Constructing Cell for", _GROUP_NAME)
        Cell.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [682.2594604492188, -0.0]
        nodes["Group Input"].location = [-813.1845092773438, -11.987015724182129]

        self.add_input_socket("DefaultBodyShader", socket_type="NodeSocketShader")
        self.add_input_socket("AureolaeShader", socket_type="NodeSocketShader")
        self.add_input_socket("FaceShader", socket_type="NodeSocketShader")
        self.add_input_socket("LipsShader", socket_type="NodeSocketShader")
        self.add_input_socket("FingernailsShader", socket_type="NodeSocketShader")
        self.add_input_socket("ToenailsShader", socket_type="NodeSocketShader")

        self.add_output_socket("Shader", socket_type="NodeSocketShader")

        nodes["Mix Shader.001"] = self.createShaderNodeMixShader(name="Mix Shader.001", x=-90.473, y=188.499, Fac=0.5)
        nodes["IsLips"] = self.createMpfbSystemValueTextureLips(name="IsLips", label="IsLips", x=-94.044, y=50.065)
        nodes["IsAureolae"] = self.createMpfbSystemValueTextureAureolae(name="IsAureolae", label="IsAureolae", x=-492.259, y=446.288)
        nodes["IsFace"] = self.createMpfbSystemValueTextureFace(name="IsFace", label="IsFace", x=-299.458, y=204.701)
        nodes["IsFingernails"] = self.createMpfbSystemValueTextureFingernails(name="IsFingernails", label="IsFingernails", x=94.169, y=-115.643)
        nodes["Mix Shader.003"] = self.createShaderNodeMixShader(name="Mix Shader.003", x=303.818, y=-212.432, Fac=0.5)
        nodes["IsToenails"] = self.createMpfbSystemValueTextureToenails(name="IsToenails", label="IsToenails", x=304.451, y=-354.752)
        nodes["Mix Shader"] = self.createShaderNodeMixShader(name="Mix Shader", x=-298.634, y=337.685, Fac=0.5)
        nodes["Mix Shader.002"] = self.createShaderNodeMixShader(name="Mix Shader.002", x=92.224, y=19.735, Fac=0.5)
        nodes["Mix Shader.004"] = self.createShaderNodeMixShader(name="Mix Shader.004", x=492.259, y=-446.288, Fac=0.5)

        self.add_link(nodes["Mix Shader.004"], "Shader", nodes["Group Output"], "Shader")
        self.add_link(nodes["IsAureolae"], "Output_0", nodes["Mix Shader"], "Fac")
        self.add_link(nodes["Mix Shader"], "Shader", nodes["Mix Shader.001"], "Shader")
        self.add_link(nodes["IsFace"], "Output_0", nodes["Mix Shader.001"], "Fac")
        self.add_link(nodes["IsLips"], "Output_0", nodes["Mix Shader.002"], "Fac")
        self.add_link(nodes["Mix Shader.001"], "Shader", nodes["Mix Shader.002"], "Shader")
        self.add_link(nodes["IsFingernails"], "Output_0", nodes["Mix Shader.003"], "Fac")
        self.add_link(nodes["Mix Shader.002"], "Shader", nodes["Mix Shader.003"], "Shader")
        self.add_link(nodes["Mix Shader.003"], "Shader", nodes["Mix Shader.004"], "Shader")
        self.add_link(nodes["IsToenails"], "Output_0", nodes["Mix Shader.004"], "Fac")
        self.add_link(nodes["Group Input"], "DefaultBodyShader", nodes["Mix Shader"], "Shader")
        self.add_link(nodes["Group Input"], "AureolaeShader", nodes["Mix Shader"], "Shader_001")
        self.add_link(nodes["Group Input"], "FaceShader", nodes["Mix Shader.001"], "Shader_001")
        self.add_link(nodes["Group Input"], "LipsShader", nodes["Mix Shader.002"], "Shader_001")
        self.add_link(nodes["Group Input"], "FingernailsShader", nodes["Mix Shader.003"], "Shader_001")
        self.add_link(nodes["Group Input"], "ToenailsShader", nodes["Mix Shader.004"], "Shader_001")



# --- paste this in the CellNodeManager class def
#
#     def createMpfbBodySectionsRouter(self, x=0.0, y=0.0, name=None, label=None, DefaultBodyShader=None, AureolaeShader=None, FaceShader=None, LipsShader=None, FingernailsShader=None, ToenailsShader=None):
#         return self._cell_singletons["MpfbBodySectionsRouter"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, DefaultBodyShader=DefaultBodyShader, AureolaeShader=AureolaeShader, FaceShader=FaceShader, LipsShader=LipsShader, FingernailsShader=FingernailsShader, ToenailsShader=ToenailsShader)
