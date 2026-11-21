"""Operator for importing an asset pack."""

import bpy, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty
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
    files: CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

    def get_logger(self):
        return _LOG

    def _resolve_filepaths(self) -> list[str]:
        """Resolve selected file paths from multi-file selection or single filepath."""
        if self.files and self.filepath:
            base_dir = self.filepath if os.path.isdir(self.filepath) else os.path.dirname(self.filepath)
            paths = [os.path.join(base_dir, f.name) for f in self.files if f.name]
            if paths:
                return paths
        if self.filepath:
            return [self.filepath]
        return []

    def hardened_execute(self, context):

        from ...assetlibrary.assetsettingspanel import ASSET_SETTINGS_PROPERTIES, ASSET_PACK_STATUS  # pylint: disable=C0415
        ctx = MpfbContext(context=context, scene_properties=ASSET_SETTINGS_PROPERTIES)

        filepaths = self._resolve_filepaths()
        if not filepaths:
            self.report({'ERROR'}, "Must select a file")
            return {'FINISHED'}

        for filepath in filepaths:
            _LOG.info(f"Installing asset pack from zip: {filepath}")
            if not os.path.exists(filepath):
                self.report({'ERROR'}, f"File does not exist: {os.path.basename(filepath)}")
                return {'FINISHED'}

        data_dir = LocationService.get_user_data()
        ASSET_PACK_STATUS["status"] = None

        total = len(filepaths)
        installed_count = 0
        fixed_count = 0
        failed_files: list[tuple[str, str]] = []

        wm = context.window_manager
        wm.progress_begin(0, total)
        try:
            for index, filepath in enumerate(filepaths):
                wm.progress_update(index)
                filename = os.path.basename(filepath)
                _LOG.info(f"Installing asset pack ({index + 1}/{total}): {filename}")
                ok, err_status, was_fixed = self._install_asset_pack(filepath, data_dir, ctx.check_zip)
                if ok:
                    installed_count += 1
                    if was_fixed:
                        fixed_count += 1
                else:
                    status = err_status or "UNKNOWN"
                    ASSET_PACK_STATUS["status"] = status
                    failed_files.append((filename, status))
                    _LOG.warn(f"Failed to install asset pack {filename}: {status}")
                wm.progress_update(index + 1)
        finally:
            wm.progress_end()

        if installed_count > 0:
            AssetService.update_all_asset_lists()

        if total == 1:
            if failed_files:
                _, status = failed_files[0]
                if status.startswith("FIX_ERROR") or status == "FIX_FAILED":
                    self.report({'WARNING'}, "Failed to fix zip, see text")
                else:
                    self.report({'WARNING'}, "Bad zip file, see text")
            elif fixed_count > 0:
                self.report({'INFO'}, "Assets fixed and installed. If not visible, restart Blender.")
            else:
                self.report({'INFO'}, "Assets should now be available. If they are not visible, then restart Blender.")
            return {'FINISHED'}

        if not failed_files:
            self.report({'INFO'}, f"Installed {installed_count} asset pack(s). If they are not visible, then restart Blender.")
        elif installed_count > 0:
            failed_names = ", ".join(name for name, _ in failed_files)
            self.report(
                {'WARNING'},
                f"Installed {installed_count} of {total} asset pack(s). Failed ({len(failed_files)}): {failed_names}. See Library Settings."
            )
        else:
            self.report({'WARNING'}, f"Failed to install all {total} asset pack(s). See Library Settings.")

        return {'FINISHED'}

    @staticmethod
    def _install_asset_pack(filepath: str, data_dir: str, check_zip_mode: str) -> tuple[bool, str | None, bool]:
        """Validate, optionally fix, and extract a single asset pack zip.

        Returns:
            (success, error_status, was_fixed)
        """
        if not os.path.isfile(filepath):
            return False, "INVALID_ZIP: File does not exist", False

        if check_zip_mode == "BLOCK":
            check = AssetService.check_asset_pack_zip(filepath)
            if check is not None:
                return False, check, False
        elif check_zip_mode == "FIX":
            check = AssetService.check_asset_pack_zip(filepath)
            if check is not None:
                result = AssetService.fix_and_extract_asset_pack_zip(filepath, data_dir)
                if result is not None:
                    return False, result, False
                return True, None, True

        try:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
        except zipfile.BadZipFile as exc:
            return False, f"INVALID_ZIP: {exc}", False
        except OSError as exc:
            return False, f"FIX_ERROR: {exc}", False

        return True, None, False


ClassManager.add_class(MPFB_OT_Load_Pack_Operator)
