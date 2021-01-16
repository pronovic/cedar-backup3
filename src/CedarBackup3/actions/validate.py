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
# Purpose  : Implements the standard 'validate' action.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements the standard 'validate' action.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging
import os

from CedarBackup3.actions.util import createWriter
from CedarBackup3.util import getFunctionReference, getUidGid

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.actions.validate")


########################################################################
# Public functions
########################################################################

#############################
# executeValidate() function
#############################

# pylint: disable=W0613
def executeValidate(configPath, options, config):
    """
    Executes the validate action.

    This action validates each of the individual sections in the config file.
    This is a "runtime" validation.  The config file itself is already valid in
    a structural sense, so what we check here that is that we can actually use
    the configuration without any problems.

    There's a separate validation function for each of the configuration
    sections.  Each validation function returns a true/false indication for
    whether configuration was valid, and then logs any configuration problems it
    finds.  This way, one pass over configuration indicates most or all of the
    obvious problems, rather than finding just one problem at a time.

    Any reported problems will be logged at the ERROR level normally, or at the
    INFO level if the quiet flag is enabled.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: If some configuration value is invalid
    """
    logger.debug("Executing the 'validate' action.")
    if options.quiet:
        logfunc = logger.info  # info so it goes to the log
    else:
        logfunc = logger.error  # error so it goes to the screen
    valid = True
    valid &= _validateReference(config, logfunc)
    valid &= _validateOptions(config, logfunc)
    valid &= _validateCollect(config, logfunc)
    valid &= _validateStage(config, logfunc)
    valid &= _validateStore(config, logfunc)
    valid &= _validatePurge(config, logfunc)
    valid &= _validateExtensions(config, logfunc)
    if valid:
        logfunc("Configuration is valid.")
    else:
        logfunc("Configuration is not valid.")


########################################################################
# Private utility functions
########################################################################

#######################
# _checkDir() function
#######################


def _checkDir(path, writable, logfunc, prefix):
    """
    Checks that the indicated directory is OK.

    The path must exist, must be a directory, must be readable and executable,
    and must optionally be writable.

    Args:
       path: Path to check
       writable: Check that path is writable
       logfunc: Function to use for logging errors
       prefix: Prefix to use on logged errors

    Returns:
        True if the directory is OK, False otherwise
    """
    if not os.path.exists(path):
        logfunc("%s [%s] does not exist." % (prefix, path))
        return False
    if not os.path.isdir(path):
        logfunc("%s [%s] is not a directory." % (prefix, path))
        return False
    if not os.access(path, os.R_OK):
        logfunc("%s [%s] is not readable." % (prefix, path))
        return False
    if not os.access(path, os.X_OK):
        logfunc("%s [%s] is not executable." % (prefix, path))
        return False
    if writable and not os.access(path, os.W_OK):
        logfunc("%s [%s] is not writable." % (prefix, path))
        return False
    return True


################################
# _validateReference() function
################################


def _validateReference(config, logfunc):
    """
    Execute runtime validations on reference configuration.

    We only validate that reference configuration exists at all.

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, false otherwise
    """
    valid = True
    if config.reference is None:
        logfunc("Required reference configuration does not exist.")
        valid = False
    return valid


##############################
# _validateOptions() function
##############################


def _validateOptions(config, logfunc):
    """
    Execute runtime validations on options configuration.

    The following validations are enforced:

       - The options section must exist
       - The working directory must exist and must be writable
       - The backup user and backup group must exist

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, false otherwise
    """
    valid = True
    if config.options is None:
        logfunc("Required options configuration does not exist.")
        valid = False
    else:
        valid &= _checkDir(config.options.workingDir, True, logfunc, "Working directory")
        try:
            getUidGid(config.options.backupUser, config.options.backupGroup)
        except ValueError:
            logfunc("Backup user:group [%s:%s] invalid." % (config.options.backupUser, config.options.backupGroup))
            valid = False
    return valid


##############################
# _validateCollect() function
##############################


def _validateCollect(config, logfunc):
    """
    Execute runtime validations on collect configuration.

    The following validations are enforced:

       - The target directory must exist and must be writable
       - Each of the individual collect directories must exist and must be readable

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, false otherwise
    """
    valid = True
    if config.collect is not None:
        valid &= _checkDir(config.collect.targetDir, True, logfunc, "Collect target directory")
        if config.collect.collectDirs is not None:
            for collectDir in config.collect.collectDirs:
                valid &= _checkDir(collectDir.absolutePath, False, logfunc, "Collect directory")
    return valid


############################
# _validateStage() function
############################


def _validateStage(config, logfunc):
    """
    Execute runtime validations on stage configuration.

    The following validations are enforced:

       - The target directory must exist and must be writable
       - Each local peer's collect directory must exist and must be readable

    *Note:* We currently do not validate anything having to do with remote peers,
    since we don't have a straightforward way of doing it.  It would require
    adding an rsh command rather than just an rcp command to configuration, and
    that just doesn't seem worth it right now.

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, False otherwise
    """
    valid = True
    if config.stage is not None:
        valid &= _checkDir(config.stage.targetDir, True, logfunc, "Stage target dir ")
        if config.stage.localPeers is not None:
            for peer in config.stage.localPeers:
                valid &= _checkDir(peer.collectDir, False, logfunc, "Local peer collect dir ")
    return valid


############################
# _validateStore() function
############################


def _validateStore(config, logfunc):
    """
    Execute runtime validations on store configuration.

    The following validations are enforced:

       - The source directory must exist and must be readable
       - The backup device (path and SCSI device) must be valid

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, False otherwise
    """
    valid = True
    if config.store is not None:
        valid &= _checkDir(config.store.sourceDir, False, logfunc, "Store source directory")
        try:
            createWriter(config)
        except ValueError:
            logfunc("Backup device [%s] [%s] is not valid." % (config.store.devicePath, config.store.deviceScsiId))
            valid = False
    return valid


############################
# _validatePurge() function
############################


def _validatePurge(config, logfunc):
    """
    Execute runtime validations on purge configuration.

    The following validations are enforced:

       - Each purge directory must exist and must be writable

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, False otherwise
    """
    valid = True
    if config.purge is not None:
        if config.purge.purgeDirs is not None:
            for purgeDir in config.purge.purgeDirs:
                valid &= _checkDir(purgeDir.absolutePath, True, logfunc, "Purge directory")
    return valid


#################################
# _validateExtensions() function
#################################


def _validateExtensions(config, logfunc):
    """
    Execute runtime validations on extensions configuration.

    The following validations are enforced:

       - Each indicated extension function must exist.

    Args:
       config: Program configuration
       logfunc: Function to use for logging errors

    Returns:
        True if configuration is valid, False otherwise
    """
    valid = True
    if config.extensions is not None:
        if config.extensions.actions is not None:
            for action in config.extensions.actions:
                try:
                    getFunctionReference(action.module, action.function)
                except ImportError:
                    logfunc("Unable to find function [%s.%s]." % (action.module, action.function))
                    valid = False
                except ValueError:
                    logfunc("Function [%s.%s] is not callable." % (action.module, action.function))
                    valid = False
    return valid
