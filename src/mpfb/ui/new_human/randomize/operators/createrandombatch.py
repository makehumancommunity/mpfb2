"""Operator for creating several randomized humans in one go."""

import random, bpy
from .....services import LogService
from .....services import ObjectService
from .....services import RandomizationService
from .....services import SystemService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec
from .. import characterbuilder
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.createrandombatch")

# The collection every character of one batch is linked into. Blender de-duplicates the name
# (".001", ".002", ...) so successive batches stay in separate collections. Since a modal
# operator cannot be a single clean undo step, deleting this collection is the documented way to
# remove a whole batch.
_BATCH_COLLECTION_NAME = "Random humans"

# The timer interval (seconds) between characters in the modal path. One character is generated
# per tick; between ticks Blender processes its event loop so the UI stays responsive.
_TIMER_INTERVAL = 0.1


class MPFB_OT_Create_Random_Human_Batch_Operator(MpfbOperator):
    """Create several randomized humans in one go, placed in the scene"""
    bl_idname = "mpfb.create_random_human_batch"
    bl_label = "Create random humans"
    # No UNDO: a modal operator does not combine reliably with the UNDO flag. The per-batch
    # collection is the documented way to remove a batch.
    bl_options = {'REGISTER'}

    def get_logger(self):
        return _LOG

    def invoke(self, context, event):
        """Interactive entry point: run modally so the UI stays responsive.

        In background mode (no window / event loop) there is nothing to run modally, so the
        synchronous execute path is used instead.
        """
        _LOG.enter()
        if bpy.app.background:
            return self.execute(context)

        if not self._setup(context):
            return {'CANCELLED'}

        wm = context.window_manager
        wm.progress_begin(0, self._count)
        self._timer = wm.event_timer_add(_TIMER_INTERVAL, window=context.window)
        wm.modal_handler_add(self)
        self._update_status(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        """Generate one character per TIMER event; ESC cancels and keeps the generated ones."""
        if event.type == 'ESC':
            self.report({'INFO'}, "Batch cancelled; the characters generated so far were kept")
            return self._finish(context, cancelled=True)

        if event.type == 'TIMER':
            # The timer keeps firing while a character is being built; guard against re-entry so
            # only one character is generated per tick.
            if self._busy:
                return {'RUNNING_MODAL'}
            self._busy = True
            try:
                self._generate_one(context, self._index)
            finally:
                self._busy = False
            self._index += 1
            context.window_manager.progress_update(self._index)
            if self._index >= self._count:
                return self._finish(context, cancelled=False)
            self._update_status(context)
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def hardened_execute(self, context):
        """Synchronous path used in background mode and by the tests."""
        _LOG.enter()
        if not self._setup(context):
            return {'FINISHED'}

        wm = context.window_manager
        wm.progress_begin(0, self._count)
        try:
            for index in range(self._count):
                self._generate_one(context, index)
                wm.progress_update(index + 1)
        finally:
            self._finish(context, cancelled=False)
        return {'FINISHED'}

    def _setup(self, context):
        """Validate and build all per-batch state; return False (after an ERROR) when invalid.

        Everything expensive or shared between characters is done once here: the spec, the base
        seed, the per-character seeds and placements, the asset discovery context and the batch
        collection. The per-character counters are reset.
        """
        scene = context.scene
        self._timer = None
        self._busy = False
        self._index = 0
        self._generated = 0
        self._skipped = 0

        self._spec = scene_to_spec(scene)
        creation = self._spec["creation"]

        rig_name = creation.get("rig", "NONE")
        if str(rig_name).startswith("rigify.") and not SystemService.check_for_rigify():
            self.report({'ERROR'}, "A rigify rig was selected, but the Rigify addon is not enabled.")
            return False

        batch_spec = self._spec.get("batch") or RandomizationService.get_default_batch_spec()
        self._batch_spec = batch_spec
        self._count = int(batch_spec.get("count", 0))
        if self._count < 1:
            self.report({'ERROR'}, "The number of characters must be at least 1.")
            return False

        base_seed = RANDOMIZE_PROPERTIES.get_value("seed", entity_reference=scene)
        if not base_seed:
            base_seed = random.randint(1, 2 ** 31 - 1)

        # Seeds and placements are derived up front from separate streams, so a character that
        # fails to build later does not shift the seeds or placements of the remaining characters.
        self._seeds = RandomizationService.derive_character_seeds(base_seed, self._count)
        self._placements = RandomizationService.compute_batch_placements(batch_spec, self._count, random.Random(base_seed))

        self._discovery = characterbuilder.build_discovery_context()

        self._collection = bpy.data.collections.new(_BATCH_COLLECTION_NAME)
        context.scene.collection.children.link(self._collection)
        return True

    def _generate_one(self, context, index):
        """Build one character, place it, stamp its seed and link it into the batch collection.

        A character that raises mid-build is removed (its partial objects deleted) and skipped
        with a WARNING; the batch continues, and the remaining characters are unaffected because
        their seeds and placements were derived up front.
        """
        self._ensure_object_mode(context)
        seed = self._seeds[index]
        rng = random.Random(seed)

        existing = set(bpy.data.objects)
        try:
            macro_details = RandomizationService.randomize_macro_info_dict(self._spec, rng)
            basemesh = characterbuilder.build_character(self._spec, macro_details, rng, self.report, self._discovery)
            basemesh["mpfb_randomization_seed"] = seed

            root = _root_of(basemesh)
            self._link_hierarchy(root)
            _place(root, self._placements[index])
            self._generated += 1
        except Exception as problem:  # pylint: disable=broad-except
            self.LOG.error("A character failed to build and was skipped", problem)
            self.report({'WARNING'}, "Character " + str(index + 1) + " failed to build and was skipped: " + str(problem))
            _delete_objects([obj for obj in bpy.data.objects if obj not in existing])
            self._skipped += 1

    def _link_hierarchy(self, root):
        """Move the character's whole object hierarchy into the batch collection.

        Each object is unlinked from every collection it was created in and linked into the batch
        collection instead, so the batch can be hidden, selected or deleted as one unit.
        """
        for obj in _collect_hierarchy(root):
            for collection in list(obj.users_collection):
                collection.objects.unlink(obj)
            self._collection.objects.link(obj)

    def _ensure_object_mode(self, context):
        """Make sure the scene is in object mode before creating a character.

        Between ticks the user may have changed the selection or entered another mode; the
        creation code assumes object mode, so it is asserted per character.
        """
        active = context.view_layer.objects.active
        if active is not None and active.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except RuntimeError:
                pass

    def _update_status(self, context):
        """Show which character is being generated in the workspace status bar."""
        status = "Generating character " + str(self._index + 1) + "/" + str(self._count) + " — ESC to cancel"
        workspace = getattr(context, "workspace", None)
        if workspace is not None:
            try:
                workspace.status_text_set(status)
            except (AttributeError, RuntimeError):
                pass

    def _finish(self, context, cancelled):
        """Clean up the timer, progress and status on every exit path, then report the summary.

        This is called from the modal path (on completion, cancel and after each character) and
        from the synchronous path, so the cursor and status text are never left stuck.
        """
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
            self._timer = None
        wm.progress_end()
        workspace = getattr(context, "workspace", None)
        if workspace is not None:
            try:
                workspace.status_text_set(None)
            except (AttributeError, RuntimeError):
                pass

        self._report_summary()
        self._advance_seed(context)
        return {'CANCELLED'} if cancelled else {'FINISHED'}

    def _report_summary(self):
        """Report the final INFO summary: generated count, skipped count and collection name."""
        overlaps = sum(1 for placement in self._placements[:self._generated + self._skipped] if placement.get("overlap"))
        if overlaps:
            self.report({'WARNING'}, str(overlaps) + " character(s) could not honor the minimum distance and were placed with an overlap")
        self.report({'INFO'}, "Batch complete: " + str(self._generated) + " generated, " + str(self._skipped) +
                    " skipped, in collection '" + self._collection.name + "'")

    def _advance_seed(self, context):
        """Advance the seed field after the batch when "new random seed" is enabled.

        This mirrors the single-character operator, so a subsequent batch produces different
        characters without further user action.
        """
        if RANDOMIZE_PROPERTIES.get_value("new_random_seed", entity_reference=context.scene):
            RANDOMIZE_PROPERTIES.set_value("seed", random.randint(1, 2 ** 31 - 1), entity_reference=context.scene)


def _root_of(blender_object):
    """Return the topmost parent of an object (the armature when rigged, else the object)."""
    root = blender_object
    while root.parent is not None:
        root = root.parent
    return root


def _collect_hierarchy(root):
    """Return the root object together with all of its recursive children."""
    result = [root]
    stack = [root]
    while stack:
        current = stack.pop()
        for child in ObjectService.get_list_of_children(current):
            result.append(child)
            stack.append(child)
    return result


def _place(root, placement):
    """Translate and rotate a character's root object according to its placement.

    Only X and Y are set (the feet-on-ground z is left untouched); the rotation is around Z.
    """
    location = placement["location"]
    root.location = (location[0], location[1], root.location[2])
    rotation = root.rotation_euler
    root.rotation_euler = (rotation[0], rotation[1], placement["rotation_z"])


def _delete_objects(objects):
    """Remove a list of objects from the blend file, ignoring already-removed ones."""
    for obj in objects:
        try:
            bpy.data.objects.remove(obj, do_unlink=True)
        except (ReferenceError, RuntimeError):
            pass


ClassManager.add_class(MPFB_OT_Create_Random_Human_Batch_Operator)
