"""MPFB's enhanced (PBR plus subsurface scattering) skin shader, built from a node tree template."""

import os, json, re, typing, bpy
from pathlib import Path
from typing import Any
from .mhmaterial import MhMaterial
from ...services import LogService
from ...services import LocationService
from ...services import NodeService
from ...services import MaterialService

_LOG = LogService.get_logger("material.enhancedskinmaterial")

TemplateValues = dict[str, str]
"""The substitution dict for the enhanced_skin.json node tree template.

Every value is a string, because each one is spliced into the JSON source in place of a
``"$key"`` placeholder before the document is parsed -- so a number is written as its digits and
a boolean as the text ``"true"`` or ``"false"``, and a string value carries its own quotes."""


class EnhancedSkinMaterial(MhMaterial):

    """An MhMaterial which applies itself as MPFB's enhanced skin node group."""

    def __init__(self, importer_presets: dict[str, Any]) -> None:
        MhMaterial.__init__(self)
        self.presets: dict[str, Any] = importer_presets

    def _template(self, template_values: TemplateValues, has: str, tex: str, key: str) -> None:
        template_values[has] = "false"
        template_values[tex] = "\"\""
        value = self.get_value(key)
        if value:
            _LOG.debug(key + " is set in mhmat")
            template_values[has] = "true"
            template_values[tex] = "\"" + value + "\""
        else:
            _LOG.debug(key + " is not set in mhmat")

    def skin_tweaks(self, template_values: TemplateValues, blender_material: bpy.types.Material) -> None:
        """Adjust the template values and the material itself for skin rather than another body part."""
        # bpy_prop_array declares no constructor and no element assignment, so no python sequence
        # satisfies it to the checker, although assigning a four element list to a fixed size float
        # array is ordinary at runtime.
        blender_material.diffuse_color = MaterialService.get_skin_diffuse_color()  # pyright: ignore[reportAttributeAccessIssue]
        template_values["Roughness"] = "0.45"

    def default_settings(self, blender_material: bpy.types.Material, group_name: str | None = None) -> TemplateValues:
        """Build the substitution dict for the template, from the presets and the parsed material."""
        tex_dir = LocationService.get_mpfb_data("textures")
        sss_file = os.path.join(tex_dir, "sss.png")

        template_values: TemplateValues = dict()
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

    def apply_node_tree(self, blender_material: bpy.types.Material, tweaks: str = "SKIN", group_name: str | None = None) -> None:
        """Replace the material's node tree with the enhanced skin template, filled in from the presets."""

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
        _LOG.dump("template data before replace", template_data)

        for key in template_values:
            value = re.sub(r'\\+', '/', template_values[key])
            template_data = template_data.replace("\"$" + key + "\"", value)

        _LOG.dump("template data after replace", template_data)

        node_tree_dict = json.loads(template_data)
        _LOG.dump("node_tree_dict", node_tree_dict)

        # Material.node_tree is None until use_nodes is set, which every caller does before
        # getting here, either directly or through MaterialService.create_empty_material().
        NodeService.apply_node_tree_from_dict(typing.cast(bpy.types.NodeTree, blender_material.node_tree), node_tree_dict, True)
