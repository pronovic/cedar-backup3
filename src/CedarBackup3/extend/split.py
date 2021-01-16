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
# Copyright (c) 2007,2010,2013,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides an extension to split up large files in staging directories.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to split up large files in staging directories.

When this extension is executed, it will look through the configured Cedar
Backup staging directory for files exceeding a specified size limit, and split
them down into smaller files using the 'split' utility.  Any directory which
has already been split (as indicated by the ``cback.split`` file) will be
ignored.

This extension requires a new configuration section <split> and is intended
to be run immediately after the standard stage action or immediately before the
standard store action.  Aside from its own configuration, it requires the
options and staging configuration sections in the standard Cedar Backup
configuration file.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
import re
from functools import total_ordering

from CedarBackup3.actions.util import findDailyDirs, getBackupFiles, writeIndicatorFile
from CedarBackup3.config import ByteQuantity, addByteQuantityNode, readByteQuantity
from CedarBackup3.util import changeOwnership, executeCommand, resolveCommand
from CedarBackup3.xmlutil import addContainerNode, createInputDom, readFirstChild

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.split")

SPLIT_COMMAND = ["split"]
SPLIT_INDICATOR = "cback.split"


########################################################################
# SplitConfig class definition
########################################################################


@total_ordering
class SplitConfig(object):

    """
    Class representing split configuration.

    Split configuration is used for splitting staging directories.

    The following restrictions exist on data in this class:

       - The size limit must be a ByteQuantity
       - The split size must be a ByteQuantity

    """

    def __init__(self, sizeLimit=None, splitSize=None):
        """
        Constructor for the ``SplitCOnfig`` class.

        Args:
           sizeLimit: Size limit of the files, in bytes
           splitSize: Size that files exceeding the limit will be split into, in bytes

        Raises:
           ValueError: If one of the values is invalid
        """
        self._sizeLimit = None
        self._splitSize = None
        self.sizeLimit = sizeLimit
        self.splitSize = splitSize

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "SplitConfig(%s, %s)" % (self.sizeLimit, self.splitSize)

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
        if self.sizeLimit != other.sizeLimit:
            if (self.sizeLimit or ByteQuantity()) < (other.sizeLimit or ByteQuantity()):
                return -1
            else:
                return 1
        if self.splitSize != other.splitSize:
            if (self.splitSize or ByteQuantity()) < (other.splitSize or ByteQuantity()):
                return -1
            else:
                return 1
        return 0

    def _setSizeLimit(self, value):
        """
        Property target used to set the size limit.
        If not ``None``, the value must be a ``ByteQuantity`` object.
        Raises:
           ValueError: If the value is not a ``ByteQuantity``
        """
        if value is None:
            self._sizeLimit = None
        else:
            if not isinstance(value, ByteQuantity):
                raise ValueError("Value must be a ``ByteQuantity`` object.")
            self._sizeLimit = value

    def _getSizeLimit(self):
        """
        Property target used to get the size limit.
        """
        return self._sizeLimit

    def _setSplitSize(self, value):
        """
        Property target used to set the split size.
        If not ``None``, the value must be a ``ByteQuantity`` object.
        Raises:
           ValueError: If the value is not a ``ByteQuantity``
        """
        if value is None:
            self._splitSize = None
        else:
            if not isinstance(value, ByteQuantity):
                raise ValueError("Value must be a ``ByteQuantity`` object.")
            self._splitSize = value

    def _getSplitSize(self):
        """
        Property target used to get the split size.
        """
        return self._splitSize

    sizeLimit = property(_getSizeLimit, _setSizeLimit, None, doc="Size limit, as a ByteQuantity")
    splitSize = property(_getSplitSize, _setSplitSize, None, doc="Split size, as a ByteQuantity")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    split-specific configuration values.  Third parties who need to read and
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
        self._split = None
        self.split = None
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
        return "LocalConfig(%s)" % (self.split)

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
        if self.split != other.split:
            if self.split < other.split:
                return -1
            else:
                return 1
        return 0

    def _setSplit(self, value):
        """
        Property target used to set the split configuration value.
        If not ``None``, the value must be a ``SplitConfig`` object.
        Raises:
           ValueError: If the value is not a ``SplitConfig``
        """
        if value is None:
            self._split = None
        else:
            if not isinstance(value, SplitConfig):
                raise ValueError("Value must be a ``SplitConfig`` object.")
            self._split = value

    def _getSplit(self):
        """
        Property target used to get the split configuration value.
        """
        return self._split

    split = property(_getSplit, _setSplit, None, "Split configuration in terms of a ``SplitConfig`` object.")

    def validate(self):
        """
        Validates configuration represented by the object.

        Split configuration must be filled in.  Within that, both the size limit
        and split size must be filled in.

        Raises:
           ValueError: If one of the validations fails
        """
        if self.split is None:
            raise ValueError("Split section is required.")
        if self.split.sizeLimit is None:
            raise ValueError("Size limit must be set.")
        if self.split.splitSize is None:
            raise ValueError("Split size must be set.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds a <split> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           sizeLimit      //cb_config/split/size_limit
           splitSize      //cb_config/split/split_size

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.split is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "split")
            addByteQuantityNode(xmlDom, sectionNode, "size_limit", self.split.sizeLimit)
            addByteQuantityNode(xmlDom, sectionNode, "split_size", self.split.splitSize)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the split configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._split = LocalConfig._parseSplit(parentNode)

    @staticmethod
    def _parseSplit(parent):
        """
        Parses an split configuration section.

        We read the following individual fields::

           sizeLimit      //cb_config/split/size_limit
           splitSize      //cb_config/split/split_size

        Args:
           parent: Parent node to search beneath

        Returns:
            ``EncryptConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        split = None
        section = readFirstChild(parent, "split")
        if section is not None:
            split = SplitConfig()
            split.sizeLimit = readByteQuantity(section, "size_limit")
            split.splitSize = readByteQuantity(section, "split_size")
        return split


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################

# pylint: disable=W0613
def executeAction(configPath, options, config):
    """
    Executes the split backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If there are I/O problems reading or writing files
    """
    logger.debug("Executing split extended action.")
    if config.options is None or config.stage is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    dailyDirs = findDailyDirs(config.stage.targetDir, SPLIT_INDICATOR)
    for dailyDir in dailyDirs:
        _splitDailyDir(
            dailyDir, local.split.sizeLimit, local.split.splitSize, config.options.backupUser, config.options.backupGroup
        )
        writeIndicatorFile(dailyDir, SPLIT_INDICATOR, config.options.backupUser, config.options.backupGroup)
    logger.info("Executed the split extended action successfully.")


##############################
# _splitDailyDir() function
##############################


def _splitDailyDir(dailyDir, sizeLimit, splitSize, backupUser, backupGroup):
    """
    Splits large files in a daily staging directory.

    Files that match INDICATOR_PATTERNS (i.e. ``"cback.store"``,
    ``"cback.stage"``, etc.) are assumed to be indicator files and are ignored.
    All other files are split.

    Args:
       dailyDir: Daily directory to encrypt
       sizeLimit: Size limit, in bytes
       splitSize: Split size, in bytes
       backupUser: User that target files should be owned by
       backupGroup: Group that target files should be owned by

    Raises:
       ValueError: If the encrypt mode is not supported
       ValueError: If the daily staging directory does not exist
    """
    logger.debug("Begin splitting contents of [%s].", dailyDir)
    fileList = getBackupFiles(dailyDir)  # ignores indicator files
    for path in fileList:
        size = float(os.stat(path).st_size)
        if size > sizeLimit:
            _splitFile(path, splitSize, backupUser, backupGroup, removeSource=True)
    logger.debug("Completed splitting contents of [%s].", dailyDir)


########################
# _splitFile() function
########################


def _splitFile(sourcePath, splitSize, backupUser, backupGroup, removeSource=False):
    """
    Splits the source file into chunks of the indicated size.

    The split files will be owned by the indicated backup user and group.  If
    ``removeSource`` is ``True``, then the source file will be removed after it is
    successfully split.

    Args:
       sourcePath: Absolute path of the source file to split
       splitSize: Encryption mode (only "gpg" is allowed)
       backupUser: User that target files should be owned by
       backupGroup: Group that target files should be owned by
       removeSource: Indicates whether to remove the source file

    Raises:
       IOError: If there is a problem accessing, splitting or removing the source file
    """
    cwd = os.getcwd()
    try:
        if not os.path.exists(sourcePath):
            raise ValueError("Source path [%s] does not exist." % sourcePath)
        dirname = os.path.dirname(sourcePath)
        filename = os.path.basename(sourcePath)
        prefix = "%s_" % filename
        bytes = int(splitSize.bytes)  # pylint: disable=W0622
        os.chdir(dirname)  # need to operate from directory that we want files written to
        command = resolveCommand(SPLIT_COMMAND)
        args = ["--verbose", "--numeric-suffixes", "--suffix-length=5", "--bytes=%d" % bytes, filename, prefix]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=False)
        if result != 0:
            raise IOError("Error [%d] calling split for [%s]." % (result, sourcePath))
        pattern = re.compile(r"(creating file [`'])(%s)(.*)(')" % prefix)
        match = pattern.search(output[-1:][0])
        if match is None:
            raise IOError("Unable to parse output from split command.")
        value = int(match.group(3).strip())
        for index in range(0, value):
            path = "%s%05d" % (prefix, index)
            if not os.path.exists(path):
                raise IOError("After call to split, expected file [%s] does not exist." % path)
            changeOwnership(path, backupUser, backupGroup)
        if removeSource:
            if os.path.exists(sourcePath):
                try:
                    os.remove(sourcePath)
                    logger.debug("Completed removing old file [%s].", sourcePath)
                except:
                    raise IOError("Failed to remove file [%s] after splitting it." % (sourcePath))
    finally:
        os.chdir(cwd)
