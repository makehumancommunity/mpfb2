from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from .molecule import Molecule

import bpy, os

_LOG = LogService.get_logger("nodemodel.abstractsystemvaluetexture")
_GROUP_NAME = "MpfbAbstractSystemValueTexture"

class MpfbAbstractSystemValueTexture(Molecule):
    def __init__(self, group_name, image_file_name):
        _GROUP_NAME = group_name
        self.image_file_name = image_file_name
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [346.0, 291.0]
        nodes["Group Input"].location = [-582.0, 1.0]

        self.add_output_socket("Value", socket_type="NodeSocketFloat", default_value=0.0)

        nodes["RGB to BW"] = self.createShaderNodeRGBToBW(name="RGB to BW", x=136.442, y=289.840, Color=[0.5, 0.5, 0.5, 1.0])
        nodes["Image Texture"] = self.createShaderNodeTexImage(name="Image Texture", x=-148.694, y=263.259)
        nodes["Texture Coordinate"] = self.createShaderNodeTexCoord(name="Texture Coordinate", x=-348.877, y=85.026)

        self.add_link(nodes["RGB to BW"], "Val", nodes["Group Output"], "Value")
        self.add_link(nodes["Texture Coordinate"], "UV", nodes["Image Texture"], "Vector")
        self.add_link(nodes["Image Texture"], "Color", nodes["RGB to BW"], "Color")

        textures_dir = LocationService.get_mpfb_data("textures")
        image_path_absolute = os.path.abspath(os.path.join(textures_dir, self.image_file_name))

        if not os.path.exists(image_path_absolute):
            raise IOError(image_path_absolute + " does not exist")

        if self.image_file_name in bpy.data.images:
            _LOG.debug("image was previously loaded", image_path_absolute)
            image = bpy.data.images[self.image_file_name]
        else:
            _LOG.debug("loading image", image_path_absolute)
            image = bpy.data.images.load(image_path_absolute)
            image.colorspace_settings.name = "sRGB"

        nodes["Image Texture"].image = image