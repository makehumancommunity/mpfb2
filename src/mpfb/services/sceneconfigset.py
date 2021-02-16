
import bpy, os, json
from fnmatch import fnmatch
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from .logservice import LogService
_LOG = LogService.get_logger("configuration.sceneconfigset")

from .blenderconfigset import BlenderConfigSet

class SceneConfigSet(BlenderConfigSet):

    def __init__(self, properties, prefix=""):
        _LOG.debug("Constructing new scene config set with prefix", prefix)
        BlenderConfigSet.__init__(self, properties, bpy.types.Scene, prefix)

    def check_and_transform_entity_reference(self, entity_reference):
        if isinstance(entity_reference, bpy.types.Context):
            entity_reference = entity_reference.scene
        return BlenderConfigSet.check_and_transform_entity_reference(self, entity_reference)

    @staticmethod
    def from_definitions_in_json_directory(properties_dir, prefix=""):
        known_properties = BlenderConfigSet.get_definitions_in_json_directory(properties_dir)
        return SceneConfigSet(known_properties, prefix)
