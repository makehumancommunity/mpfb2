"""Fundamental functionality for managing configuration settings."""

from abc import ABC, abstractmethod
import json

from .logservice import LogService
_LOG = LogService.get_logger("configuration.configurationset")


class ConfigurationSet(ABC):
    """The ConfigurationSet class is an abstract base class (ABC) designed to provide a standardized interface
    for managing configuration settings. It defines a set of abstract methods that must be implemented by any
    subclass, ensuring that the subclass provides specific functionality for getting, setting, and managing
    configuration keys and values. Additionally, it provides concrete methods for serializing and deserializing
    configuration data to and from JSON files."""

    @abstractmethod
    def get_value(self, name, default_value=None, entity_reference=None):
        """
        Retrieve the value of a configuration setting by its name.

        Args:
            name (str): The name of the configuration setting.
            default_value (optional): The default value to return if the setting is not found.
            entity_reference (optional): An optional reference to an entity for context.

        Returns:
            The value of the configuration setting.
        """
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def set_value(self, name, value, entity_reference=None):
        """
        Set the value of a configuration setting by its name.

        Args:
            name (str): The name of the configuration setting.
            value: The value to set for the configuration setting.
            entity_reference (optional): An optional reference to an entity for context.
        """
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def get_keys(self):
        """
        Retrieve a list of all configuration keys.

        Returns:
            list: A list of all configuration keys.
        """
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def has_key(self, name):
        """
        Check if a configuration key exists.

        Args:
            name (str): The name of the configuration key.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def has_key_with_value(self, name, entity_reference=None):
        """
        Check if a configuration key exists and has a value.

        Args:
            name (str): The name of the configuration key.
            entity_reference (optional): An optional reference to an entity for context.

        Returns:
            bool: True if the key exists and has a value, False otherwise.
        """
        raise NotImplementedError('This method should be overridden by subclasses')

    def as_dict(self, entity_reference=None, exclude_keys=None, json_with_overrides=None):
        """
        Convert the configuration settings to a dictionary.

        Args:
            entity_reference (optional): An optional reference to an entity for context.
            exclude_keys (list, optional): A list of keys to exclude from the dictionary.
            json_with_overrides (str, optional): Path to a JSON file with override values.

        Returns:
            dict: A dictionary of configuration settings.
        """
        _LOG.enter()
        out = dict()
        json_data = None
        if not json_with_overrides is None:
            with open(json_with_overrides, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)

        for key in self.get_keys():
            include = True
            if not exclude_keys is None:
                if key in exclude_keys:
                    include = False
            if include:
                out[key] = self.get_value(key, default_value=None, entity_reference=entity_reference)
                if not json_data is None and key in json_data:
                    out[key] = json_data[key]

        return out

    def serialize_to_json(self, json_file_path, entity_reference=None, exclude_keys=None):
        """
        Serialize the configuration settings to a JSON file.

        Args:
            json_file_path (str): The path to the JSON file.
            entity_reference (optional): An optional reference to an entity for context.
            exclude_keys (list, optional): A list of keys to exclude from the JSON file.
        """
        _LOG.enter()
        values = self.as_dict(entity_reference=entity_reference, exclude_keys=exclude_keys)
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(values, json_file, indent=4, sort_keys=True)

    def deserialize_from_json(self, json_file_path, entity_reference=None):
        """
        Deserialize configuration settings from a JSON file.

        Args:
            json_file_path (str): The path to the JSON file.
            entity_reference (optional): An optional reference to an entity for context.
        """
        _LOG.enter()
        json_data = None
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        if json_data is not None:
            for key in self.get_keys():
                if key in json_data:
                    self.set_value(key, json_data[key], entity_reference)
