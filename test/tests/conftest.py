"""Remove the datablocks each test added."""

import bpy
import pytest

# Object data is listed after "objects" on purpose: an object keeps its data in use, so the objects
# have to go first or the data cannot be removed.
TRACKED_DATABLOCK_KINDS = (
    "objects",
    "meshes",
    "armatures",
    "curves",
    "hair_curves",
    "materials",
    "images",
    "node_groups",
    "actions",
    "lights",
    "cameras",
    "worlds",
    "collections",
)


def datablock_pointers():
    """A pointer set per tracked datablock kind, for telling apart what was there before."""
    return {kind: {block.as_pointer() for block in getattr(bpy.data, kind)} for kind in TRACKED_DATABLOCK_KINDS}


def _return_to_object_mode():
    """Blender refuses to remove datablocks that are in edit mode."""
    if bpy.context.object is None or bpy.context.object.mode == 'OBJECT':
        return
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception as exception:   # a failing test may have left an unusable context
        print(f"conftest: could not return to object mode: {exception}")


def remove_datablocks_added_since(before):
    """Remove every tracked datablock which is not in the given pointer sets. Returns how many went."""
    removed = 0
    for kind in TRACKED_DATABLOCK_KINDS:
        collection = getattr(bpy.data, kind)
        added = [block for block in collection if block.as_pointer() not in before[kind]]
        for block in added:
            try:
                block.use_fake_user = False
                collection.remove(block, do_unlink=True)
                removed += 1
            except Exception as exception:
                print(f"conftest: could not remove {kind} {block!r}: {exception}")
    return removed


@pytest.fixture(autouse=True)
def clean_datablocks_after_each_test():
    """Whatever a test adds to the blend file is removed again when it finishes.

    This is autouse, so it applies to every test in the suite. A test which deliberately relies on
    data surviving into the next test would break under it -- none does, and none should, but that
    is worth remembering if a new test ever passes on its own and fails inside a full run.
    """
    before = datablock_pointers()
    yield
    _return_to_object_mode()
    remove_datablocks_added_since(before)
