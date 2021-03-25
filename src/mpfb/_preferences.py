"""This file handles addon preferences."""

import bpy

class MpfbPreferences(bpy.types.AddonPreferences):
    """Preferences for MPFB"""

    bl_idname = __package__

    multi_panel: bpy.props.BoolProperty(
        name="UI layout with multiple panels",
        description="Use a layout with multiple panels, such as one for targets, one for materials and so on, rather than everything in a single panel.",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='You need to restart blender before changes below come into effect.')
        layout.label(text='Remember to save preferences before restarting.')
        layout.prop(self, 'multi_panel')
