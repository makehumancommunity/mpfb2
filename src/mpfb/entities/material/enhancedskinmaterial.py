
import os, json
from pathlib import Path
from .mhmaterial import MhMaterial
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService

_LOG = LogService.get_logger("material.enhancedskinmaterial")


class EnhancedSkinMaterial(MhMaterial):

    def __init__(self, importer_presets):
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

    def skin_tweaks(self, template_values, blender_material):
        blender_material.diffuse_color = MaterialService.get_skin_diffuse_color()
        template_values["Roughness"] = "0.45"

    def default_settings(self, blender_material, group_name=None):
        tex_dir = LocationService.get_mpfb_data("textures")
        sss_file = os.path.join(tex_dir, "sss.png")

        template_values = dict()
        self._template(template_values, "has_diffusetexture", "diffusetexture_filename", "diffuseTexture")
        self._template(template_values, "has_normalmap", "normalmap_filename", "normalMapTexture")

        mat_type = str(self.presets["skin_material_type"]).lower()

        if "sss" in mat_type:
            template_values["has_sss"] = "true"
        else:
            template_values["has_sss"] = "false"

        template_values["ssstexture_filename"] = "\"" + sss_file + "\""
        template_values["sss_radius_scale"] = "0.1"

        if "scale_factor" in self.presets:
            factor = self.presets["scale_factor"]
            if factor == "DECIMETER":
                template_values["sss_radius_scale"] = "1"
            if factor == "CENTIMETER":
                template_values["sss_radius_scale"] = "10"

        template_values["Roughness"] = "0.5"

        if group_name:
            template_values["group_name"] = "\"" + group_name + "\""
        else:
            if blender_material.name:
                template_values["group_name"] = "\"" + blender_material.name + "\""
            else:
                template_values["group_name"] = "\"mpfb_enhanced_skin\""

        return template_values

    def apply_node_tree(self, blender_material, tweaks="SKIN", group_name=None):

        template_values = self.default_settings(blender_material, group_name)

        if tweaks == "SKIN":
            self.skin_tweaks(template_values, blender_material)

        # TODO: check if the group node is already there, and figure out if we should recreate
        # or reuse it. Atm, the group will always be recreated.
        # group_node = NodeService.find_node_by_name(blender_material.node_tree, template_values["group_name"])

        _LOG.dump("template_values", template_values)

        tree_dir = LocationService.get_mpfb_data("node_trees")
        json_file = os.path.join(tree_dir, "enhanced_skin.json")

        template_data = Path(json_file).read_text()
        for key in template_values:
            template_data = template_data.replace("\"$" + key + "\"", template_values[key])

        node_tree_dict = json.loads(template_data)
        _LOG.dump("node_tree_dict", node_tree_dict)

        NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict, True)
