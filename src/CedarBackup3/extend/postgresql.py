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
# Copyright (c) 2006,2010,2015 Kenneth J. Pronovici.
# Copyright (c) 2006 Antoine Beaupre.
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
#            Antoine Beaupre <anarcat@koumbit.org>
# Language : Python 3 (>= 3.7)
# Project  : Official Cedar Backup Extensions
# Purpose  : Provides an extension to back up PostgreSQL databases.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This file was created with a width of 132 characters, and NO tabs.

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to back up PostgreSQL databases.

This is a Cedar Backup extension used to back up PostgreSQL databases via the
Cedar Backup command line.  It requires a new configurations section
<postgresql> and is intended to be run either immediately before or immediately
after the standard collect action.  Aside from its own configuration, it
requires the options and collect configuration sections in the standard Cedar
Backup configuration file.

The backup is done via the ``pg_dump`` or ``pg_dumpall`` commands included with
the PostgreSQL product.  Output can be compressed using ``gzip`` or ``bzip2``.
Administrators can configure the extension either to back up all databases or
to back up only specific databases.  The extension assumes that the current
user has passwordless access to the database since there is no easy way to pass
a password to the ``pg_dump`` client. This can be accomplished using appropriate
voodoo in the ``pg_hda.conf`` file.

Note that this code always produces a full backup.  There is currently no
facility for making incremental backups.

You should always make ``/etc/cback3.conf`` unreadble to non-root users once you
place postgresql configuration into it, since postgresql configuration will
contain information about available PostgreSQL databases and usernames.

Use of this extension *may* expose usernames in the process listing (via
``ps``) when the backup is running if the username is specified in the
configuration.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
:author: Antoine Beaupre <anarcat@koumbit.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
from bz2 import BZ2File
from functools import total_ordering
from gzip import GzipFile

from CedarBackup3.config import VALID_COMPRESS_MODES
from CedarBackup3.util import ObjectTypeList, changeOwnership, executeCommand, pathJoin, resolveCommand
from CedarBackup3.xmlutil import (
    addBooleanNode,
    addContainerNode,
    addStringNode,
    createInputDom,
    readBoolean,
    readFirstChild,
    readString,
    readStringList,
)

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.postgresql")
POSTGRESQLDUMP_COMMAND = ["pg_dump"]
POSTGRESQLDUMPALL_COMMAND = ["pg_dumpall"]


########################################################################
# PostgresqlConfig class definition
########################################################################


@total_ordering
class PostgresqlConfig(object):

    """
    Class representing PostgreSQL configuration.

    The PostgreSQL configuration information is used for backing up PostgreSQL databases.

    The following restrictions exist on data in this class:

       - The compress mode must be one of the values in :any:`VALID_COMPRESS_MODES`.
       - The 'all' flag must be 'Y' if no databases are defined.
       - The 'all' flag must be 'N' if any databases are defined.
       - Any values in the databases list must be strings.

    """

    def __init__(self, user=None, compressMode=None, all=None, databases=None):  # pylint: disable=W0622
        """
        Constructor for the ``PostgresqlConfig`` class.

        Args:
           user: User to execute backup as
           compressMode: Compress mode for backed-up files
           all: Indicates whether to back up all databases
           databases: List of databases to back up
        """
        self._user = None
        self._compressMode = None
        self._all = None
        self._databases = None
        self.user = user
        self.compressMode = compressMode
        self.all = all
        self.databases = databases

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PostgresqlConfig(%s, %s, %s)" % (self.user, self.all, self.databases)

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
        if self.user != other.user:
            if str(self.user or "") < str(other.user or ""):
                return -1
            else:
                return 1
        if self.compressMode != other.compressMode:
            if str(self.compressMode or "") < str(other.compressMode or ""):
                return -1
            else:
                return 1
        if self.all != other.all:
            if self.all < other.all:
                return -1
            else:
                return 1
        if self.databases != other.databases:
            if self.databases < other.databases:
                return -1
            else:
                return 1
        return 0

    def _setUser(self, value):
        """
        Property target used to set the user value.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("User must be non-empty string.")
        self._user = value

    def _getUser(self):
        """
        Property target used to get the user value.
        """
        return self._user

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

    def _setAll(self, value):
        """
        Property target used to set the 'all' flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._all = True
        else:
            self._all = False

    def _getAll(self):
        """
        Property target used to get the 'all' flag.
        """
        return self._all

    def _setDatabases(self, value):
        """
        Property target used to set the databases list.
        Either the value must be ``None`` or each element must be a string.
        Raises:
           ValueError: If the value is not a string
        """
        if value is None:
            self._databases = None
        else:
            for database in value:
                if len(database) < 1:
                    raise ValueError("Each database must be a non-empty string.")
            try:
                saved = self._databases
                self._databases = ObjectTypeList(str, "string")
                self._databases.extend(value)
            except Exception as e:
                self._databases = saved
                raise e

    def _getDatabases(self):
        """
        Property target used to get the databases list.
        """
        return self._databases

    user = property(_getUser, _setUser, None, "User to execute backup as.")
    compressMode = property(_getCompressMode, _setCompressMode, None, "Compress mode to be used for backed-up files.")
    all = property(_getAll, _setAll, None, "Indicates whether to back up all databases.")
    databases = property(_getDatabases, _setDatabases, None, "List of databases to back up.")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    PostgreSQL-specific configuration values.  Third parties who need to read and
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
        self._postgresql = None
        self.postgresql = None
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
        return "LocalConfig(%s)" % (self.postgresql)

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
        if self.postgresql != other.postgresql:
            if self.postgresql < other.postgresql:
                return -1
            else:
                return 1
        return 0

    def _setPostgresql(self, value):
        """
        Property target used to set the postgresql configuration value.
        If not ``None``, the value must be a ``PostgresqlConfig`` object.
        Raises:
           ValueError: If the value is not a ``PostgresqlConfig``
        """
        if value is None:
            self._postgresql = None
        else:
            if not isinstance(value, PostgresqlConfig):
                raise ValueError("Value must be a ``PostgresqlConfig`` object.")
            self._postgresql = value

    def _getPostgresql(self):
        """
        Property target used to get the postgresql configuration value.
        """
        return self._postgresql

    postgresql = property(
        _getPostgresql, _setPostgresql, None, "Postgresql configuration in terms of a ``PostgresqlConfig`` object."
    )

    def validate(self):
        """
        Validates configuration represented by the object.

        The compress mode must be filled in.  Then, if the 'all' flag
        *is* set, no databases are allowed, and if the 'all' flag is
        *not* set, at least one database is required.

        Raises:
           ValueError: If one of the validations fails
        """
        if self.postgresql is None:
            raise ValueError("PostgreSQL section is required.")
        if self.postgresql.compressMode is None:
            raise ValueError("Compress mode value is required.")
        if self.postgresql.all:
            if self.postgresql.databases is not None and self.postgresql.databases != []:
                raise ValueError("Databases cannot be specified if 'all' flag is set.")
        else:
            if self.postgresql.databases is None or len(self.postgresql.databases) < 1:
                raise ValueError("At least one PostgreSQL database must be indicated if 'all' flag is not set.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds a <postgresql> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           user           //cb_config/postgresql/user
           compressMode   //cb_config/postgresql/compress_mode
           all            //cb_config/postgresql/all

        We also add groups of the following items, one list element per
        item::

           database       //cb_config/postgresql/database

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.postgresql is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "postgresql")
            addStringNode(xmlDom, sectionNode, "user", self.postgresql.user)
            addStringNode(xmlDom, sectionNode, "compress_mode", self.postgresql.compressMode)
            addBooleanNode(xmlDom, sectionNode, "all", self.postgresql.all)
            if self.postgresql.databases is not None:
                for database in self.postgresql.databases:
                    addStringNode(xmlDom, sectionNode, "database", database)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the postgresql configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._postgresql = LocalConfig._parsePostgresql(parentNode)

    @staticmethod
    def _parsePostgresql(parent):
        """
        Parses a postgresql configuration section.

        We read the following fields::

           user           //cb_config/postgresql/user
           compressMode   //cb_config/postgresql/compress_mode
           all            //cb_config/postgresql/all

        We also read groups of the following item, one list element per
        item::

           databases      //cb_config/postgresql/database

        Args:
           parent: Parent node to search beneath

        Returns:
            ``PostgresqlConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        postgresql = None
        section = readFirstChild(parent, "postgresql")
        if section is not None:
            postgresql = PostgresqlConfig()
            postgresql.user = readString(section, "user")
            postgresql.compressMode = readString(section, "compress_mode")
            postgresql.all = readBoolean(section, "all")
            postgresql.databases = readStringList(section, "database")
        return postgresql


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################

# pylint: disable=W0613
def executeAction(configPath, options, config):
    """
    Executes the PostgreSQL backup action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If a backup could not be written for some reason
    """
    logger.debug("Executing PostgreSQL extended action.")
    if config.options is None or config.collect is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    if local.postgresql.all:
        logger.info("Backing up all databases.")
        _backupDatabase(
            config.collect.targetDir,
            local.postgresql.compressMode,
            local.postgresql.user,
            config.options.backupUser,
            config.options.backupGroup,
            None,
        )
    if local.postgresql.databases is not None and local.postgresql.databases != []:
        logger.debug("Backing up %d individual databases.", len(local.postgresql.databases))
        for database in local.postgresql.databases:
            logger.info("Backing up database [%s].", database)
            _backupDatabase(
                config.collect.targetDir,
                local.postgresql.compressMode,
                local.postgresql.user,
                config.options.backupUser,
                config.options.backupGroup,
                database,
            )
    logger.info("Executed the PostgreSQL extended action successfully.")


def _backupDatabase(targetDir, compressMode, user, backupUser, backupGroup, database=None):
    """
    Backs up an individual PostgreSQL database, or all databases.

    This internal method wraps the public method and adds some functionality,
    like figuring out a filename, etc.

    Args:
       targetDir:  Directory into which backups should be written
       compressMode: Compress mode to be used for backed-up files
       user: User to use for connecting to the database
       backupUser: User to own resulting file
       backupGroup: Group to own resulting file
       database: Name of database, or ``None`` for all databases

    Returns:
        Name of the generated backup file

    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem executing the PostgreSQL dump
    """
    (outputFile, filename) = _getOutputFile(targetDir, database, compressMode)
    with outputFile:
        backupDatabase(user, outputFile, database)
    if not os.path.exists(filename):
        raise IOError("Dump file [%s] does not seem to exist after backup completed." % filename)
    changeOwnership(filename, backupUser, backupGroup)


def _getOutputFile(targetDir, database, compressMode):
    """
    Opens the output file used for saving the PostgreSQL dump.

    The filename is either ``"postgresqldump.txt"`` or
    ``"postgresqldump-<database>.txt"``.  The ``".gz"`` or ``".bz2"`` extension is
    added if ``compress`` is ``True``.

    Args:
       targetDir: Target directory to write file in
       database: Name of the database (if any)
       compressMode: Compress mode to be used for backed-up files

    Returns:
        Tuple of (Output file object, filename), file opened in binary mode for use with executeCommand()
    """
    if database is None:
        filename = pathJoin(targetDir, "postgresqldump.txt")
    else:
        filename = pathJoin(targetDir, "postgresqldump-%s.txt" % database)
    if compressMode == "gzip":
        filename = "%s.gz" % filename
        outputFile = GzipFile(filename, "wb")
    elif compressMode == "bzip2":
        filename = "%s.bz2" % filename
        outputFile = BZ2File(filename, "wb")
    else:
        outputFile = open(filename, "wb")
    logger.debug("PostgreSQL dump file will be [%s].", filename)
    return (outputFile, filename)


############################
# backupDatabase() function
############################


def backupDatabase(user, backupFile, database=None):
    """
    Backs up an individual PostgreSQL database, or all databases.

    This function backs up either a named local PostgreSQL database or all local
    PostgreSQL databases, using the passed in user for connectivity.
    This is *always* a full backup.  There is no facility for incremental
    backups.

    The backup data will be written into the passed-in back file.  Normally,
    this would be an object as returned from ``open``, but it is possible to
    use something like a ``GzipFile`` to write compressed output.  The caller is
    responsible for closing the passed-in backup file.

    *Note:* Typically, you would use the ``root`` user to back up all databases.

    Args:
       user (String representing PostgreSQL username): User to use for connecting to the database
       backupFile (Python file object as from ``open`` or ``file``): File use for writing backup
       database (String representing database name, or ``None`` for all databases): Name of the database to be backed up
    Raises:
       ValueError: If some value is missing or invalid
       IOError: If there is a problem executing the PostgreSQL dump
    """
    args = []
    if user is not None:
        args.append("-U")
        args.append(user)

    if database is None:
        command = resolveCommand(POSTGRESQLDUMPALL_COMMAND)
    else:
        command = resolveCommand(POSTGRESQLDUMP_COMMAND)
        args.append(database)

    result = executeCommand(command, args, returnOutput=False, ignoreStderr=True, doNotLog=True, outputFile=backupFile)[0]
    if result != 0:
        if database is None:
            raise IOError("Error [%d] executing PostgreSQL database dump for all databases." % result)
        else:
            raise IOError("Error [%d] executing PostgreSQL database dump for database [%s]." % (result, database))
