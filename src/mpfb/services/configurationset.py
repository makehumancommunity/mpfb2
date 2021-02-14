
from abc import ABC, abstractmethod
import json

from .logservice import LogService
_LOG = LogService.get_logger("configuration.configurationset")


class ConfigurationSet(ABC):

    @abstractmethod
    def get_value(self, name, default_value=None, entity_reference=None):
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def set_value(self, name, value, entity_reference=None):
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def get_keys(self):
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def has_key(self, name):
        raise NotImplementedError('This method should be overridden by subclasses')

    @abstractmethod
    def has_key_with_value(self, name, entity_reference=None):
        raise NotImplementedError('This method should be overridden by subclasses')

    def as_dict(self, entity_reference=None, exclude_keys=None, json_with_overrides=None):
        _LOG.enter()
        out = dict()
        json_data = None
        if not json_with_overrides is None:
            with open(json_with_overrides, "r") as json_file:
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
        _LOG.enter()
        values = self.as_dict(entity_reference=entity_reference, exclude_keys=exclude_keys)
        with open(json_file_path, "w") as json_file:
            json.dump(values, json_file, indent=4, sort_keys=True)

    def deserialize_from_json(self, json_file_path, entity_reference=None):
        _LOG.enter()
        json_data = None
        with open(json_file_path, "r") as json_file:
            json_data = json.load(json_file)
        if not json_data is None:
            for key in self.get_keys():
                if key in json_data:
                    self.set_value(key, json_data[key], entity_reference)
