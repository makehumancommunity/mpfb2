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
