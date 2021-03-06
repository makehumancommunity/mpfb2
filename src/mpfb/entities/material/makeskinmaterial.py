
import os, json
from pathlib import Path
from .mhmaterial import MhMaterial
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService

_LOG = LogService.get_logger("material.makeskinmaterial")


class MakeSkinMaterial(MhMaterial):

    def __init__(self, importer_presets=None):
        MhMaterial.__init__(self)
        self.presets = importer_presets

    def _template(self, template_values, has, tex, key):
        template_values[has] = "false"
        template_values[tex] = "\"\""
        if key in self._settings and self._settings[key]:
            _LOG.debug(key + " is set in mhmat")
            template_values[has] = "true"
            template_values[tex] = "\"" + self._settings[key] + "\""
        else:
            _LOG.debug(key + " is not set in mhmat")

    def apply_node_tree(self, blender_material, template_values=None):
        tree_dir = LocationService.get_mpfb_data("node_trees")
        json_file = os.path.join(tree_dir, "makeskin.json")

        if template_values is None:
            template_values = dict()
            self._template(template_values, "has_bumpmap", "bumpmap_filename", "bumpMapTexture")
            self._template(template_values, "has_diffusetexture", "diffusetexture_filename", "diffuseTexture")
            self._template(template_values, "has_displacementmap", "displacementmap_filename", "displacementMapTexture")
            self._template(template_values, "has_metallicmap", "metallicmap_filename", "metallicMapTexture")
            self._template(template_values, "has_normalmap", "normalmap_filename", "normalMapTexture")
            self._template(template_values, "has_roughnessmap", "roughnessmap_filename", "roughnessMapTexture")
            self._template(template_values, "has_transmissionmap", "transmissionmap_filename", "transmissionMapTexture")

        template_values["bump_or_normal"] = "false"
        if template_values["has_bumpmap"] == "true":
            template_values["bump_or_normal"] = "true"
        if template_values["has_normalmap"] == "true":
            template_values["bump_or_normal"] = "true"

        _LOG.dump("template_values", template_values)

        template_data = Path(json_file).read_text()
        for key in template_values:
            template_data = template_data.replace("\"$" + key + "\"", template_values[key])

        node_tree_dict = json.loads(template_data)
        _LOG.dump("node_tree", node_tree_dict)

        NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict, True)

    @staticmethod
    def create_makeskin_template_material(blender_object, scene, name="MakeSkinMaterial"):
        if blender_object is None:
            raise ValueError('Must provide an object')
        if MaterialService.has_materials(blender_object):
            raise ValueError('Object already has material')
        if scene is None:
            raise ValueError('Must provide a scene')

        from mpfb.ui.makeskin.makeskinpanel import MAKESKIN_PROPERTIES

        template_values = dict()
        for part in ["bumpmap", "diffusetexture", "displacementmap", "metallicmap", "normalmap", "roughnessmap", "transmissionmap"]:
            if MAKESKIN_PROPERTIES.get_value("create_" + part, entity_reference=scene):
                template_values["has_" + part] = "true"
            else:
                template_values["has_" + part] = "false"
            template_values[part + "_filename"] = "\"\""

        material = MaterialService.create_empty_material(name, blender_object)
        msmat = MakeSkinMaterial()
        msmat.apply_node_tree(material, template_values)
