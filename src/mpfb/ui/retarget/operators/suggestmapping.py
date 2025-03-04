from ....services import LogService
from ....services import ObjectService
from .... import ClassManager
import bpy


_LOG = LogService.get_logger("retarget.operators.suggest_retarget_mapping")


class MPFB_OT_Suggest_Retarget_Mapping_Operator(bpy.types.Operator):
    """Suggest retarget mapping"""

    bl_idname = "mpfb.suggest_retarget_mapping"
    bl_label = "Suggest mapping"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        #return(context.mode == 'OBJECT' and context.active_object.type == 'ARMATURE')
        return(context.active_object.type == 'ARMATURE')

    def process (self, bone, prefix, suffix):
        x = bone.head.x
        if self.pelvis_bone == None and len(bone.children) >= 3: #first bone from root with three or more children should be hte pelvis
            self.pelvis_bone = bone
            prefix = "pelvis"
        elif prefix.startswith("spine_") and len(bone.children) >= 3:
            prefix = "spine_03"
        elif prefix.startswith("arm") and len(bone.children) >= 2: #we expect minimum two finger bones (i.e. thumb and other fingers)
            prefix = "hand"
            if self.num_armbones[suffix] == 2:
                bone.parent.pivot_bone = "lowerarm" + suffix
                bone.parent.parent.pivot_bone = "upperarm" + suffix
            elif self.num_armbones[suffix] == 4:
                bone.parent.pivot_bone = ""
                bone.parent.parent.pivot_bone = "lowerarm" + suffix
                bone.parent.parent.parent.pivot_bone = ""
                bone.parent.parent.parent.parent.pivot_bone = "upperarm" + suffix
        elif prefix == "hand":
            prefix = self.finger_names[self.num_fingers[suffix]] #1 = thumb
            self.num_fingers[suffix] += 1
            self.num_fingerbones[suffix][prefix] = 1
        elif prefix in self.finger_names:
            if len(bone.children) < 1: #just an end bone
                bone.parent.pivot_bone = prefix + "_03" + suffix
                bone.parent.parent.pivot_bone = prefix + "_02" + suffix
                bone.parent.parent.parent.pivot_bone = prefix + "_01" + suffix
                if self.num_fingerbones[suffix][prefix] == 4:
                    bone.parent.parent.parent.parent.pivot_bone = ""
                prefix = ""
                suffix = ""
            else:
                self.num_fingerbones[suffix][prefix] += 1
        else:
            if suffix == "":
                if x > 0.02:
                    suffix = "_l"
                elif x < -0.02:
                    suffix = "_r"
            if suffix != "":
                if prefix == "spine_03":
                    prefix = "clavicle"
                elif prefix == "clavicle" or prefix.startswith("arm"):
                    self.num_armbones[suffix] += 1
                    prefix = "arm" + str(self.num_armbones[suffix])
                else:
                    if prefix == "pelvis":
                        if len(bone.children) < 1: #whatever may be attached to one side of the pelvis that is not a leg (e.g. a weapon)
                            prefix = ""
                            suffix = ""
                        else:
                            prefix = "thigh"
                    elif prefix == "thigh":
                        prefix = "calf"
                    elif prefix == "calf":
                        prefix = "foot"
                    elif prefix == "foot":
                        prefix = "ball"
                    else:
                        if len(bone.children) < 1: #just an end bone
                            prefix = ""
                            suffix = ""
                        else:
                            prefix = "leg" #any  not yet mapped leg bones, just in case
            else:
                if prefix ==  "spine_03":
                    prefix = "neck_01"
                elif prefix ==  "neck_01":
                    prefix = "head"
                elif prefix ==  "spine_01":
                    prefix = "spine_02"
                else:
                    if bone.parent and bone.parent.pivot_bone == "pelvis": #only interested in spine01 here, which should have grandchildren
                        if len(bone.children) < 1 or len(bone.children[0].children) < 1: #no grandchildren
                                prefix = ""
                        else:
                            prefix = "spine_01" #any  not yet mapped spine bones, just in case
        bone.pivot_bone = prefix + suffix
        for child in bone.children:
            self.process(child, prefix, suffix)

    def map(self, context, armature, root):
        self.num_fingers = {"_l": 0, "_r": 0}
        self.num_armbones = {"_l": 0, "_r": 0}
        self.num_fingerbones = {"_l": {}, "_r": {}}
        self.pelvis_bone = None

        self.process(root, "root", "")
        #for bone in source_armature.bones:
        #    bone.pivot_bone = self.find_pivot(bone)

    def execute(self, context):
        self.source_object = context.active_object
        for obj in context.view_layer.objects.selected:
            if obj.type == 'ARMATURE' and obj != context.active_object:
                self.target_object = obj

        source_armature = self.source_object.data
        target_armature = self.target_object.data

        context.scene.bones.clear()
        source_root = None
        for bone in source_armature.bones:
            bone.pivot_bone = ""
            if bone.parent == None:
                source_root = bone
                node = context.scene.bones.add()
                node.armature_name = source_armature.name
                node.name = bone.name

        target_root = None
        for bone in target_armature.bones:
            bone.pivot_bone = ""
            if bone.parent == None:
                target_root = bone

        self.finger_names = list(("thumb", "index", "middle", "ring", "pinky"))
        self.map(source_armature, context, source_root)

        # if source_root.head.z > 1 and target_root.head.z < 1
        #  #root rotation is around the middle of the object. If the target has root at the bottom, better map root to pelvis
        #     source_root.pivot_bone = "pelvis"
        #     self.pelvis_bone.pivot_bone = ""

        self.map(target_armature, context, target_root)

        mapping_source = {}
        for bone in source_armature.bones:
            mapping_source[bone.name] = bone.pivot_bone
        print(mapping_source)

        mapping_target = {}
        for bone in target_armature.bones:
            if bone.pivot_bone != "":
                mapping_target[bone.pivot_bone] = bone.name
        print(mapping_target)

        for bone in source_armature.bones:
            if mapping_source[bone.name] in mapping_target:
                bone.target_bone = mapping_target[mapping_source[bone.name]]
            else:
                bone.target_bone = ""

        return {'FINISHED'}

    # def find_pivot(self, bone):
    #     x = bone.head.x
    #     z = bone.head.z
    #     name = bone.name.lower()
    #     suffix = ""
    #     prefix = ""
    #     if not  bone.parent:
    #         return "root"         #sometimes it is better to map the pelvis to the root (if that is what root motion rotates around)
    #     elif "pelvis" in name or "hip" in name:
    #         self.pelvis_found = True
    #         self.pelvis_height = z
    #         return "pelvis"
    #     if x > 0.02 or "_r" in name or "r_" in name or "right" in name:
    #     #if "_r" in name or "r_" in name or "right" in name:
    #         suffix = "_r"
    #     elif x < -0.02 or "_l" in name or "l_" in name or "left" in name:
    #     #elif "_l" in name or "l_" in name or "left" in name:
    #         suffix = "_l"
    #     if self.pelvis_found:
    #         if z > self.pelvis_height + 0.02:
    #             if suffix != "":
    #                 prefix = "arm"
    #             else:
    #                 prefix = "spine"
    #         elif z < self.pelvis_height - 0.02:
    #             prefix = "leg"
    #     if "thigh" in name or ("up" in name and "leg" in name):
    #         return "thigh" + suffix
    #     elif "calf" in name or (not "up" in name and "leg" in name):
    #         return "calf" + suffix
    #     elif "foot" in name:
    #         return "foot" + suffix
    #     elif "toe" in name:
    #         return "ball" + suffix
    #     elif "clavicle" in name or "shoulder" in name:
    #         return "clavicle" + suffix
    #     elif "arm" in name  and not "fore" in name:
    #         return "upperarm" + suffix
    #     elif "arm" in name  and "fore" in name :
    #         return "lowerarm" + suffix
    #     elif "hand" in name:
    #         return "hand" + suffix
    #     return prefix + suffix


ClassManager.add_class(MPFB_OT_Suggest_Retarget_Mapping_Operator)
