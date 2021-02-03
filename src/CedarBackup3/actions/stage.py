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
# Copyright (c) 2004-2008,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Implements the standard 'stage' action.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements the standard 'stage' action.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging
import os
import time

from CedarBackup3.actions.constants import DIR_TIME_FORMAT, STAGE_INDICATOR
from CedarBackup3.actions.util import writeIndicatorFile
from CedarBackup3.peer import LocalPeer, RemotePeer
from CedarBackup3.util import changeOwnership, getUidGid, isRunningAsRoot, isStartOfWeek, pathJoin

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.actions.stage")


########################################################################
# Public functions
########################################################################

##########################
# executeStage() function
##########################

# pylint: disable=W0613
# noinspection PyTypeChecker
def executeStage(configPath, options, config):
    """
    Executes the stage backup action.

    *Note:* The daily directory is derived once and then we stick with it, just
    in case a backup happens to span midnite.

    *Note:* As portions of the stage action is complete, we will write various
    indicator files so that it's obvious what actions have been completed.  Each
    peer gets a stage indicator in its collect directory, and then the master
    gets a stage indicator in its daily staging directory.  The store process
    uses the master's stage indicator to decide whether a directory is ready to
    be stored.  Currently, nothing uses the indicator at each peer, and it
    exists for reference only.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If there are problems reading or writing files
    """
    logger.debug("Executing the 'stage' action.")
    if config.options is None or config.stage is None:
        raise ValueError("Stage configuration is not properly filled in.")
    dailyDir = _getDailyDir(config)
    localPeers = _getLocalPeers(config)
    remotePeers = _getRemotePeers(config)
    allPeers = localPeers + remotePeers
    stagingDirs = _createStagingDirs(config, dailyDir, allPeers)
    for peer in allPeers:
        logger.info("Staging peer [%s].", peer.name)
        ignoreFailures = _getIgnoreFailuresFlag(options, config, peer)
        if not peer.checkCollectIndicator():
            if not ignoreFailures:
                logger.error("Peer [%s] was not ready to be staged.", peer.name)
            else:
                logger.info("Peer [%s] was not ready to be staged.", peer.name)
            continue
        logger.debug("Found collect indicator.")
        targetDir = stagingDirs[peer.name]
        if isRunningAsRoot():
            # Since we're running as root, we can change ownership
            ownership = getUidGid(config.options.backupUser, config.options.backupGroup)
            logger.debug("Using target dir [%s], ownership [%d:%d].", targetDir, ownership[0], ownership[1])
        else:
            # Non-root cannot change ownership, so don't set it
            ownership = None
            logger.debug("Using target dir [%s], ownership [None].", targetDir)
        try:
            count = peer.stagePeer(targetDir=targetDir, ownership=ownership)  # note: utilize effective user's default umask
            logger.info("Staged %d files for peer [%s].", count, peer.name)
            peer.writeStageIndicator()
        except (ValueError, IOError, OSError) as e:
            logger.error("Error staging [%s]: %s", peer.name, e)
    writeIndicatorFile(dailyDir, STAGE_INDICATOR, config.options.backupUser, config.options.backupGroup)
    logger.info("Executed the 'stage' action successfully.")


########################################################################
# Private utility functions
########################################################################

################################
# _createStagingDirs() function
################################


def _createStagingDirs(config, dailyDir, peers):
    """
    Creates staging directories as required.

    The main staging directory is the passed in daily directory, something like
    ``staging/2002/05/23``.  Then, individual peers get their own directories,
    i.e. ``staging/2002/05/23/host``.

    Args:
       config: Config object
       dailyDir: Daily staging directory
       peers: List of all configured peers

    Returns:
        Dictionary mapping peer name to staging directory
    """
    mapping = {}
    if os.path.isdir(dailyDir):
        logger.warning("Staging directory [%s] already existed.", dailyDir)
    else:
        try:
            logger.debug("Creating staging directory [%s].", dailyDir)
            os.makedirs(dailyDir)
            for path in [dailyDir, pathJoin(dailyDir, ".."), pathJoin(dailyDir, "..", "..")]:
                changeOwnership(path, config.options.backupUser, config.options.backupGroup)
        except Exception as e:
            raise Exception("Unable to create staging directory: %s" % e)
    for peer in peers:
        peerDir = pathJoin(dailyDir, peer.name)
        mapping[peer.name] = peerDir
        if os.path.isdir(peerDir):
            logger.warning("Peer staging directory [%s] already existed.", peerDir)
        else:
            try:
                logger.debug("Creating peer staging directory [%s].", peerDir)
                os.makedirs(peerDir)
                changeOwnership(peerDir, config.options.backupUser, config.options.backupGroup)
            except Exception as e:
                raise Exception("Unable to create staging directory: %s" % e)
    return mapping


########################################################################
# Private attribute "getter" functions
########################################################################

####################################
# _getIgnoreFailuresFlag() function
####################################


def _getIgnoreFailuresFlag(options, config, peer):
    """
    Gets the ignore failures flag based on options, configuration, and peer.
    Args:
       options: Options object
       config: Configuration object
       peer: Peer to check
    Returns:
        Whether to ignore stage failures for this peer
    """
    logger.debug("Ignore failure mode for this peer: %s", peer.ignoreFailureMode)
    if peer.ignoreFailureMode is None or peer.ignoreFailureMode == "none":
        return False
    elif peer.ignoreFailureMode == "all":
        return True
    else:
        if options.full or isStartOfWeek(config.options.startingDay):
            return peer.ignoreFailureMode == "weekly"
        else:
            return peer.ignoreFailureMode == "daily"


##########################
# _getDailyDir() function
##########################


def _getDailyDir(config):
    """
    Gets the daily staging directory.

    This is just a directory in the form ``staging/YYYY/MM/DD``, i.e.
    ``staging/2000/10/07``, except it will be an absolute path based on
    ``config.stage.targetDir``.

    Args:
       config: Config object

    Returns:
        Path of daily staging directory
    """
    dailyDir = pathJoin(config.stage.targetDir, time.strftime(DIR_TIME_FORMAT))
    logger.debug("Daily staging directory is [%s].", dailyDir)
    return dailyDir


############################
# _getLocalPeers() function
############################


def _getLocalPeers(config):
    """
    Return a list of :any:`LocalPeer` objects based on configuration.
    Args:
       config: Config object
    Returns:
        List of :any:`LocalPeer` objects
    """
    localPeers = []
    configPeers = None
    if config.stage.hasPeers():
        logger.debug("Using list of local peers from stage configuration.")
        configPeers = config.stage.localPeers
    elif config.peers is not None and config.peers.hasPeers():
        logger.debug("Using list of local peers from peers configuration.")
        configPeers = config.peers.localPeers
    if configPeers is not None:
        for peer in configPeers:
            localPeer = LocalPeer(peer.name, peer.collectDir, peer.ignoreFailureMode)
            localPeers.append(localPeer)
            logger.debug("Found local peer: [%s]", localPeer.name)
    return localPeers


#############################
# _getRemotePeers() function
#############################


def _getRemotePeers(config):
    """
    Return a list of :any:`RemotePeer` objects based on configuration.
    Args:
       config: Config object
    Returns:
        List of :any:`RemotePeer` objects
    """
    remotePeers = []
    configPeers = None
    if config.stage.hasPeers():
        logger.debug("Using list of remote peers from stage configuration.")
        configPeers = config.stage.remotePeers
    elif config.peers is not None and config.peers.hasPeers():
        logger.debug("Using list of remote peers from peers configuration.")
        configPeers = config.peers.remotePeers
    if configPeers is not None:
        for peer in configPeers:
            remoteUser = _getRemoteUser(config, peer)
            localUser = _getLocalUser(config)
            rcpCommand = _getRcpCommand(config, peer)
            remotePeer = RemotePeer(
                peer.name,
                peer.collectDir,
                config.options.workingDir,
                remoteUser,
                rcpCommand,
                localUser,
                ignoreFailureMode=peer.ignoreFailureMode,
            )
            remotePeers.append(remotePeer)
            logger.debug("Found remote peer: [%s]", remotePeer.name)
    return remotePeers


############################
# _getRemoteUser() function
############################


def _getRemoteUser(config, remotePeer):
    """
    Gets the remote user associated with a remote peer.
    Use peer's if possible, otherwise take from options section.
    Args:
       config: Config object
       remotePeer: Configuration-style remote peer object
    Returns:
        Name of remote user associated with remote peer
    """
    if remotePeer.remoteUser is None:
        return config.options.backupUser
    return remotePeer.remoteUser


###########################
# _getLocalUser() function
###########################


def _getLocalUser(config):
    """
    Gets the remote user associated with a remote peer.
    Args:
       config: Config object
    Returns:
        Name of local user that should be used
    """
    if not isRunningAsRoot():
        return None
    return config.options.backupUser


############################
# _getRcpCommand() function
############################


def _getRcpCommand(config, remotePeer):
    """
    Gets the RCP command associated with a remote peer.
    Use peer's if possible, otherwise take from options section.
    Args:
       config: Config object
       remotePeer: Configuration-style remote peer object
    Returns:
        RCP command associated with remote peer
    """
    if remotePeer.rcpCommand is None:
        return config.options.rcpCommand
    return remotePeer.rcpCommand
