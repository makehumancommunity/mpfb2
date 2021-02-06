#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains helpers for staging the import from makehuman."""

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("socketobject.init")
_LOG.trace("initializing socket object module")
