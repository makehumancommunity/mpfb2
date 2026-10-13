
from .logservice import LogService

from collections.abc import Sequence
from typing import Any
import re
import json

_LOG = LogService.get_logger("entities.jsoncall")


class JsonCall():

    def __init__(self, function: str, params: dict[str, Any] | None = None, data: Any = None) -> None:
        _LOG.debug("Constructing new jsoncall object for function", function)
        self.params: dict[str, Any]
        if params is None:
            self.params = {}
        else:
            self.params = params
        self.data: Any = data
        self.function: str = function
        self.error: str = ""

    def populate_from_json(self, json_data: str) -> None:
        _LOG.enter()
        json_data = json_data.replace('\\', '\\\\')  # allow windows paths in data
        j = json.loads(json_data)
        if not j:
            return
        self.function = j["function"]
        self.error = j["error"]
        if j["params"]:
            for key in j["params"]:
                self.params[key] = j["params"][key]
        if j["data"]:
            self.data = j["data"]

    def set_data(self, data: Any = "") -> None:
        _LOG.enter()
        self.data = data

    def get_data(self) -> Any:
        _LOG.enter()
        return self.data

    def set_param(self, name: str, value: Any) -> None:
        _LOG.enter()
        self.params[name] = value

    def get_param(self, name: str) -> Any:
        _LOG.enter()
        if not name in self.params:
            return None
        return self.params[name]

    def set_function(self, func: str) -> None:
        _LOG.enter()
        self.function = func

    def get_function(self) -> str:
        _LOG.enter()
        return self.function

    def set_error(self, error: str) -> None:
        _LOG.enter()
        self.error = error

    def get_error(self) -> str:
        _LOG.enter()
        return self.error

    def _guess_value_type(self, val: Any) -> str:
        _LOG.enter()
        if val is None:
            return "none"

        if self._is_dict(val):
            return "dict"

        if self._is_array(val):
            return "array"

        if self._is_numeric(val):
            return "numeric"

        return "string"

    def _is_array(self, val: Any) -> bool:
        _LOG.enter()
        return hasattr(val, '__len__') and (not isinstance(val, str))

    def _is_dict(self, val: Any) -> bool:
        _LOG.enter()
        return isinstance(val, dict)

    def _is_numeric(self, val: Any) -> bool | re.Match[str] | None:
        _LOG.enter()
        if val is None:
            return False
        if isinstance(val, int):
            return True
        if isinstance(val, float):
            return True
        num_format = re.compile(r"^[\-]?[0-9][0-9]*\.?[0-9]+$")
        isnumber = re.match(num_format, str(val))
        return isnumber

    def _number_as_string(self, val: Any) -> str:
        _LOG.enter()
        if isinstance(val, float):
            return "{0:.8f}".format(val)
        return str(val)

    def _dict_as_string(self, val: dict[str, Any]) -> str:
        _LOG.enter()
        ret = "{ "

        first = True

        for key in val.keys():
            if first:
                first = False
            else:
                ret = ret + ", "
            ret = ret + self.python_value_to_json_value(val[key], key)

        return ret + " }"

    def _array_as_string(self, array: Sequence[Any]) -> str:
        _LOG.enter()
        ret = "[ "
        for i in range(len(array)):
            val = array[i]
            ret = ret + self.python_value_to_json_value(val)
            if i + 1 < len(array):
                ret += ","
        return ret + " ]"

    def python_value_to_json_value(self, val: Any, key_name: str | None = None) -> str:
        _LOG.enter()
        out = ""

        if key_name:
            out = "\"" + key_name + "\": "

        variable_type = self._guess_value_type(val)

        if val is None:
            return out + "null"

        if variable_type == "dict":
            return out + self._dict_as_string(val)

        if variable_type == "array":
            return out + self._array_as_string(val)

        if variable_type == "numeric":
            return out + self._number_as_string(val)

        return out + "\"" + str(val) + "\""

    def serialize(self) -> str:
        _LOG.enter()
        ret = "{\n"
        ret = ret + "  \"function\": \"" + self.function + "\",\n"
        ret = ret + "  \"error\": \"" + self.error + "\",\n"
        ret = ret + "  \"params\": {\n"

        first = True

        for key in self.params.keys():
            if not first:
                ret = ret + ",\n"
            else:
                first = False
            ret = ret + "    " + self.python_value_to_json_value(self.params[key], key)

        ret = ret + "\n  },\n"

        ret = ret + "  " + self.python_value_to_json_value(self.data, "data") + "\n}\n"

        return ret.replace('\\', '\\\\')  # allow windows paths in data

