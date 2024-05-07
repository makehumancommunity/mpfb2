"""Operator for writing a MHCLO file."""

import bpy, os, shutil
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.entities.meshcrossref import MeshCrossRef
from mpfb import ClassManager

_LOG = LogService.get_logger("makeclothes.basemesh_xref")
_LOG.set_level(LogService.DEBUG)

class MPFB_OT_BasemeshXrefOperator(bpy.types.Operator):
    """Create a cache with cross-reference tables for the base mesh. This is generic for all base meshes, irregardless of shape and normally only needs to be done once. Note that this can take a long time, up towards 30 seconds"""
    bl_idname = "mpfb.basemesh_xref"
    bl_label = "Create xref cache"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        basemesh = None
        for obj in context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj

        if not basemesh:
            self.report({'ERROR'}, "No base mesh selected.")
            return {'CANCELLED'}

        cache_dir = LocationService.get_user_cache("basemesh_xref")

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        _LOG.debug("Cache dir", cache_dir)

        xref = MeshCrossRef(basemesh, after_modifiers=False, build_faces_by_group_reference=True, cache_dir=cache_dir, write_cache=True, read_cache=False)
        _LOG.debug("Xref", xref)

        self.report({'INFO'}, "The xref cache was created.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_BasemeshXrefOperator)
