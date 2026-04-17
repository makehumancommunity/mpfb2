"""Operator for importing an asset pack."""

import bpy, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .....services import LogService
from .....services import LocationService
from .....services import AssetService
import zipfile
from ..... import ClassManager
from ....mpfboperator import MpfbOperator
from ....mpfbcontext import MpfbContext, ContextResolveEffort

_LOG = LogService.get_logger("assetlibrary.loadpack")

class MPFB_OT_Load_Pack_Operator(MpfbOperator, ImportHelper):
    """Install an asset pack from ZIP file. You can find more asset packs to download
    by clicking the asset packs button under "system and resources" -> "web resources"
    """
    bl_idname = "mpfb.load_pack"
    bl_label = "Load pack from zip file"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(default='*.zip', options={'HIDDEN'})

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES, ASSET_PACK_STATUS  # pylint: disable=C0415
        ctx = MpfbContext(context=context, scene_properties=ASSET_SETTINGS_PROPERTIES)

        if not self.filepath:
            self.report({'ERROR'}, "Must select a file")
            return {'FINISHED'}

        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File does not exist?")
            return {'FINISHED'}

        data_dir = LocationService.get_user_data()

        ASSET_PACK_STATUS["status"] = None

        if ctx.check_zip == "BLOCK":
            check = AssetService.check_asset_pack_zip(self.filepath)
            if check is not None:
                ASSET_PACK_STATUS["status"] = check
                self.report({'WARNING'}, "Bad zip file, see text")
                return {'FINISHED'}

        with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
            zip_ref.extractall(data_dir)

        AssetService.update_all_asset_lists()

        self.report({'INFO'}, "Assets should now be available. If they are not visible, then restart Blender.")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_Load_Pack_Operator)
