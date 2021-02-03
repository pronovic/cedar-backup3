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
# Copyright (c) 2006-2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides an extension to back up mbox email files.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to back up mbox email files.

Backing up email
================

   Email folders (often stored as mbox flatfiles) are not well-suited being backed
   up with an incremental backup like the one offered by Cedar Backup.  This is
   because mbox files often change on a daily basis, forcing the incremental
   backup process to back them up every day in order to avoid losing data.  This
   can result in quite a bit of wasted space when backing up large folders.  (Note
   that the alternative maildir format does not share this problem, since it
   typically uses one file per message.)

   One solution to this problem is to design a smarter incremental backup process,
   which backs up baseline content on the first day of the week, and then backs up
   only new messages added to that folder on every other day of the week.  This way,
   the backup for any single day is only as large as the messages placed into the
   folder on that day.  The backup isn't as "perfect" as the incremental backup
   process, because it doesn't preserve information about messages deleted from
   the backed-up folder.  However, it should be much more space-efficient, and
   in a recovery situation, it seems better to restore too much data rather
   than too little.

What is this extension?
=======================

   This is a Cedar Backup extension used to back up mbox email files via the Cedar
   Backup command line.  Individual mbox files or directories containing mbox
   files can be backed up using the same collect modes allowed for filesystems in
   the standard Cedar Backup collect action: weekly, daily, incremental.  It
   implements the "smart" incremental backup process discussed above, using
   functionality provided by the ``grepmail`` utility.

   This extension requires a new configuration section <mbox> and is intended to
   be run either immediately before or immediately after the standard collect
   action.  Aside from its own configuration, it requires the options and collect
   configuration sections in the standard Cedar Backup configuration file.

   The mbox action is conceptually similar to the standard collect action,
   except that mbox directories are not collected recursively.  This implies
   some configuration changes (i.e. there's no need for global exclusions or an
   ignore file).  If you back up a directory, all of the mbox files in that
   directory are backed up into a single tar file using the indicated
   compression method.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import datetime
import logging
import os
import pickle
import tempfile
from bz2 import BZ2File
from functools import total_ordering
from gzip import GzipFile

from CedarBackup3.config import VALID_COLLECT_MODES, VALID_COMPRESS_MODES
from CedarBackup3.filesystem import BackupFileList, FilesystemList
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

logger = logging.getLogger("CedarBackup3.log.extend.mbox")

GREPMAIL_COMMAND = ["grepmail"]
REVISION_PATH_EXTENSION = "mboxlast"


########################################################################
# MboxFile class definition
########################################################################


@total_ordering
class MboxFile(object):

    """
    Class representing mbox file configuration..

    The following restrictions exist on data in this class:

       - The absolute path must be absolute.
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.

    """

    def __init__(self, absolutePath=None, collectMode=None, compressMode=None):
        """
        Constructor for the ``MboxFile`` class.

        You should never directly instantiate this class.

        Args:
           absolutePath: Absolute path to an mbox file on disk
           collectMode: Overridden collect mode for this directory
           compressMode: Overridden compression mode for this directory
        """
        self._absolutePath = None
        self._collectMode = None
        self._compressMode = None
        self.absolutePath = absolutePath
        self.collectMode = collectMode
        self.compressMode = compressMode

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "MboxFile(%s, %s, %s)" % (self.absolutePath, self.collectMode, self.compressMode)

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
        if self.absolutePath != other.absolutePath:
            if str(self.absolutePath or "") < str(other.absolutePath or ""):
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

    def _setAbsolutePath(self, value):
        """
        Property target used to set the absolute path.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Absolute path must be, er, an absolute path.")
        self._absolutePath = encodePath(value)

    def _getAbsolutePath(self):
        """
        Property target used to get the absolute path.
        """
        return self._absolutePath

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

    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, doc="Absolute path to the mbox file.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this mbox file.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Overridden compress mode for this mbox file.")


########################################################################
# MboxDir class definition
########################################################################


@total_ordering
class MboxDir(object):

    """
    Class representing mbox directory configuration..

    The following restrictions exist on data in this class:

       - The absolute path must be absolute.
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.

    Unlike collect directory configuration, this is the only place exclusions
    are allowed (no global exclusions at the <mbox> configuration level).  Also,
    we only allow relative exclusions and there is no configured ignore file.
    This is because mbox directory backups are not recursive.

    """

    def __init__(self, absolutePath=None, collectMode=None, compressMode=None, relativeExcludePaths=None, excludePatterns=None):
        """
        Constructor for the ``MboxDir`` class.

        You should never directly instantiate this class.

        Args:
           absolutePath: Absolute path to a mbox file on disk
           collectMode: Overridden collect mode for this directory
           compressMode: Overridden compression mode for this directory
           relativeExcludePaths: List of relative paths to exclude
           excludePatterns: List of regular expression patterns to exclude
        """
        self._absolutePath = None
        self._collectMode = None
        self._compressMode = None
        self._relativeExcludePaths = None
        self._excludePatterns = None
        self.absolutePath = absolutePath
        self.collectMode = collectMode
        self.compressMode = compressMode
        self.relativeExcludePaths = relativeExcludePaths
        self.excludePatterns = excludePatterns

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "MboxDir(%s, %s, %s, %s, %s)" % (
            self.absolutePath,
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
        if self.absolutePath != other.absolutePath:
            if str(self.absolutePath or "") < str(other.absolutePath or ""):
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

    def _setAbsolutePath(self, value):
        """
        Property target used to set the absolute path.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Absolute path must be, er, an absolute path.")
        self._absolutePath = encodePath(value)

    def _getAbsolutePath(self):
        """
        Property target used to get the absolute path.
        """
        return self._absolutePath

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

    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, doc="Absolute path to the mbox directory.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this mbox directory.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Overridden compress mode for this mbox directory.")
    relativeExcludePaths = property(_getRelativeExcludePaths, _setRelativeExcludePaths, None, "List of relative paths to exclude.")
    excludePatterns = property(_getExcludePatterns, _setExcludePatterns, None, "List of regular expression patterns to exclude.")


########################################################################
# MboxConfig class definition
########################################################################


@total_ordering
class MboxConfig(object):

    """
    Class representing mbox configuration.

    Mbox configuration is used for backing up mbox email files.

    The following restrictions exist on data in this class:

       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
       - The ``mboxFiles`` list must be a list of ``MboxFile`` objects
       - The ``mboxDirs`` list must be a list of ``MboxDir`` objects

    For the ``mboxFiles`` and ``mboxDirs`` lists, validation is accomplished
    through the :any:`util.ObjectTypeList` list implementation that overrides common
    list methods and transparently ensures that each element is of the proper
    type.

    Unlike collect configuration, no global exclusions are allowed on this
    level.  We only allow relative exclusions at the mbox directory level.
    Also, there is no configured ignore file.  This is because mbox directory
    backups are not recursive.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, collectMode=None, compressMode=None, mboxFiles=None, mboxDirs=None):
        """
        Constructor for the ``MboxConfig`` class.

        Args:
           collectMode: Default collect mode
           compressMode: Default compress mode
           mboxFiles: List of mbox files to back up
           mboxDirs: List of mbox directories to back up

        Raises:
           ValueError: If one of the values is invalid
        """
        self._collectMode = None
        self._compressMode = None
        self._mboxFiles = None
        self._mboxDirs = None
        self.collectMode = collectMode
        self.compressMode = compressMode
        self.mboxFiles = mboxFiles
        self.mboxDirs = mboxDirs

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "MboxConfig(%s, %s, %s, %s)" % (self.collectMode, self.compressMode, self.mboxFiles, self.mboxDirs)

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
        if self.mboxFiles != other.mboxFiles:
            if self.mboxFiles < other.mboxFiles:
                return -1
            else:
                return 1
        if self.mboxDirs != other.mboxDirs:
            if self.mboxDirs < other.mboxDirs:
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

    def _setMboxFiles(self, value):
        """
        Property target used to set the mboxFiles list.
        Either the value must be ``None`` or each element must be an ``MboxFile``.
        Raises:
           ValueError: If the value is not an ``MboxFile``
        """
        if value is None:
            self._mboxFiles = None
        else:
            try:
                saved = self._mboxFiles
                self._mboxFiles = ObjectTypeList(MboxFile, "MboxFile")
                self._mboxFiles.extend(value)
            except Exception as e:
                self._mboxFiles = saved
                raise e

    def _getMboxFiles(self):
        """
        Property target used to get the mboxFiles list.
        """
        return self._mboxFiles

    def _setMboxDirs(self, value):
        """
        Property target used to set the mboxDirs list.
        Either the value must be ``None`` or each element must be an ``MboxDir``.
        Raises:
           ValueError: If the value is not an ``MboxDir``
        """
        if value is None:
            self._mboxDirs = None
        else:
            try:
                saved = self._mboxDirs
                self._mboxDirs = ObjectTypeList(MboxDir, "MboxDir")
                self._mboxDirs.extend(value)
            except Exception as e:
                self._mboxDirs = saved
                raise e

    def _getMboxDirs(self):
        """
        Property target used to get the mboxDirs list.
        """
        return self._mboxDirs

    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Default collect mode.")
    compressMode = property(_getCompressMode, _setCompressMode, None, doc="Default compress mode.")
    mboxFiles = property(_getMboxFiles, _setMboxFiles, None, doc="List of mbox files to back up.")
    mboxDirs = property(_getMboxDirs, _setMboxDirs, None, doc="List of mbox directories to back up.")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    Mbox-specific configuration values.  Third parties who need to read and
    write configuration related to this extension should access it through the
    constructor, ``validate`` and ``addConfig`` methods.

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
        self._mbox = None
        self.mbox = None
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
        return "LocalConfig(%s)" % (self.mbox)

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
        if self.mbox != other.mbox:
            if self.mbox < other.mbox:
                return -1
            else:
                return 1
        return 0

    def _setMbox(self, value):
        """
        Property target used to set the mbox configuration value.
        If not ``None``, the value must be a ``MboxConfig`` object.
        Raises:
           ValueError: If the value is not a ``MboxConfig``
        """
        if value is None:
            self._mbox = None
        else:
            if not isinstance(value, MboxConfig):
                raise ValueError("Value must be a ``MboxConfig`` object.")
            self._mbox = value

    def _getMbox(self):
        """
        Property target used to get the mbox configuration value.
        """
        return self._mbox

    mbox = property(_getMbox, _setMbox, None, "Mbox configuration in terms of a ``MboxConfig`` object.")

    def validate(self):
        """
        Validates configuration represented by the object.

        Mbox configuration must be filled in.  Within that, the collect mode and
        compress mode are both optional, but the list of repositories must
        contain at least one entry.

        Each configured file or directory must contain an absolute path, and then
        must be either able to take collect mode and compress mode configuration
        from the parent ``MboxConfig`` object, or must set each value on its own.

        Raises:
           ValueError: If one of the validations fails
        """
        if self.mbox is None:
            raise ValueError("Mbox section is required.")
        if (self.mbox.mboxFiles is None or len(self.mbox.mboxFiles) < 1) and (
            self.mbox.mboxDirs is None or len(self.mbox.mboxDirs) < 1
        ):
            raise ValueError("At least one mbox file or directory must be configured.")
        if self.mbox.mboxFiles is not None:
            for mboxFile in self.mbox.mboxFiles:
                if mboxFile.absolutePath is None:
                    raise ValueError("Each mbox file must set an absolute path.")
                if self.mbox.collectMode is None and mboxFile.collectMode is None:
                    raise ValueError("Collect mode must either be set in parent mbox section or individual mbox file.")
                if self.mbox.compressMode is None and mboxFile.compressMode is None:
                    raise ValueError("Compress mode must either be set in parent mbox section or individual mbox file.")
        if self.mbox.mboxDirs is not None:
            for mboxDir in self.mbox.mboxDirs:
                if mboxDir.absolutePath is None:
                    raise ValueError("Each mbox directory must set an absolute path.")
                if self.mbox.collectMode is None and mboxDir.collectMode is None:
                    raise ValueError("Collect mode must either be set in parent mbox section or individual mbox directory.")
                if self.mbox.compressMode is None and mboxDir.compressMode is None:
                    raise ValueError("Compress mode must either be set in parent mbox section or individual mbox directory.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds an <mbox> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           collectMode    //cb_config/mbox/collectMode
           compressMode   //cb_config/mbox/compressMode

        We also add groups of the following items, one list element per
        item::

           mboxFiles      //cb_config/mbox/file
           mboxDirs       //cb_config/mbox/dir

        The mbox files and mbox directories are added by ``_addMboxFile`` and
        ``_addMboxDir``.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.mbox is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "mbox")
            addStringNode(xmlDom, sectionNode, "collect_mode", self.mbox.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", self.mbox.compressMode)
            if self.mbox.mboxFiles is not None:
                for mboxFile in self.mbox.mboxFiles:
                    LocalConfig._addMboxFile(xmlDom, sectionNode, mboxFile)
            if self.mbox.mboxDirs is not None:
                for mboxDir in self.mbox.mboxDirs:
                    LocalConfig._addMboxDir(xmlDom, sectionNode, mboxDir)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the mbox configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._mbox = LocalConfig._parseMbox(parentNode)

    @staticmethod
    def _parseMbox(parent):
        """
        Parses an mbox configuration section.

        We read the following individual fields::

           collectMode    //cb_config/mbox/collect_mode
           compressMode   //cb_config/mbox/compress_mode

        We also read groups of the following item, one list element per
        item::

           mboxFiles      //cb_config/mbox/file
           mboxDirs       //cb_config/mbox/dir

        The mbox files are parsed by :any:`_parseMboxFiles` and the mbox
        directories are parsed by :any:`_parseMboxDirs`.

        Args:
           parent: Parent node to search beneath

        Returns:
            ``MboxConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        mbox = None
        section = readFirstChild(parent, "mbox")
        if section is not None:
            mbox = MboxConfig()
            mbox.collectMode = readString(section, "collect_mode")
            mbox.compressMode = readString(section, "compress_mode")
            mbox.mboxFiles = LocalConfig._parseMboxFiles(section)
            mbox.mboxDirs = LocalConfig._parseMboxDirs(section)
        return mbox

    @staticmethod
    def _parseMboxFiles(parent):
        """
        Reads a list of ``MboxFile`` objects from immediately beneath the parent.

        We read the following individual fields::

           absolutePath            abs_path
           collectMode             collect_mode
           compressMode            compess_mode

        Args:
           parent: Parent node to search beneath

        Returns:
            List of ``MboxFile`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parent, "file"):
            if isElement(entry):
                mboxFile = MboxFile()
                mboxFile.absolutePath = readString(entry, "abs_path")
                mboxFile.collectMode = readString(entry, "collect_mode")
                mboxFile.compressMode = readString(entry, "compress_mode")
                lst.append(mboxFile)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseMboxDirs(parent):
        """
        Reads a list of ``MboxDir`` objects from immediately beneath the parent.

        We read the following individual fields::

           absolutePath            abs_path
           collectMode             collect_mode
           compressMode            compess_mode

        We also read groups of the following items, one list element per
        item::

           relativeExcludePaths    exclude/rel_path
           excludePatterns         exclude/pattern

        The exclusions are parsed by :any:`_parseExclusions`.

        Args:
           parent: Parent node to search beneath

        Returns:
            List of ``MboxDir`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parent, "dir"):
            if isElement(entry):
                mboxDir = MboxDir()
                mboxDir.absolutePath = readString(entry, "abs_path")
                mboxDir.collectMode = readString(entry, "collect_mode")
                mboxDir.compressMode = readString(entry, "compress_mode")
                (mboxDir.relativeExcludePaths, mboxDir.excludePatterns) = LocalConfig._parseExclusions(entry)
                lst.append(mboxDir)
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
    def _addMboxFile(xmlDom, parentNode, mboxFile):
        """
        Adds an mbox file container as the next child of a parent.

        We add the following fields to the document::

           absolutePath            file/abs_path
           collectMode             file/collect_mode
           compressMode            file/compress_mode

        The <file> node itself is created as the next child of the parent node.
        This method only adds one mbox file node.  The parent must loop for each
        mbox file in the ``MboxConfig`` object.

        If ``mboxFile`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
           mboxFile: MboxFile to be added to the document
        """
        if mboxFile is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "file")
            addStringNode(xmlDom, sectionNode, "abs_path", mboxFile.absolutePath)
            addStringNode(xmlDom, sectionNode, "collect_mode", mboxFile.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", mboxFile.compressMode)

    @staticmethod
    def _addMboxDir(xmlDom, parentNode, mboxDir):
        """
        Adds an mbox directory container as the next child of a parent.

        We add the following fields to the document::

           absolutePath            dir/abs_path
           collectMode             dir/collect_mode
           compressMode            dir/compress_mode

        We also add groups of the following items, one list element per item::

           relativeExcludePaths    dir/exclude/rel_path
           excludePatterns         dir/exclude/pattern

        The <dir> node itself is created as the next child of the parent node.
        This method only adds one mbox directory node.  The parent must loop for
        each mbox directory in the ``MboxConfig`` object.

        If ``mboxDir`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
           mboxDir: MboxDir to be added to the document
        """
        if mboxDir is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "dir")
            addStringNode(xmlDom, sectionNode, "abs_path", mboxDir.absolutePath)
            addStringNode(xmlDom, sectionNode, "collect_mode", mboxDir.collectMode)
            addStringNode(xmlDom, sectionNode, "compress_mode", mboxDir.compressMode)
            if (mboxDir.relativeExcludePaths is not None and mboxDir.relativeExcludePaths != []) or (
                mboxDir.excludePatterns is not None and mboxDir.excludePatterns != []
            ):
                excludeNode = addContainerNode(xmlDom, sectionNode, "exclude")
                if mboxDir.relativeExcludePaths is not None:
                    for relativePath in mboxDir.relativeExcludePaths:
                        addStringNode(xmlDom, excludeNode, "rel_path", relativePath)
                if mboxDir.excludePatterns is not None:
                    for pattern in mboxDir.excludePatterns:
                        addStringNode(xmlDom, excludeNode, "pattern", pattern)


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################


def executeAction(configPath, options, config):
    """
    Executes the mbox backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If a backup could not be written for some reason
    """
    logger.debug("Executing mbox extended action.")
    newRevision = datetime.datetime.today()  # mark here so all actions are after this date/time
    if config.options is None or config.collect is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    todayIsStart = isStartOfWeek(config.options.startingDay)
    fullBackup = options.full or todayIsStart
    logger.debug("Full backup flag is [%s]", fullBackup)
    if local.mbox.mboxFiles is not None:
        for mboxFile in local.mbox.mboxFiles:
            logger.debug("Working with mbox file [%s]", mboxFile.absolutePath)
            collectMode = _getCollectMode(local, mboxFile)
            compressMode = _getCompressMode(local, mboxFile)
            lastRevision = _loadLastRevision(config, mboxFile, fullBackup, collectMode)
            if fullBackup or (collectMode in ["daily", "incr"]) or (collectMode == "weekly" and todayIsStart):
                logger.debug("Mbox file meets criteria to be backed up today.")
                _backupMboxFile(config, mboxFile.absolutePath, fullBackup, collectMode, compressMode, lastRevision, newRevision)
            else:
                logger.debug("Mbox file will not be backed up, per collect mode.")
            if collectMode == "incr":
                _writeNewRevision(config, mboxFile, newRevision)
    if local.mbox.mboxDirs is not None:
        for mboxDir in local.mbox.mboxDirs:
            logger.debug("Working with mbox directory [%s]", mboxDir.absolutePath)
            collectMode = _getCollectMode(local, mboxDir)
            compressMode = _getCompressMode(local, mboxDir)
            lastRevision = _loadLastRevision(config, mboxDir, fullBackup, collectMode)
            (excludePaths, excludePatterns) = _getExclusions(mboxDir)
            if fullBackup or (collectMode in ["daily", "incr"]) or (collectMode == "weekly" and todayIsStart):
                logger.debug("Mbox directory meets criteria to be backed up today.")
                _backupMboxDir(
                    config,
                    mboxDir.absolutePath,
                    fullBackup,
                    collectMode,
                    compressMode,
                    lastRevision,
                    newRevision,
                    excludePaths,
                    excludePatterns,
                )
            else:
                logger.debug("Mbox directory will not be backed up, per collect mode.")
            if collectMode == "incr":
                _writeNewRevision(config, mboxDir, newRevision)
    logger.info("Executed the mbox extended action successfully.")


def _getCollectMode(local, item):
    """
    Gets the collect mode that should be used for an mbox file or directory.
    Use file- or directory-specific value if possible, otherwise take from mbox section.
    Args:
       local: LocalConfig object
       item: Mbox file or directory
    Returns:
        Collect mode to use
    """
    if item.collectMode is None:
        collectMode = local.mbox.collectMode
    else:
        collectMode = item.collectMode
    logger.debug("Collect mode is [%s]", collectMode)
    return collectMode


def _getCompressMode(local, item):
    """
    Gets the compress mode that should be used for an mbox file or directory.
    Use file- or directory-specific value if possible, otherwise take from mbox section.
    Args:
       local: LocalConfig object
       item: Mbox file or directory
    Returns:
        Compress mode to use
    """
    if item.compressMode is None:
        compressMode = local.mbox.compressMode
    else:
        compressMode = item.compressMode
    logger.debug("Compress mode is [%s]", compressMode)
    return compressMode


def _getRevisionPath(config, item):
    """
    Gets the path to the revision file associated with a repository.
    Args:
       config: Cedar Backup configuration
       item: Mbox file or directory
    Returns:
        Absolute path to the revision file associated with the repository
    """
    normalized = buildNormalizedPath(item.absolutePath)
    filename = "%s.%s" % (normalized, REVISION_PATH_EXTENSION)
    revisionPath = pathJoin(config.options.workingDir, filename)
    logger.debug("Revision file path is [%s]", revisionPath)
    return revisionPath


def _loadLastRevision(config, item, fullBackup, collectMode):
    """
    Loads the last revision date for this item from disk and returns it.

    If this is a full backup, or if the revision file cannot be loaded for some
    reason, then ``None`` is returned.  This indicates that there is no previous
    revision, so the entire mail file or directory should be backed up.

    *Note:* We write the actual revision object to disk via pickle, so we don't
    deal with the datetime precision or format at all.  Whatever's in the object
    is what we write.

    Args:
       config: Cedar Backup configuration
       item: Mbox file or directory
       fullBackup: Indicates whether this is a full backup
       collectMode: Indicates the collect mode for this item

    Returns:
        Revision date as a datetime.datetime object or ``None``
    """
    revisionPath = _getRevisionPath(config, item)
    if fullBackup:
        revisionDate = None
        logger.debug("Revision file ignored because this is a full backup.")
    elif collectMode in ["weekly", "daily"]:
        revisionDate = None
        logger.debug("No revision file based on collect mode [%s].", collectMode)
    else:
        logger.debug("Revision file will be used for non-full incremental backup.")
        if not os.path.isfile(revisionPath):
            revisionDate = None
            logger.debug("Revision file [%s] does not exist on disk.", revisionPath)
        else:
            try:
                with open(revisionPath, "rb") as f:
                    revisionDate = pickle.load(f, fix_imports=True)  # be compatible with Python 2
                logger.debug("Loaded revision file [%s] from disk: [%s]", revisionPath, revisionDate)
            except Exception as e:
                revisionDate = None
                logger.error("Failed loading revision file [%s] from disk: %s", revisionPath, e)
    return revisionDate


def _writeNewRevision(config, item, newRevision):
    """
    Writes new revision information to disk.

    If we can't write the revision file successfully for any reason, we'll log
    the condition but won't throw an exception.

    *Note:* We write the actual revision object to disk via pickle, so we don't
    deal with the datetime precision or format at all.  Whatever's in the object
    is what we write.

    Args:
       config: Cedar Backup configuration
       item: Mbox file or directory
       newRevision: Revision date as a datetime.datetime object
    """
    revisionPath = _getRevisionPath(config, item)
    try:
        with open(revisionPath, "wb") as f:
            pickle.dump(newRevision, f, 0, fix_imports=True)  # be compatible with Python 2
        changeOwnership(revisionPath, config.options.backupUser, config.options.backupGroup)
        logger.debug("Wrote new revision file [%s] to disk: [%s]", revisionPath, newRevision)
    except Exception as e:
        logger.error("Failed to write revision file [%s] to disk: %s", revisionPath, e)


def _getExclusions(mboxDir):
    """
    Gets exclusions (file and patterns) associated with an mbox directory.

    The returned files value is a list of absolute paths to be excluded from the
    backup for a given directory.  It is derived from the mbox directory's
    relative exclude paths.

    The returned patterns value is a list of patterns to be excluded from the
    backup for a given directory.  It is derived from the mbox directory's list
    of patterns.

    Args:
       mboxDir: Mbox directory object

    Returns:
        Tuple (files, patterns) indicating what to exclude
    """
    paths = []
    if mboxDir.relativeExcludePaths is not None:
        for relativePath in mboxDir.relativeExcludePaths:
            paths.append(pathJoin(mboxDir.absolutePath, relativePath))
    patterns = []
    if mboxDir.excludePatterns is not None:
        patterns.extend(mboxDir.excludePatterns)
    logger.debug("Exclude paths: %s", paths)
    logger.debug("Exclude patterns: %s", patterns)
    return (paths, patterns)


def _getBackupPath(config, mboxPath, compressMode, newRevision, targetDir=None):
    """
    Gets the backup file path (including correct extension) associated with an mbox path.

    We assume that if the target directory is passed in, that we're backing up a
    directory.  Under these circumstances, we'll just use the basename of the
    individual path as the output file.

    *Note:* The backup path only contains the current date in YYYYMMDD format,
    but that's OK because the index information (stored elsewhere) is the actual
    date object.

    Args:
       config: Cedar Backup configuration
       mboxPath: Path to the indicated mbox file or directory
       compressMode: Compress mode to use for this mbox path
       newRevision: Revision this backup path represents
       targetDir: Target directory in which the path should exist

    Returns:
        Absolute path to the backup file associated with the repository
    """
    if targetDir is None:
        normalizedPath = buildNormalizedPath(mboxPath)
        revisionDate = newRevision.strftime("%Y%m%d")
        filename = "mbox-%s-%s" % (revisionDate, normalizedPath)
    else:
        filename = os.path.basename(mboxPath)
    if compressMode == "gzip":
        filename = "%s.gz" % filename
    elif compressMode == "bzip2":
        filename = "%s.bz2" % filename
    if targetDir is None:
        backupPath = pathJoin(config.collect.targetDir, filename)
    else:
        backupPath = pathJoin(targetDir, filename)
    logger.debug("Backup file path is [%s]", backupPath)
    return backupPath


def _getTarfilePath(config, mboxPath, compressMode, newRevision):
    """
    Gets the tarfile backup file path (including correct extension) associated
    with an mbox path.

    Along with the path, the tar archive mode is returned in a form that can
    be used with :any:`BackupFileList.generateTarfile`.

    *Note:* The tarfile path only contains the current date in YYYYMMDD format,
    but that's OK because the index information (stored elsewhere) is the actual
    date object.

    Args:
       config: Cedar Backup configuration
       mboxPath: Path to the indicated mbox file or directory
       compressMode: Compress mode to use for this mbox path
       newRevision: Revision this backup path represents

    Returns:
        Tuple of (absolute path to tarfile, tar archive mode)
    """
    normalizedPath = buildNormalizedPath(mboxPath)
    revisionDate = newRevision.strftime("%Y%m%d")
    filename = "mbox-%s-%s.tar" % (revisionDate, normalizedPath)
    if compressMode == "gzip":
        filename = "%s.gz" % filename
        archiveMode = "targz"
    elif compressMode == "bzip2":
        filename = "%s.bz2" % filename
        archiveMode = "tarbz2"
    else:
        archiveMode = "tar"
    tarfilePath = pathJoin(config.collect.targetDir, filename)
    logger.debug("Tarfile path is [%s]", tarfilePath)
    return (tarfilePath, archiveMode)


def _getOutputFile(backupPath, compressMode):
    """
    Opens the output file used for saving backup information.

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


def _backupMboxFile(config, absolutePath, fullBackup, collectMode, compressMode, lastRevision, newRevision, targetDir=None):
    """
    Backs up an individual mbox file.

    Args:
       config: Cedar Backup configuration
       absolutePath: Path to mbox file to back up
       fullBackup: Indicates whether this should be a full backup
       collectMode: Indicates the collect mode for this item
       compressMode: Compress mode of file ("none", "gzip", "bzip")
       lastRevision: Date of last backup as datetime.datetime
       newRevision: Date of new (current) backup as datetime.datetime
       targetDir: Target directory to write the backed-up file into

    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem backing up the mbox file
    """
    if fullBackup or collectMode != "incr" or lastRevision is None:
        args = ["-a", "-u", absolutePath]  # remove duplicates but fetch entire mailbox
    else:
        revisionDate = lastRevision.strftime("%Y-%m-%dT%H:%M:%S")  # ISO-8601 format; grepmail calls Date::Parse::str2time()
        args = ["-a", "-u", "-d", "since %s" % revisionDate, absolutePath]
    command = resolveCommand(GREPMAIL_COMMAND)
    backupPath = _getBackupPath(config, absolutePath, compressMode, newRevision, targetDir=targetDir)
    with _getOutputFile(backupPath, compressMode) as outputFile:
        result = executeCommand(command, args, returnOutput=False, ignoreStderr=True, doNotLog=True, outputFile=outputFile)[0]
        if result != 0:
            raise IOError("Error [%d] executing grepmail on [%s]." % (result, absolutePath))
    logger.debug("Completed backing up mailbox [%s].", absolutePath)
    return backupPath


def _backupMboxDir(
    config, absolutePath, fullBackup, collectMode, compressMode, lastRevision, newRevision, excludePaths, excludePatterns
):
    """
    Backs up a directory containing mbox files.

    Args:
       config: Cedar Backup configuration
       absolutePath: Path to mbox directory to back up
       fullBackup: Indicates whether this should be a full backup
       collectMode: Indicates the collect mode for this item
       compressMode: Compress mode of file ("none", "gzip", "bzip")
       lastRevision: Date of last backup as datetime.datetime
       newRevision: Date of new (current) backup as datetime.datetime
       excludePaths: List of absolute paths to exclude
       excludePatterns: List of patterns to exclude

    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem backing up the mbox file
    """
    try:
        tmpdir = tempfile.mkdtemp(dir=config.options.workingDir)
        mboxList = FilesystemList()
        mboxList.excludeDirs = True
        mboxList.excludePaths = excludePaths
        mboxList.excludePatterns = excludePatterns
        mboxList.addDirContents(absolutePath, recursive=False)
        tarList = BackupFileList()
        for item in mboxList:
            backupPath = _backupMboxFile(
                config,
                item,
                fullBackup,
                collectMode,
                "none",  # no need to compress inside compressed tar
                lastRevision,
                newRevision,
                targetDir=tmpdir,
            )
            tarList.addFile(backupPath)
        (tarfilePath, archiveMode) = _getTarfilePath(config, absolutePath, compressMode, newRevision)
        tarList.generateTarfile(tarfilePath, archiveMode, ignore=True, flat=True)
        changeOwnership(tarfilePath, config.options.backupUser, config.options.backupGroup)
        logger.debug("Completed backing up directory [%s].", absolutePath)
    finally:
        try:
            for cleanitem in tarList:
                if os.path.exists(cleanitem):
                    try:
                        os.remove(cleanitem)
                    except:
                        pass
        except:
            pass
        try:
            os.rmdir(tmpdir)
        except:
            pass
