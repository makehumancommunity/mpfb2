import os, bpy
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import SceneConfigSet
from ...services import UiService
from ...services import RigService
from ..abstractpanel import Abstract_Panel

_LOG = LogService.get_logger("sculpt.sculptpanel")

_LOC = os.path.dirname(__file__)
SCULPT_PROPERTIES_DIR = os.path.join(_LOC, "properties")
SCULPT_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(SCULPT_PROPERTIES_DIR, prefix="SCL_")

class MPFB_PT_SculptPanel(Abstract_Panel):
    bl_label = "Set up for sculpt"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Operations_Panel"

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene

        if context.object is None:
            return

        objtype = ObjectService.get_object_type(context.object)

        if not objtype or objtype == "Skeleton":
            return

        SCULPT_PROPERTIES.draw_properties(scene, layout, ["sculpt_strategy"])

        strategy = SCULPT_PROPERTIES.get_value("sculpt_strategy", entity_reference=scene)

        if not strategy:
            return

        SCULPT_PROPERTIES.draw_properties(scene, layout, ["setup_multires"])

        multires = SCULPT_PROPERTIES.get_value("setup_multires", entity_reference=scene)

        props = []

        if multires:
            props.append("subdivisions")
            props.append("multires_first")

        if objtype == "Basemesh":
            props.append("delete_helpers")

        if objtype in ["Basemesh", "Proxymeshes"]:
            props.append("remove_delete")

        if strategy in ["SOURCEDESTCOPY", "DESTCOPY"]:
            props.append("apply_armature")
            props.append("normal_material")
            material = SCULPT_PROPERTIES.get_value("normal_material", entity_reference=scene)
            if material:
                props.append("resolution")
            props.append("adjust_settings")

        if strategy == "SOURCEDESTCOPY":
            props.append("hide_origin")
        else:
            props.append("hide_related")

        props.append("enter_sculpt")

        SCULPT_PROPERTIES.draw_properties(scene, layout, props)
        layout.operator("mpfb.setup_sculpt")


ClassManager.add_class(MPFB_PT_SculptPanel)
