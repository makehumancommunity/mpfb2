import os, json, shutil
from pathlib import Path
from .mhmaterial import MhMaterial
from .mhmatkeys import MHMAT_KEYS
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService

_LOG = LogService.get_logger("material.makeskinmaterial")

_TEXTURE_NAMES = [
    "bumpmap",
    "diffuse",
    "displacementmap",
    "metallicmap",
    "normalmap",
    "roughnessmap",
    "transmissionmap",
    "aomap",
    "emissioncolormap",
    "emissionstrengthmap",
    "subsurfacecolormap",
    "subsurfacestrengthmap",
    "specularmap"]

_NODE_SOCKET_VALUES = [] # key name, node name, socket name
_NODE_SOCKET_VALUES.append(["diffuseColor", "Principled BSDF", "Base Color"]) # First pick up color from principled
_NODE_SOCKET_VALUES.append(["diffuseColor", "diffuseIntensity", "Color1"]) # Then overwrite with intensity node if any
_NODE_SOCKET_VALUES.append(["diffuseIntensity", "diffuseIntensity", "Fac"])
_NODE_SOCKET_VALUES.append(["bumpmapIntensity", "bumpmap", "Strength"])
_NODE_SOCKET_VALUES.append(["normalmapIntensity", "normalmap", "Strength"])
_NODE_SOCKET_VALUES.append(["displacementmapIntensity", "displacementmap", "Scale"])
_NODE_SOCKET_VALUES.append(["metallic", "Principled BSDF", "Metallic"])
_NODE_SOCKET_VALUES.append(["ior", "Principled BSDF", "IOR"])
_NODE_SOCKET_VALUES.append(["roughness", "Principled BSDF", "Roughness"])

class MakeSkinMaterial(MhMaterial):

    def __init__(self, importer_presets=None):
        MhMaterial.__init__(self)
        self.presets = importer_presets

    def _template(self, template_values, has, tex, key):
        template_values[has] = "false"
        template_values[tex] = "\"\""
        setting = self.get_value(key)
        if setting:
            _LOG.debug(key + " is set in mhmat", setting)
            setting = setting.replace("\\\\", "/")
            setting = setting.replace("\\", "/")
            template_values[has] = "true"
            template_values[tex] = "\"" + setting + "\""
        else:
            _LOG.debug(key + " is not set in mhmat")

    def apply_node_tree(self, blender_material, template_values=None):
        tree_dir = LocationService.get_mpfb_data("node_trees")
        json_file = os.path.join(tree_dir, "makeskin.json")

        if template_values is None:
            template_values = dict()
            self._template(template_values, "has_bumpmap", "bumpmap_filename", "bumpMapTexture")
            self._template(template_values, "has_diffuse", "diffuse_filename", "diffuseTexture")
            self._template(template_values, "has_displacementmap", "displacementmap_filename", "displacementMapTexture")
            self._template(template_values, "has_metallicmap", "metallicmap_filename", "metallicMapTexture")
            self._template(template_values, "has_normalmap", "normalmap_filename", "normalMapTexture")
            self._template(template_values, "has_roughnessmap", "roughnessmap_filename", "roughnessMapTexture")
            self._template(template_values, "has_transmissionmap", "transmissionmap_filename", "transmissionMapTexture")
            self._template(template_values, "has_ao", "ao_filename", "aomapTexture")
            self._template(template_values, "has_emc", "emc_filename", "emissionColorMapTexture")
            self._template(template_values, "has_ems", "ems_filename", "emissionStrengthMapTexture")
            self._template(template_values, "has_subc", "subc_filename", "subsurfaceColorMapTexture")
            self._template(template_values, "has_subs", "subs_filename", "subsurfaceStrengthMapTexture")
            self._template(template_values, "has_specularmap", "specularmap_filename", "specularMapTexture")
            

        template_values["bump_or_normal"] = "false"
        if template_values["has_bumpmap"] == "true":
            template_values["bump_or_normal"] = "true"
        if template_values["has_normalmap"] == "true":
            template_values["bump_or_normal"] = "true"

        _LOG.dump("template_values", template_values)

        color_keys = {
            "diffuseColor": "[0.5, 0.5, 0.5, 1.0]"
        }
        for key in color_keys.keys():
            if not key in template_values:
                value = self.get_value(key)
                if value:
                    if len(value) < 4:
                        value.append(1.0)
                    template_values[key] = str(value)
                else:
                    template_values[key] = color_keys[key]

        template_data = Path(json_file).read_text()
        for key in template_values:
            template_data = template_data.replace("\"$" + key + "\"", template_values[key])

        _LOG.dump("Template data", template_data)

        node_tree_dict = dict()
        parse_error = None

        try:
            node_tree_dict = json.loads(template_data)
        except Exception as exc:
            _LOG.error("An error was thrown when trying to parse the template data:", exc)
            _LOG.error("Full contents of template data", "\n\n" + str(template_data) + "\n\n")
            parse_error = "Failed to parse material: " + str(exc) + ". See material.makeskinmaterial log for more info."

        if not parse_error is None:
            raise ValueError(parse_error)

        _LOG.dump("node_tree", node_tree_dict)

        NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict, True)

    def _set_texture(self, node_tree, name):
        _LOG.enter()
        node = NodeService.find_node_by_name(node_tree, name)
        _LOG.debug("expected_name, node", (name, node))
        self._settings[name] = None
        if not node is None:
            node_info = NodeService.get_node_info(node)
            if "filename" in node_info and node_info["filename"]:
                self._settings[name] = node_info["filename"]
            else:
                _LOG.warn("The following texture node did not have an image file, so cannot set a MHMAT key for it", name)
        else:
            _LOG.debug("Could not find a node for", name)

    def _set_config_value(self, blender_object, expected_name):
        from mpfb.ui.makeskin import MakeSkinObjectProperties
        if MakeSkinObjectProperties.has_key(expected_name):
            self._settings[expected_name] = MakeSkinObjectProperties.get_value(expected_name, entity_reference=blender_object)

    def populate_from_object(self, blender_object):
        blender_material = blender_object.material_slots[0].material

        key_by_name = dict()

        for key in MHMAT_KEYS:
            _LOG.debug("key", (key.key_name, key.default_value, key.key_group))
            self._settings[key.key_name] = key.default_value
            key_by_name[key.key_name] = key
            if key.key_group == "Texture":
                self._set_texture(blender_material.node_tree, key.key_name)
            if key.key_group in ["Metadata", "Various"]:
                self._set_config_value(blender_object, key.key_name)

        for nsv in _NODE_SOCKET_VALUES:
            setting_name = nsv[0]
            node_name = nsv[1]
            socket_name = nsv[2]

            node = NodeService.find_node_by_name(blender_material.node_tree, node_name)
            if node:
                socket_values = NodeService.get_socket_default_values(node)
                if socket_values and socket_name in socket_values:
                    self._settings[setting_name] = socket_values[socket_name]

        from mpfb.ui.makeskin import MakeSkinObjectProperties
        if MakeSkinObjectProperties.get_value("sss_enable", entity_reference=blender_object):
            self._settings["sssEnabled"] = True
            node = NodeService.find_node_by_name(blender_material.node_tree, "Principled BSDF")
            socket_values = NodeService.get_socket_default_values(node)
            radius = socket_values["Subsurface Radius"]
            self._settings["sssRScale"] = radius[0]
            self._settings["sssGScale"] = radius[1]
            self._settings["sssBScale"] = radius[2]
        else:
            self._settings["sssEnabled"] = False

        _LOG.dump("\n\n\nRESULTS, POPULATE FROM OBJECT\n\n\n", self._settings)

    def check_that_all_textures_are_saved(self, blender_object):
        material = blender_object.material_slots[0].material
        node_tree = material.node_tree

        for texture_name_base in _TEXTURE_NAMES:
            texture_name = texture_name_base + "Texture"
            node = NodeService.find_node_by_name(node_tree, texture_name)
            _LOG.debug("texture name, node", (texture_name, node))
            if node:
                # The material has this kind of texture, check that its image exists
                node_info = NodeService.get_node_info(node)
                if not "filename" in node_info or not node_info["filename"]:
                    return "The " + texture_name + " node has an unsaved image"
                if not os.path.exists(node_info["filename"]):
                    return "The " + texture_name + " refers to an image which does not exist as a file"
            else:
                # The material isn't using this kind of texture
                _LOG.debug("No node was found for", texture_name)

        return None

    def export_to_disk(self, mhmat_path, normalize_textures=True):
        if normalize_textures:
            mhmat_loc = os.path.dirname(mhmat_path)
            mhmat_base = str(os.path.basename(mhmat_path)).replace(".mhmat", "").replace(" ", "_")
            for key in self._settings:
                if key.endswith("Texture") and self._settings[key] and not "litsphere" in key:
                    textureType = "_" + key.replace("Texture", "")
                    src = self._settings[key]
                    fn, ext = os.path.splitext(src)
                    dest = os.path.join(mhmat_loc, mhmat_base + textureType + ext)
                    _LOG.debug("src, dest", (src, dest))
                    shutil.copy(src, dest)
                    newfn = os.path.basename(dest)
                    self._settings[key] = newfn

        mhmat_string = self.as_mhmat()
        _LOG.dump("material", mhmat_string)
        with open(mhmat_path, "w") as mhmat:
            mhmat.write(mhmat_string)

    # TODO: Method for writing MHMAT attributes as BlenderConfigSet attributes

    @staticmethod
    def create_makeskin_template_material(blender_object, scene, name="MakeSkinMaterial"):

        from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES

        if blender_object is None:
            raise ValueError('Must provide an object')
        if MaterialService.has_materials(blender_object) and not MAKESKIN_PROPERTIES.get_value("overwrite", entity_reference=scene):
            raise ValueError('Object already has material')
        if scene is None:
            raise ValueError('Must provide a scene')

        template_values = dict()
        for part in _TEXTURE_NAMES:
            _LOG.debug("part", part)
            if MAKESKIN_PROPERTIES.get_value("create_" + part, entity_reference=scene):
                template_values["has_" + part] = "true"
            else:
                template_values["has_" + part] = "false"
            template_values[part + "_filename"] = "\"\""

        _LOG.debug("Template values", template_values)

        material = MaterialService.create_empty_material(name, blender_object)
        msmat = MakeSkinMaterial()
        msmat.apply_node_tree(material, template_values)
