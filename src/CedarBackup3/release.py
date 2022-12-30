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
   URL: Homepage URL

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

# Historically, this information was tracked directly within this file as part of the
# release process.  In modern Python, it's better to rely on the package metadata, which
# is managed by Poetry on our behalf.
#
# The metadata will always be set any time the package has been completely and properly
# installed.  However, there are other cases where it won't be available, such as when
# running the smoke tests during the Debian build process, or when running the unit tests
# from within the source tree as a part of the Debian CI suite. So, default values are
# provided.
#
# Note: previously, we also tracked release date and copyright date range, but that
# information is not available in the package metadata.  These values are maintained to
# avoid breaking the public interface, but are always "unset".

from importlib.metadata import metadata

try:
    _METADATA = metadata("cedar-backup3")
except ImportError:
    _METADATA = {}

AUTHOR = _METADATA["Author"] if "Author" in _METADATA else "unset"
EMAIL = _METADATA["Author-email"] if "Author-email" in _METADATA else "unset"
VERSION = _METADATA["Version"] if "Version" in _METADATA else "0.0.0"
URL = _METADATA["Home-page"] if "Home-page" in _METADATA else "unset"

COPYRIGHT = "unset"
DATE = "unset"
