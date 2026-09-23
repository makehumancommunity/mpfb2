"""Operator for unloading previously equipped proxy assets."""

import bpy
from bpy.props import StringProperty
from .....services import LogService
from .....services import ObjectService
from .....services import HumanService
from .....entities.objectproperties import GeneralObjectProperties
from ..... import ClassManager
from ....mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.unloadlibraryproxy")

class MPFB_OT_Unload_Library_Proxy_Operator(MpfbOperator):
    """Unequip proxy asset that has been previously loaded"""
    bl_idname = "mpfb.unload_library_proxy"
    bl_label = "Unequip"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Asset source fragment", default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.debug("filepath", self.filepath)

        blender_object = context.active_object

        rig = None
        basemesh = None

        if blender_object and not blender_object is None:
            if ObjectService.object_is_basemesh(blender_object):
                basemesh = blender_object
            else:
                basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")

            rig = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Skeleton")

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        parent = rig
        if not parent:
            parent = basemesh

        asset = None
        for child in ObjectService.find_related_mesh_assets(parent, only_children=True):
            source = GeneralObjectProperties.get_value("asset_source", entity_reference=child)
            if source == self.filepath and ObjectService.object_is(child, "Proxymeshes"):
                asset = child

        _LOG.debug("Asset", asset)

        if not asset:
            self.report({'ERROR'}, "Could not find asset?")
            return {'FINISHED'}

        HumanService.unload_mhclo_asset(basemesh, asset)

        # The proxy loader may have added a mask modifier hiding the base mesh. As there is no
        # longer any proxy to stand in for the base mesh, that modifier has to go too.
        if basemesh:
            for modifier in list(basemesh.modifiers):
                if modifier.type == 'MASK' and modifier.name == "Hide base mesh":
                    basemesh.modifiers.remove(modifier)

        _LOG.debug("basemesh, parent", (basemesh, basemesh.parent if basemesh else None))

        parent = basemesh
        if basemesh and basemesh.parent is not None:
            parent = basemesh.parent

        if parent:
            ObjectService.select_object(parent)

        self.report({'INFO'}, "Proxy was unloaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Unload_Library_Proxy_Operator)
