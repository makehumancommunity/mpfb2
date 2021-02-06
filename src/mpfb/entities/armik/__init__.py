#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("armik.init")
_LOG.trace("initializing armik module")
