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
# Copyright (c) 2005,2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides an extension to back up Subversion repositories.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to back up Subversion repositories.

This is a Cedar Backup extension used to back up Subversion repositories via
the Cedar Backup command line.  Each Subversion repository can be backed using
the same collect modes allowed for filesystems in the standard Cedar Backup
collect action: weekly, daily, incremental.

This extension requires a new configuration section <subversion> and is
intended to be run either immediately before or immediately after the standard
collect action.  Aside from its own configuration, it requires the options and
collect configuration sections in the standard Cedar Backup configuration file.

There are two different kinds of Subversion repositories at this writing: BDB
(Berkeley Database) and FSFS (a "filesystem within a filesystem").  Although
the repository type can be specified in configuration, that information is just
kept around for reference.  It doesn't affect the backup.  Both kinds of
repositories are backed up in the same way, using ``svnadmin dump`` in an
incremental mode.

It turns out that FSFS repositories can also be backed up just like any
other filesystem directory.  If you would rather do that, then use the normal
collect action.  This is probably simpler, although it carries its own
advantages and disadvantages (plus you will have to be careful to exclude
the working directories Subversion uses when building an update to commit).
Check the Subversion documentation for more information.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
import pickle
from bz2 import BZ2File
from functools import total_ordering
from gzip import GzipFile

from CedarBackup3.config import VALID_COLLECT_MODES, VALID_COMPRESS_MODES
from CedarBackup3.filesystem import FilesystemList
from CedarBackup3.util import (
    ObjectTypeList,
    RegexList,
    UnorderedList,
    buildNormalizedPath,
    changeOwnership,
    encodePath,
    executeCommand,
    isStartOfWeek,
    pathJoin,
    resolveCommand,
)
from CedarBackup3.xmlutil import (
    addContainerNode,
    addStringNode,
    createInputDom,
    isElement,
    readChildren,
    readFirstChild,
    readString,
    readStringList,
)

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.subversion")

SVNLOOK_COMMAND = ["svnlook"]
SVNADMIN_COMMAND = ["svnadmin"]

REVISION_PATH_EXTENSION = "svnlast"


########################################################################
# RepositoryDir class definition
########################################################################


@total_ordering
class RepositoryDir(object):

    """
    Class representing Subversion repository directory.

    A repository directory is a directory that contains one or more Subversion
    repositories.

    The following restrictions exist on data in this class:

       - The directory path must be absolute.
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.

    The repository type value is kept around just for reference.  It doesn't
    affect the behavior of the backup.

    Relative exclusions are allowed here.  However, there is no configured
    ignore file, because repository dir backups are not recursive.

    """

    def __init__(
        self,
        repositoryType=None,
        directoryPath=None,
        collectMode=None,
        compressMode=None,
        relativeExcludePaths=None,
        excludePatterns=None,
    ):
        """
        Constructor for the ``RepositoryDir`` class.

        Args:
           repositoryType: Type of repository, for reference
           directoryPath: Absolute path of the Subversion parent directory
           collectMode: Overridden collect mode for this directory
           compressMode: Overridden compression mode for this directory
           relativeExcludePaths: List of relative paths to exclude
           excludePatterns: List of regular expression patterns to exclude
        """
        self._repositoryType = None
        self._directoryPath = None
        self._collectMode = None
        self._compressMode = None
        self._relativeExcludePaths = None
        self._excludePatterns = None
        self.repositoryType = repositoryType
        self.directoryPath = directoryPath
        self.collectMode = collectMode
        self.compressMode = compressMode
        self.relativeExcludePaths = relativeExcludePaths
        self.excludePatterns = excludePatterns

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "RepositoryDir(%s, %s, %s, %s, %s, %s)" % (
            self.repositoryType,
            self.directoryPath,
            self.collectMode,
            self.compressMode,
            self.relativeExcludePaths,
            self.excludePatterns,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.repositoryType != other.repositoryType:
            if str(self.repositoryType or "") < str(other.repositoryType or ""):
                return -1
            else:
                return 1
        if self.directoryPath != other.directoryPath:
            if str(self.directoryPath or "") < str(other.directoryPath or ""):
                return -1
            else:
                return 1
        if self.collectMode != other.collectMode:
            if str(self.collectMode or "") < str(other.collectMode or ""):
                return -1
            else:
                return 1
        if self.compressMode != other.compressMode:
            if str(self.compressMode or "") < str(other.compressMode or ""):
                return -1
            else:
                return 1
        if self.relativeExcludePaths != other.relativeExcludePaths:
            if self.relativeExcludePaths < other.relativeExcludePaths:
                return -1
            else:
                return 1
        if self.excludePatterns != other.excludePatterns:
            if self.excludePatterns < other.excludePatterns:
                return -1
            else:
                return 1
        return 0

    def _setRepositoryType(self, value):
        """
        Property target used to set the repository type.
        There is no validation; this value is kept around just for reference.
        """
        self._repositoryType = value

    def _getRepositoryType(self):
        """
        Property target used to get the repository type.
        """
        return self._repositoryType

    def _setDirectoryPath(self, value):
        """
        Property target used to set the directory path.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Repository path must be an absolute path.")
        self._directoryPath = encodePath(value)

    def _getDirectoryPath(self):
        """
        Property target used to get the repository path.
        """
        return self._directoryPath

    def _setCollectMode(self, value):
        """
        Property target used to set the collect mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COLLECT_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COLLECT_MODES:
                raise ValueError("Collect mode must be one of %s." % VALID_COLLECT_MODES)
        self._collectMode = value

    def _getCollectMode(self):
        """
        Property target used to get the collect mode.
        """
        return self._collectMode

    def _setCompressMode(self, value):
        """
        Property target used to set the compress mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COMPRESS_MODES:
                raise ValueError("Compress mode must be one of %s." % VALID_COMPRESS_MODES)
        self._compressMode = value

    def _getCompressMode(self):
        """
        Property target used to get the compress mode.
        """
        return self._compressMode

    def _setRelativeExcludePaths(self, value):
        """
        Property target used to set the relative exclude paths list.
        Elements do not have to exist on disk at the time of assignment.
        """
        if value is None:
            self._relativeExcludePaths = None
        else:
            try:
                saved = self._relativeExcludePaths
                self._relativeExcludePaths = UnorderedList()
                self._relativeExcludePaths.extend(value)
            except Exception as e:
                self._relativeExcludePaths = saved
                raise e

    def _getRelativeExcludePaths(self):
        """
        Property target used to get the relative exclude paths list.
        """
        return self._relativeExcludePaths

    def _setExcludePatterns(self, value):
        """
        Property target used to set the exclude patterns list.
        """
        if value is None:
            self._excludePatterns = None
        else:
            try:
                saved = self._excludePatterns
                self._excludePatterns = RegexList()
                self._excludePatterns.extend(value)
            except Exception as e:
                self._excludePatterns = saved
                raise e

    def _getExcludePatterns(self):
        """
        Property target used to get the exclude patterns list.
        """
        return self._excludePatterns

    repositoryType = property(_getRepositoryType, _setRepositoryType, None, doc="Type of this repository, for reference.")
    directoryPath = property(_getDirectoryPath, _setDirectoryPath, None, doc="Absolute path of the Subversion parent directory.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this repository.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Overridden compress mode for this repository.")
    relativeExcludePaths = property(_getRelativeExcludePaths, _setRelativeExcludePaths, None, "List of relative paths to exclude.")
    excludePatterns = property(_getExcludePatterns, _setExcludePatterns, None, "List of regular expression patterns to exclude.")


########################################################################
# Repository class definition
########################################################################


@total_ordering
class Repository(object):

    """
    Class representing generic Subversion repository configuration..

    The following restrictions exist on data in this class:

       - The respository path must be absolute.
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.

    The repository type value is kept around just for reference.  It doesn't
    affect the behavior of the backup.

    """

    def __init__(self, repositoryType=None, repositoryPath=None, collectMode=None, compressMode=None):
        """
        Constructor for the ``Repository`` class.

        Args:
           repositoryType: Type of repository, for reference
           repositoryPath: Absolute path to a Subversion repository on disk
           collectMode: Overridden collect mode for this directory
           compressMode: Overridden compression mode for this directory
        """
        self._repositoryType = None
        self._repositoryPath = None
        self._collectMode = None
        self._compressMode = None
        self.repositoryType = repositoryType
        self.repositoryPath = repositoryPath
        self.collectMode = collectMode
        self.compressMode = compressMode

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "Repository(%s, %s, %s, %s)" % (self.repositoryType, self.repositoryPath, self.collectMode, self.compressMode)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.repositoryType != other.repositoryType:
            if str(self.repositoryType or "") < str(other.repositoryType or ""):
                return -1
            else:
                return 1
        if self.repositoryPath != other.repositoryPath:
            if str(self.repositoryPath or "") < str(other.repositoryPath or ""):
                return -1
            else:
                return 1
        if self.collectMode != other.collectMode:
            if str(self.collectMode or "") < str(other.collectMode or ""):
                return -1
            else:
                return 1
        if self.compressMode != other.compressMode:
            if str(self.compressMode or "") < str(other.compressMode or ""):
                return -1
            else:
                return 1
        return 0

    def _setRepositoryType(self, value):
        """
        Property target used to set the repository type.
        There is no validation; this value is kept around just for reference.
        """
        self._repositoryType = value

    def _getRepositoryType(self):
        """
        Property target used to get the repository type.
        """
        return self._repositoryType

    def _setRepositoryPath(self, value):
        """
        Property target used to set the repository path.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Repository path must be an absolute path.")
        self._repositoryPath = encodePath(value)

    def _getRepositoryPath(self):
        """
        Property target used to get the repository path.
        """
        return self._repositoryPath

    def _setCollectMode(self, value):
        """
        Property target used to set the collect mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COLLECT_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COLLECT_MODES:
                raise ValueError("Collect mode must be one of %s." % VALID_COLLECT_MODES)
        self._collectMode = value

    def _getCollectMode(self):
        """
        Property target used to get the collect mode.
        """
        return self._collectMode

    def _setCompressMode(self, value):
        """
        Property target used to set the compress mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COMPRESS_MODES:
                raise ValueError("Compress mode must be one of %s." % VALID_COMPRESS_MODES)
        self._compressMode = value

    def _getCompressMode(self):
        """
        Property target used to get the compress mode.
        """
        return self._compressMode

    repositoryType = property(_getRepositoryType, _setRepositoryType, None, doc="Type of this repository, for reference.")
    repositoryPath = property(_getRepositoryPath, _setRepositoryPath, None, doc="Path to the repository to collect.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this repository.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Overridden compress mode for this repository.")


########################################################################
# SubversionConfig class definition
########################################################################


@total_ordering
class SubversionConfig(object):

    """
    Class representing Subversion configuration.

    Subversion configuration is used for backing up Subversion repositories.

    The following restrictions exist on data in this class:

       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
       - The repositories list must be a list of ``Repository`` objects.
       - The repositoryDirs list must be a list of ``RepositoryDir`` objects.

    For the two lists, validation is accomplished through the
    :any:`util.ObjectTypeList` list implementation that overrides common list
    methods and transparently ensures that each element has the correct type.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, collectMode=None, compressMode=None, repositories=None, repositoryDirs=None):
        """
        Constructor for the ``SubversionConfig`` class.

        Args:
           collectMode: Default collect mode
           compressMode: Default compress mode
           repositories: List of Subversion repositories to back up
           repositoryDirs: List of Subversion parent directories to back up

        Raises:
           ValueError: If one of the values is invalid
        """
        self._collectMode = None
        self._compressMode = None
        self._repositories = None
        self._repositoryDirs = None
        self.collectMode = collectMode
        self.compressMode = compressMode
        self.repositories = repositories
        self.repositoryDirs = repositoryDirs

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "SubversionConfig(%s, %s, %s, %s)" % (self.collectMode, self.compressMode, self.repositories, self.repositoryDirs)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        Lists within this class are "unordered" for equality comparisons.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.collectMode != other.collectMode:
            if str(self.collectMode or "") < str(other.collectMode or ""):
                return -1
            else:
                return 1
        if self.compressMode != other.compressMode:
            if str(self.compressMode or "") < str(other.compressMode or ""):
                return -1
            else:
                return 1
        if self.repositories != other.repositories:
            if self.repositories < other.repositories:
                return -1
            else:
                return 1
        if self.repositoryDirs != other.repositoryDirs:
            if self.repositoryDirs < other.repositoryDirs:
                return -1
            else:
                return 1
        return 0

    def _setCollectMode(self, value):
        """
        Property target used to set the collect mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COLLECT_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COLLECT_MODES:
                raise ValueError("Collect mode must be one of %s." % VALID_COLLECT_MODES)
        self._collectMode = value

    def _getCollectMode(self):
        """
        Property target used to get the collect mode.
        """
        return self._collectMode

    def _setCompressMode(self, value):
        """
        Property target used to set the compress mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_COMPRESS_MODES:
                raise ValueError("Compress mode must be one of %s." % VALID_COMPRESS_MODES)
        self._compressMode = value

    def _getCompressMode(self):
        """
        Property target used to get the compress mode.
        """
        return self._compressMode

    def _setRepositories(self, value):
        """
        Property target used to set the repositories list.
        Either the value must be ``None`` or each element must be a ``Repository``.
        Raises:
           ValueError: If the value is not a ``Repository``
        """
        if value is None:
            self._repositories = None
        else:
            try:
                saved = self._repositories
                self._repositories = ObjectTypeList(Repository, "Repository")
                self._repositories.extend(value)
            except Exception as e:
                self._repositories = saved
                raise e

    def _getRepositories(self):
        """
        Property target used to get the repositories list.
        """
        return self._repositories

    def _setRepositoryDirs(self, value):
        """
        Property target used to set the repositoryDirs list.
        Either the value must be ``None`` or each element must be a ``Repository``.
        Raises:
           ValueError: If the value is not a ``Repository``
        """
        if value is None:
            self._repositoryDirs = None
        else:
            try:
                saved = self._repositoryDirs
                self._repositoryDirs = ObjectTypeList(RepositoryDir, "RepositoryDir")
                self._repositoryDirs.extend(value)
            except Exception as e:
                self._repositoryDirs = saved
                raise e

    def _getRepositoryDirs(self):
        """
        Property target used to get the repositoryDirs list.
        """
        return self._repositoryDirs

    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Default collect mode.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Default compress mode.")
    repositories = property(_getRepositories, _setRepositories, None, doc="List of Subversion repositories to back up.")
    repositoryDirs = property(_getRepositoryDirs, _setRepositoryDirs, None, doc="List of Subversion parent directories to back up.")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    Subversion-specific configuration values.  Third parties who need to read
    and write configuration related to this extension should access it through
    the constructor, ``validate`` and ``addConfig`` methods.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, xmlData=None, xmlPath=None, validate=True):
        """
        Initializes a configuration object.

        If you initialize the object without passing either ``xmlData`` or
        ``xmlPath`` then configuration will be empty and will be invalid until it
        is filled in properly.

        No reference to the original XML data or original path is saved off by
        this class.  Once the data has been parsed (successfully or not) this
        original information is discarded.

        Unless the ``validate`` argument is ``False``, the :any:`LocalConfig.validate`
        method will be called (with its default arguments) against configuration
        after successfully parsing any passed-in XML.  Keep in mind that even if
        ``validate`` is ``False``, it might not be possible to parse the passed-in
        XML document if lower-level validations fail.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to read in
        invalid configuration from disk.

        Args:
           xmlData (String data): XML data representing configuration
           xmlPath (Absolute path to a file on disk): Path to an XML file on disk
           validate (Boolean true/false): Validate the document after parsing it
        Raises:
           ValueError: If both ``xmlData`` and ``xmlPath`` are passed-in
           ValueError: If the XML data in ``xmlData`` or ``xmlPath`` cannot be parsed
           ValueError: If the parsed configuration document is not valid
        """
        self._subversion = None
        self.subversion = None
        if xmlData is not None and xmlPath is not None:
            raise ValueError("Use either xmlData or xmlPath, but not both.")
        if xmlData is not None:
            self._parseXmlData(xmlData)
            if validate:
                self.validate()
        elif xmlPath is not None:
            with open(xmlPath) as f:
                xmlData = f.read()
            self._parseXmlData(xmlData)
            if validate:
                self.validate()

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "LocalConfig(%s)" % (self.subversion)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, iplemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        Lists within this class are "unordered" for equality comparisons.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.subversion != other.subversion:
            if self.subversion < other.subversion:
                return -1
            else:
                return 1
        return 0

    def _setSubversion(self, value):
        """
        Property target used to set the subversion configuration value.
        If not ``None``, the value must be a ``SubversionConfig`` object.
        Raises:
           ValueError: If the value is not a ``SubversionConfig``
        """
        if value is None:
            self._subversion = None
        else:
            if not isinstance(value, SubversionConfig):
                raise ValueError("Value must be a ``SubversionConfig`` object.")
            self._subversion = value

    def _getSubversion(self):
        """
        Property target used to get the subversion configuration value.
        """
        return self._subversion

    subversion = property(
        _getSubversion, _setSubversion, None, "Subversion configuration in terms of a ``SubversionConfig`` object."
    )

    def validate(self):
        """
        Validates configuration represented by the object.

        Subversion configuration must be filled in.  Within that, the collect
        mode and compress mode are both optional, but the list of repositories
        must contain at least one entry.

        Each repository must contain a repository path, and then must be either
        able to take collect mode and compress mode configuration from the parent
        ``SubversionConfig`` object, or must set each value on its own.

        Raises:
           ValueError: If one of the validations fails
        """
        if self.subversion is None:
            raise ValueError("Subversion section is required.")
        if (self.subversion.repositories is None or len(self.subversion.repositories) < 1) and (
            self.subversion.repositoryDirs is None or len(self.subversion.repositoryDirs) < 1
        ):
            raise ValueError("At least one Subversion repository must be configured.")
        if self.subversion.repositories is not None:
            for repository in self.subversion.repositories:
                if repository.repositoryPath is None:
                    raise ValueError("Each repository must set a repository path.")
                if self.subversion.collectMode is None and repository.collectMode is None:
                    raise ValueError("Collect mode must either be set in parent section or individual repository.")
                if self.subversion.compressMode is None and repository.compressMode is None:
                    raise ValueError("Compress mode must either be set in parent section or individual repository.")
        if self.subversion.repositoryDirs is not None:
            for repositoryDir in self.subversion.repositoryDirs:
                if repositoryDir.directoryPath is None:
                    raise ValueError("Each repository directory must set a directory path.")
                if self.subversion.collectMode is None and repositoryDir.collectMode is None:
                    raise ValueError("Collect mode must either be set in parent section or repository directory.")
                if self.subversion.compressMode is None and repositoryDir.compressMode is None:
                    raise ValueError("Compress mode must either be set in parent section or repository directory.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds a <subversion> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           collectMode    //cb_config/subversion/collectMode
           compressMode   //cb_config/subversion/compressMode

        We also add groups of the following items, one list element per
        item::

           repository     //cb_config/subversion/repository
           repository_dir //cb_config/subversion/repository_dir

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.subversion is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "subversion")
            addStringNode(xmlDom, sectionNode, "collect_mode", self.subversion.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", self.subversion.compressMode)
            if self.subversion.repositories is not None:
                for repository in self.subversion.repositories:
                    LocalConfig._addRepository(xmlDom, sectionNode, repository)
            if self.subversion.repositoryDirs is not None:
                for repositoryDir in self.subversion.repositoryDirs:
                    LocalConfig._addRepositoryDir(xmlDom, sectionNode, repositoryDir)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the subversion configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._subversion = LocalConfig._parseSubversion(parentNode)

    @staticmethod
    def _parseSubversion(parent):
        """
        Parses a subversion configuration section.

        We read the following individual fields::

           collectMode    //cb_config/subversion/collect_mode
           compressMode   //cb_config/subversion/compress_mode

        We also read groups of the following item, one list element per
        item::

           repositories    //cb_config/subversion/repository
           repository_dirs //cb_config/subversion/repository_dir

        The repositories are parsed by :any:`_parseRepositories`, and the repository
        dirs are parsed by :any:`_parseRepositoryDirs`.

        Args:
           parent: Parent node to search beneath

        Returns:
            ``SubversionConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        subversion = None
        section = readFirstChild(parent, "subversion")
        if section is not None:
            subversion = SubversionConfig()
            subversion.collectMode = readString(section, "collect_mode")
            subversion.compressMode = readString(section, "compress_mode")
            subversion.repositories = LocalConfig._parseRepositories(section)
            subversion.repositoryDirs = LocalConfig._parseRepositoryDirs(section)
        return subversion

    @staticmethod
    def _parseRepositories(parent):
        """
        Reads a list of ``Repository`` objects from immediately beneath the parent.

        We read the following individual fields::

           repositoryType          type
           repositoryPath          abs_path
           collectMode             collect_mode
           compressMode            compess_mode

        The type field is optional, and its value is kept around only for
        reference.

        Args:
           parent: Parent node to search beneath

        Returns:
            List of ``Repository`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parent, "repository"):
            if isElement(entry):
                repository = Repository()
                repository.repositoryType = readString(entry, "type")
                repository.repositoryPath = readString(entry, "abs_path")
                repository.collectMode = readString(entry, "collect_mode")
                repository.compressMode = readString(entry, "compress_mode")
                lst.append(repository)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _addRepository(xmlDom, parentNode, repository):
        """
        Adds a repository container as the next child of a parent.

        We add the following fields to the document::

           repositoryType          repository/type
           repositoryPath          repository/abs_path
           collectMode             repository/collect_mode
           compressMode            repository/compress_mode

        The <repository> node itself is created as the next child of the parent
        node.  This method only adds one repository node.  The parent must loop
        for each repository in the ``SubversionConfig`` object.

        If ``repository`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
           repository: Repository to be added to the document
        """
        if repository is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "repository")
            addStringNode(xmlDom, sectionNode, "type", repository.repositoryType)
            addStringNode(xmlDom, sectionNode, "abs_path", repository.repositoryPath)
            addStringNode(xmlDom, sectionNode, "collect_mode", repository.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", repository.compressMode)

    @staticmethod
    def _parseRepositoryDirs(parent):
        """
        Reads a list of ``RepositoryDir`` objects from immediately beneath the parent.

        We read the following individual fields::

           repositoryType          type
           directoryPath           abs_path
           collectMode             collect_mode
           compressMode            compess_mode

        We also read groups of the following items, one list element per
        item::

           relativeExcludePaths    exclude/rel_path
           excludePatterns         exclude/pattern

        The exclusions are parsed by :any:`_parseExclusions`.

        The type field is optional, and its value is kept around only for
        reference.

        Args:
           parent: Parent node to search beneath

        Returns:
            List of ``RepositoryDir`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parent, "repository_dir"):
            if isElement(entry):
                repositoryDir = RepositoryDir()
                repositoryDir.repositoryType = readString(entry, "type")
                repositoryDir.directoryPath = readString(entry, "abs_path")
                repositoryDir.collectMode = readString(entry, "collect_mode")
                repositoryDir.compressMode = readString(entry, "compress_mode")
                (repositoryDir.relativeExcludePaths, repositoryDir.excludePatterns) = LocalConfig._parseExclusions(entry)
                lst.append(repositoryDir)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseExclusions(parentNode):
        """
        Reads exclusions data from immediately beneath the parent.

        We read groups of the following items, one list element per item::

           relative    exclude/rel_path
           patterns    exclude/pattern

        If there are none of some pattern (i.e. no relative path items) then
        ``None`` will be returned for that item in the tuple.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            Tuple of (relative, patterns) exclusions
        """
        section = readFirstChild(parentNode, "exclude")
        if section is None:
            return (None, None)
        else:
            relative = readStringList(section, "rel_path")
            patterns = readStringList(section, "pattern")
            return (relative, patterns)

    @staticmethod
    def _addRepositoryDir(xmlDom, parentNode, repositoryDir):
        """
        Adds a repository dir container as the next child of a parent.

        We add the following fields to the document::

           repositoryType          repository_dir/type
           directoryPath           repository_dir/abs_path
           collectMode             repository_dir/collect_mode
           compressMode            repository_dir/compress_mode

        We also add groups of the following items, one list element per item::

           relativeExcludePaths    dir/exclude/rel_path
           excludePatterns         dir/exclude/pattern

        The <repository_dir> node itself is created as the next child of the
        parent node.  This method only adds one repository node.  The parent must
        loop for each repository dir in the ``SubversionConfig`` object.

        If ``repositoryDir`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
           repositoryDir: Repository dir to be added to the document
        """
        if repositoryDir is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "repository_dir")
            addStringNode(xmlDom, sectionNode, "type", repositoryDir.repositoryType)
            addStringNode(xmlDom, sectionNode, "abs_path", repositoryDir.directoryPath)
            addStringNode(xmlDom, sectionNode, "collect_mode", repositoryDir.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", repositoryDir.compressMode)
            if (repositoryDir.relativeExcludePaths is not None and repositoryDir.relativeExcludePaths != []) or (
                repositoryDir.excludePatterns is not None and repositoryDir.excludePatterns != []
            ):
                excludeNode = addContainerNode(xmlDom, sectionNode, "exclude")
                if repositoryDir.relativeExcludePaths is not None:
                    for relativePath in repositoryDir.relativeExcludePaths:
                        addStringNode(xmlDom, excludeNode, "rel_path", relativePath)
                if repositoryDir.excludePatterns is not None:
                    for pattern in repositoryDir.excludePatterns:
                        addStringNode(xmlDom, excludeNode, "pattern", pattern)


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################


def executeAction(configPath, options, config):
    """
    Executes the Subversion backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If a backup could not be written for some reason
    """
    logger.debug("Executing Subversion extended action.")
    if config.options is None or config.collect is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    todayIsStart = isStartOfWeek(config.options.startingDay)
    fullBackup = options.full or todayIsStart
    logger.debug("Full backup flag is [%s]", fullBackup)
    if local.subversion.repositories is not None:
        for repository in local.subversion.repositories:
            _backupRepository(config, local, todayIsStart, fullBackup, repository)
    if local.subversion.repositoryDirs is not None:
        for repositoryDir in local.subversion.repositoryDirs:
            logger.debug("Working with repository directory [%s].", repositoryDir.directoryPath)
            for repositoryPath in _getRepositoryPaths(repositoryDir):
                repository = Repository(
                    repositoryDir.repositoryType, repositoryPath, repositoryDir.collectMode, repositoryDir.compressMode
                )
                _backupRepository(config, local, todayIsStart, fullBackup, repository)
            logger.info("Completed backing up Subversion repository directory [%s].", repositoryDir.directoryPath)
    logger.info("Executed the Subversion extended action successfully.")


def _getCollectMode(local, repository):
    """
    Gets the collect mode that should be used for a repository.
    Use repository's if possible, otherwise take from subversion section.
    Args:
       repository: Repository object
    Returns:
        Collect mode to use
    """
    if repository.collectMode is None:
        collectMode = local.subversion.collectMode
    else:
        collectMode = repository.collectMode
    logger.debug("Collect mode is [%s]", collectMode)
    return collectMode


def _getCompressMode(local, repository):
    """
    Gets the compress mode that should be used for a repository.
    Use repository's if possible, otherwise take from subversion section.
    Args:
       local: LocalConfig object
       repository: Repository object
    Returns:
        Compress mode to use
    """
    if repository.compressMode is None:
        compressMode = local.subversion.compressMode
    else:
        compressMode = repository.compressMode
    logger.debug("Compress mode is [%s]", compressMode)
    return compressMode


def _getRevisionPath(config, repository):
    """
    Gets the path to the revision file associated with a repository.
    Args:
       config: Config object
       repository: Repository object
    Returns:
        Absolute path to the revision file associated with the repository
    """
    normalized = buildNormalizedPath(repository.repositoryPath)
    filename = "%s.%s" % (normalized, REVISION_PATH_EXTENSION)
    revisionPath = pathJoin(config.options.workingDir, filename)
    logger.debug("Revision file path is [%s]", revisionPath)
    return revisionPath


def _getBackupPath(config, repositoryPath, compressMode, startRevision, endRevision):
    """
    Gets the backup file path (including correct extension) associated with a repository.
    Args:
       config: Config object
       repositoryPath: Path to the indicated repository
       compressMode: Compress mode to use for this repository
       startRevision: Starting repository revision
       endRevision: Ending repository revision
    Returns:
        Absolute path to the backup file associated with the repository
    """
    normalizedPath = buildNormalizedPath(repositoryPath)
    filename = "svndump-%d:%d-%s.txt" % (startRevision, endRevision, normalizedPath)
    if compressMode == "gzip":
        filename = "%s.gz" % filename
    elif compressMode == "bzip2":
        filename = "%s.bz2" % filename
    backupPath = pathJoin(config.collect.targetDir, filename)
    logger.debug("Backup file path is [%s]", backupPath)
    return backupPath


def _getRepositoryPaths(repositoryDir):
    """
    Gets a list of child repository paths within a repository directory.
    Args:
       repositoryDir: RepositoryDirectory
    """
    (excludePaths, excludePatterns) = _getExclusions(repositoryDir)
    fsList = FilesystemList()
    fsList.excludeFiles = True
    fsList.excludeLinks = True
    fsList.excludePaths = excludePaths
    fsList.excludePatterns = excludePatterns
    fsList.addDirContents(path=repositoryDir.directoryPath, recursive=False, addSelf=False)
    return fsList


def _getExclusions(repositoryDir):
    """
    Gets exclusions (file and patterns) associated with an repository directory.

    The returned files value is a list of absolute paths to be excluded from the
    backup for a given directory.  It is derived from the repository directory's
    relative exclude paths.

    The returned patterns value is a list of patterns to be excluded from the
    backup for a given directory.  It is derived from the repository directory's
    list of patterns.

    Args:
       repositoryDir: Repository directory object

    Returns:
        Tuple (files, patterns) indicating what to exclude
    """
    paths = []
    if repositoryDir.relativeExcludePaths is not None:
        for relativePath in repositoryDir.relativeExcludePaths:
            paths.append(pathJoin(repositoryDir.directoryPath, relativePath))
    patterns = []
    if repositoryDir.excludePatterns is not None:
        patterns.extend(repositoryDir.excludePatterns)
    logger.debug("Exclude paths: %s", paths)
    logger.debug("Exclude patterns: %s", patterns)
    return (paths, patterns)


def _backupRepository(config, local, todayIsStart, fullBackup, repository):
    """
    Backs up an individual Subversion repository.

    This internal method wraps the public methods and adds some functionality
    to work better with the extended action itself.

    Args:
       config: Cedar Backup configuration
       local: Local configuration
       todayIsStart: Indicates whether today is start of week
       fullBackup: Full backup flag
       repository: Repository to operate on

    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem executing the Subversion dump
    """
    logger.debug("Working with repository [%s]", repository.repositoryPath)
    logger.debug("Repository type is [%s]", repository.repositoryType)
    collectMode = _getCollectMode(local, repository)
    compressMode = _getCompressMode(local, repository)
    revisionPath = _getRevisionPath(config, repository)
    if not (fullBackup or (collectMode in ["daily", "incr"]) or (collectMode == "weekly" and todayIsStart)):
        logger.debug("Repository will not be backed up, per collect mode.")
        return
    logger.debug("Repository meets criteria to be backed up today.")
    if collectMode != "incr" or fullBackup:
        startRevision = 0
        endRevision = getYoungestRevision(repository.repositoryPath)
        logger.debug("Using full backup, revision: (%d, %d).", startRevision, endRevision)
    else:
        if fullBackup:
            startRevision = 0
            endRevision = getYoungestRevision(repository.repositoryPath)
        else:
            startRevision = _loadLastRevision(revisionPath) + 1
            endRevision = getYoungestRevision(repository.repositoryPath)
            if startRevision > endRevision:
                logger.info("No need to back up repository [%s]; no new revisions.", repository.repositoryPath)
                return
        logger.debug("Using incremental backup, revision: (%d, %d).", startRevision, endRevision)
    backupPath = _getBackupPath(config, repository.repositoryPath, compressMode, startRevision, endRevision)
    with _getOutputFile(backupPath, compressMode) as outputFile:
        backupRepository(repository.repositoryPath, outputFile, startRevision, endRevision)
    if not os.path.exists(backupPath):
        raise IOError("Dump file [%s] does not seem to exist after backup completed." % backupPath)
    changeOwnership(backupPath, config.options.backupUser, config.options.backupGroup)
    if collectMode == "incr":
        _writeLastRevision(config, revisionPath, endRevision)
    logger.info("Completed backing up Subversion repository [%s].", repository.repositoryPath)


def _getOutputFile(backupPath, compressMode):
    """
    Opens the output file used for saving the Subversion dump.

    If the compress mode is "gzip", we'll open a ``GzipFile``, and if the
    compress mode is "bzip2", we'll open a ``BZ2File``.  Otherwise, we'll just
    return an object from the normal ``open()`` method.

    Args:
       backupPath: Path to file to open
       compressMode: Compress mode of file ("none", "gzip", "bzip")

    Returns:
        Output file object, opened in binary mode for use with executeCommand()
    """
    if compressMode == "gzip":
        return GzipFile(backupPath, "wb")
    elif compressMode == "bzip2":
        return BZ2File(backupPath, "wb")
    else:
        return open(backupPath, "wb")


def _loadLastRevision(revisionPath):
    """
    Loads the indicated revision file from disk into an integer.

    If we can't load the revision file successfully (either because it doesn't
    exist or for some other reason), then a revision of -1 will be returned -
    but the condition will be logged.  This way, we err on the side of backing
    up too much, because anyone using this will presumably be adding 1 to the
    revision, so they don't duplicate any backups.

    Args:
       revisionPath: Path to the revision file on disk

    Returns:
        Integer representing last backed-up revision, -1 on error or if none can be read
    """
    if not os.path.isfile(revisionPath):
        startRevision = -1
        logger.debug("Revision file [%s] does not exist on disk.", revisionPath)
    else:
        try:
            with open(revisionPath, "rb") as f:
                startRevision = pickle.load(f, fix_imports=True)  # be compatible with Python 2
            logger.debug("Loaded revision file [%s] from disk: %d.", revisionPath, startRevision)
        except Exception as e:
            startRevision = -1
            logger.error("Failed loading revision file [%s] from disk: %s", revisionPath, e)
    return startRevision


def _writeLastRevision(config, revisionPath, endRevision):
    """
    Writes the end revision to the indicated revision file on disk.

    If we can't write the revision file successfully for any reason, we'll log
    the condition but won't throw an exception.

    Args:
       config: Config object
       revisionPath: Path to the revision file on disk
       endRevision: Last revision backed up on this run
    """
    try:
        with open(revisionPath, "wb") as f:
            pickle.dump(endRevision, f, 0, fix_imports=True)
        changeOwnership(revisionPath, config.options.backupUser, config.options.backupGroup)
        logger.debug("Wrote new revision file [%s] to disk: %d.", revisionPath, endRevision)
    except Exception as e:
        logger.error("Failed to write revision file [%s] to disk: %s", revisionPath, e)


##############################
# backupRepository() function
##############################


def backupRepository(repositoryPath, backupFile, startRevision=None, endRevision=None):
    """
    Backs up an individual Subversion repository.

    The starting and ending revision values control an incremental backup.  If
    the starting revision is not passed in, then revision zero (the start of the
    repository) is assumed.  If the ending revision is not passed in, then the
    youngest revision in the database will be used as the endpoint.

    The backup data will be written into the passed-in back file.  Normally,
    this would be an object as returned from ``open``, but it is possible to use
    something like a ``GzipFile`` to write compressed output.  The caller is
    responsible for closing the passed-in backup file.

    *Note:* This function should either be run as root or as the owner of the
    Subversion repository.

    *Note:* It is apparently *not* a good idea to interrupt this function.
    Sometimes, this leaves the repository in a "wedged" state, which requires
    recovery using ``svnadmin recover``.

    Args:
       repositoryPath (String path representing Subversion repository on disk): Path to Subversion repository to back up
       backupFile (Python file object as from ``open`` or ``file``): Python file object to use for writing backup
       startRevision (Integer value >= 0): Starting repository revision to back up (for incremental backups)
       endRevision (Integer value >= 0): Ending repository revision to back up (for incremental backups)
    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem executing the Subversion dump
    """
    if startRevision is None:
        startRevision = 0
    if endRevision is None:
        endRevision = getYoungestRevision(repositoryPath)
    if int(startRevision) < 0:
        raise ValueError("Start revision must be >= 0.")
    if int(endRevision) < 0:
        raise ValueError("End revision must be >= 0.")
    if startRevision > endRevision:
        raise ValueError("Start revision must be <= end revision.")
    args = ["dump", "--quiet", "-r%s:%s" % (startRevision, endRevision), "--incremental", repositoryPath]
    command = resolveCommand(SVNADMIN_COMMAND)
    result = executeCommand(command, args, returnOutput=False, ignoreStderr=True, doNotLog=True, outputFile=backupFile)[0]
    if result != 0:
        raise IOError("Error [%d] executing Subversion dump for repository [%s]." % (result, repositoryPath))
    logger.debug("Completed dumping subversion repository [%s].", repositoryPath)


#################################
# getYoungestRevision() function
#################################


def getYoungestRevision(repositoryPath):
    """
    Gets the youngest (newest) revision in a Subversion repository using ``svnlook``.

    *Note:* This function should either be run as root or as the owner of the
    Subversion repository.

    Args:
       repositoryPath (String path representing Subversion repository on disk): Path to Subversion repository to look in
    Returns:
        Youngest revision as an integer

    Raises:
       ValueError: If there is a problem parsing the ``svnlook`` output
       IOError: If there is a problem executing the ``svnlook`` command
    """
    args = ["youngest", repositoryPath]
    command = resolveCommand(SVNLOOK_COMMAND)
    (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
    if result != 0:
        raise IOError("Error [%d] executing 'svnlook youngest' for repository [%s]." % (result, repositoryPath))
    if len(output) != 1:
        raise ValueError("Unable to parse 'svnlook youngest' output.")
    return int(output[0])


########################################################################
# Deprecated functionality
########################################################################


class BDBRepository(Repository):

    """
    Class representing Subversion BDB (Berkeley Database) repository configuration.
    This object is deprecated.  Use a simple :any:`Repository` instead.
    """

    def __init__(self, repositoryPath=None, collectMode=None, compressMode=None):
        """
        Constructor for the ``BDBRepository`` class.
        """
        super(BDBRepository, self).__init__("BDB", repositoryPath, collectMode, compressMode)

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "BDBRepository(%s, %s, %s)" % (self.repositoryPath, self.collectMode, self.compressMode)


class FSFSRepository(Repository):

    """
    Class representing Subversion FSFS repository configuration.
    This object is deprecated.  Use a simple :any:`Repository` instead.
    """

    def __init__(self, repositoryPath=None, collectMode=None, compressMode=None):
        """
        Constructor for the ``FSFSRepository`` class.
        """
        super(FSFSRepository, self).__init__("FSFS", repositoryPath, collectMode, compressMode)

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "FSFSRepository(%s, %s, %s)" % (self.repositoryPath, self.collectMode, self.compressMode)


def backupBDBRepository(repositoryPath, backupFile, startRevision=None, endRevision=None):
    """
    Backs up an individual Subversion BDB repository.
    This function is deprecated.  Use :any:`backupRepository` instead.
    """
    return backupRepository(repositoryPath, backupFile, startRevision, endRevision)


def backupFSFSRepository(repositoryPath, backupFile, startRevision=None, endRevision=None):
    """
    Backs up an individual Subversion FSFS repository.
    This function is deprecated.  Use :any:`backupRepository` instead.
    """
    return backupRepository(repositoryPath, backupFile, startRevision, endRevision)
