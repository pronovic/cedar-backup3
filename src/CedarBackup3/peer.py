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
# Purpose  : Provides backup peer-related objects.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides backup peer-related objects and utility functions.

Module Attributes
=================

Attributes:
   DEF_COLLECT_INDICATOR: Name of the default collect indicator file
   DEF_STAGE_INDICATOR: Name of the default stage indicator file

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging
import os
import shutil
import sys

from CedarBackup3.config import VALID_FAILURE_MODES
from CedarBackup3.filesystem import FilesystemList
from CedarBackup3.util import encodePath, executeCommand, isRunningAsRoot, pathJoin, resolveCommand, splitCommandLine

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.peer")

DEF_RCP_COMMAND = ["/usr/bin/scp", "-B", "-q", "-C"]
DEF_RSH_COMMAND = ["/usr/bin/ssh"]
DEF_CBACK_COMMAND = "/usr/bin/cback3"

DEF_COLLECT_INDICATOR = "cback.collect"
DEF_STAGE_INDICATOR = "cback.stage"

SU_COMMAND = ["su"]


########################################################################
# LocalPeer class definition
########################################################################


class LocalPeer(object):

    ######################
    # Class documentation
    ######################

    """
    Backup peer representing a local peer in a backup pool.

    This is a class representing a local (non-network) peer in a backup pool.
    Local peers are backed up by simple filesystem copy operations.  A local
    peer has associated with it a name (typically, but not necessarily, a
    hostname) and a collect directory.

    The public methods other than the constructor are part of a "backup peer"
    interface shared with the ``RemotePeer`` class.

    """

    ##############
    # Constructor
    ##############

    def __init__(self, name, collectDir, ignoreFailureMode=None):
        """
        Initializes a local backup peer.

        Note that the collect directory must be an absolute path, but does not
        have to exist when the object is instantiated.  We do a lazy validation
        on this value since we could (potentially) be creating peer objects
        before an ongoing backup completed.

        Args:
           name: Name of the backup peer
           collectDir: Path to the peer's collect directory
           ignoreFailureMode: Ignore failure mode for this peer, one of ``VALID_FAILURE_MODES``
        Raises:
           ValueError: If the name is empty
           ValueError: If collect directory is not an absolute path
        """
        self._name = None
        self._collectDir = None
        self._ignoreFailureMode = None
        self.name = name
        self.collectDir = collectDir
        self.ignoreFailureMode = ignoreFailureMode

    #############
    # Properties
    #############

    def _setName(self, value):
        """
        Property target used to set the peer name.
        The value must be a non-empty string and cannot be ``None``.
        Raises:
           ValueError: If the value is an empty string or ``None``
        """
        if value is None or len(value) < 1:
            raise ValueError("Peer name must be a non-empty string.")
        self._name = value

    def _getName(self):
        """
        Property target used to get the peer name.
        """
        return self._name

    def _setCollectDir(self, value):
        """
        Property target used to set the collect directory.
        The value must be an absolute path and cannot be ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is ``None`` or is not an absolute path
           ValueError: If a path cannot be encoded properly
        """
        if value is None or not os.path.isabs(value):
            raise ValueError("Collect directory must be an absolute path.")
        self._collectDir = encodePath(value)

    def _getCollectDir(self):
        """
        Property target used to get the collect directory.
        """
        return self._collectDir

    def _setIgnoreFailureMode(self, value):
        """
        Property target used to set the ignoreFailure mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_FAILURE_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_FAILURE_MODES:
                raise ValueError("Ignore failure mode must be one of %s." % VALID_FAILURE_MODES)
        self._ignoreFailureMode = value

    def _getIgnoreFailureMode(self):
        """
        Property target used to get the ignoreFailure mode.
        """
        return self._ignoreFailureMode

    name = property(_getName, _setName, None, "Name of the peer.")
    collectDir = property(_getCollectDir, _setCollectDir, None, "Path to the peer's collect directory (an absolute local path).")
    ignoreFailureMode = property(_getIgnoreFailureMode, _setIgnoreFailureMode, None, "Ignore failure mode for peer.")

    #################
    # Public methods
    #################

    def stagePeer(self, targetDir, ownership=None, permissions=None):
        """
        Stages data from the peer into the indicated local target directory.

        The collect and target directories must both already exist before this
        method is called.  If passed in, ownership and permissions will be
        applied to the files that are copied.

        *Note:* The caller is responsible for checking that the indicator exists,
        if they care.  This function only stages the files within the directory.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        Args:
           targetDir: Target directory to write data into
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
        Returns:
            Number of files copied from the source directory to the target directory

        Raises:
           ValueError: If collect directory is not a directory or does not exist
           ValueError: If target directory is not a directory, does not exist or is not absolute
           ValueError: If a path cannot be encoded properly
           IOError: If there were no files to stage (i.e. the directory was empty)
           IOError: If there is an IO error copying a file
           OSError: If there is an OS error copying or changing permissions on a file
        """
        targetDir = encodePath(targetDir)
        if not os.path.isabs(targetDir):
            logger.debug("Target directory [%s] not an absolute path.", targetDir)
            raise ValueError("Target directory must be an absolute path.")
        if not os.path.exists(self.collectDir) or not os.path.isdir(self.collectDir):
            logger.debug("Collect directory [%s] is not a directory or does not exist on disk.", self.collectDir)
            raise ValueError("Collect directory is not a directory or does not exist on disk.")
        if not os.path.exists(targetDir) or not os.path.isdir(targetDir):
            logger.debug("Target directory [%s] is not a directory or does not exist on disk.", targetDir)
            raise ValueError("Target directory is not a directory or does not exist on disk.")
        count = LocalPeer._copyLocalDir(self.collectDir, targetDir, ownership, permissions)
        if count == 0:
            raise IOError("Did not copy any files from local peer.")
        return count

    def checkCollectIndicator(self, collectIndicator=None):
        """
        Checks the collect indicator in the peer's staging directory.

        When a peer has completed collecting its backup files, it will write an
        empty indicator file into its collect directory.  This method checks to
        see whether that indicator has been written.  We're "stupid" here - if
        the collect directory doesn't exist, you'll naturally get back ``False``.

        If you need to, you can override the name of the collect indicator file
        by passing in a different name.

        Args:
           collectIndicator: Name of the collect indicator file to check
        Returns:
            Boolean true/false depending on whether the indicator exists
        Raises:
           ValueError: If a path cannot be encoded properly
        """
        collectIndicator = encodePath(collectIndicator)
        if collectIndicator is None:
            return os.path.exists(pathJoin(self.collectDir, DEF_COLLECT_INDICATOR))
        else:
            return os.path.exists(pathJoin(self.collectDir, collectIndicator))

    def writeStageIndicator(self, stageIndicator=None, ownership=None, permissions=None):
        """
        Writes the stage indicator in the peer's staging directory.

        When the master has completed collecting its backup files, it will write
        an empty indicator file into the peer's collect directory.  The presence
        of this file implies that the staging process is complete.

        If you need to, you can override the name of the stage indicator file by
        passing in a different name.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid`
        function to get the associated uid/gid as an ownership tuple.

        Args:
           stageIndicator: Name of the indicator file to write
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
        Raises:
           ValueError: If collect directory is not a directory or does not exist
           ValueError: If a path cannot be encoded properly
           IOError: If there is an IO error creating the file
           OSError: If there is an OS error creating or changing permissions on the file
        """
        stageIndicator = encodePath(stageIndicator)
        if not os.path.exists(self.collectDir) or not os.path.isdir(self.collectDir):
            logger.debug("Collect directory [%s] is not a directory or does not exist on disk.", self.collectDir)
            raise ValueError("Collect directory is not a directory or does not exist on disk.")
        if stageIndicator is None:
            fileName = pathJoin(self.collectDir, DEF_STAGE_INDICATOR)
        else:
            fileName = pathJoin(self.collectDir, stageIndicator)
        LocalPeer._copyLocalFile(None, fileName, ownership, permissions)  # None for sourceFile results in an empty target

    ##################
    # Private methods
    ##################

    @staticmethod
    def _copyLocalDir(sourceDir, targetDir, ownership=None, permissions=None):
        """
        Copies files from the source directory to the target directory.

        This function is not recursive.  Only the files in the directory will be
        copied.   Ownership and permissions will be left at their default values
        if new values are not specified.  The source and target directories are
        allowed to be soft links to a directory, but besides that soft links are
        ignored.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid`
        function to get the associated uid/gid as an ownership tuple.

        Args:
           sourceDir: Source directory
           targetDir: Target directory
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
        Returns:
            Number of files copied from the source directory to the target directory

        Raises:
           ValueError: If source or target is not a directory or does not exist
           ValueError: If a path cannot be encoded properly
           IOError: If there is an IO error copying the files
           OSError: If there is an OS error copying or changing permissions on a files
        """
        filesCopied = 0
        sourceDir = encodePath(sourceDir)
        targetDir = encodePath(targetDir)
        for fileName in os.listdir(sourceDir):
            sourceFile = pathJoin(sourceDir, fileName)
            targetFile = pathJoin(targetDir, fileName)
            LocalPeer._copyLocalFile(sourceFile, targetFile, ownership, permissions)
            filesCopied += 1
        return filesCopied

    @staticmethod
    def _copyLocalFile(sourceFile=None, targetFile=None, ownership=None, permissions=None, overwrite=True):
        """
        Copies a source file to a target file.

        If the source file is ``None`` then the target file will be created or
        overwritten as an empty file.  If the target file is ``None``, this method
        is a no-op.  Attempting to copy a soft link or a directory will result in
        an exception.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid`
        function to get the associated uid/gid as an ownership tuple.

        *Note:* We will not overwrite a target file that exists when this method
        is invoked.  If the target already exists, we'll raise an exception.

        Args:
           sourceFile: Source file to copy
           targetFile: Target file to create
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
           overwrite: Indicates whether it's OK to overwrite the target file
        Raises:
           ValueError: If the passed-in source file is not a regular file
           ValueError: If a path cannot be encoded properly
           IOError: If the target file already exists
           IOError: If there is an IO error copying the file
           OSError: If there is an OS error copying or changing permissions on a file
        """
        targetFile = encodePath(targetFile)
        sourceFile = encodePath(sourceFile)
        if targetFile is None:
            return
        if not overwrite:
            if os.path.exists(targetFile):
                raise IOError("Target file [%s] already exists." % targetFile)
        if sourceFile is None:
            with open(targetFile, "w") as f:
                f.write("")
        else:
            if os.path.isfile(sourceFile) and not os.path.islink(sourceFile):
                shutil.copy(sourceFile, targetFile)
            else:
                logger.debug("Source [%s] is not a regular file.", sourceFile)
                raise ValueError("Source is not a regular file.")
        if ownership is not None:
            if sys.platform != "win32":
                os.chown(targetFile, ownership[0], ownership[1])  # pylint: disable=no-member
        if permissions is not None:
            os.chmod(targetFile, permissions)


########################################################################
# RemotePeer class definition
########################################################################


class RemotePeer(object):

    ######################
    # Class documentation
    ######################

    """
    Backup peer representing a remote peer in a backup pool.

    This is a class representing a remote (networked) peer in a backup pool.
    Remote peers are backed up using an rcp-compatible copy command.  A remote
    peer has associated with it a name (which must be a valid hostname), a
    collect directory, a working directory and a copy method (an rcp-compatible
    command).

    You can also set an optional local user value.  This username will be used
    as the local user for any remote copies that are required.  It can only be
    used if the root user is executing the backup.  The root user will ``su`` to
    the local user and execute the remote copies as that user.

    The copy method is associated with the peer and not with the actual request
    to copy, because we can envision that each remote host might have a
    different connect method.

    The public methods other than the constructor are part of a "backup peer"
    interface shared with the ``LocalPeer`` class.

    """

    ##############
    # Constructor
    ##############

    def __init__(
        self,
        name=None,
        collectDir=None,
        workingDir=None,
        remoteUser=None,
        rcpCommand=None,
        localUser=None,
        rshCommand=None,
        cbackCommand=None,
        ignoreFailureMode=None,
    ):
        """
        Initializes a remote backup peer.

        *Note:* If provided, each command will eventually be parsed into a list of
        strings suitable for passing to ``util.executeCommand`` in order to avoid
        security holes related to shell interpolation.   This parsing will be
        done by the :any:`util.splitCommandLine` function.  See the documentation for
        that function for some important notes about its limitations.

        Args:
           name: Name of the backup peer, a valid DNS name
           collectDir: Path to the peer's collect directory, absolute path
           workingDir: Working directory that can be used to create temporary files, etc, an absolute path
           remoteUser: Name of the Cedar Backup user on the remote peer
           localUser: Name of the Cedar Backup user on the current host
           rcpCommand: An rcp-compatible copy command to use for copying files from the peer
           rshCommand: An rsh-compatible copy command to use for remote shells to the peer
           cbackCommand: A chack-compatible command to use for executing managed actions
           ignoreFailureMode: Ignore failure mode for this peer, one of ``VALID_FAILURE_MODES``
        Raises:
           ValueError: If collect directory is not an absolute path
        """
        self._name = None
        self._collectDir = None
        self._workingDir = None
        self._remoteUser = None
        self._localUser = None
        self._rcpCommand = None
        self._rcpCommandList = None
        self._rshCommand = None
        self._rshCommandList = None
        self._cbackCommand = None
        self._ignoreFailureMode = None
        self.name = name
        self.collectDir = collectDir
        self.workingDir = workingDir
        self.remoteUser = remoteUser
        self.localUser = localUser
        self.rcpCommand = rcpCommand
        self.rshCommand = rshCommand
        self.cbackCommand = cbackCommand
        self.ignoreFailureMode = ignoreFailureMode

    #############
    # Properties
    #############

    def _setName(self, value):
        """
        Property target used to set the peer name.
        The value must be a non-empty string and cannot be ``None``.
        Raises:
           ValueError: If the value is an empty string or ``None``
        """
        if value is None or len(value) < 1:
            raise ValueError("Peer name must be a non-empty string.")
        self._name = value

    def _getName(self):
        """
        Property target used to get the peer name.
        """
        return self._name

    def _setCollectDir(self, value):
        """
        Property target used to set the collect directory.
        The value must be an absolute path and cannot be ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is ``None`` or is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Collect directory must be an absolute path.")
        self._collectDir = encodePath(value)

    def _getCollectDir(self):
        """
        Property target used to get the collect directory.
        """
        return self._collectDir

    def _setWorkingDir(self, value):
        """
        Property target used to set the working directory.
        The value must be an absolute path and cannot be ``None``.
        Raises:
           ValueError: If the value is ``None`` or is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Working directory must be an absolute path.")
        self._workingDir = encodePath(value)

    def _getWorkingDir(self):
        """
        Property target used to get the working directory.
        """
        return self._workingDir

    def _setRemoteUser(self, value):
        """
        Property target used to set the remote user.
        The value must be a non-empty string and cannot be ``None``.
        Raises:
           ValueError: If the value is an empty string or ``None``
        """
        if value is None or len(value) < 1:
            raise ValueError("Peer remote user must be a non-empty string.")
        self._remoteUser = value

    def _getRemoteUser(self):
        """
        Property target used to get the remote user.
        """
        return self._remoteUser

    def _setLocalUser(self, value):
        """
        Property target used to set the local user.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Peer local user must be a non-empty string.")
        self._localUser = value

    def _getLocalUser(self):
        """
        Property target used to get the local user.
        """
        return self._localUser

    def _setRcpCommand(self, value):
        """
        Property target to set the rcp command.

        The value must be a non-empty string or ``None``.  Its value is stored in
        the two forms: "raw" as provided by the client, and "parsed" into a list
        suitable for being passed to :any:`util.executeCommand` via
        :any:`util.splitCommandLine`.

        However, all the caller will ever see via the property is the actual
        value they set (which includes seeing ``None``, even if we translate that
        internally to ``DEF_RCP_COMMAND``).  Internally, we should always use
        ``self._rcpCommandList`` if we want the actual command list.

        Raises:
           ValueError: If the value is an empty string
        """
        if value is None:
            self._rcpCommand = None
            self._rcpCommandList = DEF_RCP_COMMAND
        else:
            if len(value) >= 1:
                self._rcpCommand = value
                self._rcpCommandList = splitCommandLine(self._rcpCommand)
            else:
                raise ValueError("The rcp command must be a non-empty string.")

    def _getRcpCommand(self):
        """
        Property target used to get the rcp command.
        """
        return self._rcpCommand

    def _setRshCommand(self, value):
        """
        Property target to set the rsh command.

        The value must be a non-empty string or ``None``.  Its value is stored in
        the two forms: "raw" as provided by the client, and "parsed" into a list
        suitable for being passed to :any:`util.executeCommand` via
        :any:`util.splitCommandLine`.

        However, all the caller will ever see via the property is the actual
        value they set (which includes seeing ``None``, even if we translate that
        internally to ``DEF_RSH_COMMAND``).  Internally, we should always use
        ``self._rshCommandList`` if we want the actual command list.

        Raises:
           ValueError: If the value is an empty string
        """
        if value is None:
            self._rshCommand = None
            self._rshCommandList = DEF_RSH_COMMAND
        else:
            if len(value) >= 1:
                self._rshCommand = value
                self._rshCommandList = splitCommandLine(self._rshCommand)
            else:
                raise ValueError("The rsh command must be a non-empty string.")

    def _getRshCommand(self):
        """
        Property target used to get the rsh command.
        """
        return self._rshCommand

    def _setCbackCommand(self, value):
        """
        Property target to set the cback command.

        The value must be a non-empty string or ``None``.  Unlike the other
        command, this value is only stored in the "raw" form provided by the
        client.

        Raises:
           ValueError: If the value is an empty string
        """
        if value is None:
            self._cbackCommand = None
        else:
            if len(value) >= 1:
                self._cbackCommand = value
            else:
                raise ValueError("The cback command must be a non-empty string.")

    def _getCbackCommand(self):
        """
        Property target used to get the cback command.
        """
        return self._cbackCommand

    def _setIgnoreFailureMode(self, value):
        """
        Property target used to set the ignoreFailure mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_FAILURE_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_FAILURE_MODES:
                raise ValueError("Ignore failure mode must be one of %s." % VALID_FAILURE_MODES)
        self._ignoreFailureMode = value

    def _getIgnoreFailureMode(self):
        """
        Property target used to get the ignoreFailure mode.
        """
        return self._ignoreFailureMode

    name = property(_getName, _setName, None, "Name of the peer (a valid DNS hostname).")
    collectDir = property(_getCollectDir, _setCollectDir, None, "Path to the peer's collect directory (an absolute local path).")
    workingDir = property(_getWorkingDir, _setWorkingDir, None, "Path to the peer's working directory (an absolute local path).")
    remoteUser = property(_getRemoteUser, _setRemoteUser, None, "Name of the Cedar Backup user on the remote peer.")
    localUser = property(_getLocalUser, _setLocalUser, None, "Name of the Cedar Backup user on the current host.")
    rcpCommand = property(_getRcpCommand, _setRcpCommand, None, "An rcp-compatible copy command to use for copying files.")
    rshCommand = property(_getRshCommand, _setRshCommand, None, "An rsh-compatible command to use for remote shells to the peer.")
    cbackCommand = property(
        _getCbackCommand, _setCbackCommand, None, "A chack-compatible command to use for executing managed actions."
    )
    ignoreFailureMode = property(_getIgnoreFailureMode, _setIgnoreFailureMode, None, "Ignore failure mode for peer.")

    #################
    # Public methods
    #################

    def stagePeer(self, targetDir, ownership=None, permissions=None):
        """
        Stages data from the peer into the indicated local target directory.

        The target directory must already exist before this method is called.  If
        passed in, ownership and permissions will be applied to the files that
        are copied.

        *Note:* The returned count of copied files might be inaccurate if some of
        the copied files already existed in the staging directory prior to the
        copy taking place.  We don't clear the staging directory first, because
        some extension might also be using it.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        *Note:* Unlike the local peer version of this method, an I/O error might
        or might not be raised if the directory is empty.  Since we're using a
        remote copy method, we just don't have the fine-grained control over our
        exceptions that's available when we can look directly at the filesystem,
        and we can't control whether the remote copy method thinks an empty
        directory is an error.

        Args:
           targetDir: Target directory to write data into
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
        Returns:
            Number of files copied from the source directory to the target directory

        Raises:
           ValueError: If target directory is not a directory, does not exist or is not absolute
           ValueError: If a path cannot be encoded properly
           IOError: If there were no files to stage (i.e. the directory was empty)
           IOError: If there is an IO error copying a file
           OSError: If there is an OS error copying or changing permissions on a file
        """
        targetDir = encodePath(targetDir)
        if not os.path.isabs(targetDir):
            logger.debug("Target directory [%s] not an absolute path.", targetDir)
            raise ValueError("Target directory must be an absolute path.")
        if not os.path.exists(targetDir) or not os.path.isdir(targetDir):
            logger.debug("Target directory [%s] is not a directory or does not exist on disk.", targetDir)
            raise ValueError("Target directory is not a directory or does not exist on disk.")
        count = RemotePeer._copyRemoteDir(
            self.remoteUser,
            self.localUser,
            self.name,
            self._rcpCommand,
            self._rcpCommandList,
            self.collectDir,
            targetDir,
            ownership,
            permissions,
        )
        if count == 0:
            raise IOError("Did not copy any files from local peer.")
        return count

    def checkCollectIndicator(self, collectIndicator=None):
        """
        Checks the collect indicator in the peer's staging directory.

        When a peer has completed collecting its backup files, it will write an
        empty indicator file into its collect directory.  This method checks to
        see whether that indicator has been written.  If the remote copy command
        fails, we return ``False`` as if the file weren't there.

        If you need to, you can override the name of the collect indicator file
        by passing in a different name.

        *Note:* Apparently, we can't count on all rcp-compatible implementations
        to return sensible errors for some error conditions.  As an example, the
        ``scp`` command in Debian 'woody' returns a zero (normal) status even when
        it can't find a host or if the login or path is invalid.  Because of
        this, the implementation of this method is rather convoluted.

        Args:
           collectIndicator: Name of the collect indicator file to check
        Returns:
            Boolean true/false depending on whether the indicator exists
        Raises:
           ValueError: If a path cannot be encoded properly
        """
        try:
            if collectIndicator is None:
                sourceFile = pathJoin(self.collectDir, DEF_COLLECT_INDICATOR)
                targetFile = pathJoin(self.workingDir, DEF_COLLECT_INDICATOR)
            else:
                collectIndicator = encodePath(collectIndicator)
                sourceFile = pathJoin(self.collectDir, collectIndicator)
                targetFile = pathJoin(self.workingDir, collectIndicator)
            logger.debug("Fetch remote [%s] into [%s].", sourceFile, targetFile)
            if os.path.exists(targetFile):
                try:
                    os.remove(targetFile)
                except:
                    raise Exception("Error: collect indicator [%s] already exists!" % targetFile)
            try:
                RemotePeer._copyRemoteFile(
                    self.remoteUser,
                    self.localUser,
                    self.name,
                    self._rcpCommand,
                    self._rcpCommandList,
                    sourceFile,
                    targetFile,
                    overwrite=False,
                )
                if os.path.exists(targetFile):
                    return True
                else:
                    return False
            except Exception as e:
                logger.info("Failed looking for collect indicator: %s", e)
                return False
        finally:
            if os.path.exists(targetFile):
                try:
                    os.remove(targetFile)
                except:
                    pass

    def writeStageIndicator(self, stageIndicator=None):
        """
        Writes the stage indicator in the peer's staging directory.

        When the master has completed collecting its backup files, it will write
        an empty indicator file into the peer's collect directory.  The presence
        of this file implies that the staging process is complete.

        If you need to, you can override the name of the stage indicator file by
        passing in a different name.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        Args:
           stageIndicator: Name of the indicator file to write
        Raises:
           ValueError: If a path cannot be encoded properly
           IOError: If there is an IO error creating the file
           OSError: If there is an OS error creating or changing permissions on the file
        """
        stageIndicator = encodePath(stageIndicator)
        if stageIndicator is None:
            sourceFile = pathJoin(self.workingDir, DEF_STAGE_INDICATOR)
            targetFile = pathJoin(self.collectDir, DEF_STAGE_INDICATOR)
        else:
            sourceFile = pathJoin(self.workingDir, DEF_STAGE_INDICATOR)
            targetFile = pathJoin(self.collectDir, stageIndicator)
        try:
            if not os.path.exists(sourceFile):
                with open(sourceFile, "w") as f:
                    f.write("")
            RemotePeer._pushLocalFile(
                self.remoteUser, self.localUser, self.name, self._rcpCommand, self._rcpCommandList, sourceFile, targetFile
            )
        finally:
            if os.path.exists(sourceFile):
                try:
                    os.remove(sourceFile)
                except:
                    pass

    def executeRemoteCommand(self, command):
        """
        Executes a command on the peer via remote shell.

        Args:
           command: Command to execute
        Raises:
           IOError: If there is an error executing the command on the remote peer
        """
        RemotePeer._executeRemoteCommand(
            self.remoteUser, self.localUser, self.name, self._rshCommand, self._rshCommandList, command
        )

    def executeManagedAction(self, action, fullBackup):
        """
        Executes a managed action on this peer.

        Args:
           action: Name of the action to execute
           fullBackup: Whether a full backup should be executed

        Raises:
           IOError: If there is an error executing the action on the remote peer
        """
        try:
            command = RemotePeer._buildCbackCommand(self.cbackCommand, action, fullBackup)
            self.executeRemoteCommand(command)
        except IOError as e:
            logger.info(e)
            raise IOError("Failed to execute action [%s] on managed client [%s]." % (action, self.name))

    ##################
    # Private methods
    ##################

    @staticmethod
    def _getDirContents(path):
        """
        Returns the contents of a directory in terms of a Set.

        The directory's contents are read as a :any:`FilesystemList` containing only
        files, and then the list is converted into a set object for later use.

        Args:
           path: Directory path to get contents for
        Returns:
            Set of files in the directory
        Raises:
           ValueError: If path is not a directory or does not exist
        """
        contents = FilesystemList()
        contents.excludeDirs = True
        contents.excludeLinks = True
        contents.addDirContents(path)
        return set(contents)

    @staticmethod
    def _copyRemoteDir(
        remoteUser, localUser, remoteHost, rcpCommand, rcpCommandList, sourceDir, targetDir, ownership=None, permissions=None
    ):
        """
        Copies files from the source directory to the target directory.

        This function is not recursive.  Only the files in the directory will be
        copied.   Ownership and permissions will be left at their default values
        if new values are not specified.  Behavior when copying soft links from
        the collect directory is dependent on the behavior of the specified rcp
        command.

        *Note:* The returned count of copied files might be inaccurate if some of
        the copied files already existed in the staging directory prior to the
        copy taking place.  We don't clear the staging directory first, because
        some extension might also be using it.

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        *Note:* We don't have a good way of knowing exactly what files we copied
        down from the remote peer, unless we want to parse the output of the rcp
        command (ugh).  We could change permissions on everything in the target
        directory, but that's kind of ugly too.  Instead, we use Python's set
        functionality to figure out what files were added while we executed the
        rcp command.  This isn't perfect - for instance, it's not correct if
        someone else is messing with the directory at the same time we're doing
        the remote copy - but it's about as good as we're going to get.

        *Note:* Apparently, we can't count on all rcp-compatible implementations
        to return sensible errors for some error conditions.  As an example, the
        ``scp`` command in Debian 'woody' returns a zero (normal) status even
        when it can't find a host or if the login or path is invalid.  We try
        to work around this by issuing ``IOError`` if we don't copy any files from
        the remote host.

        Args:
           remoteUser: Name of the Cedar Backup user on the remote peer
           localUser: Name of the Cedar Backup user on the current host
           remoteHost: Hostname of the remote peer
           rcpCommand: An rcp-compatible copy command to use for copying files from the peer
           rcpCommandList: An rcp-compatible copy command to use for copying files, as for :any:`util.executeCommand`
           sourceDir: Source directory
           targetDir: Target directory
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
        Returns:
            Number of files copied from the source directory to the target directory

        Raises:
           ValueError: If source or target is not a directory or does not exist
           IOError: If there is an IO error copying the files
        """
        beforeSet = RemotePeer._getDirContents(targetDir)
        if localUser is not None:
            try:
                if not isRunningAsRoot():
                    raise IOError("Only root can remote copy as another user.")
            except AttributeError:
                pass
            actualCommand = "%s %s@%s:%s/* %s" % (rcpCommand, remoteUser, remoteHost, sourceDir, targetDir)
            command = resolveCommand(SU_COMMAND)
            result = executeCommand(command, [localUser, "-c", actualCommand])[0]
            if result != 0:
                raise IOError("Error (%d) copying files from remote host as local user [%s]." % (result, localUser))
        else:
            copySource = "%s@%s:%s/*" % (remoteUser, remoteHost, sourceDir)
            command = resolveCommand(rcpCommandList)
            result = executeCommand(command, [copySource, targetDir])[0]
            if result != 0:
                raise IOError("Error (%d) copying files from remote host." % result)
        afterSet = RemotePeer._getDirContents(targetDir)
        if len(afterSet) == 0:
            raise IOError("Did not copy any files from remote peer.")
        differenceSet = afterSet.difference(beforeSet)  # files we added as part of copy
        if len(differenceSet) == 0:
            raise IOError("Apparently did not copy any new files from remote peer.")
        for targetFile in differenceSet:
            if ownership is not None:
                if sys.platform != "win32":
                    os.chown(targetFile, ownership[0], ownership[1])  # pylint: disable=no-member
            if permissions is not None:
                os.chmod(targetFile, permissions)
        return len(differenceSet)

    @staticmethod
    def _copyRemoteFile(
        remoteUser,
        localUser,
        remoteHost,
        rcpCommand,
        rcpCommandList,
        sourceFile,
        targetFile,
        ownership=None,
        permissions=None,
        overwrite=True,
    ):
        """
        Copies a remote source file to a target file.

        *Note:* Internally, we have to go through and escape any spaces in the
        source path with double-backslash, otherwise things get screwed up.   It
        doesn't seem to be required in the target path. I hope this is portable
        to various different rcp methods, but I guess it might not be (all I have
        to test with is OpenSSH).

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        *Note:* We will not overwrite a target file that exists when this method
        is invoked.  If the target already exists, we'll raise an exception.

        *Note:* Apparently, we can't count on all rcp-compatible implementations
        to return sensible errors for some error conditions.  As an example, the
        ``scp`` command in Debian 'woody' returns a zero (normal) status even when
        it can't find a host or if the login or path is invalid.  We try to work
        around this by issuing ``IOError`` the target file does not exist when
        we're done.

        Args:
           remoteUser: Name of the Cedar Backup user on the remote peer
           remoteHost: Hostname of the remote peer
           localUser: Name of the Cedar Backup user on the current host
           rcpCommand: An rcp-compatible copy command to use for copying files from the peer
           rcpCommandList: An rcp-compatible copy command to use for copying files, as for :any:`util.executeCommand`
           sourceFile: Source file to copy
           targetFile: Target file to create
           ownership: Owner and group that files should have, tuple of numeric ``(uid, gid)``
           permissions: Unix permissions mode that the staged files should have, in octal like ``0640``
           overwrite: Indicates whether it's OK to overwrite the target file
        Raises:
           IOError: If the target file already exists
           IOError: If there is an IO error copying the file
           OSError: If there is an OS error changing permissions on the file
        """
        if not overwrite:
            if os.path.exists(targetFile):
                raise IOError("Target file [%s] already exists." % targetFile)
        if localUser is not None:
            try:
                if not isRunningAsRoot():
                    raise IOError("Only root can remote copy as another user.")
            except AttributeError:
                pass
            actualCommand = "%s %s@%s:%s %s" % (rcpCommand, remoteUser, remoteHost, sourceFile.replace(" ", "\\ "), targetFile)
            command = resolveCommand(SU_COMMAND)
            result = executeCommand(command, [localUser, "-c", actualCommand])[0]
            if result != 0:
                raise IOError("Error (%d) copying [%s] from remote host as local user [%s]." % (result, sourceFile, localUser))
        else:
            copySource = "%s@%s:%s" % (remoteUser, remoteHost, sourceFile.replace(" ", "\\ "))
            command = resolveCommand(rcpCommandList)
            result = executeCommand(command, [copySource, targetFile])[0]
            if result != 0:
                raise IOError("Error (%d) copying [%s] from remote host." % (result, sourceFile))
        if not os.path.exists(targetFile):
            raise IOError("Apparently unable to copy file from remote host.")
        if ownership is not None:
            if sys.platform != "win32":
                os.chown(targetFile, ownership[0], ownership[1])  # pylint: disable=no-member
        if permissions is not None:
            os.chmod(targetFile, permissions)

    @staticmethod
    def _pushLocalFile(remoteUser, localUser, remoteHost, rcpCommand, rcpCommandList, sourceFile, targetFile, overwrite=True):
        """
        Copies a local source file to a remote host.

        *Note:* We will not overwrite a target file that exists when this method
        is invoked.  If the target already exists, we'll raise an exception.

        *Note:* Internally, we have to go through and escape any spaces in the
        source and target paths with double-backslash, otherwise things get
        screwed up.  I hope this is portable to various different rcp methods,
        but I guess it might not be (all I have to test with is OpenSSH).

        *Note:* If you have user/group as strings, call the :any:`util.getUidGid` function
        to get the associated uid/gid as an ownership tuple.

        Args:
           remoteUser: Name of the Cedar Backup user on the remote peer
           localUser: Name of the Cedar Backup user on the current host
           remoteHost: Hostname of the remote peer
           rcpCommand: An rcp-compatible copy command to use for copying files from the peer
           rcpCommandList: An rcp-compatible copy command to use for copying files, as for :any:`util.executeCommand`
           sourceFile: Source file to copy
           targetFile: Target file to create
           overwrite: Indicates whether it's OK to overwrite the target file
        Raises:
           IOError: If there is an IO error copying the file
           OSError: If there is an OS error changing permissions on the file
        """
        if not overwrite:
            if os.path.exists(targetFile):
                raise IOError("Target file [%s] already exists." % targetFile)
        if localUser is not None:
            try:
                if not isRunningAsRoot():
                    raise IOError("Only root can remote copy as another user.")
            except AttributeError:
                pass
            actualCommand = '%s "%s" "%s@%s:%s"' % (rcpCommand, sourceFile, remoteUser, remoteHost, targetFile)
            command = resolveCommand(SU_COMMAND)
            result = executeCommand(command, [localUser, "-c", actualCommand])[0]
            if result != 0:
                raise IOError("Error (%d) copying [%s] to remote host as local user [%s]." % (result, sourceFile, localUser))
        else:
            copyTarget = "%s@%s:%s" % (remoteUser, remoteHost, targetFile.replace(" ", "\\ "))
            command = resolveCommand(rcpCommandList)
            result = executeCommand(command, [sourceFile.replace(" ", "\\ "), copyTarget])[0]
            if result != 0:
                raise IOError("Error (%d) copying [%s] to remote host." % (result, sourceFile))

    @staticmethod
    def _executeRemoteCommand(remoteUser, localUser, remoteHost, rshCommand, rshCommandList, remoteCommand):
        """
        Executes a command on the peer via remote shell.

        Args:
           remoteUser: Name of the Cedar Backup user on the remote peer
           localUser: Name of the Cedar Backup user on the current host
           remoteHost: Hostname of the remote peer
           rshCommand: An rsh-compatible copy command to use for remote shells to the peer
           rshCommandList: An rsh-compatible copy command to use for remote shells to the peer, as for :any:`util.executeCommand`
           remoteCommand: The command to be executed on the remote host, with no special shell characters
        Raises:
           IOError: If there is an error executing the remote command
        """
        actualCommand = "%s %s@%s '%s'" % (rshCommand, remoteUser, remoteHost, remoteCommand)
        if localUser is not None:
            try:
                if not isRunningAsRoot():
                    raise IOError("Only root can remote shell as another user.")
            except AttributeError:
                pass
            command = resolveCommand(SU_COMMAND)
            result = executeCommand(command, [localUser, "-c", actualCommand])[0]
            if result != 0:
                raise IOError('Command failed [su -c %s "%s"]' % (localUser, actualCommand))
        else:
            command = resolveCommand(rshCommandList)
            result = executeCommand(command, ["%s@%s" % (remoteUser, remoteHost), "%s" % remoteCommand])[0]
            if result != 0:
                raise IOError("Command failed [%s]" % (actualCommand))

    @staticmethod
    def _buildCbackCommand(cbackCommand, action, fullBackup):
        """
        Builds a Cedar Backup command line for the named action.

        *Note:* If the cback command is None, then DEF_CBACK_COMMAND is used.

        Args:
           cbackCommand: cback command to execute, including required options
           action: Name of the action to execute
           fullBackup: Whether a full backup should be executed

        Returns:
            String suitable for passing to :any:`_executeRemoteCommand` as remoteCommand
        Raises:
           ValueError: If action is None
        """
        if action is None:
            raise ValueError("Action cannot be None.")
        if cbackCommand is None:
            cbackCommand = DEF_CBACK_COMMAND
        if fullBackup:
            return "%s --full %s" % (cbackCommand, action)
        else:
            return "%s %s" % (cbackCommand, action)
