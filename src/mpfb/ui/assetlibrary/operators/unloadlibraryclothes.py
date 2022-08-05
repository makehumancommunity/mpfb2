"""Operator for unloading previously equipped mhclo assets."""

import bpy
from bpy.props import StringProperty
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.humanservice import HumanService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb import ClassManager

_LOG = LogService.get_logger("assetlibrary.unloadlibraryclothes")

class MPFB_OT_Unload_Library_Clothes_Operator(bpy.types.Operator):
    """Unequip mhclo asset that has been previously loaded"""
    bl_idname = "mpfb.unload_library_clothes"
    bl_label = "Unequip"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Asset source fragment", default="")

    def execute(self, context):

        _LOG.debug("filepath", self.filepath)

        scene = context.scene

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
        for child in ObjectService.get_list_of_children(parent):
            source = GeneralObjectProperties.get_value("asset_source", entity_reference=child)
            if source == self.filepath:
                asset = child

        _LOG.debug("Asset", asset)

        if not asset:
            self.report({'ERROR'}, "Could not find asset?")
            return {'FINISHED'}

        HumanService.unload_mhclo_asset(basemesh, asset)

        #_LOG.debug("Will call add_mhclo_asset: (asset_type, material_type)", (self.object_type, self.material_type))
        #HumanService.add_mhclo_asset(self.filepath, basemesh, asset_type=self.object_type, subdiv_levels=subdiv_levels, material_type=self.material_type)

        self.report({'INFO'}, "Clothes were unloaded")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Unload_Library_Clothes_Operator)
