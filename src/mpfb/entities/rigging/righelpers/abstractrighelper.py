"""Helper for managing mode switches."""

import bpy, typing

from ....services import LogService
_LOG = LogService.get_logger("abstractrighelper")

HelperMode = typing.Literal["EDIT", "POSE", "OBJECT"]
"""The three interaction modes the rig helpers switch between.

A ``Literal`` rather than a bare ``str`` because ``bpy.ops.object.mode_set()`` declares its ``mode``
argument as a literal of the full set of object modes, and because these three are the only ones the
helpers have any use for."""

class AbstractRigHelper():
    """
    A helper class for managing rig-related operations in Blender.

    This class provides methods to switch between different modes (Edit, Pose, Object)
    and ensures that mode changes are performed only when necessary.
    """

    def checked_mode_set(self, mode: HelperMode) -> None:
        """
        Set the Blender mode if it's different from the current mode.

        Args:
            mode: The desired Blender mode ('EDIT', 'POSE', or 'OBJECT').

        Note:
            This method checks the current mode before switching to avoid unnecessary mode changes.
        """
        current_mode = bpy.context.mode
        if current_mode != mode:
            _LOG.debug("Switching mode (from, to)", (current_mode, mode))
            bpy.ops.object.mode_set(mode=mode, toggle=False)
        else:
            _LOG.trace("Current mode is already", mode)

    def edit_mode(self) -> None:
        """
        Switch to Edit mode.

        This method is a convenience wrapper for switching to 'EDIT' mode.
        """
        self.checked_mode_set('EDIT')

    def pose_mode(self) -> None:
        """
        Switch to Pose mode.

        This method is a convenience wrapper for switching to 'POSE' mode.
        """
        self.checked_mode_set('POSE')

    def object_mode(self) -> None:
        """
        Switch to Object mode.

        This method is a convenience wrapper for switching to 'OBJECT' mode.
        """
        self.checked_mode_set('OBJECT')
