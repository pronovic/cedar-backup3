# -*- coding: iso-8859-1 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Copyright (c) 2010,2015 Kenneth J. Pronovici.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# Version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copies of the GNU General Public License are available from
# the Free Software Foundation website, http://www.gnu.org/.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python 3 (>= 3.7)
# Project  : Cedar Backup, release 3
# Purpose  : Implements customized behavior.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements customized behavior.

Some behaviors need to vary when packaged for certain platforms.  For instance,
while Cedar Backup generally uses cdrecord and mkisofs, Debian ships compatible
utilities called wodim and genisoimage. I want there to be one single place
where Cedar Backup is patched for Debian, rather than having to maintain a
variety of patches in different places.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.customize")

PLATFORM = "standard"
# PLATFORM = "debian"

DEBIAN_CDRECORD = "/usr/bin/wodim"
DEBIAN_MKISOFS = "/usr/bin/genisoimage"


#######################################################################
# Public functions
#######################################################################

################################
# customizeOverrides() function
################################


def customizeOverrides(config, platform=PLATFORM):
    """
    Modify command overrides based on the configured platform.

    On some platforms, we want to add command overrides to configuration.  Each
    override will only be added if the configuration does not already contain an
    override with the same name.  That way, the user still has a way to choose
    their own version of the command if they want.

    Args:
       config: Configuration to modify
       platform: Platform that is in use
    """
    if platform == "debian":
        logger.info("Overriding cdrecord for Debian platform: %s", DEBIAN_CDRECORD)
        config.options.addOverride("cdrecord", DEBIAN_CDRECORD)
        logger.info("Overriding mkisofs for Debian platform: %s", DEBIAN_MKISOFS)
        config.options.addOverride("mkisofs", DEBIAN_MKISOFS)
