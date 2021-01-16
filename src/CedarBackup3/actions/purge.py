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
# Copyright (c) 2004-2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Implements the standard 'purge' action.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements the standard 'purge' action.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging

from CedarBackup3.filesystem import PurgeItemList

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.actions.purge")


########################################################################
# Public functions
########################################################################

##########################
# executePurge() function
##########################

# pylint: disable=W0613
def executePurge(configPath, options, config):
    """
    Executes the purge backup action.

    For each configured directory, we create a purge item list, remove from the
    list anything that's younger than the configured retain days value, and then
    purge from the filesystem what's left.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
    """
    logger.debug("Executing the 'purge' action.")
    if config.options is None or config.purge is None:
        raise ValueError("Purge configuration is not properly filled in.")
    if config.purge.purgeDirs is not None:
        for purgeDir in config.purge.purgeDirs:
            purgeList = PurgeItemList()
            purgeList.addDirContents(purgeDir.absolutePath)  # add everything within directory
            purgeList.removeYoungFiles(purgeDir.retainDays)  # remove young files *from the list* so they won't be purged
            purgeList.purgeItems()  # remove remaining items from the filesystem
    logger.info("Executed the 'purge' action successfully.")
