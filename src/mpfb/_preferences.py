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

    mpfb_user_data: bpy.props.StringProperty(
        name="Path to MPFB user data",
        description="If you want to store MPFB user data somewhere other than in the default location, you can enter the path to an existing directory here",
        default=""
    )

    mh_user_data: bpy.props.StringProperty(
        name="Path to MakeHuman user data",
        description="If you want to use assets and models created from or downloaded with MakeHuman, you can specify the path to the data directory here. It is usually ~/Documents/makehuman/v1py3/data or something looking like that",
        default=""
    )

    mh_auto_user_data: bpy.props.BoolProperty(
        name="Autodiscover path to MakeHuman user data",
        description="If the path to the MakeHuman user data directory is not specified, then try to figure it out automatically. If the path is explicitly set, this setting will have no effect",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='You need to restart blender before changes below come into effect.')
        layout.label(text='Remember to save preferences before restarting.')
        layout.prop(self, 'multi_panel')
        layout.prop(self, 'mpfb_user_data')
        layout.prop(self, 'mh_user_data')
        layout.prop(self, 'mh_auto_user_data')
