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
# Project  : Official Cedar Backup Extensions
# Purpose  : Provides an extension to encrypt staging directories.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to encrypt staging directories.

When this extension is executed, all backed-up files in the configured Cedar
Backup staging directory will be encrypted using gpg.  Any directory which has
already been encrypted (as indicated by the ``cback.encrypt`` file) will be
ignored.

This extension requires a new configuration section <encrypt> and is intended
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
from functools import total_ordering

from CedarBackup3.actions.util import findDailyDirs, getBackupFiles, writeIndicatorFile
from CedarBackup3.util import changeOwnership, executeCommand, resolveCommand
from CedarBackup3.xmlutil import addContainerNode, addStringNode, createInputDom, readFirstChild, readString

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.encrypt")

GPG_COMMAND = [
    "gpg",
]
VALID_ENCRYPT_MODES = [
    "gpg",
]
ENCRYPT_INDICATOR = "cback.encrypt"


########################################################################
# EncryptConfig class definition
########################################################################


@total_ordering
class EncryptConfig(object):

    """
    Class representing encrypt configuration.

    Encrypt configuration is used for encrypting staging directories.

    The following restrictions exist on data in this class:

       - The encrypt mode must be one of the values in ``VALID_ENCRYPT_MODES``
       - The encrypt target value must be a non-empty string

    """

    def __init__(self, encryptMode=None, encryptTarget=None):
        """
        Constructor for the ``EncryptConfig`` class.

        Args:
           encryptMode: Encryption mode
           encryptTarget: Encryption target (for instance, GPG recipient)

        Raises:
           ValueError: If one of the values is invalid
        """
        self._encryptMode = None
        self._encryptTarget = None
        self.encryptMode = encryptMode
        self.encryptTarget = encryptTarget

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "EncryptConfig(%s, %s)" % (self.encryptMode, self.encryptTarget)

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
        if self.encryptMode != other.encryptMode:
            if str(self.encryptMode or "") < str(other.encryptMode or ""):
                return -1
            else:
                return 1
        if self.encryptTarget != other.encryptTarget:
            if str(self.encryptTarget or "") < str(other.encryptTarget or ""):
                return -1
            else:
                return 1
        return 0

    def _setEncryptMode(self, value):
        """
        Property target used to set the encrypt mode.
        If not ``None``, the mode must be one of the values in ``VALID_ENCRYPT_MODES``.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_ENCRYPT_MODES:
                raise ValueError("Encrypt mode must be one of %s." % VALID_ENCRYPT_MODES)
        self._encryptMode = value

    def _getEncryptMode(self):
        """
        Property target used to get the encrypt mode.
        """
        return self._encryptMode

    def _setEncryptTarget(self, value):
        """
        Property target used to set the encrypt target.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Encrypt target must be non-empty string.")
        self._encryptTarget = value

    def _getEncryptTarget(self):
        """
        Property target used to get the encrypt target.
        """
        return self._encryptTarget

    encryptMode = property(_getEncryptMode, _setEncryptMode, None, doc="Encrypt mode.")
    encryptTarget = property(_getEncryptTarget, _setEncryptTarget, None, doc="Encrypt target (i.e. GPG recipient).")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    encrypt-specific configuration values.  Third parties who need to read and
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
        self._encrypt = None
        self.encrypt = None
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
        return "LocalConfig(%s)" % (self.encrypt)

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
        if self.encrypt != other.encrypt:
            if self.encrypt < other.encrypt:
                return -1
            else:
                return 1
        return 0

    def _setEncrypt(self, value):
        """
        Property target used to set the encrypt configuration value.
        If not ``None``, the value must be a ``EncryptConfig`` object.
        Raises:
           ValueError: If the value is not a ``EncryptConfig``
        """
        if value is None:
            self._encrypt = None
        else:
            if not isinstance(value, EncryptConfig):
                raise ValueError("Value must be a ``EncryptConfig`` object.")
            self._encrypt = value

    def _getEncrypt(self):
        """
        Property target used to get the encrypt configuration value.
        """
        return self._encrypt

    encrypt = property(_getEncrypt, _setEncrypt, None, "Encrypt configuration in terms of a ``EncryptConfig`` object.")

    def validate(self):
        """
        Validates configuration represented by the object.

        Encrypt configuration must be filled in.  Within that, both the encrypt
        mode and encrypt target must be filled in.

        Raises:
           ValueError: If one of the validations fails
        """
        if self.encrypt is None:
            raise ValueError("Encrypt section is required.")
        if self.encrypt.encryptMode is None:
            raise ValueError("Encrypt mode must be set.")
        if self.encrypt.encryptTarget is None:
            raise ValueError("Encrypt target must be set.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds an <encrypt> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           encryptMode    //cb_config/encrypt/encrypt_mode
           encryptTarget  //cb_config/encrypt/encrypt_target

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.encrypt is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "encrypt")
            addStringNode(xmlDom, sectionNode, "encrypt_mode", self.encrypt.encryptMode)
            addStringNode(xmlDom, sectionNode, "encrypt_target", self.encrypt.encryptTarget)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the encrypt configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._encrypt = LocalConfig._parseEncrypt(parentNode)

    @staticmethod
    def _parseEncrypt(parent):
        """
        Parses an encrypt configuration section.

        We read the following individual fields::

           encryptMode    //cb_config/encrypt/encrypt_mode
           encryptTarget  //cb_config/encrypt/encrypt_target

        Args:
           parent: Parent node to search beneath

        Returns:
            ``EncryptConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        encrypt = None
        section = readFirstChild(parent, "encrypt")
        if section is not None:
            encrypt = EncryptConfig()
            encrypt.encryptMode = readString(section, "encrypt_mode")
            encrypt.encryptTarget = readString(section, "encrypt_target")
        return encrypt


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################

# pylint: disable=W0613
def executeAction(configPath, options, config):
    """
    Executes the encrypt backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If there are I/O problems reading or writing files
    """
    logger.debug("Executing encrypt extended action.")
    if config.options is None or config.stage is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    if local.encrypt.encryptMode not in ["gpg"]:
        raise ValueError("Unknown encrypt mode [%s]" % local.encrypt.encryptMode)
    if local.encrypt.encryptMode == "gpg":
        _confirmGpgRecipient(local.encrypt.encryptTarget)
    dailyDirs = findDailyDirs(config.stage.targetDir, ENCRYPT_INDICATOR)
    for dailyDir in dailyDirs:
        _encryptDailyDir(
            dailyDir, local.encrypt.encryptMode, local.encrypt.encryptTarget, config.options.backupUser, config.options.backupGroup
        )
        writeIndicatorFile(dailyDir, ENCRYPT_INDICATOR, config.options.backupUser, config.options.backupGroup)
    logger.info("Executed the encrypt extended action successfully.")


##############################
# _encryptDailyDir() function
##############################


def _encryptDailyDir(dailyDir, encryptMode, encryptTarget, backupUser, backupGroup):
    """
    Encrypts the contents of a daily staging directory.

    Indicator files are ignored.  All other files are encrypted.  The only valid
    encrypt mode is ``"gpg"``.

    Args:
       dailyDir: Daily directory to encrypt
       encryptMode: Encryption mode (only "gpg" is allowed)
       encryptTarget: Encryption target (GPG recipient for "gpg" mode)
       backupUser: User that target files should be owned by
       backupGroup: Group that target files should be owned by

    Raises:
       ValueError: If the encrypt mode is not supported
       ValueError: If the daily staging directory does not exist
    """
    logger.debug("Begin encrypting contents of [%s].", dailyDir)
    fileList = getBackupFiles(dailyDir)  # ignores indicator files
    for path in fileList:
        _encryptFile(path, encryptMode, encryptTarget, backupUser, backupGroup, removeSource=True)
    logger.debug("Completed encrypting contents of [%s].", dailyDir)


##########################
# _encryptFile() function
##########################


def _encryptFile(sourcePath, encryptMode, encryptTarget, backupUser, backupGroup, removeSource=False):
    """
    Encrypts the source file using the indicated mode.

    The encrypted file will be owned by the indicated backup user and group.  If
    ``removeSource`` is ``True``, then the source file will be removed after it is
    successfully encrypted.

    Currently, only the ``"gpg"`` encrypt mode is supported.

    Args:
       sourcePath: Absolute path of the source file to encrypt
       encryptMode: Encryption mode (only "gpg" is allowed)
       encryptTarget: Encryption target (GPG recipient)
       backupUser: User that target files should be owned by
       backupGroup: Group that target files should be owned by
       removeSource: Indicates whether to remove the source file

    Returns:
        Path to the newly-created encrypted file

    Raises:
       ValueError: If an invalid encrypt mode is passed in
       IOError: If there is a problem accessing, encrypting or removing the source file
    """
    if not os.path.exists(sourcePath):
        raise ValueError("Source path [%s] does not exist." % sourcePath)
    if encryptMode == "gpg":
        encryptedPath = _encryptFileWithGpg(sourcePath, recipient=encryptTarget)
    else:
        raise ValueError("Unknown encrypt mode [%s]" % encryptMode)
    changeOwnership(encryptedPath, backupUser, backupGroup)
    if removeSource:
        if os.path.exists(sourcePath):
            try:
                os.remove(sourcePath)
                logger.debug("Completed removing old file [%s].", sourcePath)
            except:
                raise IOError("Failed to remove file [%s] after encrypting it." % (sourcePath))
    return encryptedPath


#################################
# _encryptFileWithGpg() function
#################################


def _encryptFileWithGpg(sourcePath, recipient):
    """
    Encrypts the indicated source file using GPG.

    The encrypted file will be in GPG's binary output format and will have the
    same name as the source file plus a ``".gpg"`` extension.  The source file
    will not be modified or removed by this function call.

    Args:
       sourcePath: Absolute path of file to be encrypted
       recipient: Recipient name to be passed to GPG's ``"-r"`` option

    Returns:
        Path to the newly-created encrypted file

    Raises:
       IOError: If there is a problem encrypting the file
    """
    encryptedPath = "%s.gpg" % sourcePath
    command = resolveCommand(GPG_COMMAND)
    args = ["--batch", "--yes", "-e", "-r", recipient, "-o", encryptedPath, sourcePath]
    result = executeCommand(command, args)[0]
    if result != 0:
        raise IOError("Error [%d] calling gpg to encrypt [%s]." % (result, sourcePath))
    if not os.path.exists(encryptedPath):
        raise IOError("After call to [%s], encrypted file [%s] does not exist." % (command, encryptedPath))
    logger.debug("Completed encrypting file [%s] to [%s].", sourcePath, encryptedPath)
    return encryptedPath


#################################
# _confirmGpgRecpient() function
#################################


def _confirmGpgRecipient(recipient):
    """
    Confirms that a recipient's public key is known to GPG.
    Throws an exception if there is a problem, or returns normally otherwise.
    Args:
       recipient: Recipient name
    Raises:
       IOError: If the recipient's public key is not known to GPG
    """
    command = resolveCommand(GPG_COMMAND)
    args = ["--batch", "-k", recipient]  # should use --with-colons if the output will be parsed
    result = executeCommand(command, args)[0]
    if result != 0:
        raise IOError("GPG unable to find public key for [%s]." % recipient)
