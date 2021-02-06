#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json
from pathlib import Path
from .mhmaterial import MhMaterial
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.nodeservice import NodeService

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

    def apply_node_tree(self, blender_material):
        tree_dir = LocationService.get_mpfb_data("node_trees")
        json_file = os.path.join(tree_dir, "makeskin.json")

        template_values = dict()
        self._template(template_values, "has_bumpmap", "bumpmap_filename", "bumpMapTexture")
        self._template(template_values, "has_diffusetexture", "diffusetexture_filename", "diffuseTexture")
        self._template(template_values, "has_displacementmap", "displacementmap_filename", "displacementMapTexture")
        self._template(template_values, "has_metallicmap", "metallicmap_filename", "metallicMapTexture")
        self._template(template_values, "has_normalmap", "normalmap_filename", "normalMapTexture")
        self._template(template_values, "has_roughnessmap", "roughnessmap_filename", "roughnessMapTexture")
        self._template(template_values, "has_transmissionmap", "transmissionmap_filename", "transmissionMapTexture")

        _LOG.dump("template_values", template_values)

        template_data = Path(json_file).read_text()
        for key in template_values:
            template_data = template_data.replace("\"$" + key + "\"", template_values[key])

        node_tree_dict = json.loads(template_data)
        _LOG.dump("node_tree", node_tree_dict)

        NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict)
