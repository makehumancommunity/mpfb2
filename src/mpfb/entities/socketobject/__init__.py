"""This module contains helpers for staging the import from makehuman."""

from ...services import LogService

_LOG = LogService.get_logger("socketobject.init")
_LOG.trace("initializing socket object module")

from ._extra_vertex_groups import vertex_group_information as _extra_vgroup

ALL_EXTRA_GROUPS = dict(_extra_vgroup)
BASEMESH_EXTRA_GROUPS = dict(_extra_vgroup["basemesh"])
