"""Icons for the modeling panels"""

from mpfb.services.locationservice import LocationService
from mpfb.services.logservice import LogService
import bpy.utils.previews
import os, re

_LOG = LogService.get_logger("model.modelingicons")

MODELING_ICONS = bpy.utils.previews.new()

_TARGETS_DIR = LocationService.get_mpfb_data("targets")
_IMAGES_DIR = os.path.join(_TARGETS_DIR, "_images")

for image in os.listdir(_IMAGES_DIR):
    if ".png" in image:
        name = re.sub(r"\.png$", "", image)
        name = re.sub("^r-", "", name)
        name = re.sub("^l-", "", name)
        image_path = os.path.join(_IMAGES_DIR, image)
        _LOG.debug("Will try to load icon", (name, image_path))
        MODELING_ICONS.load(name, image_path, 'IMAGE')
