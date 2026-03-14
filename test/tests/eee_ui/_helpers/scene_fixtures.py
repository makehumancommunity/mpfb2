"""Scene fixtures for UI tests: HumanFixture, HumanWithRigFixture, HumanWithRigAndClothesFixture, SceneSnapshot,
BasemeshWithTargetFixture, TwoHumansWithRigsFixture, BasemeshWithMakeSkinFixture."""

import bpy
import pytest


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
