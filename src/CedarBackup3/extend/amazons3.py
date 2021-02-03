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
# Copyright (c) 2014-2015 Kenneth J. Pronovici.
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
# Purpose  : "Store" type extension that writes data to Amazon S3.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Store-type extension that writes data to Amazon S3.

This extension requires a new configuration section <amazons3> and is intended
to be run immediately after the standard stage action, replacing the standard
store action.  Aside from its own configuration, it requires the options and
staging configuration sections in the standard Cedar Backup configuration file.
Since it is intended to replace the store action, it does not rely on any store
configuration.

The underlying functionality relies on the U{AWS CLI interface
<http://aws.amazon.com/documentation/cli/>}.  Before you use this extension,
you need to set up your Amazon S3 account and configure the AWS CLI connection
per Amazon's documentation.  The extension assumes that the backup is being
executed as root, and switches over to the configured backup user to
communicate with AWS.  So, make sure you configure AWS CLI as the backup user
and not root.

You can optionally configure Cedar Backup to encrypt data before sending it
to S3.  To do that, provide a complete command line using the ``${input``} and
``${output``} variables to represent the original input file and the encrypted
output file.  This command will be executed as the backup user.

For instance, you can use something like this with GPG::

   /usr/bin/gpg -c --no-use-agent --batch --yes --passphrase-file /home/backup/.passphrase -o ${output} ${input}

The GPG mechanism depends on a strong passphrase for security.  One way to
generate a strong passphrase is using your system random number generator, i.e.::

   dd if=/dev/urandom count=20 bs=1 | xxd -ps

(See U{StackExchange <http://security.stackexchange.com/questions/14867/gpg-encryption-security>}
for more details about that advice.) If you decide to use encryption, make sure
you save off the passphrase in a safe place, so you can get at your backup data
later if you need to.  And obviously, make sure to set permissions on the
passphrase file so it can only be read by the backup user.

This extension was written for and tested on Linux.  It will throw an exception
if run on Windows.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import datetime
import json
import logging
import os
import shutil
import sys
import tempfile
from functools import total_ordering

from CedarBackup3.actions.constants import DIR_TIME_FORMAT, STAGE_INDICATOR
from CedarBackup3.actions.util import writeIndicatorFile
from CedarBackup3.config import ByteQuantity, addByteQuantityNode, readByteQuantity
from CedarBackup3.filesystem import BackupFileList, FilesystemList
from CedarBackup3.util import (
    UNIT_BYTES,
    changeOwnership,
    displayBytes,
    executeCommand,
    isRunningAsRoot,
    isStartOfWeek,
    pathJoin,
    resolveCommand,
)
from CedarBackup3.xmlutil import (
    addBooleanNode,
    addContainerNode,
    addStringNode,
    createInputDom,
    readBoolean,
    readFirstChild,
    readString,
)

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.amazons3")

SU_COMMAND = ["su"]
AWS_COMMAND = ["aws"]

STORE_INDICATOR = "cback.amazons3"


########################################################################
# AmazonS3Config class definition
########################################################################


@total_ordering
class AmazonS3Config(object):

    """
    Class representing Amazon S3 configuration.

    Amazon S3 configuration is used for storing backup data in Amazon's S3 cloud
    storage using the ``s3cmd`` tool.

    The following restrictions exist on data in this class:

       - The s3Bucket value must be a non-empty string
       - The encryptCommand value, if set, must be a non-empty string
       - The full backup size limit, if set, must be a ByteQuantity >= 0
       - The incremental backup size limit, if set, must be a ByteQuantity >= 0

    """

    def __init__(
        self, warnMidnite=None, s3Bucket=None, encryptCommand=None, fullBackupSizeLimit=None, incrementalBackupSizeLimit=None
    ):
        """
        Constructor for the ``AmazonS3Config`` class.

        Args:
           warnMidnite: Whether to generate warnings for crossing midnite
           s3Bucket: Name of the Amazon S3 bucket in which to store the data
           encryptCommand: Command used to encrypt backup data before upload to S3
           fullBackupSizeLimit: Maximum size of a full backup, a ByteQuantity
           incrementalBackupSizeLimit: Maximum size of an incremental backup, a ByteQuantity

        Raises:
           ValueError: If one of the values is invalid
        """
        self._warnMidnite = None
        self._s3Bucket = None
        self._encryptCommand = None
        self._fullBackupSizeLimit = None
        self._incrementalBackupSizeLimit = None
        self.warnMidnite = warnMidnite
        self.s3Bucket = s3Bucket
        self.encryptCommand = encryptCommand
        self.fullBackupSizeLimit = fullBackupSizeLimit
        self.incrementalBackupSizeLimit = incrementalBackupSizeLimit

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "AmazonS3Config(%s, %s, %s, %s, %s)" % (
            self.warnMidnite,
            self.s3Bucket,
            self.encryptCommand,
            self.fullBackupSizeLimit,
            self.incrementalBackupSizeLimit,
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
        if self.warnMidnite != other.warnMidnite:
            if self.warnMidnite < other.warnMidnite:
                return -1
            else:
                return 1
        if self.s3Bucket != other.s3Bucket:
            if str(self.s3Bucket or "") < str(other.s3Bucket or ""):
                return -1
            else:
                return 1
        if self.encryptCommand != other.encryptCommand:
            if str(self.encryptCommand or "") < str(other.encryptCommand or ""):
                return -1
            else:
                return 1
        if self.fullBackupSizeLimit != other.fullBackupSizeLimit:
            if (self.fullBackupSizeLimit or ByteQuantity()) < (other.fullBackupSizeLimit or ByteQuantity()):
                return -1
            else:
                return 1
        if self.incrementalBackupSizeLimit != other.incrementalBackupSizeLimit:
            if (self.incrementalBackupSizeLimit or ByteQuantity()) < (other.incrementalBackupSizeLimit or ByteQuantity()):
                return -1
            else:
                return 1
        return 0

    def _setWarnMidnite(self, value):
        """
        Property target used to set the midnite warning flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._warnMidnite = True
        else:
            self._warnMidnite = False

    def _getWarnMidnite(self):
        """
        Property target used to get the midnite warning flag.
        """
        return self._warnMidnite

    def _setS3Bucket(self, value):
        """
        Property target used to set the S3 bucket.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("S3 bucket must be non-empty string.")
        self._s3Bucket = value

    def _getS3Bucket(self):
        """
        Property target used to get the S3 bucket.
        """
        return self._s3Bucket

    def _setEncryptCommand(self, value):
        """
        Property target used to set the encrypt command.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Encrypt command must be non-empty string.")
        self._encryptCommand = value

    def _getEncryptCommand(self):
        """
        Property target used to get the encrypt command.
        """
        return self._encryptCommand

    def _setFullBackupSizeLimit(self, value):
        """
        Property target used to set the full backup size limit.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._fullBackupSizeLimit = None
        else:
            if isinstance(value, ByteQuantity):
                self._fullBackupSizeLimit = value
            else:
                self._fullBackupSizeLimit = ByteQuantity(value, UNIT_BYTES)

    def _getFullBackupSizeLimit(self):
        """
        Property target used to get the full backup size limit.
        """
        return self._fullBackupSizeLimit

    def _setIncrementalBackupSizeLimit(self, value):
        """
        Property target used to set the incremental backup size limit.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._incrementalBackupSizeLimit = None
        else:
            if isinstance(value, ByteQuantity):
                self._incrementalBackupSizeLimit = value
            else:
                self._incrementalBackupSizeLimit = ByteQuantity(value, UNIT_BYTES)

    def _getIncrementalBackupSizeLimit(self):
        """
        Property target used to get the incremental backup size limit.
        """
        return self._incrementalBackupSizeLimit

    warnMidnite = property(_getWarnMidnite, _setWarnMidnite, None, "Whether to generate warnings for crossing midnite.")
    s3Bucket = property(_getS3Bucket, _setS3Bucket, None, doc="Amazon S3 Bucket in which to store data")
    encryptCommand = property(_getEncryptCommand, _setEncryptCommand, None, doc="Command used to encrypt data before upload to S3")
    fullBackupSizeLimit = property(
        _getFullBackupSizeLimit, _setFullBackupSizeLimit, None, doc="Maximum size of a full backup, as a ByteQuantity"
    )
    incrementalBackupSizeLimit = property(
        _getIncrementalBackupSizeLimit,
        _setIncrementalBackupSizeLimit,
        None,
        doc="Maximum size of an incremental backup, as a ByteQuantity",
    )


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    amazons3-specific configuration values.  Third parties who need to read and
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
        self._amazons3 = None
        self.amazons3 = None
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
        return "LocalConfig(%s)" % (self.amazons3)

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
        if self.amazons3 != other.amazons3:
            if self.amazons3 < other.amazons3:
                return -1
            else:
                return 1
        return 0

    def _setAmazonS3(self, value):
        """
        Property target used to set the amazons3 configuration value.
        If not ``None``, the value must be a ``AmazonS3Config`` object.
        Raises:
           ValueError: If the value is not a ``AmazonS3Config``
        """
        if value is None:
            self._amazons3 = None
        else:
            if not isinstance(value, AmazonS3Config):
                raise ValueError("Value must be a ``AmazonS3Config`` object.")
            self._amazons3 = value

    def _getAmazonS3(self):
        """
        Property target used to get the amazons3 configuration value.
        """
        return self._amazons3

    amazons3 = property(_getAmazonS3, _setAmazonS3, None, "AmazonS3 configuration in terms of a ``AmazonS3Config`` object.")

    def validate(self):
        """
        Validates configuration represented by the object.

        AmazonS3 configuration must be filled in.  Within that, the s3Bucket target must be filled in

        Raises:
           ValueError: If one of the validations fails
        """
        if self.amazons3 is None:
            raise ValueError("AmazonS3 section is required.")
        if self.amazons3.s3Bucket is None:
            raise ValueError("AmazonS3 s3Bucket must be set.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds an <amazons3> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           warnMidnite                 //cb_config/amazons3/warn_midnite
           s3Bucket                    //cb_config/amazons3/s3_bucket
           encryptCommand              //cb_config/amazons3/encrypt
           fullBackupSizeLimit         //cb_config/amazons3/full_size_limit
           incrementalBackupSizeLimit  //cb_config/amazons3/incr_size_limit

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.amazons3 is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "amazons3")
            addBooleanNode(xmlDom, sectionNode, "warn_midnite", self.amazons3.warnMidnite)
            addStringNode(xmlDom, sectionNode, "s3_bucket", self.amazons3.s3Bucket)
            addStringNode(xmlDom, sectionNode, "encrypt", self.amazons3.encryptCommand)
            addByteQuantityNode(xmlDom, sectionNode, "full_size_limit", self.amazons3.fullBackupSizeLimit)
            addByteQuantityNode(xmlDom, sectionNode, "incr_size_limit", self.amazons3.incrementalBackupSizeLimit)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the amazons3 configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._amazons3 = LocalConfig._parseAmazonS3(parentNode)

    @staticmethod
    def _parseAmazonS3(parent):
        """
        Parses an amazons3 configuration section.

        We read the following individual fields::

           warnMidnite                 //cb_config/amazons3/warn_midnite
           s3Bucket                    //cb_config/amazons3/s3_bucket
           encryptCommand              //cb_config/amazons3/encrypt
           fullBackupSizeLimit         //cb_config/amazons3/full_size_limit
           incrementalBackupSizeLimit  //cb_config/amazons3/incr_size_limit

        Args:
           parent: Parent node to search beneath

        Returns:
            ``AmazonS3Config`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        amazons3 = None
        section = readFirstChild(parent, "amazons3")
        if section is not None:
            amazons3 = AmazonS3Config()
            amazons3.warnMidnite = readBoolean(section, "warn_midnite")
            amazons3.s3Bucket = readString(section, "s3_bucket")
            amazons3.encryptCommand = readString(section, "encrypt")
            amazons3.fullBackupSizeLimit = readByteQuantity(section, "full_size_limit")
            amazons3.incrementalBackupSizeLimit = readByteQuantity(section, "incr_size_limit")
        return amazons3


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################


def executeAction(configPath, options, config):
    """
    Executes the amazons3 backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If there are I/O problems reading or writing files
    """
    logger.debug("Executing amazons3 extended action.")
    if not isRunningAsRoot():
        logger.error("Error: the amazons3 extended action must be run as root.")
        raise ValueError("The amazons3 extended action must be run as root.")
    if sys.platform == "win32":
        logger.error("Error: the amazons3 extended action is not supported on Windows.")
        raise ValueError("The amazons3 extended action is not supported on Windows.")
    if config.options is None or config.stage is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    stagingDirs = _findCorrectDailyDir(options, config, local)
    _applySizeLimits(options, config, local, stagingDirs)
    _writeToAmazonS3(config, local, stagingDirs)
    _writeStoreIndicator(config, stagingDirs)
    logger.info("Executed the amazons3 extended action successfully.")


########################################################################
# Private utility functions
########################################################################

#########################
# _findCorrectDailyDir()
#########################


def _findCorrectDailyDir(options, config, local):
    """
    Finds the correct daily staging directory to be written to Amazon S3.

    This is substantially similar to the same function in store.py.  The
    main difference is that it doesn't rely on store configuration at all.

    Args:
       options: Options object
       config: Config object
       local: Local config object

    Returns:
        Correct staging dir, as a dict mapping directory to date suffix
    Raises:
       IOError: If the staging directory cannot be found
    """
    oneDay = datetime.timedelta(days=1)
    today = datetime.date.today()
    yesterday = today - oneDay
    tomorrow = today + oneDay
    todayDate = today.strftime(DIR_TIME_FORMAT)
    yesterdayDate = yesterday.strftime(DIR_TIME_FORMAT)
    tomorrowDate = tomorrow.strftime(DIR_TIME_FORMAT)
    todayPath = pathJoin(config.stage.targetDir, todayDate)
    yesterdayPath = pathJoin(config.stage.targetDir, yesterdayDate)
    tomorrowPath = pathJoin(config.stage.targetDir, tomorrowDate)
    todayStageInd = pathJoin(todayPath, STAGE_INDICATOR)
    yesterdayStageInd = pathJoin(yesterdayPath, STAGE_INDICATOR)
    tomorrowStageInd = pathJoin(tomorrowPath, STAGE_INDICATOR)
    todayStoreInd = pathJoin(todayPath, STORE_INDICATOR)
    yesterdayStoreInd = pathJoin(yesterdayPath, STORE_INDICATOR)
    tomorrowStoreInd = pathJoin(tomorrowPath, STORE_INDICATOR)
    if options.full:
        if os.path.isdir(todayPath) and os.path.exists(todayStageInd):
            logger.info("Amazon S3 process will use current day's staging directory [%s]", todayPath)
            return {todayPath: todayDate}
        raise IOError("Unable to find staging directory to process (only tried today due to full option).")
    else:
        if os.path.isdir(todayPath) and os.path.exists(todayStageInd) and not os.path.exists(todayStoreInd):
            logger.info("Amazon S3 process will use current day's staging directory [%s]", todayPath)
            return {todayPath: todayDate}
        elif os.path.isdir(yesterdayPath) and os.path.exists(yesterdayStageInd) and not os.path.exists(yesterdayStoreInd):
            logger.info("Amazon S3 process will use previous day's staging directory [%s]", yesterdayPath)
            if local.amazons3.warnMidnite:
                logger.warning("Warning: Amazon S3 process crossed midnite boundary to find data.")
            return {yesterdayPath: yesterdayDate}
        elif os.path.isdir(tomorrowPath) and os.path.exists(tomorrowStageInd) and not os.path.exists(tomorrowStoreInd):
            logger.info("Amazon S3 process will use next day's staging directory [%s]", tomorrowPath)
            if local.amazons3.warnMidnite:
                logger.warning("Warning: Amazon S3 process crossed midnite boundary to find data.")
            return {tomorrowPath: tomorrowDate}
        raise IOError("Unable to find unused staging directory to process (tried today, yesterday, tomorrow).")


##############################
# _applySizeLimits() function
##############################


def _applySizeLimits(options, config, local, stagingDirs):
    """
    Apply size limits, throwing an exception if any limits are exceeded.

    Size limits are optional.  If a limit is set to None, it does not apply.
    The full size limit applies if the full option is set or if today is the
    start of the week.  The incremental size limit applies otherwise.  Limits
    are applied to the total size of all the relevant staging directories.

    Args:
       options: Options object
       config: Config object
       local: Local config object
       stagingDirs: Dictionary mapping directory path to date suffix

    Raises:
       ValueError: Under many generic error conditions
       ValueError: If a size limit has been exceeded
    """
    if options.full or isStartOfWeek(config.options.startingDay):
        logger.debug("Using Amazon S3 size limit for full backups.")
        limit = local.amazons3.fullBackupSizeLimit
    else:
        logger.debug("Using Amazon S3 size limit for incremental backups.")
        limit = local.amazons3.incrementalBackupSizeLimit
    if limit is None:
        logger.debug("No Amazon S3 size limit will be applied.")
    else:
        logger.debug("Amazon S3 size limit is: %s", limit)
        contents = BackupFileList()
        for stagingDir in stagingDirs:
            contents.addDirContents(stagingDir)
        total = contents.totalSize()
        logger.debug("Amazon S3 backup size is: %s", displayBytes(total))
        if total > limit:
            logger.error("Amazon S3 size limit exceeded: %s > %s", displayBytes(total), limit)
            raise ValueError("Amazon S3 size limit exceeded: %s > %s" % (displayBytes(total), limit))
        else:
            logger.info("Total size does not exceed Amazon S3 size limit, so backup can continue.")


##############################
# _writeToAmazonS3() function
##############################


def _writeToAmazonS3(config, local, stagingDirs):
    """
    Writes the indicated staging directories to an Amazon S3 bucket.

    Each of the staging directories listed in ``stagingDirs`` will be written to
    the configured Amazon S3 bucket from local configuration.  The directories
    will be placed into the image at the root by date, so staging directory
    ``/opt/stage/2005/02/10`` will be placed into the S3 bucket at ``/2005/02/10``.
    If an encrypt commmand is provided, the files will be encrypted first.

    Args:
       config: Config object
       local: Local config object
       stagingDirs: Dictionary mapping directory path to date suffix

    Raises:
       ValueError: Under many generic error conditions
       IOError: If there is a problem writing to Amazon S3
    """
    for stagingDir in list(stagingDirs.keys()):
        logger.debug("Storing stage directory to Amazon S3 [%s].", stagingDir)
        dateSuffix = stagingDirs[stagingDir]
        s3BucketUrl = "s3://%s/%s" % (local.amazons3.s3Bucket, dateSuffix)
        logger.debug("S3 bucket URL is [%s]", s3BucketUrl)
        _clearExistingBackup(config, s3BucketUrl)
        if local.amazons3.encryptCommand is None:
            logger.debug("Encryption is disabled; files will be uploaded in cleartext.")
            _uploadStagingDir(config, stagingDir, s3BucketUrl)
            _verifyUpload(config, stagingDir, s3BucketUrl)
        else:
            logger.debug("Encryption is enabled; files will be uploaded after being encrypted.")
            encryptedDir = tempfile.mkdtemp(dir=config.options.workingDir)
            changeOwnership(encryptedDir, config.options.backupUser, config.options.backupGroup)
            try:
                _encryptStagingDir(config, local, stagingDir, encryptedDir)
                _uploadStagingDir(config, encryptedDir, s3BucketUrl)
                _verifyUpload(config, encryptedDir, s3BucketUrl)
            finally:
                if os.path.exists(encryptedDir):
                    shutil.rmtree(encryptedDir)


##################################
# _writeStoreIndicator() function
##################################


def _writeStoreIndicator(config, stagingDirs):
    """
    Writes a store indicator file into staging directories.
    Args:
       config: Config object
       stagingDirs: Dictionary mapping directory path to date suffix
    """
    for stagingDir in list(stagingDirs.keys()):
        writeIndicatorFile(stagingDir, STORE_INDICATOR, config.options.backupUser, config.options.backupGroup)


##################################
# _clearExistingBackup() function
##################################


def _clearExistingBackup(config, s3BucketUrl):
    """
    Clear any existing backup files for an S3 bucket URL.
    Args:
       config: Config object
       s3BucketUrl: S3 bucket URL associated with the staging directory
    """
    suCommand = resolveCommand(SU_COMMAND)
    awsCommand = resolveCommand(AWS_COMMAND)
    actualCommand = "%s s3 rm --recursive %s/" % (awsCommand[0], s3BucketUrl)
    result = executeCommand(suCommand, [config.options.backupUser, "-c", actualCommand])[0]
    if result != 0:
        raise IOError("Error [%d] calling AWS CLI to clear existing backup for [%s]." % (result, s3BucketUrl))
    logger.debug("Completed clearing any existing backup in S3 for [%s]", s3BucketUrl)


###############################
# _uploadStagingDir() function
###############################


def _uploadStagingDir(config, stagingDir, s3BucketUrl):
    """
    Upload the contents of a staging directory out to the Amazon S3 cloud.
    Args:
       config: Config object
       stagingDir: Staging directory to upload
       s3BucketUrl: S3 bucket URL associated with the staging directory
    """
    # The version of awscli in Debian stretch (1.11.13-1) has a problem
    # uploading empty files, due to running with Python 3 rather than Python 2
    # as the upstream maintainers intended.  To work around this, I'm explicitly
    # excluding files like cback.stage, cback.collect, etc. which should be the
    # only empty files we ever try to copy.  See: https://github.com/aws/aws-cli/issues/2403
    suCommand = resolveCommand(SU_COMMAND)
    awsCommand = resolveCommand(AWS_COMMAND)
    actualCommand = '%s s3 cp --recursive --exclude "*cback.*" %s/ %s/' % (awsCommand[0], stagingDir, s3BucketUrl)
    result = executeCommand(suCommand, [config.options.backupUser, "-c", actualCommand])[0]
    if result != 0:
        raise IOError("Error [%d] calling AWS CLI to upload staging directory to [%s]." % (result, s3BucketUrl))
    logger.debug("Completed uploading staging dir [%s] to [%s]", stagingDir, s3BucketUrl)


###########################
# _verifyUpload() function
###########################


def _verifyUpload(config, stagingDir, s3BucketUrl):
    """
    Verify that a staging directory was properly uploaded to the Amazon S3 cloud.
    Args:
       config: Config object
       stagingDir: Staging directory to verify
       s3BucketUrl: S3 bucket URL associated with the staging directory
    """
    (bucket, prefix) = s3BucketUrl.replace("s3://", "").split("/", 1)
    suCommand = resolveCommand(SU_COMMAND)
    awsCommand = resolveCommand(AWS_COMMAND)
    query = "Contents[].{Key: Key, Size: Size}"
    actualCommand = "%s s3api list-objects --bucket %s --prefix %s --query '%s'" % (awsCommand[0], bucket, prefix, query)
    (result, data) = executeCommand(suCommand, [config.options.backupUser, "-c", actualCommand], returnOutput=True)
    if result != 0:
        raise IOError("Error [%d] calling AWS CLI verify upload to [%s]." % (result, s3BucketUrl))
    contents = {}
    for entry in json.loads("".join(data)):
        key = entry["Key"].replace(prefix, "")
        size = int(entry["Size"])
        contents[key] = size
    files = FilesystemList()
    files.excludeBasenamePatterns = [r"cback\..*"]  # because these are excluded from the upload
    files.addDirContents(stagingDir)
    for entry in files:
        if os.path.isfile(entry):
            key = entry.replace(stagingDir, "")
            size = int(os.stat(entry).st_size)
            if key not in contents:
                raise IOError("File was apparently not uploaded: [%s]" % entry)
            else:
                if size != contents[key]:
                    raise IOError("File size differs [%s], expected %s bytes but got %s bytes" % (entry, size, contents[key]))
    logger.debug("Completed verifying upload from [%s] to [%s].", stagingDir, s3BucketUrl)


################################
# _encryptStagingDir() function
################################


def _encryptStagingDir(config, local, stagingDir, encryptedDir):
    """
    Encrypt a staging directory, creating a new directory in the process.
    Args:
       config: Config object
       stagingDir: Staging directory to use as source
       encryptedDir: Target directory into which encrypted files should be written
    """
    suCommand = resolveCommand(SU_COMMAND)
    files = FilesystemList()
    files.addDirContents(stagingDir)
    for cleartext in files:
        if os.path.isfile(cleartext):
            encrypted = "%s%s" % (encryptedDir, cleartext.replace(stagingDir, ""))
            if int(os.stat(cleartext).st_size) == 0:
                with open(encrypted, "a") as f:
                    f.close()  # don't bother encrypting empty files
            else:
                actualCommand = local.amazons3.encryptCommand.replace("${input}", cleartext).replace("${output}", encrypted)
                subdir = os.path.dirname(encrypted)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
                    changeOwnership(subdir, config.options.backupUser, config.options.backupGroup)
                result = executeCommand(suCommand, [config.options.backupUser, "-c", actualCommand])[0]
                if result != 0:
                    raise IOError("Error [%d] encrypting [%s]." % (result, cleartext))
    logger.debug("Completed encrypting staging directory [%s] into [%s]", stagingDir, encryptedDir)
