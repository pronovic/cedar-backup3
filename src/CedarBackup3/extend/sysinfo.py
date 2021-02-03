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
# Copyright (c) 2005,2010,2015 Kenneth J. Pronovici.
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
# Project  : Official Cedar Backup Extensions
# Purpose  : Provides an extension to save off important system recovery information.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to save off important system recovery information.

This is a simple Cedar Backup extension used to save off important system
recovery information.  It saves off three types of information:

   - Currently-installed Debian packages via ``dpkg --get-selections``
   - Disk partition information via ``fdisk -l``
   - System-wide mounted filesystem contents, via ``ls -laR``

The saved-off information is placed into the collect directory and is
compressed using ``bzip2`` to save space.

This extension relies on the options and collect configurations in the standard
Cedar Backup configuration file, but requires no new configuration of its own.
No public functions other than the action are exposed since all of this is
pretty simple.

*Note:* If the ``dpkg`` or ``fdisk`` commands cannot be found in their normal
locations or executed by the current user, those steps will be skipped and a
note will be logged at the INFO level.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
from bz2 import BZ2File

from CedarBackup3.util import changeOwnership, executeCommand, pathJoin, resolveCommand

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.sysinfo")

DPKG_PATH = "/usr/bin/dpkg"
FDISK_PATH = "/sbin/fdisk"

DPKG_COMMAND = [DPKG_PATH, "--get-selections"]
FDISK_COMMAND = [FDISK_PATH, "-l"]
LS_COMMAND = ["ls", "-laR", "/"]


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################

# pylint: disable=W0613
def executeAction(configPath, options, config):
    """
    Executes the sysinfo backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If the backup process fails for some reason
    """
    logger.debug("Executing sysinfo extended action.")
    if config.options is None or config.collect is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    _dumpDebianPackages(config.collect.targetDir, config.options.backupUser, config.options.backupGroup)
    _dumpPartitionTable(config.collect.targetDir, config.options.backupUser, config.options.backupGroup)
    _dumpFilesystemContents(config.collect.targetDir, config.options.backupUser, config.options.backupGroup)
    logger.info("Executed the sysinfo extended action successfully.")


def _dumpDebianPackages(targetDir, backupUser, backupGroup, compress=True):
    """
    Dumps a list of currently installed Debian packages via ``dpkg``.
    Args:
       targetDir: Directory to write output file into
       backupUser: User which should own the resulting file
       backupGroup: Group which should own the resulting file
       compress: Indicates whether to compress the output file
    Raises:
       IOError: If the dump fails for some reason
    """
    if not os.path.exists(DPKG_PATH):
        logger.info("Not executing Debian package dump since %s doesn't seem to exist.", DPKG_PATH)
    elif not os.access(DPKG_PATH, os.X_OK):
        logger.info("Not executing Debian package dump since %s cannot be executed.", DPKG_PATH)
    else:
        (outputFile, filename) = _getOutputFile(targetDir, "dpkg-selections", compress)
        with outputFile:
            command = resolveCommand(DPKG_COMMAND)
            result = executeCommand(command, [], returnOutput=False, ignoreStderr=True, doNotLog=True, outputFile=outputFile)[0]
            if result != 0:
                raise IOError("Error [%d] executing Debian package dump." % result)
        if not os.path.exists(filename):
            raise IOError("File [%s] does not seem to exist after Debian package dump finished." % filename)
        changeOwnership(filename, backupUser, backupGroup)


def _dumpPartitionTable(targetDir, backupUser, backupGroup, compress=True):
    """
    Dumps information about the partition table via ``fdisk``.
    Args:
       targetDir: Directory to write output file into
       backupUser: User which should own the resulting file
       backupGroup: Group which should own the resulting file
       compress: Indicates whether to compress the output file
    Raises:
       IOError: If the dump fails for some reason
    """
    if not os.path.exists(FDISK_PATH):
        logger.info("Not executing partition table dump since %s doesn't seem to exist.", FDISK_PATH)
    elif not os.access(FDISK_PATH, os.X_OK):
        logger.info("Not executing partition table dump since %s cannot be executed.", FDISK_PATH)
    else:
        (outputFile, filename) = _getOutputFile(targetDir, "fdisk-l", compress)
        with outputFile:
            command = resolveCommand(FDISK_COMMAND)
            result = executeCommand(command, [], returnOutput=False, ignoreStderr=True, outputFile=outputFile)[0]
            if result != 0:
                raise IOError("Error [%d] executing partition table dump." % result)
        if not os.path.exists(filename):
            raise IOError("File [%s] does not seem to exist after partition table dump finished." % filename)
        changeOwnership(filename, backupUser, backupGroup)


def _dumpFilesystemContents(targetDir, backupUser, backupGroup, compress=True):
    """
    Dumps complete listing of filesystem contents via ``ls -laR``.
    Args:
       targetDir: Directory to write output file into
       backupUser: User which should own the resulting file
       backupGroup: Group which should own the resulting file
       compress: Indicates whether to compress the output file
    Raises:
       IOError: If the dump fails for some reason
    """
    (outputFile, filename) = _getOutputFile(targetDir, "ls-laR", compress)
    with outputFile:
        # Note: can't count on return status from 'ls', so we don't check it.
        command = resolveCommand(LS_COMMAND)
        executeCommand(command, [], returnOutput=False, ignoreStderr=True, doNotLog=True, outputFile=outputFile)
    if not os.path.exists(filename):
        raise IOError("File [%s] does not seem to exist after filesystem contents dump finished." % filename)
    changeOwnership(filename, backupUser, backupGroup)


def _getOutputFile(targetDir, name, compress=True):
    """
    Opens the output file used for saving a dump to the filesystem.

    The filename will be ``name.txt`` (or ``name.txt.bz2`` if ``compress`` is
    ``True``), written in the target directory.

    Args:
       targetDir: Target directory to write file in
       name: Name of the file to create
       compress: Indicates whether to write compressed output

    Returns:
        Tuple of (Output file object, filename), file opened in binary mode for use with executeCommand()
    """
    filename = pathJoin(targetDir, "%s.txt" % name)
    if compress:
        filename = "%s.bz2" % filename
    logger.debug("Dump file will be [%s].", filename)
    if compress:
        outputFile = BZ2File(filename, "wb")
    else:
        outputFile = open(filename, "wb")
    return (outputFile, filename)
