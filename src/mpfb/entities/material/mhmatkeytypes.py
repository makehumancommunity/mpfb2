"""The parser class hierarchy for the key/value lines of an MHMAT material file."""

import re
import typing
from typing import Any

MhMatValue = str | float | bool | list[float] | list[str] | None
"""Every value an ``MhMatKey`` subclass can parse out of an MHMAT line.

Which member of the union a given key yields is decided by the key's class and nothing else:
``MhMatStringKey`` and ``MhMatFileKey`` give a ``str``, ``MhMatFloatKey`` a ``float``,
``MhMatColorKey`` a three element ``list[float]``, ``MhMatStringShaderKey`` a two element
``list[str]``, and the two boolean classes a ``bool``.

``None`` is a member because every ``parse()`` in the hierarchy returns ``(key_name, None)`` when
its own regular expression does not match the line it was handed -- which happens for a key line
carrying no value at all, since the key name alone satisfies ``line_matches_key()`` but not the
``([a-zA-Z]+)\\s+(.*)`` pattern. The two boolean classes can additionally return the empty string,
for a line whose value is whitespace only, so their declared value type is wider than ``bool``.

A union rather than ``Any`` so that the ``None`` stays visible at the call sites: ``MhMaterial``
reads the second element of the tuple without testing it in three places."""


class MhMatKey:

    """One MHMAT key: its name, its group and how to parse its value out of a line.

    This is the abstract base of the hierarchy. It can match a line against its own key name and
    serialise a value back to a string, but ``parse()`` raises, so a usable key is always one of
    the subclasses below."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various") -> None:
        self.key_name: str = key_name
        self.default_value: Any = default_value
        self.key_name_lower: str = key_name.lower()
        self.key_group: str = key_group

    def line_matches_key(self, input_line: str | None) -> bool:
        """Return True if the line starts with this key's name, ignoring case."""
        if not input_line:
            return False
        line = str(input_line).lower()
        return line.startswith(self.key_name_lower)

    def parse(self, input_line: str) -> tuple[str, MhMatValue]:
        """Parse the value out of a line and return it together with this key's name.

        Must be overridden; the base implementation raises ``ValueError``. An override returns
        ``(key_name, None)`` when the line does not carry a value it can read."""
        raise ValueError('parse() should be overridden by specific key classes')

    def as_string(self, value: Any) -> str:
        """Serialise a parsed value back to the text that would appear after the key name."""
        return str(value)

# parse lines like name, description
#


class MhMatStringKey(MhMatKey):

    """A key whose value is everything after the key name, taken verbatim."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, str | None]:
        line = str(input_line).strip()
        value: str | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
        return self.key_name, value

# parse filenames like diffuseTexture, normalmapTexture ...
#
# a path could be:
#   * absolute filepath
#   * relative filepath like "materials/clothname.png"
#   * a filename
#


class MhMatFileKey(MhMatKey):

    """A key whose value is a file path, resolved against the directory of the material file.

    The inherited ``parse()`` is not overridden and still raises, so a caller holding one of these
    has to call ``parse_file()`` instead. ``MhMaterial._parse_material_line()`` does exactly that,
    on an ``isinstance`` test."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various", blendMaterial: bool = False) -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)
        self.blendMaterial: bool = blendMaterial

    def parse_file(self, input_line: str, location: str) -> tuple[str, str]:
        """Parse a path out of a line, made absolute against location, and return it with this key's name."""
        line = str(input_line).strip()
        value: str | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
        # A key line with no value after the key name -- "diffuseTexture" on its own, or with only
        # trailing whitespace, which the strip() above removes -- satisfies line_matches_key() but
        # not the regex, so value is still None at this point. Every read below is unguarded, so
        # such a line raises AttributeError here rather than returning (key_name, None) the way
        # each sibling parse() does for the same input. The cast records that assumption in one
        # place; adding the "if value is not None" guard the siblings have is a logic change rather
        # than an annotation, so it is left as it stands.
        value = typing.cast(str, value)
        if not self.blendMaterial:
            if not value.startswith("/"):
                value = location + "/" + value
        else:
            # TODO: handle case where location is absolute. We cannot use basename since the path
            # TODO: continues into the structure of the file
            value = location + "/" + value
        value = value.replace("\\\\", "/") # Try to avoid windows style slashes
        value = value.replace("\\", "/")
        return self.key_name, value


class MhMatFloatKey(MhMatKey):

    """A key whose value is a single float."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, float | None]:
        line = str(input_line).strip()
        value: float | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                # float() is unguarded, so a value which is not a number raises ValueError out of
                # the whole material load rather than being reported as an unparseable line.
                value = float(str(match.group(2)).strip())
        return self.key_name, value

    def as_string(self, value: float) -> str:
        return "%.4f" % value


class MhMatBooleanKey(MhMatKey):

    """A key whose value is a boolean, written as true/t/1 for True and anything else for False.

    The declared value type is wider than ``bool`` on purpose: a line whose value is whitespace
    only yields the empty string rather than ``False``, and a line with no value at all yields
    ``None``. Both are falsy, which is why the distinction has never mattered to a caller."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, bool | str | None]:
        line = str(input_line).strip()
        value: bool | str | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip().lower()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.key_name, value


class MhMatColorKey(MhMatKey):

    """A key whose value is three space separated floats, read as an RGB triplet."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Various") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, list[float] | None]:
        line = str(input_line).strip()
        value: list[float] | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$', line)
            if match:
                red = float(str(match.group(2)).strip())
                green = float(str(match.group(3)).strip())
                blue = float(str(match.group(4)).strip())
                value = [red, green, blue]
        return self.key_name, value

    def as_string(self, value: typing.Sequence[float]) -> str:
        return "%.4f %.4f %.4f" % (value[0], value[1], value[2])


class MhMatStringShaderKey(MhMatKey):

    """A shader key written as "key subkey value", parsed into the pair [subkey, value]."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Shader") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, list[str] | None]:
        line = str(input_line).strip()
        value: list[str] | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                subkey = str(match.group(2))
                ivalue = str(match.group(3)).strip()
                value = [subkey, ivalue]
        return self.key_name, value


class MhMatBooleanShaderKey(MhMatKey):

    """A shader key written as "key subkey boolvalue", parsed into just the boolean.

    The declared value type is wider than ``bool`` for the same reason as ``MhMatBooleanKey``'s,
    although the regex here cannot in fact produce the empty string, since it requires a
    non-whitespace third token."""

    def __init__(self, key_name: str, default_value: Any = None, key_group: str = "Shader") -> None:
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line: str) -> tuple[str, bool | str | None]:
        line = str(input_line).strip()
        value: bool | str | None = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                value = str(match.group(3)).strip()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.key_name, value
