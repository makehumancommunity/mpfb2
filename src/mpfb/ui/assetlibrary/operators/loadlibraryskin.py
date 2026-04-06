"""Operator for importing MHCLO skin from asset library."""

import bpy
from bpy.props import StringProperty
from ....services import LogService
from ....services import ObjectService
from ....services import HumanService
from .... import ClassManager
from ...mpfboperator import MpfbOperator

_LOG = LogService.get_logger("assetlibrary.loadlibraryskin")


class MPFB_OT_Load_Library_Skin_Operator(MpfbOperator):
    """Load skin MHMAT from asset library"""
    bl_idname = "mpfb.load_library_skin"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(name="filepath", description="Full path to asset", default="")

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        _LOG.debug("filepath", self.filepath)

        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES  # pylint: disable=C0415
        from ....mpfbcontext import MpfbContext

        ctx = MpfbContext(context=context, scene_properties=ASSET_SETTINGS_PROPERTIES)

        material_instances = ctx.material_instances

        blender_object = context.active_object
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")
        bodyproxy = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Proxymeshes")

        if ctx.skin_type in ["LAYERED", "GAMEENGINE", "MAKESKIN"]:
            material_instances = False

        HumanService.set_character_skin(self.filepath, basemesh, bodyproxy=bodyproxy, skin_type=ctx.skin_type, material_instances=material_instances)

        for slot in basemesh.material_slots:
            if str(slot.material.name).lower().endswith("body"):
                basemesh.active_material_index = slot.slot_index

        if bodyproxy:
            for slot in bodyproxy.material_slots:
                if str(slot.material.name).lower().endswith("body"):
                    bodyproxy.active_material_index = slot.slot_index

        self.report({'INFO'}, "Skin was loaded")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Load_Library_Skin_Operator)
