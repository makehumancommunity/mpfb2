
import re, os
from .mhmatkeys import MHMAT_KEY_GROUPS, MHMAT_NAME_TO_KEY
from .mhmatkeytypes import MhMatFileKey
from mpfb.services.socketservice import SocketService
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("material.mhmaterial")

class MhMaterial:

    def __init__(self):

        self._settings = dict()
        self._shader_config = dict()

        # TODO: handle litsphere and shaderconfig
        self.lit_sphere = dict()
        self.shader_config = dict()

    def _parse_material_line(self, line):
        match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
        if match:
            key = match.group(1)
            key_lower = key.lower()
            value = None

            if key_lower in MHMAT_NAME_TO_KEY:
                key_obj = MHMAT_NAME_TO_KEY[key_lower]
                key_correct_case = key_obj.keyName
                if key != key_correct_case:
                    _LOG.debug("Autofixing case: " + key + " -> " + key_correct_case)
                    key = key_correct_case
                if isinstance(key_obj, MhMatFileKey):
                    location = None # TODO: This will crash, we need a proper location here
                    (used_key, value) = key_obj.parseFile(line, location)
                else:
                    (used_key, value) = key_obj.parse(line)
                _LOG.debug("actual key from key object", used_key)
            else:
                if key not in ["shader", "shader_config"]:
                    _LOG.warn("Not a valid key: ", key)
            #
            # handle multiple occurences of tag (create a comma-separated entry)
            #
            if key == 'tag':
                if self._settings[key]:
                    self._settings[key] += ", " + value
                else:
                    self._settings[key] = value
            elif key == 'shaderParam':
                if value[0] == "litsphereTexture":
                    match = re.search(r'^litspheres\/(.*)\.png$', value[1])
                    if match:
                        self._settings["litsphereTexture"] = match.group(1)
                        _LOG.debug("litsphereTexture", self._settings["litsphereTexture"])
            else:
                self._settings[key] = value
        else:
            if line.startswith("shader"):
                # TODO: check for shader_config, shader
                pass
            else:
                _LOG.warn("Unparseable line:", line)

    def populate_from_mhmat(self, file_name):

        full_path = os.path.abspath(file_name)
        file_location = os.path.dirname(full_path)

        with open(full_path, 'r') as f:
            line = f.readline()
            while line:
                parsed_line = line.strip()
                if parsed_line and not parsed_line.startswith("#") and not parsed_line.startswith("/"):
                    self._parse_material_line(line)
                line = f.readline()
        _LOG.dump("Final material:", self._settings)

    def _populate(self, material_info, load_mhmat_if_provided=False):
        _LOG.dump("material_info", material_info)
        if "materialFile" in material_info and str(material_info["materialFile"]).strip() and load_mhmat_if_provided:
            self.populate_from_mhmat(material_info["materialFile"])
        else:
            for key in material_info:
                if key != "materialFile":
                    self._settings[key] = material_info[key]
            _LOG.dump("Final material:", self._settings)

    def populate_from_body_material_socket_call(self, load_mhmat_if_provided=False):
        material_info = SocketService.get_body_material_info()
        self._populate(material_info, load_mhmat_if_provided)

    def populate_from_proxy_material_socket_call(self, uuid, load_mhmat_if_provided=False):
        material_info = SocketService.get_proxy_material_info(uuid)
        self._populate(material_info, load_mhmat_if_provided)

    def as_mhmat(self):
        mat = "# This is a material for MakeHuman\n"

        for key_group in MHMAT_KEY_GROUPS:
            mat = mat + "\n// " + key_group + "\n\n"
            for key_name_lower in MHMAT_NAME_TO_KEY.keys():
                key_obj = MHMAT_NAME_TO_KEY[key_name_lower]
                key_name = key_obj.keyName
                if key_obj.keyGroup == key_group and not self._settings[key_name] is None:
                    if key_name == "tag":
                        for elem in self._settings["tag"].split(","):
                            mat = mat + "tag " + elem.strip() + "\n"
                    else:
                        mat = mat + key_name + " " + key_obj.asString(self._settings[key_name]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Shader properties (only affects how things look in MakeHuman)\n\n"

        if self.lit_sphere:
            mat = mat + "shader shaders/glsl/litsphere\n"
            mat = mat + "shaderParam litsphereTexture litspheres/" + str(self.lit_sphere) + ".png\n"
        for key in self.shader_config.keys():
            mat = mat + "shader_config " + key + " " + str(self.shader_config[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// The following settings would also have been valid, but do currently not have a value\n//\n"
        for key_name in MHMAT_NAME_TO_KEY.keys():
            key_obj = MHMAT_NAME_TO_KEY[key_name]
            key = key_obj.keyName
            if key not in self._settings or self._settings[key] is None:
                mat = mat + "// " + key + "\n"

        return mat
