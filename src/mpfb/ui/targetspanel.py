#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
import bpy

_LOG = LogService.get_logger("ui.targetspanel")

class MPFB_PT_Targets_Panel(bpy.types.Panel):
    bl_label = "Targets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("TARGETSCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene

ClassManager.add_class(MPFB_PT_Targets_Panel)
