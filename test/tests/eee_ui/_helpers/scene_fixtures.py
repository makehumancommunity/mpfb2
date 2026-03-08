"""Scene fixtures for UI tests: HumanFixture, HumanWithRigFixture, HumanWithRigAndClothesFixture, SceneSnapshot."""

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
