"""The MakeSkin workflow: an MHMAT material as a blender node tree, and back again."""

import os, json, shutil, typing, bpy
from pathlib import Path
from typing import Any
from .mhmaterial import MhMaterial
from .mhmatkeys import MHMAT_KEYS
from .mhmatkeytypes import MhMatKey
from ...services import LogService
from ...services import LocationService
from ...services import NodeService
from ...services import MaterialService

_LOG = LogService.get_logger("material.makeskinmaterial")

TemplateValues = dict[str, str]
"""The substitution dict for the makeskin.json node tree template.

Every value is a string, because each one is spliced into the JSON source in place of a
``"$key"`` placeholder before the document is parsed. A boolean is therefore the text ``"true"``
or ``"false"``, a colour the text of a JSON array, and a file name carries its own quotes."""

_WARN_BL4_NAMES = [
    "subsurfaceColorMap"
    ]

_TEXTURE_NAMES = [
    "aomap",
    "bumpmap",
    "diffuse",
    "displacementmap",
    "emissionColorMap",
    "emissionStrengthMap",
    "metallicmap",
    "normalmap",
    "opacitymap",
    "roughnessmap",
    "specularmap",
    "subsurfaceStrengthMap",
    "transmissionmap"
    ]

_NONCOLOR = [
    "aomap",
    "bumpmap",
    "displacementmap",
    "emissionStrengthMap",
    "metallicmap",
    "normalmap",
    "opacitymap",
    "roughnessmap",
    "specularmap",
    "subsurfaceStrengthMap",
    "transmissionmap"
    ]

_NODE_SOCKET_VALUES: list[list[str]] = []  # key name, node name, socket name
_NODE_SOCKET_VALUES.append(["diffuseColor", "Principled BSDF", "Base Color"])  # First pick up color from principled
_NODE_SOCKET_VALUES.append(["diffuseColor", "diffuseIntensity", "Color1"])  # Then overwrite with intensity node if any
_NODE_SOCKET_VALUES.append(["diffuseIntensity", "diffuseIntensity", "Fac"])
_NODE_SOCKET_VALUES.append(["bumpmapIntensity", "bumpmap", "Strength"])
_NODE_SOCKET_VALUES.append(["normalmapIntensity", "normalmap", "Strength"])
# The MHMAT key is "displacementMapIntensity", with a capital M. This row writes a settings entry
# which no key in MHMAT_KEYS matches, so as_mhmat() never writes the value out again.
_NODE_SOCKET_VALUES.append(["displacementmapIntensity", "displacementmap", "Scale"])
_NODE_SOCKET_VALUES.append(["metallic", "Principled BSDF", "Metallic"])
_NODE_SOCKET_VALUES.append(["ior", "Principled BSDF", "IOR"])
_NODE_SOCKET_VALUES.append(["roughness", "Principled BSDF", "Roughness"])


class MakeSkinMaterial(MhMaterial):

    """An MhMaterial which can be applied as, and read back out of, a MakeSkin node tree."""

    def __init__(self, importer_presets: dict[str, Any] | None = None) -> None:
        MhMaterial.__init__(self)
        self.presets: dict[str, Any] | None = importer_presets

    def _template(self, template_values: TemplateValues, has: str, tex: str, key: str) -> None:
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

    def apply_node_tree(self, blender_material: bpy.types.Material, template_values: TemplateValues | None = None) -> None:
        """Replace the material's node tree with the makeskin template, filled in from this material."""
        tree_dir = LocationService.get_mpfb_data("node_trees")
        json_file = os.path.join(tree_dir, "makeskin.json")

        if template_values is None:
            template_values = dict()
            self._template(template_values, "has_aomap", "aomap_filename", "aomapTexture")
            self._template(template_values, "has_bumpmap", "bumpmap_filename", "bumpMapTexture")
            self._template(template_values, "has_diffuse", "diffuse_filename", "diffuseTexture")
            self._template(template_values, "has_displacementmap", "displacementmap_filename", "displacementMapTexture")
            self._template(template_values, "has_emissionColorMap", "emissionColorMap_filename", "emissionColorMapTexture")
            self._template(template_values, "has_emissionStrengthMap", "emissionStrengthMap_filename", "emissionStrengthMapTexture")
            self._template(template_values, "has_metallicmap", "metallicmap_filename", "metallicMapTexture")
            self._template(template_values, "has_normalmap", "normalmap_filename", "normalMapTexture")
            self._template(template_values, "has_opacitymap", "opacitymap_filename", "opacityMapTexture")
            self._template(template_values, "has_roughnessmap", "roughnessmap_filename", "roughnessMapTexture")
            self._template(template_values, "has_specularmap", "specularmap_filename", "specularMapTexture")
            # self._template(template_values, "has_subsurfaceColorMap", "subsurfaceColorMap_filename", "subsurfaceColorMapTexture")
            self._template(template_values, "has_subsurfaceStrengthMap", "subsurfaceStrengthMap_filename", "subsurfaceStrengthMapTexture")
            self._template(template_values, "has_transmissionmap", "transmissionmap_filename", "transmissionMapTexture")

        for key in _WARN_BL4_NAMES:
            if self.get_value(key):
                _LOG.warn("The " + key + " texture is not supported in Blender 4+")

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
            if key not in template_values:
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

        # Material.node_tree is None until use_nodes is set, which every caller does before getting
        # here, either directly or through MaterialService.create_empty_material().
        NodeService.apply_node_tree_from_dict(typing.cast(bpy.types.NodeTree, blender_material.node_tree), node_tree_dict, True)

    def _set_texture(self, node_tree: bpy.types.NodeTree, name: str) -> None:
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

    def _set_config_value(self, blender_object: bpy.types.Object, expected_name: str) -> None:
        from ...ui.create_assets.makeskin import MakeSkinObjectProperties
        if MakeSkinObjectProperties.has_key(expected_name):
            self._settings[expected_name] = MakeSkinObjectProperties.get_value(expected_name, entity_reference=blender_object)

    def ensure_uvmap_node_for_texture_nodes(self, blender_object: bpy.types.Object) -> None:
        """Give every texture node in the object's first material a UV map node, where it has none.

        Only the thirteen node names built from _TEXTURE_NAMES are looked at, which is every
        texture node the makeskin template creates."""
        material = typing.cast(bpy.types.Material, blender_object.material_slots[0].material)
        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        for texture_name_base in _TEXTURE_NAMES:
            texture_name = texture_name_base + "Texture"
            node = NodeService.find_node_by_name(node_tree, texture_name)
            _LOG.debug("texture name, node", (texture_name, node))
            if node is not None:
                uvmap_node = NodeService.find_node_linked_to_socket(node_tree, node, "Vector")
                _LOG.debug("vector node, node", (uvmap_node, node))
                if uvmap_node is None:
                    node_name = node.name + "UVMap"
                    node_label = node.label + " UVMap"
                    node_x = node.location.x - 300
                    node_y = node.location.y - 200

                    uvmap_node = NodeService.create_node(
                        node_tree,
                        "ShaderNodeUVMap",
                        name=node_name,
                        label=node_label,
                        xpos=node_x,
                        ypos=node_y)

                    NodeService.add_link(node_tree, uvmap_node, node, "UV", "Vector")
                    # create_node() returns the Node base class, which carries nothing specific to
                    # the type the name selected; uv_map is declared on ShaderNodeUVMap.
                    typing.cast(bpy.types.ShaderNodeUVMap, uvmap_node).uv_map = \
                        typing.cast(bpy.types.Mesh, blender_object.data).uv_layers[0].name

    def populate_from_object(self, blender_object: bpy.types.Object) -> None:
        """Read an existing MakeSkin material off an object and store it as MHMAT settings."""
        blender_material = typing.cast(bpy.types.Material, blender_object.material_slots[0].material)

        key_by_name: dict[str, MhMatKey] = dict()

        for key in MHMAT_KEYS:
            _LOG.debug("populate from object", (key.key_name, key.default_value, key.key_group))
            self._settings[key.key_name] = key.default_value
            key_by_name[key.key_name] = key
            if key.key_group == "Texture":
                self._set_texture(typing.cast(bpy.types.NodeTree, blender_material.node_tree), key.key_name)
            if key.key_group in ["Metadata", "Various"]:
                self._set_config_value(blender_object, key.key_name)

        for nsv in _NODE_SOCKET_VALUES:
            setting_name = nsv[0]
            node_name = nsv[1]
            socket_name = nsv[2]

            node = NodeService.find_node_by_name(typing.cast(bpy.types.NodeTree, blender_material.node_tree), node_name)
            if node:
                socket_values = NodeService.get_socket_default_values(node)
                if socket_values and socket_name in socket_values:
                    self._settings[setting_name] = socket_values[socket_name]

        from ...ui.create_assets.makeskin import MakeSkinObjectProperties
        if MakeSkinObjectProperties.get_value("sss_enable", entity_reference=blender_object):
            self._settings["sssEnabled"] = True
            # A makeskin material always has a principled node, since the template's own is not
            # conditional, so this lookup cannot come back empty for a material this class made.
            node = typing.cast(bpy.types.Node,
                               NodeService.find_node_by_name(typing.cast(bpy.types.NodeTree, blender_material.node_tree), "Principled BSDF"))
            socket_values = NodeService.get_socket_default_values(node)
            if "Subsurface Radius" in socket_values:
                radius = socket_values["Subsurface Radius"]
                self._settings["sssRScale"] = radius[0]
                self._settings["sssGScale"] = radius[1]
                self._settings["sssBScale"] = radius[2]
            else:
                _LOG.warn("Expected to find a Subsurface Radius socket, but it did not exist on the principled BSDF node. Values are", socket_values)
        else:
            self._settings["sssEnabled"] = False

        _LOG.dump("\n\n\nRESULTS, POPULATE FROM OBJECT\n\n\n", self._settings)

    def check_that_all_textures_are_saved(self, blender_object: bpy.types.Object, mhmat_dir: str | None = None,
                                          mhmat_bn: str | None = None) -> str | None:
        """Save any unsaved texture image, and return a message describing the first one which could not be.

        Only the thirteen node names built from _TEXTURE_NAMES are looked at, which is every
        texture node the makeskin template creates."""
        material = typing.cast(bpy.types.Material, blender_object.material_slots[0].material)
        node_tree = typing.cast(bpy.types.NodeTree, material.node_tree)

        for texture_name_base in _TEXTURE_NAMES:
            texture_name = texture_name_base + "Texture"
            node = NodeService.find_node_by_name(node_tree, texture_name)
            _LOG.debug("texture name, node", (texture_name, node))
            if node:
                # Only ShaderNodeTexImage carries an image, and the names searched for are the
                # template's own image texture nodes.
                image = typing.cast(bpy.types.ShaderNodeTexImage, node).image
                if not image:
                    return "The " + node.name + " does not have an image"
                node_info = NodeService.get_node_info(node)
                if "filename" not in node_info or not node_info["filename"]:
                    if mhmat_bn and mhmat_dir:
                        image.filepath_raw = os.path.join(mhmat_dir, mhmat_bn + "_" + texture_name_base + ".png")
                        image.file_format = 'PNG'
                        image.save()
                        self._set_texture(node_tree, texture_name)
                    else:
                        _LOG.warn("basename or dirname is none", (mhmat_bn, mhmat_dir))
                        return "The " + node.name + " has an unsaved image !!?"
                else:
                    image.save()
            else:
                # The material isn't using this kind of texture
                _LOG.debug("No node was found for", texture_name)

        return None

    def export_to_disk(self, mhmat_path: str, normalize_textures: bool = True) -> None:
        """Write this material as an MHMAT file, optionally copying its textures in beside it."""
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
                    if src != dest:
                        shutil.copy(src, dest)
                    newfn = os.path.basename(dest)
                    self._settings[key] = newfn

        mhmat_string = self.as_mhmat()
        _LOG.dump("material", mhmat_string)
        with open(mhmat_path, "w") as mhmat:
            mhmat.write(mhmat_string)

    # TODO: Method for writing MHMAT attributes as BlenderConfigSet attributes

    @staticmethod
    def create_makeskin_template_material(blender_object: bpy.types.Object, scene: bpy.types.Scene,
                                          name: str = "MakeSkinMaterial") -> None:
        """Create a new material on the object from the makeskin template, as the scene settings ask for."""

        from ...ui.create_assets.makeskin.makeskinpanel import MAKESKIN_PROPERTIES

        if blender_object is None:
            raise ValueError('Must provide an object')
        if scene is None:
            raise ValueError('Must provide a scene')

        template_values: TemplateValues = dict()
        for part in _TEXTURE_NAMES:
            _LOG.debug("checking texture", part)
            if MAKESKIN_PROPERTIES.get_value("create_" + part, entity_reference=scene):
                template_values["has_" + part] = "true"
            else:
                template_values["has_" + part] = "false"
            template_values[part + "_filename"] = "\"\""

        _LOG.debug("Template values", template_values)

        material = MaterialService.create_empty_material(name, blender_object)
        msmat = MakeSkinMaterial()
        msmat.apply_node_tree(material, template_values)

        resolution = MAKESKIN_PROPERTIES.get_value("resolution", entity_reference=scene)
        if resolution and resolution != "NONE":
            for part in _TEXTURE_NAMES:
                if MAKESKIN_PROPERTIES.get_value("create_" + part, entity_reference=scene):
                    # The template was given the same create_<part> flags above, so the node for an
                    # enabled part always exists here. Four of the thirteen are keyed in
                    # makeskin.json under an abbreviated name -- aoTexture, emcTexture, emsTexture
                    # and subsTexture -- but each of those carries the full <part>Texture name in
                    # its own "name" entry, which is what the node ends up called.
                    node = typing.cast(bpy.types.ShaderNodeTexImage,
                                       NodeService.find_node_by_name(typing.cast(bpy.types.NodeTree, material.node_tree), part + "Texture"))
                    _LOG.debug("create image for", (part, node))
                    side = int(resolution)
                    bpy.ops.image.new(name=part + "Texture", width=side, height=side)
                    node.image = bpy.data.images[part + "Texture"]
                    if part in _NONCOLOR:
                        # Image.colorspace_settings cannot be None: it is an embedded struct rather
                        # than a pointer, so there is nothing for it to be null for. The RNA enum
                        # behind its name carries only "NONE" statically, because the real
                        # colorspace list is populated from OCIO at runtime, so no stub can know
                        # "Non-Color".
                        colorspace = typing.cast(bpy.types.ColorManagedInputColorspaceSettings,
                                                 typing.cast(bpy.types.Image, node.image).colorspace_settings)
                        colorspace.name = "Non-Color"  # pyright: ignore[reportAttributeAccessIssue]
