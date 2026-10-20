"""Module for convenience methods for hair editor"""

import os, bpy, json, time
from typing import TYPE_CHECKING

from .logservice import LogService
from .locationservice import LocationService

if TYPE_CHECKING:
    import numpy as np

_LOG = LogService.get_logger("services.haireditorservice")

class HairEditorService():
    """The HairEditorService class provides useful functions for the hair editor. All method are static methods."""

    # search_term -> (resolved path or None, time.time() of the lookup)
    _BLEND_PATH_CACHE = {}
    _MISSING_BLEND_TTL = 2.0

    # hair.blend in the first version of hair editor asset pack is about 19.6 MB, current one about 27.3 MB.
    # Anything below this is taken to be the old pack, which lacks assets the newer features rely on.
    _OUTDATED_HAIR_BLEND_MAX_BYTES = 23 * 1024 * 1024

    def __init__(self) -> None:
        raise RuntimeError("You should not instance HairEditorService. Use its static methods instead.")

    @staticmethod
    def read_image_pixels(image: bpy.types.Image) -> "np.ndarray":
        """An image pixels as a flat float32 array of width*height*channels."""
        import numpy as np

        width, height = image.size
        buffer = np.empty(width * height * image.channels, dtype=np.float32)
        image.pixels.foreach_get(buffer)
        return buffer

    @staticmethod
    def write_image_pixels(image: bpy.types.Image, values: "np.ndarray") -> None:
        """Write a flat float array back into an image."""
        import numpy as np

        image.pixels.foreach_set(np.ascontiguousarray(values, dtype=np.float32).ravel())

    @staticmethod
    def _get_hair_or_fur_blend_path(search_term: str = "hair") -> str | None:
        """The path to the hair or fur asset blend, or None.

        Cached because the panel asks on every redraw. A found path is kept, a missing one expires
        after a couple of seconds so that newly installed asset packs are noticed.
        """
        cached = HairEditorService._BLEND_PATH_CACHE.get(search_term)
        if cached is not None:
            path, looked_up_at = cached
            if path is not None or (time.time() - looked_up_at) < HairEditorService._MISSING_BLEND_TTL:
                return path

        path = HairEditorService._search_for_hair_or_fur_blend(search_term)
        HairEditorService._BLEND_PATH_CACHE[search_term] = (path, time.time())
        return path

    @staticmethod
    def _search_for_hair_or_fur_blend(search_term: str = "hair") -> str | None:
        user_data_hair = LocationService.get_user_data("hair")
        if os.path.exists(user_data_hair):
            blend = os.path.join(user_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("User path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                return os.path.realpath(os.path.abspath(blend))

        system_data_hair = LocationService.get_mpfb_data("hair")
        if os.path.exists(system_data_hair):
            blend = os.path.join(system_data_hair, "haireditor", search_term + ".blend")
            _LOG.debug("System path for " + search_term + " blend", (blend, os.path.exists(blend)))
            if os.path.exists(blend) and os.path.isfile(blend):
                # The blends ship in the addon data folder, so this is the normal case and not a warning
                _LOG.debug("Using the bundled " + search_term + " blend", blend)
                return os.path.realpath(os.path.abspath(blend))

        _LOG.debug("No hair blend found.")
        return None

    @staticmethod
    def get_hair_blend_path() -> str | None:
        """Get the path to the hair blend file.

        Returns:
            str or None: The absolute path to the hair blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="hair")

    @staticmethod
    def get_fur_blend_path() -> str | None:
        """Get the path to the fur blend file.

        Returns:
            str or None: The absolute path to the fur blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="fur")

    @staticmethod
    def is_hair_asset_installed() -> bool:
        """Check if the hair asset blend file is installed.

        Returns:
            bool: True if the hair blend file exists, False otherwise.
        """
        return HairEditorService.get_hair_blend_path() is not None

    @staticmethod
    def is_hair_pack_outdated() -> bool:
        """Check if the installed hair asset blend comes from the old asset pack.

        The pack itself carries no version, so the size of hair.blend is used to tell the two apart.
        """
        path = HairEditorService.get_hair_blend_path()
        if path is None:
            return False
        try:
            return os.path.getsize(path) < HairEditorService._OUTDATED_HAIR_BLEND_MAX_BYTES
        except OSError:
            return False

    @staticmethod
    def is_fur_asset_installed() -> bool:
        """Check if the fur asset blend file is installed.

        Returns:
            bool: True if the fur blend file exists, False otherwise.
        """
        return HairEditorService.get_fur_blend_path() is not None

    @staticmethod
    def is_rendered(obj: bpy.types.Object, scene: bpy.types.Scene, view_layer: bpy.types.ViewLayer) -> bool:
        """Check if cycles would render the object."""
        if obj.hide_render:
            return False
        return HairEditorService._rendered_through(view_layer.layer_collection, obj, False)

    @staticmethod
    def _rendered_through(layer_collection: bpy.types.LayerCollection, obj: bpy.types.Object, hidden_above: bool) -> bool:
        """Whether some path from this layer collection down to obj has no collection hidden for render or excluded on it."""
        hidden = hidden_above or layer_collection.exclude or layer_collection.collection.hide_render
        if not hidden and obj.name in layer_collection.collection.objects:
            return True
        return any(HairEditorService._rendered_through(child, obj, hidden) for child in layer_collection.children)

    @staticmethod
    def join_texture_node_to_shader(img_node: bpy.types.Node | None, shader_nodes: list[bpy.types.Node], group_node: bpy.types.Node, links: bpy.types.NodeLinks, storage_key: str, store_links: bool) -> None:
        """Joins given texture node to principled shaders inside "Hair shader EEVEE" group node
           and stores previous links so they can be recreated later
        """
        """ if (storage_key in group_node and store_links):
            del group_node[storage_key] """
        saved = {}
        for p in shader_nodes:
            inp = p.inputs[0]
            existing = [(ln.from_node.name, ln.from_socket.name) for ln in inp.links]
            if existing:
                saved[p.name] = existing
                for ln in list(inp.links):
                    links.remove(ln)
            if img_node:
                links.new(img_node.outputs['Color'], inp)
        if store_links:
            group_node[storage_key] = json.dumps(saved)
        return

    @staticmethod
    def restore_shader_links(img_node: bpy.types.Node | None, shader_nodes: list[bpy.types.Node], group_node: bpy.types.Node, nodes: bpy.types.Nodes, links: bpy.types.NodeLinks, storage_key: str) -> None:
        """Restores previous color links to principled shaders inside "Hair shader EEVEE" group node
           after turing off usage of texture
        """
        saved = {}
        if storage_key in group_node:
            try:
                saved = json.loads(group_node[storage_key])
            except Exception:
                saved = {}
        # remove any texture links
        if img_node:
            for p in shader_nodes:
                inp = p.inputs[0]
                for ln in list(inp.links):
                    if ln.from_node == img_node:
                        links.remove(ln)
        # re-link saved
        restored = 0
        for p in shader_nodes:
            inp = p.inputs[0]
            for from_name, sock_name in saved.get(p.name, []):
                src = nodes.get(from_name)
                if src:
                    out = src.outputs.get(sock_name)
                    if out:
                        links.new(out, inp)
                        restored += 1
        if storage_key in group_node:
            del group_node[storage_key]
        _LOG.debug("Restored %d original link(s)", restored)
        return

    @staticmethod
    def discard_unused_images(images_before_load: set[str]) -> None:
        """Throw away unused images which came along when an asset was loaded (asset packs contain textures of other assets).

        Args:
            images_before_load: The names of the images which existed before the asset was loaded, as
                returned by list_image_names().
        """
        for image in [image for image in bpy.data.images if image.name not in images_before_load]:
            if image.users < 1:
                _LOG.debug("Discarding unused image which came with an asset", image.name)
                bpy.data.images.remove(image)

    @staticmethod
    def list_image_names() -> set[str]:
        """The names of all images currently in the file, for use with discard_unused_images()."""
        return {image.name for image in bpy.data.images}

    @staticmethod
    def attach_curves_to_basemesh(hair_obj: bpy.types.Object, basemesh: bpy.types.Object) -> bool:
        """Make freshly loaded hair curves grow on the given basemesh.

        Assets are stored with the character they were groomed on, so the imported one is removed afterwards.

        Args:
            hair_obj: The hair curves object which was just loaded from an asset.
            basemesh: The basemesh the curves should grow on.

        Returns:
            bool: True if the curves were attached, False if the object cannot carry a surface.
        """
        _LOG.enter()
        if hair_obj.type != "CURVES" or not hasattr(hair_obj.data, "surface"):
            return False

        imported_surface = hair_obj.data.surface
        hair_obj.data.surface = basemesh

        if imported_surface is None or imported_surface == basemesh:
            return True

        # Something in the scene is using the mesh, so it cant be thrown away
        if imported_surface.users_collection:
            _LOG.debug("Keeping the surface which came with the asset, since it is in use", imported_surface.name)
            return True

        mesh = imported_surface.data
        materials = list(mesh.materials) if mesh else []

        _LOG.debug("Discarding the surface which came with the asset", imported_surface.name)
        bpy.data.objects.remove(imported_surface, do_unlink=True)

        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        for material in materials:
            if material.users == 0:
                bpy.data.materials.remove(material)

        return True
