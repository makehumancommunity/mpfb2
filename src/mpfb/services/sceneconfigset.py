"""Extra functionality for storing configuration settings on blender scenes"""

import bpy
from .logservice import LogService
_LOG = LogService.get_logger("configuration.sceneconfigset")

from .blenderconfigset import BlenderConfigSet


class SceneConfigSet(BlenderConfigSet):

    """Specific management of configuration when the storage entity is the scene"""

    def __init__(self, properties, prefix=""):
        _LOG.debug("Constructing new scene config set with prefix", prefix)
        BlenderConfigSet.__init__(self, properties, bpy.types.Scene, prefix)

    def check_and_transform_entity_reference(self, entity_reference):
        """
        Validates and transforms the entity reference to ensure it matches the expected Blender scene type.

        Args:
            entity_reference: The entity reference to check and transform.

        Returns:
            The validated and transformed entity reference.
        """
        if isinstance(entity_reference, bpy.types.Context):
            entity_reference = entity_reference.scene
        return BlenderConfigSet.check_and_transform_entity_reference(self, entity_reference)

    @staticmethod
    def from_definitions_in_json_directory(properties_dir, prefix=""):
        """
        Creates a SceneConfigSet instance from property definitions in a specified directory.

        Args:
            properties_dir (str): The directory containing JSON files with property definitions.
            prefix (str, optional): A prefix to add to the property names.

        Returns:
            SceneConfigSet: An instance of SceneConfigSet with properties loaded from the JSON files.
        """
        known_properties = BlenderConfigSet.get_definitions_in_json_directory(properties_dir)
        return SceneConfigSet(known_properties, prefix)
