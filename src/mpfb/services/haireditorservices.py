"""Module for convenience methods for hair editor"""

import os, bpy, json, time

from .logservice import LogService
from .locationservice import LocationService

_LOG = LogService.get_logger("services.haireditorservice")

class HairEditorService():
    """The HairEditorService class provides useful functions for the hair editor. All method are static methods."""

    # search_term -> (resolved path or None, time.time() of the lookup)
    _BLEND_PATH_CACHE = {}
    _MISSING_BLEND_TTL = 2.0

    # hair.blend in the first version of hair editor asset pack is about 19.6 MB, current one about 27.3 MB.
    # Anything below this is taken to be the old pack, which lacks assets the newer features rely on.
    _OUTDATED_HAIR_BLEND_MAX_BYTES = 23 * 1024 * 1024

    def __init__(self):
        raise RuntimeError("You should not instance HairEditorService. Use its static methods instead.")

    @staticmethod
    def read_image_pixels(image):
        """An image pixels as a flat float32 array of width*height*channels."""
        import numpy as np

        width, height = image.size
        buffer = np.empty(width * height * image.channels, dtype=np.float32)
        image.pixels.foreach_get(buffer)
        return buffer

    @staticmethod
    def write_image_pixels(image, values):
        """Write a flat float array back into an image."""
        import numpy as np

        image.pixels.foreach_set(np.ascontiguousarray(values, dtype=np.float32).ravel())

    @staticmethod
    def _get_hair_or_fur_blend_path(search_term="hair"):
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
    def _search_for_hair_or_fur_blend(search_term="hair"):
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
    def get_hair_blend_path():
        """Get the path to the hair blend file.

        Returns:
            str or None: The absolute path to the hair blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="hair")

    @staticmethod
    def get_fur_blend_path():
        """Get the path to the fur blend file.

        Returns:
            str or None: The absolute path to the fur blend file if found, None otherwise.
            The function first checks in the user data directory, then falls back to the system data directory.
        """
        return HairEditorService._get_hair_or_fur_blend_path(search_term="fur")

    @staticmethod
    def is_hair_asset_installed():
        """Check if the hair asset blend file is installed.

        Returns:
            bool: True if the hair blend file exists, False otherwise.
        """
        return HairEditorService.get_hair_blend_path() is not None

    @staticmethod
    def is_hair_pack_outdated():
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
    def is_fur_asset_installed():
        """Check if the fur asset blend file is installed.

        Returns:
            bool: True if the fur blend file exists, False otherwise.
        """
        return HairEditorService.get_fur_blend_path() is not None

    @staticmethod
    def is_rendered(obj, scene, view_layer):
        """Check if cycles would render the object."""
        if obj.hide_render:
            return False
        return HairEditorService._rendered_through(view_layer.layer_collection, obj, False)

    @staticmethod
    def _rendered_through(layer_collection, obj, hidden_above):
        """Whether some path from this layer collection down to obj has no collection hidden for render or excluded on it."""
        hidden = hidden_above or layer_collection.exclude or layer_collection.collection.hide_render
        if not hidden and obj.name in layer_collection.collection.objects:
            return True
        return any(HairEditorService._rendered_through(child, obj, hidden) for child in layer_collection.children)

    @staticmethod
    def join_texture_node_to_shader(img_node, shader_nodes, group_node, links, storage_key, store_links):
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
    def restore_shader_links(img_node, shader_nodes, group_node, nodes, links, storage_key):
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