"""Shared type aliases for the MPFB services and entities layers.

This module exists so that type shapes which cross more than one module are declared once
rather than redefined per module. It deliberately imports nothing from MPFB, so that
importing it can never disturb the deferred-import rule in ``__init__.py`` or introduce a
cycle between services. It is annotation support only and must not gain runtime logic.
"""

from collections.abc import Callable
from typing import Any

PropertyDefinition = dict[str, Any]
"""The dict shape describing a single blender property in a ConfigurationSet.

Recognized keys are ``name`` (the short, unprefixed name), ``type`` (one of ``boolean``,
``string``, ``path``, ``dir_path``, ``int``, ``float``, ``vector_location``, ``color`` or
``enum``), ``description`` and ``default``, plus the optional ``label``, ``subtype``,
``aliases``, ``min``, ``max`` and ``items``. ``BlenderConfigSet`` adds ``full_name``, the
prefixed name the property is actually registered under, to its own copy of the dict.

This is an alias rather than a ``TypedDict`` on purpose: these dicts are read straight from
JSON, copied with ``dict()``, and then extended in place with ``full_name``, none of which a
``TypedDict`` models well.
"""

PropertyAccessorFactory = Callable[[Any, str], Any]
"""A factory which builds a blender property get/set callback for a single property.

It is called with the ConfigurationSet the property belongs to and the short name of that
property, and returns the callback to hand to ``bpy.props`` as ``get=`` or ``set=``. The
configuration set is typed as ``Any`` rather than ``ConfigurationSet`` so that this module
stays free of MPFB imports; the returned callback is typed as ``Any`` because its own
signature depends on the property type it is being built for.
"""

BoneInfo = dict[str, Any]
"""Everything a rig definition records about a single bone.

The stable keys are ``parent`` (a bone name or the empty string), ``head`` and ``tail`` (each a
nested dict, see ``entities.rig.BoneEndInfo``), ``use_connect``, ``use_local_location``,
``use_inherit_rotation``, ``inherit_scale``, ``collections`` (a sorted list of bone collection
names) and ``roll``. ``bendy_bone``, ``rotation_mode``, ``constraints``, ``roll_strategy``,
``roll_reference_z`` and ``rigify`` are present only when they carry something. Version 100
definitions instead carried ``layers``, a 32 element bool list, which ``Rig._upgrade_definition()``
rewrites into ``collections``.

An alias rather than a ``TypedDict`` because the dict is built up across four passes --
``add_data_bone_info()``, ``add_edit_bone_info()``, ``add_pose_bone_info()`` and the strategy
matching -- so no single point in the code sees the complete shape, and because ``cleanup_float_values()``
reads and rewrites several entries through computed keys."""

RigDefinition = dict[str, BoneInfo]
"""The ``bones`` section of a rig file: bone name to its ``BoneInfo``."""

RigHeader = dict[str, Any]
"""The top level of a rig file.

``version`` holds the format version as an int and ``bones`` holds the ``RigDefinition``; both are
always present. ``is_subrig`` is a bool, ``scale_factor`` a float, ``collections`` a list of bone
collection names, ``extra_bones`` a list of bone names and ``rigify_ui`` a ``RigifyUi``. An alias
rather than a ``TypedDict`` because a version 100 file has only the two mandatory keys, so every
other entry is read with ``get()`` and may be absent."""

RigifyUi = dict[str, Any]
"""The rigify colour and bone collection settings carried in a rig file's ``rigify_ui`` entry.

``rigify_colors_lock`` is a bool, ``selection_colors`` a dict with ``select`` and ``active``,
``colors`` a list of ``{name, normal}`` dicts, and ``collections`` a dict keyed by bone collection
name holding ``is_visible``, ``ui_row``, ``ui_title``, ``sel_set`` and ``color_set_id``. A version
100 file instead carries ``layers`` and ``rigify_layers``, which
``RigifyHelpers.upgrade_rigify_ui_layers()`` replaces with ``collections``. An alias and not a
``TypedDict`` precisely because of that rewrite: the same dict holds the old keys on the way in and
the new ones on the way out."""

RigifyBoneInfo = dict[str, Any]
"""The ``rigify`` entry of a ``BoneInfo``.

``rigify_type`` holds the name of a rigify rig class and ``rigify_parameters`` a dict of that
class's parameters. Both are optional, and an empty dict is the normal state for a bone rigify does
not drive. The parameter values are whatever the rigify add-on registered, so they are read and
written as ``Any``."""

RigHelperSettings = dict[str, Any]
"""The settings dict the rig helper classes under ``entities.rigging.righelpers`` are constructed with.

It is a ``SceneConfigSet.as_dict()`` result, so the keys are the short names of the helper
properties -- ``arm_helpers_type``, ``leg_helpers_type``, ``finger_helpers_type``,
``eye_parenting_strategy``, ``hide_fk`` and the rest -- and the values arrive as ``Any``. An alias
rather than a ``TypedDict`` both for that reason and because the helpers test for membership before
reading, since a caller may hand over a dict built for one limb only."""

RigifySettings = dict[str, Any]
"""The settings dict ``RigifyHelpers`` is constructed with.

A separate name from ``RigHelperSettings`` because it is a different property set -- ``name``,
``produce`` and ``meta_rig_action`` -- even though the two definitions coincide. Same reasoning for
the alias: the values come from ``SceneConfigSet.as_dict()`` as ``Any`` and are read with
``in``/``get()``."""

BoneOrientation = dict[str, Any]
"""The recorded position of one bone, as ``RigService.get_bone_orientation_info_as_dict()`` writes it.

``head``, ``tail`` and ``matrix`` are ``mathutils`` copies and are present for both pose and edit
bones. An edit bone entry additionally carries ``roll`` and ``length`` as floats and ``parent`` as a
bone name or the empty string. An alias and not a ``TypedDict`` because the two variants share one
dict type and the pose variant has only three of the six keys."""

BoneOrientationInfo = dict[str, dict[str, BoneOrientation]]
"""A snapshot of the positions of every bone in an armature.

Two keys, ``pose_bones`` and ``edit_bones``, each mapping a bone name to its ``BoneOrientation``.
The rig helpers take this snapshot before entering edit mode, because the values they need are
readable in one mode and the bones they create in the other."""
