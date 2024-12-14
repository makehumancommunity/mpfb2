"""This file handles addon preferences for MPFB."""

import bpy


def update_second_root(self, context):
    from .services import LocationService


def update_mh_data(self, context):
    from .services import LocationService
    LocationService.update_mh_data()


class MpfbPreferences(bpy.types.AddonPreferences):
    """Preferences for MPFB"""

    bl_idname = __package__

    #===========================================================================
    # multi_panel: bpy.props.BoolProperty(
    #     name="UI layout with multiple panels",
    #     description="Use a layout with multiple panels, such as one for targets, one for materials and so on, rather than everything in a single panel.",
    #     default=False
    # )
    #===========================================================================

    mpfb_user_data: bpy.props.StringProperty(
        name="Path to MPFB user data",
        description="If you want to store MPFB user data somewhere other than in the default location, you can enter the path to an existing directory here",
        default=""
    )

    mpfb_second_root: bpy.props.StringProperty(
        name="Secondary asset root",
        description="If you want to discover assets from an additional directory, enter the path here. This should be equivalent of a \"data\" directory, ie it should contain subdirs \"clothes\", \"hair\" and so on. Note that only mesh and material assets will be found here",
        default="",
        update=update_second_root
    )

    mh_user_data: bpy.props.StringProperty(
        name="Path to MakeHuman user data",
        description="If you want to use assets and models created from or downloaded with MakeHuman, you can specify the path to the data directory here. It is usually ~/Documents/makehuman/v1py3/data or something looking like that",
        default="",
        update=update_mh_data
    )

    mh_auto_user_data: bpy.props.BoolProperty(
        name="Autodiscover path to MakeHuman user data",
        description="If the path to the MakeHuman user data directory is not specified, then try to figure it out automatically. If the path is explicitly set, this setting will have no effect",
        default=False
    )

    mpfb_excepthook: bpy.props.BoolProperty(
        name="Globally log all uncaught exceptions",
        description="In order to log unhandled exceptions, MPFB can override the global exception handler. This might cause problems when reloading and/or together with other modules. However, if you run into a crash and need a proper log, you can enable this temporarily",
        default=False
    )

    mpfb_codechecks: bpy.props.BoolProperty(
        name="Dynamically perform code checks on startup",
        description="This is mainly geared towards developers. Enable this to output warnings to the log for when an operator or a panel does not use code robustness wrappers",
        default=False
    )

    mpfb_shelf_label: bpy.props.StringProperty(
        name="Shelf label",
        description="If you want to use a different name for the MPFB shelf tab, you can enter any non-empty string here",
        default=""
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='You need to restart blender before some of these changes come into effect.')
        layout.label(text='Remember to save preferences before restarting.')
#        layout.prop(self, 'multi_panel')
        layout.prop(self, 'mpfb_user_data')
        layout.prop(self, 'mpfb_second_root')
        layout.prop(self, 'mpfb_excepthook')
        layout.prop(self, 'mpfb_codechecks')
        layout.prop(self, 'mpfb_shelf_label')
        layout.prop(self, 'mh_user_data')
        layout.prop(self, 'mh_auto_user_data')
