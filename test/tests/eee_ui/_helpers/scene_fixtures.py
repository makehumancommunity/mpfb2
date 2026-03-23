"""Scene fixtures for UI tests: HumanFixture, HumanWithRigFixture, HumanWithRigAndClothesFixture, SceneSnapshot,
BasemeshWithTargetFixture, TwoHumansWithRigsFixture, BasemeshWithMakeSkinFixture,
BasemeshWithV2SkinFixture, TwoMixamoArmaturesFixture, OpenPoseRigFixture,
SceneWithCameraFixture."""

import bpy
import pytest
from ... import dynamic_import

# Somewhat ugly workaround, but if we're importing this module we are in unit testing mode.
# Thus it will make sense to always raise exceptions in MpfbOperator
set_raise_exceptions_in_mpfboperator = dynamic_import("mpfb.ui.mpfboperator", "set_raise_exceptions_in_mpfboperator")
set_raise_exceptions_in_mpfboperator(True)

class SceneSnapshot:
    """Records object names before a test; deletes new objects on cleanup."""

    def __init__(self):
        self._before = None

    def take(self):
        self._before = set(obj.name for obj in bpy.data.objects)

    def cleanup(self):
        if self._before is None:
            return
        to_delete = [obj for obj in bpy.data.objects if obj.name not in self._before]
        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)


class HumanFixture:
    """Creates a minimal basemesh for a test and deletes it on cleanup."""

    def __init__(self):
        self.basemesh = None
        self._snapshot = SceneSnapshot()

    def setup(self):
        from ... import HumanService, ObjectService   # lazy import (runs inside Blender)
        self._snapshot.take()
        self.basemesh = HumanService.create_human()
        assert self.basemesh is not None, "HumanFixture: failed to create basemesh"
        ObjectService.activate_blender_object(self.basemesh)
        return self

    def cleanup(self):
        self._snapshot.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


class HumanWithRigFixture(HumanFixture):
    """Extends HumanFixture with a default rig."""

    def __init__(self):
        super().__init__()
        self.rig = None

    def setup(self):
        super().setup()
        from ... import HumanService, ObjectService   # lazy import
        try:
            HumanService.add_builtin_rig(self.basemesh, "default")
            self.rig = self.basemesh.parent
            ObjectService.activate_blender_object(self.rig)
        except Exception as exc:
            self.cleanup()
            pytest.skip(f"HumanWithRigFixture: could not add rig: {exc}")
        return self


class HumanWithRigAndClothesFixture(HumanWithRigFixture):
    """Extends HumanWithRigFixture with a clothes asset loaded from testdata."""

    _MHCLO = None   # resolved once, then cached

    def __init__(self):
        super().__init__()
        self.clothes = None

    @classmethod
    def _get_mhclo_path(cls):
        if cls._MHCLO is None:
            import os
            cls._MHCLO = os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "testdata", "better_socks_low.mhclo"
            )
        return cls._MHCLO

    def setup(self):
        super().setup()
        from ... import HumanService, ObjectService   # lazy import
        try:
            self.clothes = HumanService.add_mhclo_asset(
                self._get_mhclo_path(), self.basemesh
            )
            assert self.clothes is not None, "HumanWithRigAndClothesFixture: add_mhclo_asset returned None"
            ObjectService.activate_blender_object(self.basemesh)
        except Exception as exc:
            self.cleanup()
            pytest.skip(f"HumanWithRigAndClothesFixture: could not add clothes: {exc}")
        return self


class BasemeshWithTargetFixture:
    """Creates a basemesh that already has a named 'test_target' shape key.

    Satisfies the poll() check used by WriteTargetOperator, WriteLibTargetOperator,
    PrintTargetOperator, SymmetrizeLeftOperator, and SymmetrizeRightOperator.
    """

    def __init__(self):
        self.basemesh = None
        self.target_name = "test_target"
        self._snapshot = SceneSnapshot()

    def setup(self):
        from ... import HumanService, ObjectService, TargetService  # lazy import
        self._snapshot.take()
        self.basemesh = HumanService.create_human()
        assert self.basemesh is not None, "BasemeshWithTargetFixture: failed to create basemesh"
        MakeTargetObjectProperties = _get_make_target_object_properties()
        MakeTargetObjectProperties.set_value("name", self.target_name, entity_reference=self.basemesh)
        TargetService.create_shape_key(self.basemesh, self.target_name)
        ObjectService.activate_blender_object(self.basemesh)
        return self

    def cleanup(self):
        self._snapshot.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


def _get_make_target_object_properties():
    """Lazily resolve MakeTargetObjectProperties via dynamic_import."""
    from ... import dynamic_import
    return dynamic_import("mpfb.ui.create_assets.maketarget", "MakeTargetObjectProperties")


class TwoHumansWithRigsFixture:
    """Creates two human+rig pairs with both armatures selected.

    Required by MPFB_OT_Auto_Transfer_Weights_Operator.poll(), which checks for
    exactly two armatures selected, each with a basemesh child.
    """

    def __init__(self):
        self.rig1 = None
        self.rig2 = None
        self.basemesh1 = None
        self.basemesh2 = None
        self._snapshot = SceneSnapshot()

    def setup(self):
        from ... import HumanService, ObjectService  # lazy import
        self._snapshot.take()
        try:
            self.basemesh1 = HumanService.create_human()
            assert self.basemesh1 is not None, "TwoHumansWithRigsFixture: failed to create basemesh1"
            HumanService.add_builtin_rig(self.basemesh1, "default")
            self.rig1 = self.basemesh1.parent

            self.basemesh2 = HumanService.create_human()
            assert self.basemesh2 is not None, "TwoHumansWithRigsFixture: failed to create basemesh2"
            HumanService.add_builtin_rig(self.basemesh2, "default")
            self.rig2 = self.basemesh2.parent

            ObjectService.deselect_and_deactivate_all()
            self.rig1.select_set(True)
            self.rig2.select_set(True)
            ObjectService.activate_blender_object(self.rig1)
        except Exception as exc:
            self.cleanup()
            pytest.skip(f"TwoHumansWithRigsFixture: could not set up two rigs: {exc}")
        return self

    def cleanup(self):
        self._snapshot.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


class BasemeshWithMakeSkinFixture:
    """Creates a basemesh with a MakeSkin template material applied.

    Satisfies the precondition for CreateInkOperator and WriteInkOperator, which
    require the active basemesh to have a MakeSkin material.
    """

    def __init__(self):
        self.basemesh = None
        self.material = None
        self._human_fixture = HumanFixture()

    def setup(self):
        from ... import MaterialService, dynamic_import  # lazy import
        self._human_fixture.setup()
        self.basemesh = self._human_fixture.basemesh

        MPFB_OT_CreateMaterialOperator = dynamic_import(
            "mpfb.ui.create_assets.makeskin.operators",
            "MPFB_OT_CreateMaterialOperator"
        )
        from .mock_operator_base import MockOperatorBase
        import bpy
        result = MPFB_OT_CreateMaterialOperator.execute(MockOperatorBase(), bpy.context)
        assert result == {'FINISHED'}, f"BasemeshWithMakeSkinFixture: material creation returned {result}"
        assert MaterialService.has_materials(self.basemesh), "BasemeshWithMakeSkinFixture: no material on basemesh"
        self.material = self.basemesh.data.materials[0]
        return self

    def cleanup(self):
        self._human_fixture.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


class BasemeshWithV2SkinFixture:
    """Creates a basemesh with a V2 skin material applied.

    Satisfies the precondition for MPFB_OT_Remove_Makeup_Operator and
    MPFB_OT_Set_Normalmap_Operator, which require the active basemesh to have
    a V2 skin material.
    """

    def __init__(self):
        self.basemesh = None
        self.material = None
        self._human_fixture = HumanFixture()

    def setup(self):
        from ... import MaterialService, dynamic_import  # lazy import
        self._human_fixture.setup()
        self.basemesh = self._human_fixture.basemesh

        MPFB_OT_Create_V2_Skin_Operator = dynamic_import(
            "mpfb.ui.operations.matops.operators.createv2skin",
            "MPFB_OT_Create_V2_Skin_Operator"
        )
        from .mock_operator_base import MockOperatorBase
        import bpy
        result = MPFB_OT_Create_V2_Skin_Operator.execute(MockOperatorBase(), bpy.context)
        assert result == {'FINISHED'}, f"BasemeshWithV2SkinFixture: v2 skin creation returned {result}"
        assert MaterialService.has_materials(self.basemesh), "BasemeshWithV2SkinFixture: no material on basemesh"
        self.material = self.basemesh.data.materials[0]
        return self

    def cleanup(self):
        self._human_fixture.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


class TwoMixamoArmaturesFixture:
    """Creates two armatures containing the standard Mixamo bone set, both selected.

    Required by MPFB_OT_Map_Mixamo_Operator and MPFB_OT_Repeat_Animation_Operator,
    which expect two armatures selected with bones named with the mixamorig: prefix.
    Source armature is the active object.
    """

    MIXAMO_BONES = [
        "mixamorig:Hips", "mixamorig:Spine", "mixamorig:Spine1",
        "mixamorig:LeftUpLeg", "mixamorig:RightUpLeg",
        "mixamorig:LeftLeg", "mixamorig:RightLeg",
        "mixamorig:LeftFoot", "mixamorig:RightFoot",
        "mixamorig:LeftArm", "mixamorig:RightArm",
        "mixamorig:LeftForeArm", "mixamorig:RightForeArm",
        "mixamorig:LeftHand", "mixamorig:RightHand",
        "mixamorig:Head", "mixamorig:Neck",
        "mixamorig:LeftShoulder", "mixamorig:RightShoulder",
    ]

    def _make_mixamo_armature(self, name):
        import bpy
        arm_data = bpy.data.armatures.new(name + "_data")
        arm_obj = bpy.data.objects.new(name, arm_data)
        bpy.context.scene.collection.objects.link(arm_obj)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name in self.MIXAMO_BONES:
            bone = arm_data.edit_bones.new(bone_name)
            bone.head = (0, 0, 0)
            bone.tail = (0, 0, 0.1)
        bpy.ops.object.mode_set(mode='OBJECT')
        return arm_obj

    def __init__(self):
        self.src_arm = None
        self.dst_arm = None
        self._snapshot = SceneSnapshot()

    def setup(self):
        from ... import ObjectService  # lazy import
        self._snapshot.take()
        try:
            self.src_arm = self._make_mixamo_armature("mixamo_src")
            self.dst_arm = self._make_mixamo_armature("mixamo_dst")
            ObjectService.deselect_and_deactivate_all()
            self.src_arm.select_set(True)
            self.dst_arm.select_set(True)
            ObjectService.activate_blender_object(self.src_arm)
        except Exception as exc:
            self.cleanup()
            pytest.skip(f"TwoMixamoArmaturesFixture: could not create mixamo armatures: {exc}")
        return self

    def cleanup(self):
        self._snapshot.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()


class OpenPoseRigFixture(HumanFixture):
    """Extends HumanFixture with an OpenPose rig attached to the basemesh.

    Required by MPFB_OT_OpenPose_Visible_Bones_Operator and
    MPFB_OT_Save_Openpose_Operator, which expect an OpenPose rig to be active.
    """

    def __init__(self):
        super().__init__()
        self.rig = None

    def setup(self):
        super().setup()
        from ... import HumanService, ObjectService  # lazy import
        try:
            HumanService.add_builtin_rig(self.basemesh, "openpose")
            self.rig = self.basemesh.parent
            ObjectService.activate_blender_object(self.rig)
        except Exception as exc:
            self.cleanup()
            pytest.skip(f"OpenPoseRigFixture: could not add openpose rig: {exc}")
        return self


class SceneWithCameraFixture:
    """Adds a camera to the scene.

    Required by MPFB_OT_Save_Openpose_Operator, which needs a camera present.
    Can be used standalone or layered on top of another fixture.
    """

    def __init__(self):
        self._snapshot = SceneSnapshot()
        self.camera = None

    def setup(self):
        import bpy
        self._snapshot.take()
        cam_data = bpy.data.cameras.new("test_camera")
        self.camera = bpy.data.objects.new("test_camera", cam_data)
        bpy.context.scene.collection.objects.link(self.camera)
        return self

    def cleanup(self):
        self._snapshot.cleanup()

    def __enter__(self):
        return self.setup()

    def __exit__(self, *args):
        self.cleanup()
