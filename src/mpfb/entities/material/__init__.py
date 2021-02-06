#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("material.init")
_LOG.trace("initializing material module")
