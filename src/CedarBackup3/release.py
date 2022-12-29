# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python 3 (>= 3.7)
# Project  : Cedar Backup, release 3
# Purpose  : Provides location to maintain release information.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

"""
Provides a location to maintain version information.

Module Attributes
=================

Attributes:
   AUTHOR: Author of software
   EMAIL: Email address of author
   VERSION: Software version
   URL: URL of Cedar Backup webpage

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

# Historically, this information was tracked directly within this file as
# part of the release process.  In modern Python, it's better to rely on
# the package metadata, which is managed by Poetry on our behalf.  We used
# to track release date and copyright date range, but that information is
# not available in the package metadata.

from importlib.metadata import metadata

METADATA = metadata("cedar-backup3")
AUTHOR = METADATA["Author"]
EMAIL = METADATA["Author-email"]
VERSION = METADATA["Version"]
URL = METADATA["Home-page"]
