
import re


class MhMatKey:

    def __init__(self, key_name, default_value=None, key_group="Various"):
        self.key_name = key_name
        self.default_value = default_value
        self.key_name_lower = key_name.lower()
        self.key_group = key_group

    def line_matches_key(self, input_line):
        if not input_line:
            return False
        line = str(input_line).lower()
        return line.startswith(self.key_name_lower)

    def parse(self, input_line):
        raise ValueError('parse() should be overridden by specific key classes')

    def as_string(self, value):
        return str(value)

# parse lines like name, description
#


class MhMatStringKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Various"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
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

    def __init__(self, key_name, default_value=None, key_group="Various", blendMaterial=False):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)
        self.blendMaterial = blendMaterial

    def parse_file(self, input_line, location):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
        if not self.blendMaterial:
            if not value.startswith("/"):
                value = location + "/" + value
        else:
            # TODO: handle case where location is absolute. We cannot use basename since the path
            # TODO: continues into the structure of the file
            value = location + "/" + value
        return self.key_name, value


class MhMatFloatKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Various"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
                value = float(value)
        return self.key_name, value

    def as_string(self, value):
        return "%.4f" % value


class MhMatBooleanKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Various"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip().lower()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.key_name, value


class MhMatColorKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Various"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$', line)
            if match:
                red = float(str(match.group(2)).strip())
                green = float(str(match.group(3)).strip())
                blue = float(str(match.group(4)).strip())
                value = [red, green, blue]
        return self.key_name, value

    def as_string(self, value):
        return "%.4f %.4f %.4f" % (value[0], value[1], value[2])


class MhMatStringShaderKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Shader"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                subkey = str(match.group(2))
                ivalue = str(match.group(3)).strip()
                value = [subkey, ivalue]
        return self.key_name, value


class MhMatBooleanShaderKey(MhMatKey):

    def __init__(self, key_name, default_value=None, key_group="Shader"):
        MhMatKey.__init__(self, key_name=key_name, default_value=default_value, key_group=key_group)

    def parse(self, input_line):
        line = str(input_line).strip()
        value = None
        if self.line_matches_key(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                value = str(match.group(3)).strip()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.key_name, value
