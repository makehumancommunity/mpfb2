import bpy

from rna_prop_ui import rna_idprop_quote_path

from mpfb._classmanager import ClassManager
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.ui.abstractpanel import Abstract_Panel

from . import BOP_PROPERTIES, BoneOpsEditBoneProperties, BoneOpsBoneProperties, BoneOpsArmatureProperties
from .operators import MPFB_OT_Reapply_Bone_Strategy_Operator, MPFB_OT_Set_Roll_Strategy_Operator,\
    MPFB_OT_Set_Bone_End_Strategy_Operator, MPFB_OT_Show_Strategy_Vertices_Operator,\
    MPFB_OT_Save_Strategy_Vertices_Operator, MPFB_OT_Copy_Connected_Strategy_Operator

_LOG = LogService.get_logger("poseops.bonestratpanel")


class MPFB_PT_BonestratPanel(Abstract_Panel):
    bl_label = "MPFB Bone Strategies"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        bone = context.edit_bone or context.bone
        if not bone:
            return False

        obj = context.active_object

        return ((context.edit_bone or obj and obj.type == "MESH" and obj.mode == "EDIT")
                and BoneOpsArmatureProperties.get_value("developer_mode", entity_reference=bone.id_data))

    def _draw_end_strategy(self, context, properties, armature, bone, is_tail: bool):
        end = "tail" if is_tail else "head"

        box = self.layout.box()

        # Title row
        row = box.row()
        row.label(text=end.capitalize() + " Strategy:")
        row.operator(MPFB_OT_Reapply_Bone_Strategy_Operator.bl_idname, text="", icon="FILE_REFRESH").is_tail = is_tail

        # Chosen strategy header
        box2 = box.box()
        row = box2.row()

        id_strategy = end + "_strategy"
        strategy = properties.get_value(id_strategy, entity_reference=bone)
        has_vertices = False

        if "CUBE" == strategy:
            row.label(text="Joint", icon="BONE_DATA")
        elif "VERTEX" == strategy:
            has_vertices = True
            row.label(text="Vertex", icon="VERTEXSEL")
        elif "MEAN" == strategy:
            has_vertices = True
            row.label(text="Mean", icon="PIVOT_MEDIAN")
        elif "XYZ" == strategy:
            has_vertices = True
            row.label(text="XYZ", icon="EMPTY_AXIS")
        elif "DEFAULT" == strategy:
            row.label(text="No match", icon="CANCEL")
        elif not strategy:
            row.label(text="Unknown", icon="QUESTION")
        else:
            properties.draw_properties(bone, row, [id_strategy], text="", icon="ERROR")

        icon = "LOCKED" if properties.get_value(end + "_strategy_lock", entity_reference=bone) else "UNLOCKED"
        properties.draw_properties(bone, row, [end + "_strategy_lock"], text="", icon=icon)

        # Buttons for switching to/from Edit mode and modifying vertices
        op_sel = MPFB_OT_Show_Strategy_Vertices_Operator
        op_save = MPFB_OT_Save_Strategy_Vertices_Operator
        in_mesh_edit = False

        if has_vertices:
            row2 = row.row(align=True)

            if context.active_object and context.active_object.type == "MESH" and context.active_object.mode == "EDIT":
                in_mesh_edit = True
                props = row2.operator(op_save.bl_idname, text="", icon="ARMATURE_DATA")
                props.switch = True
                props.save = False
                props = row2.operator(op_save.bl_idname, text="", icon="CHECKMARK")
                props.switch = True
                props.save = True
                props.is_tail = is_tail
                props.index = -1
            else:
                props = row2.operator(op_sel.bl_idname, text="", icon="MESH_DATA")
                props.select = False
                props = row2.operator(op_sel.bl_idname, text="", icon="EYEDROPPER")
                props.select = True
                props.is_tail = is_tail
                props.index = -1

        # Chosen strategy data
        data_row = box2.row()

        if "CUBE" == strategy:
            id_cube = end + "_cube_name"
            id_name = properties.get_fullname_key_from_shortname_key(id_cube)
            is_error = "joint" not in properties.get_value(id_cube, entity_reference=bone)
            icon = "ERROR" if is_error else "GROUP_VERTEX"

            row = data_row.row()
            row.alert = is_error

            _rig, basemesh, _mesh = ObjectService.find_armature_context_objects(armature, only_basemesh=True)
            if basemesh:
                row.prop_search(bone, id_name, basemesh, "vertex_groups", text="", icon=icon)
            else:
                row.prop(bone, id_name, text="", icon=icon)

        elif "VERTEX" == strategy:
            properties.draw_properties(bone, data_row, [end + "_vertex_index"], text="")

        elif strategy in ("XYZ", "MEAN"):
            id_name = properties.get_fullname_key_from_shortname_key(end + "_vertex_indices")
            id_path = rna_idprop_quote_path(id_name)

            data = list(bone.get(id_name, []))

            if data:
                col = data_row.column(align=True)
                for i in range(len(data)):
                    row = col.row()
                    row.prop(bone, id_path, index=i, text="")

                    if strategy == "XYZ" and in_mesh_edit:
                        row2 = row.row(align=True)
                        props = row2.operator(op_sel.bl_idname, text="", icon="EYEDROPPER")
                        props.select = True
                        props.is_tail = is_tail
                        props.index = i
                        props = row2.operator(op_save.bl_idname, text="", icon="GREASEPENCIL")
                        props.switch = False
                        props.save = True
                        props.is_tail = is_tail
                        props.index = i
            else:
                data_row.label(text="No vertices", icon="ERROR")
        else:
            data_row.separator()

        if has_vertices and in_mesh_edit and strategy != "XYZ":
            row2 = data_row.row(align=True)
            props = row2.operator(op_sel.bl_idname, text="", icon="EYEDROPPER")
            props.select = True
            props.is_tail = is_tail
            props.index = -1
            props = row2.operator(op_save.bl_idname, text="", icon="GREASEPENCIL")
            props.switch = False
            props.save = True
            props.is_tail = is_tail
            props.index = -1

        # Buttons for switching to a different strategy mode
        box.label(text="Change to:")

        row = box.row(align=True)
        op = MPFB_OT_Set_Bone_End_Strategy_Operator

        for strategy_id, strategy_info in op.known_strategies.items():
            selected = strategy_id == strategy
            op_row = row
            if selected:
                op_row = row.row(align=True)
                op_row.enabled = False

            props = op_row.operator(op.bl_idname, text=strategy_info[0])
            props.is_tail = is_tail
            props.strategy = strategy_id

    def _draw_roll_strategy(self, properties, _armature, bone):
        box = self._create_box(self.layout, "Roll Strategy:")
        op = MPFB_OT_Set_Roll_Strategy_Operator

        strategy = properties.get_value("roll_strategy", entity_reference=bone)
        col = box.column(align=True)

        for strategy_id, strategy_info in op.known_strategies.items():
            selected = strategy == strategy_id
            props = col.operator(op.bl_idname, text=strategy_info[0], depress=selected)
            props.strategy = strategy_id

        if strategy not in op.known_strategies:
            properties.draw_properties(bone, col, ["roll_strategy"], text="", icon="ERROR")

    def draw(self, context):
        _LOG.enter()

        layout = self.layout
        scene = context.scene
        armature = context.object

        if context.edit_bone:
            bone = context.edit_bone
            properties = BoneOpsEditBoneProperties
        else:
            bone = context.bone
            properties = BoneOpsBoneProperties

        # Find armature by bone
        if not armature or armature.data != bone.id_data:
            armature = ObjectService.find_by_data(bone.id_data)

        box = layout.box()
        row = box.row()
        BOP_PROPERTIES.draw_properties(scene, row, ['keep_linked'])
        row.operator(MPFB_OT_Copy_Connected_Strategy_Operator.bl_idname, text="", icon="SNAP_ON")

        self._draw_end_strategy(context, properties, armature, bone, False)
        self._draw_end_strategy(context, properties, armature, bone, True)

        self._draw_roll_strategy(properties, armature, bone)


ClassManager.add_class(MPFB_PT_BonestratPanel)
