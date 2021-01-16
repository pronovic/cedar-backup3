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
# Copyright (c) 2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Implements the standard 'initialize' action.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements the standard 'initialize' action.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging

from CedarBackup3.actions.util import initializeMediaState

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.actions.initialize")


########################################################################
# Public functions
########################################################################

###############################
# executeInitialize() function
###############################

# pylint: disable=W0613
def executeInitialize(configPath, options, config):
    """
    Executes the initialize action.

    The initialize action initializes the media currently in the writer
    device so that Cedar Backup can recognize it later.  This is an optional
    step; it's only required if checkMedia is set on the store configuration.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration

    """
    logger.debug("Executing the 'initialize' action.")
    if config.options is None or config.store is None:
        raise ValueError("Store configuration is not properly filled in.")
    initializeMediaState(config)
    logger.info("Executed the 'initialize' action successfully.")
