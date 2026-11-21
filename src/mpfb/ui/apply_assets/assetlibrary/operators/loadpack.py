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

_TIMER_INTERVAL = 0.05

_INSTALL_PROGRESS = {
    "active": False,
    "index": 0,
    "total": 0,
    "filename": "",
}


def _draw_statusbar_progress(self, _context):
    """Draw asset pack installation progress bar in Blender's bottom status bar."""
    if not _INSTALL_PROGRESS["active"]:
        return
    total = max(1, _INSTALL_PROGRESS["total"])
    index = _INSTALL_PROGRESS["index"]
    factor = min(1.0, max(0.0, index / total))
    filename = _INSTALL_PROGRESS["filename"]
    row = self.layout.row(align=True)
    row.progress(
        factor=factor,
        type='BAR',
        text=f"Installing asset packs ({index}/{total}): {filename}  [ESC to cancel]",
    )


def _tag_statusbar_redraw(context):
    """Request an immediate redraw of the bottom status bar area."""
    if not context or not context.window or not context.window.screen:
        return
    for area in context.window.screen.areas:
        if area.type == 'STATUSBAR':
            area.tag_redraw()


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

        self._filepaths = filepaths
        self._data_dir = data_dir
        self._check_zip_mode = ctx.check_zip
        self._asset_pack_status = ASSET_PACK_STATUS
        self._index = 0
        self._total = len(filepaths)
        self._installed_count = 0
        self._fixed_count = 0
        self._failed_files: list[tuple[str, str]] = []
        self._timer = None
        self._busy = False
        self._statusbar_appended = False

        # Background / headless mode has no interactive event loop for modal timers
        if bpy.app.background or context.window is None:
            return self._run_sync(context)

        wm = context.window_manager
        _INSTALL_PROGRESS["active"] = True
        _INSTALL_PROGRESS["index"] = 0
        _INSTALL_PROGRESS["total"] = self._total
        _INSTALL_PROGRESS["filename"] = os.path.basename(self._filepaths[0])
        bpy.types.STATUSBAR_HT_header.append(_draw_statusbar_progress)
        self._statusbar_appended = True
        _tag_statusbar_redraw(context)

        self._timer = wm.event_timer_add(_TIMER_INTERVAL, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        """Install one zip per TIMER tick so Blender can redraw the bottom status bar."""
        if event.type == 'ESC':
            return self._finish(context, cancelled=True)

        if event.type == 'TIMER':
            if self._busy:
                return {'RUNNING_MODAL'}
            self._busy = True
            try:
                self._process_next_zip(context)
            finally:
                self._busy = False

            if self._index >= self._total:
                return self._finish(context, cancelled=False)
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def _run_sync(self, context):
        """Synchronous installation path for background mode and unit tests."""
        try:
            while self._index < self._total:
                self._process_next_zip(context)
        finally:
            self._finish(context, cancelled=False)
        return {'FINISHED'}

    def _process_next_zip(self, context):
        """Install the zip at self._index and advance progress state."""
        filepath = self._filepaths[self._index]
        filename = os.path.basename(filepath)
        _LOG.info(f"Installing asset pack ({self._index + 1}/{self._total}): {filename}")

        _INSTALL_PROGRESS["index"] = self._index
        _INSTALL_PROGRESS["filename"] = filename
        _tag_statusbar_redraw(context)

        ok, err_status, was_fixed = self._install_asset_pack(filepath, self._data_dir, self._check_zip_mode)
        if ok:
            self._installed_count += 1
            if was_fixed:
                self._fixed_count += 1
        else:
            status = err_status or "UNKNOWN"
            self._asset_pack_status["status"] = status
            self._failed_files.append((filename, status))
            _LOG.warn(f"Failed to install asset pack {filename}: {status}")

        self._index += 1
        _INSTALL_PROGRESS["index"] = self._index
        _tag_statusbar_redraw(context)

    def _finish(self, context, cancelled: bool = False):
        """Clean up timer, status bar progress, and report final summary."""
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
            self._timer = None

        _INSTALL_PROGRESS["active"] = False
        if self._statusbar_appended:
            try:
                bpy.types.STATUSBAR_HT_header.remove(_draw_statusbar_progress)
            except ValueError:
                pass
            self._statusbar_appended = False
        _tag_statusbar_redraw(context)

        if self._installed_count > 0:
            AssetService.update_all_asset_lists()

        if cancelled:
            self.report(
                {'WARNING'},
                f"Asset pack installation cancelled ({self._installed_count} of {self._total} installed)."
            )
            return {'CANCELLED'}

        if self._total == 1:
            if self._failed_files:
                _, status = self._failed_files[0]
                if status.startswith("FIX_ERROR") or status == "FIX_FAILED":
                    self.report({'WARNING'}, "Failed to fix zip, see text")
                else:
                    self.report({'WARNING'}, "Bad zip file, see text")
            elif self._fixed_count > 0:
                self.report({'INFO'}, "Assets fixed and installed. If not visible, restart Blender.")
            else:
                self.report({'INFO'}, "Assets should now be available. If they are not visible, then restart Blender.")
            return {'FINISHED'}

        if not self._failed_files:
            self.report({'INFO'}, f"Installed {self._installed_count} asset pack(s). If they are not visible, then restart Blender.")
        elif self._installed_count > 0:
            failed_names = ", ".join(name for name, _ in self._failed_files)
            self.report(
                {'WARNING'},
                f"Installed {self._installed_count} of {self._total} asset pack(s). Failed ({len(self._failed_files)}): {failed_names}. See Library Settings."
            )
        else:
            self.report({'WARNING'}, f"Failed to install all {self._total} asset pack(s). See Library Settings.")

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
