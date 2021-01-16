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
# Copyright (c) 2014-2016,2020 Kenneth J. Pronovici.
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
# Purpose  : Cedar Backup tool to synchronize an Amazon S3 bucket.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Notes
########################################################################

"""
Synchonizes a local directory with an Amazon S3 bucket.

No configuration is required; all necessary information is taken from the
command-line.  The only thing configuration would help with is the path
resolver interface, and it doesn't seem worth it to require configuration just
to get that.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules and constants
########################################################################

import getopt
import json
import logging
import os
import sys
import warnings
from functools import total_ordering
from pathlib import Path

import chardet

from CedarBackup3.cli import DEFAULT_LOGFILE, DEFAULT_MODE, DEFAULT_OWNERSHIP, setupLogging
from CedarBackup3.filesystem import FilesystemList
from CedarBackup3.release import AUTHOR, COPYRIGHT, DATE, EMAIL, VERSION
from CedarBackup3.util import Diagnostics, encodePath, executeCommand, splitCommandLine

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.tools.amazons3")

AWS_COMMAND = ["aws"]

SHORT_SWITCHES = "hVbql:o:m:OdsDvuw"
LONG_SWITCHES = [
    "help",
    "version",
    "verbose",
    "quiet",
    "logfile=",
    "owner=",
    "mode=",
    "output",
    "debug",
    "stack",
    "diagnostics",
    "verifyOnly",
    "uploadOnly",
    "ignoreWarnings",
]


#######################################################################
# Options class
#######################################################################


@total_ordering
class Options(object):

    ######################
    # Class documentation
    ######################

    """
    Class representing command-line options for the cback3-amazons3-sync script.

    The ``Options`` class is a Python object representation of the command-line
    options of the cback3-amazons3-sync script.

    The object representation is two-way: a command line string or a list of
    command line arguments can be used to create an ``Options`` object, and then
    changes to the object can be propogated back to a list of command-line
    arguments or to a command-line string.  An ``Options`` object can even be
    created from scratch programmatically (if you have a need for that).

    There are two main levels of validation in the ``Options`` class.  The first
    is field-level validation.  Field-level validation comes into play when a
    given field in an object is assigned to or updated.  We use Python's
    ``property`` functionality to enforce specific validations on field values,
    and in some places we even use customized list classes to enforce
    validations on list members.  You should expect to catch a ``ValueError``
    exception when making assignments to fields if you are programmatically
    filling an object.

    The second level of validation is post-completion validation.  Certain
    validations don't make sense until an object representation of options is
    fully "complete".  We don't want these validations to apply all of the time,
    because it would make building up a valid object from scratch a real pain.
    For instance, we might have to do things in the right order to keep from
    throwing exceptions, etc.

    All of these post-completion validations are encapsulated in the
    :any:`Options.validate` method.  This method can be called at any time by a
    client, and will always be called immediately after creating a ``Options``
    object from a command line and before exporting a ``Options`` object back to
    a command line.  This way, we get acceptable ease-of-use but we also don't
    accept or emit invalid command lines.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    ##############
    # Constructor
    ##############

    def __init__(self, argumentList=None, argumentString=None, validate=True):
        """
        Initializes an options object.

        If you initialize the object without passing either ``argumentList`` or
        ``argumentString``, the object will be empty and will be invalid until it
        is filled in properly.

        No reference to the original arguments is saved off by this class.  Once
        the data has been parsed (successfully or not) this original information
        is discarded.

        The argument list is assumed to be a list of arguments, not including the
        name of the command, something like ``sys.argv[1:]``.  If you pass
        ``sys.argv`` instead, things are not going to work.

        The argument string will be parsed into an argument list by the
        :any:`util.splitCommandLine` function (see the documentation for that
        function for some important notes about its limitations).  There is an
        assumption that the resulting list will be equivalent to ``sys.argv[1:]``,
        just like ``argumentList``.

        Unless the ``validate`` argument is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) after successfully
        parsing any passed-in command line.  This validation ensures that
        appropriate actions, etc. have been specified.  Keep in mind that even if
        ``validate`` is ``False``, it might not be possible to parse the passed-in
        command line, so an exception might still be raised.

        *Note:* The command line format is specified by the ``_usage`` function.
        Call ``_usage`` to see a usage statement for the cback3-amazons3-sync script.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to read in
        invalid command line arguments.

        Args:
           argumentList (List of arguments, i.e. ``sys.argv``): Command line for a program
           argumentString (String, i.e. "cback3-amazons3-sync --verbose stage store"): Command line for a program
           validate (Boolean true/false): Validate the command line after parsing it
        Raises:
           getopt.GetoptError: If the command-line arguments could not be parsed
           ValueError: If the command-line arguments are invalid
        """
        self._help = False
        self._version = False
        self._verbose = False
        self._quiet = False
        self._logfile = None
        self._owner = None
        self._mode = None
        self._output = False
        self._debug = False
        self._stacktrace = False
        self._diagnostics = False
        self._verifyOnly = False
        self._uploadOnly = False
        self._ignoreWarnings = False
        self._sourceDir = None
        self._s3BucketUrl = None
        if argumentList is not None and argumentString is not None:
            raise ValueError("Use either argumentList or argumentString, but not both.")
        if argumentString is not None:
            argumentList = splitCommandLine(argumentString)
        if argumentList is not None:
            self._parseArgumentList(argumentList)
            if validate:
                self.validate()

    #########################
    # String representations
    #########################

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return self.buildArgumentString(validate=False)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    #############################
    # Standard comparison method
    #############################

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
        if self.help != other.help:
            if self.help < other.help:
                return -1
            else:
                return 1
        if self.version != other.version:
            if self.version < other.version:
                return -1
            else:
                return 1
        if self.verbose != other.verbose:
            if self.verbose < other.verbose:
                return -1
            else:
                return 1
        if self.quiet != other.quiet:
            if self.quiet < other.quiet:
                return -1
            else:
                return 1
        if self.logfile != other.logfile:
            if str(self.logfile or "") < str(other.logfile or ""):
                return -1
            else:
                return 1
        if self.owner != other.owner:
            if str(self.owner or "") < str(other.owner or ""):
                return -1
            else:
                return 1
        if self.mode != other.mode:
            if int(self.mode or 0) < int(other.mode or 0):
                return -1
            else:
                return 1
        if self.output != other.output:
            if self.output < other.output:
                return -1
            else:
                return 1
        if self.debug != other.debug:
            if self.debug < other.debug:
                return -1
            else:
                return 1
        if self.stacktrace != other.stacktrace:
            if self.stacktrace < other.stacktrace:
                return -1
            else:
                return 1
        if self.diagnostics != other.diagnostics:
            if self.diagnostics < other.diagnostics:
                return -1
            else:
                return 1
        if self.verifyOnly != other.verifyOnly:
            if self.verifyOnly < other.verifyOnly:
                return -1
            else:
                return 1
        if self.uploadOnly != other.uploadOnly:
            if self.uploadOnly < other.uploadOnly:
                return -1
            else:
                return 1
        if self.ignoreWarnings != other.ignoreWarnings:
            if self.ignoreWarnings < other.ignoreWarnings:
                return -1
            else:
                return 1
        if self.sourceDir != other.sourceDir:
            if str(self.sourceDir or "") < str(other.sourceDir or ""):
                return -1
            else:
                return 1
        if self.s3BucketUrl != other.s3BucketUrl:
            if str(self.s3BucketUrl or "") < str(other.s3BucketUrl or ""):
                return -1
            else:
                return 1
        return 0

    #############
    # Properties
    #############

    def _setHelp(self, value):
        """
        Property target used to set the help flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._help = True
        else:
            self._help = False

    def _getHelp(self):
        """
        Property target used to get the help flag.
        """
        return self._help

    def _setVersion(self, value):
        """
        Property target used to set the version flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._version = True
        else:
            self._version = False

    def _getVersion(self):
        """
        Property target used to get the version flag.
        """
        return self._version

    def _setVerbose(self, value):
        """
        Property target used to set the verbose flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._verbose = True
        else:
            self._verbose = False

    def _getVerbose(self):
        """
        Property target used to get the verbose flag.
        """
        return self._verbose

    def _setQuiet(self, value):
        """
        Property target used to set the quiet flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._quiet = True
        else:
            self._quiet = False

    def _getQuiet(self):
        """
        Property target used to get the quiet flag.
        """
        return self._quiet

    def _setLogfile(self, value):
        """
        Property target used to set the logfile parameter.
        Raises:
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The logfile parameter must be a non-empty string.")
        self._logfile = encodePath(value)

    def _getLogfile(self):
        """
        Property target used to get the logfile parameter.
        """
        return self._logfile

    def _setOwner(self, value):
        """
        Property target used to set the owner parameter.
        If not ``None``, the owner must be a ``(user,group)`` tuple or list.
        Strings (and inherited children of strings) are explicitly disallowed.
        The value will be normalized to a tuple.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._owner = None
        else:
            if isinstance(value, str):
                raise ValueError("Must specify user and group tuple for owner parameter.")
            if len(value) != 2:
                raise ValueError("Must specify user and group tuple for owner parameter.")
            if len(value[0]) < 1 or len(value[1]) < 1:
                raise ValueError("User and group tuple values must be non-empty strings.")
            self._owner = (value[0], value[1])

    def _getOwner(self):
        """
        Property target used to get the owner parameter.
        The parameter is a tuple of ``(user, group)``.
        """
        return self._owner

    def _setMode(self, value):
        """
        Property target used to set the mode parameter.
        """
        if value is None:
            self._mode = None
        else:
            try:
                if isinstance(value, str):
                    value = int(value, 8)
                else:
                    value = int(value)
            except TypeError:
                raise ValueError("Mode must be an octal integer >= 0, i.e. 644.")
            if value < 0:
                raise ValueError("Mode must be an octal integer >= 0. i.e. 644.")
            self._mode = value

    def _getMode(self):
        """
        Property target used to get the mode parameter.
        """
        return self._mode

    def _setOutput(self, value):
        """
        Property target used to set the output flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._output = True
        else:
            self._output = False

    def _getOutput(self):
        """
        Property target used to get the output flag.
        """
        return self._output

    def _setDebug(self, value):
        """
        Property target used to set the debug flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._debug = True
        else:
            self._debug = False

    def _getDebug(self):
        """
        Property target used to get the debug flag.
        """
        return self._debug

    def _setStacktrace(self, value):
        """
        Property target used to set the stacktrace flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._stacktrace = True
        else:
            self._stacktrace = False

    def _getStacktrace(self):
        """
        Property target used to get the stacktrace flag.
        """
        return self._stacktrace

    def _setDiagnostics(self, value):
        """
        Property target used to set the diagnostics flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._diagnostics = True
        else:
            self._diagnostics = False

    def _getDiagnostics(self):
        """
        Property target used to get the diagnostics flag.
        """
        return self._diagnostics

    def _setVerifyOnly(self, value):
        """
        Property target used to set the verifyOnly flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._verifyOnly = True
        else:
            self._verifyOnly = False

    def _getVerifyOnly(self):
        """
        Property target used to get the verifyOnly flag.
        """
        return self._verifyOnly

    def _setUploadOnly(self, value):
        """
        Property target used to set the uploadOnly flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._uploadOnly = True
        else:
            self._uploadOnly = False

    def _getUploadOnly(self):
        """
        Property target used to get the uploadOnly flag.
        """
        return self._uploadOnly

    def _setIgnoreWarnings(self, value):
        """
        Property target used to set the ignoreWarnings flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._ignoreWarnings = True
        else:
            self._ignoreWarnings = False

    def _getIgnoreWarnings(self):
        """
        Property target used to get the ignoreWarnings flag.
        """
        return self._ignoreWarnings

    def _setSourceDir(self, value):
        """
        Property target used to set the sourceDir parameter.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The sourceDir parameter must be a non-empty string.")
        self._sourceDir = value

    def _getSourceDir(self):
        """
        Property target used to get the sourceDir parameter.
        """
        return self._sourceDir

    def _setS3BucketUrl(self, value):
        """
        Property target used to set the s3BucketUrl parameter.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The s3BucketUrl parameter must be a non-empty string.")
        self._s3BucketUrl = value

    def _getS3BucketUrl(self):
        """
        Property target used to get the s3BucketUrl parameter.
        """
        return self._s3BucketUrl

    help = property(_getHelp, _setHelp, None, "Command-line help (``-h,--help``) flag.")
    version = property(_getVersion, _setVersion, None, "Command-line version (``-V,--version``) flag.")
    verbose = property(_getVerbose, _setVerbose, None, "Command-line verbose (``-b,--verbose``) flag.")
    quiet = property(_getQuiet, _setQuiet, None, "Command-line quiet (``-q,--quiet``) flag.")
    logfile = property(_getLogfile, _setLogfile, None, "Command-line logfile (``-l,--logfile``) parameter.")
    owner = property(_getOwner, _setOwner, None, "Command-line owner (``-o,--owner``) parameter, as tuple ``(user,group)``.")
    mode = property(_getMode, _setMode, None, "Command-line mode (``-m,--mode``) parameter.")
    output = property(_getOutput, _setOutput, None, "Command-line output (``-O,--output``) flag.")
    debug = property(_getDebug, _setDebug, None, "Command-line debug (``-d,--debug``) flag.")
    stacktrace = property(_getStacktrace, _setStacktrace, None, "Command-line stacktrace (``-s,--stack``) flag.")
    diagnostics = property(_getDiagnostics, _setDiagnostics, None, "Command-line diagnostics (``-D,--diagnostics``) flag.")
    verifyOnly = property(_getVerifyOnly, _setVerifyOnly, None, "Command-line verifyOnly (``-v,--verifyOnly``) flag.")
    uploadOnly = property(_getUploadOnly, _setUploadOnly, None, "Command-line uploadOnly (``-u,--uploadOnly``) flag.")
    ignoreWarnings = property(
        _getIgnoreWarnings, _setIgnoreWarnings, None, "Command-line ignoreWarnings (``-w,--ignoreWarnings``) flag"
    )
    sourceDir = property(_getSourceDir, _setSourceDir, None, "Command-line sourceDir, source of sync.")
    s3BucketUrl = property(_getS3BucketUrl, _setS3BucketUrl, None, "Command-line s3BucketUrl, target of sync.")

    ##################
    # Utility methods
    ##################

    def validate(self):
        """
        Validates command-line options represented by the object.

        Unless ``--help`` or ``--version`` are supplied, at least one action must
        be specified.  Other validations (as for allowed values for particular
        options) will be taken care of at assignment time by the properties
        functionality.

        *Note:* The command line format is specified by the ``_usage`` function.
        Call ``_usage`` to see a usage statement for the cback3-amazons3-sync script.

        Raises:
           ValueError: If one of the validations fails
        """
        if not self.help and not self.version and not self.diagnostics:
            if self.sourceDir is None or self.s3BucketUrl is None:
                raise ValueError("Source directory and S3 bucket URL are both required.")

    def buildArgumentList(self, validate=True):
        """
        Extracts options into a list of command line arguments.

        The original order of the various arguments (if, indeed, the object was
        initialized with a command-line) is not preserved in this generated
        argument list.   Besides that, the argument list is normalized to use the
        long option names (i.e. --version rather than -V).  The resulting list
        will be suitable for passing back to the constructor in the
        ``argumentList`` parameter.  Unlike :any:`buildArgumentString`, string
        arguments are not quoted here, because there is no need for it.

        Unless the ``validate`` parameter is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) against the
        options before extracting the command line.  If the options are not valid,
        then an argument list will not be extracted.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to extract an
        invalid command line.

        Args:
           validate (Boolean true/false): Validate the options before extracting the command line
        Returns:
            List representation of command-line arguments
        Raises:
           ValueError: If options within the object are invalid
        """
        if validate:
            self.validate()
        argumentList = []
        if self._help:
            argumentList.append("--help")
        if self.version:
            argumentList.append("--version")
        if self.verbose:
            argumentList.append("--verbose")
        if self.quiet:
            argumentList.append("--quiet")
        if self.logfile is not None:
            argumentList.append("--logfile")
            argumentList.append(self.logfile)
        if self.owner is not None:
            argumentList.append("--owner")
            argumentList.append("%s:%s" % (self.owner[0], self.owner[1]))
        if self.mode is not None:
            argumentList.append("--mode")
            argumentList.append("%o" % self.mode)
        if self.output:
            argumentList.append("--output")
        if self.debug:
            argumentList.append("--debug")
        if self.stacktrace:
            argumentList.append("--stack")
        if self.diagnostics:
            argumentList.append("--diagnostics")
        if self.verifyOnly:
            argumentList.append("--verifyOnly")
        if self.uploadOnly:
            argumentList.append("--uploadOnly")
        if self.ignoreWarnings:
            argumentList.append("--ignoreWarnings")
        if self.sourceDir is not None:
            argumentList.append(self.sourceDir)
        if self.s3BucketUrl is not None:
            argumentList.append(self.s3BucketUrl)
        return argumentList

    def buildArgumentString(self, validate=True):
        """
        Extracts options into a string of command-line arguments.

        The original order of the various arguments (if, indeed, the object was
        initialized with a command-line) is not preserved in this generated
        argument string.   Besides that, the argument string is normalized to use
        the long option names (i.e. --version rather than -V) and to quote all
        string arguments with double quotes (``"``).  The resulting string will be
        suitable for passing back to the constructor in the ``argumentString``
        parameter.

        Unless the ``validate`` parameter is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) against the options
        before extracting the command line.  If the options are not valid, then
        an argument string will not be extracted.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to extract an
        invalid command line.

        Args:
           validate (Boolean true/false): Validate the options before extracting the command line
        Returns:
            String representation of command-line arguments
        Raises:
           ValueError: If options within the object are invalid
        """
        if validate:
            self.validate()
        argumentString = ""
        if self._help:
            argumentString += "--help "
        if self.version:
            argumentString += "--version "
        if self.verbose:
            argumentString += "--verbose "
        if self.quiet:
            argumentString += "--quiet "
        if self.logfile is not None:
            argumentString += '--logfile "%s" ' % self.logfile
        if self.owner is not None:
            argumentString += '--owner "%s:%s" ' % (self.owner[0], self.owner[1])
        if self.mode is not None:
            argumentString += "--mode %o " % self.mode
        if self.output:
            argumentString += "--output "
        if self.debug:
            argumentString += "--debug "
        if self.stacktrace:
            argumentString += "--stack "
        if self.diagnostics:
            argumentString += "--diagnostics "
        if self.verifyOnly:
            argumentString += "--verifyOnly "
        if self.uploadOnly:
            argumentString += "--uploadOnly "
        if self.ignoreWarnings:
            argumentString += "--ignoreWarnings "
        if self.sourceDir is not None:
            argumentString += '"%s" ' % self.sourceDir
        if self.s3BucketUrl is not None:
            argumentString += '"%s" ' % self.s3BucketUrl
        return argumentString

    def _parseArgumentList(self, argumentList):
        """
        Internal method to parse a list of command-line arguments.

        Most of the validation we do here has to do with whether the arguments
        can be parsed and whether any values which exist are valid.  We don't do
        any validation as to whether required elements exist or whether elements
        exist in the proper combination (instead, that's the job of the
        :any:`validate` method).

        For any of the options which supply parameters, if the option is
        duplicated with long and short switches (i.e. ``-l`` and a ``--logfile``)
        then the long switch is used.  If the same option is duplicated with the
        same switch (long or short), then the last entry on the command line is
        used.

        Args:
           argumentList (List of arguments to a command, i.e. ``sys.argv[1:]``): List of arguments to a command
        Raises:
           ValueError: If the argument list cannot be successfully parsed
        """
        switches = {}
        opts, remaining = getopt.getopt(argumentList, SHORT_SWITCHES, LONG_SWITCHES)
        for o, a in opts:  # push the switches into a hash
            switches[o] = a
        if "-h" in switches or "--help" in switches:
            self.help = True
        if "-V" in switches or "--version" in switches:
            self.version = True
        if "-b" in switches or "--verbose" in switches:
            self.verbose = True
        if "-q" in switches or "--quiet" in switches:
            self.quiet = True
        if "-l" in switches:
            self.logfile = switches["-l"]
        if "--logfile" in switches:
            self.logfile = switches["--logfile"]
        if "-o" in switches:
            self.owner = switches["-o"].split(":", 1)
        if "--owner" in switches:
            self.owner = switches["--owner"].split(":", 1)
        if "-m" in switches:
            self.mode = switches["-m"]
        if "--mode" in switches:
            self.mode = switches["--mode"]
        if "-O" in switches or "--output" in switches:
            self.output = True
        if "-d" in switches or "--debug" in switches:
            self.debug = True
        if "-s" in switches or "--stack" in switches:
            self.stacktrace = True
        if "-D" in switches or "--diagnostics" in switches:
            self.diagnostics = True
        if "-v" in switches or "--verifyOnly" in switches:
            self.verifyOnly = True
        if "-u" in switches or "--uploadOnly" in switches:
            self.uploadOnly = True
        if "-w" in switches or "--ignoreWarnings" in switches:
            self.ignoreWarnings = True
        try:
            (self.sourceDir, self.s3BucketUrl) = remaining
        except ValueError:
            pass


#######################################################################
# Public functions
#######################################################################

#################
# cli() function
#################


def cli():
    """
    Implements the command-line interface for the ``cback3-amazons3-sync`` script.

    Essentially, this is the "main routine" for the cback3-amazons3-sync script.  It does
    all of the argument processing for the script, and then also implements the
    tool functionality.

    This function looks pretty similiar to ``CedarBackup3.cli.cli()``.  It's not
    easy to refactor this code to make it reusable and also readable, so I've
    decided to just live with the duplication.

    A different error code is returned for each type of failure:

       - ``1``: The Python interpreter version is < 3.7
       - ``2``: Error processing command-line arguments
       - ``3``: Error configuring logging
       - ``5``: Backup was interrupted with a CTRL-C or similar
       - ``6``: Error executing other parts of the script

    *Note:* This script uses print rather than logging to the INFO level, because
    it is interactive.  Underlying Cedar Backup functionality uses the logging
    mechanism exclusively.

    Returns:
        Error code as described above
    """
    try:
        if list(map(int, [sys.version_info[0], sys.version_info[1]])) < [3, 7]:
            sys.stderr.write("Python 3 version 3.7 or greater required.\n")
            return 1
    except:
        # sys.version_info isn't available before 2.0
        sys.stderr.write("Python 3 version 3.7 or greater required.\n")
        return 1

    try:
        options = Options(argumentList=sys.argv[1:])
    except Exception as e:
        _usage()
        sys.stderr.write(" *** Error: %s\n" % e)
        return 2

    if options.help:
        _usage()
        return 0
    if options.version:
        _version()
        return 0
    if options.diagnostics:
        _diagnostics()
        return 0

    if options.stacktrace:
        logfile = setupLogging(options)
    else:
        try:
            logfile = setupLogging(options)
        except Exception as e:
            sys.stderr.write("Error setting up logging: %s\n" % e)
            return 3

    logger.info("Cedar Backup Amazon S3 sync run started.")
    logger.info("Options were [%s]", options)
    logger.info("Logfile is [%s]", logfile)
    Diagnostics().logDiagnostics(method=logger.info)

    if options.stacktrace:
        _executeAction(options)
    else:
        try:
            _executeAction(options)
        except KeyboardInterrupt:
            logger.error("Backup interrupted.")
            logger.info("Cedar Backup Amazon S3 sync run completed with status 5.")
            return 5
        except Exception as e:
            logger.error("Error executing backup: %s", e)
            logger.info("Cedar Backup Amazon S3 sync run completed with status 6.")
            return 6

    logger.info("Cedar Backup Amazon S3 sync run completed with status 0.")
    return 0


#######################################################################
# Utility functions
#######################################################################

####################
# _usage() function
####################


def _usage(fd=sys.stderr):
    """
    Prints usage information for the cback3-amazons3-sync script.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write(" Usage: cback3-amazons3-sync [switches] sourceDir s3bucketUrl\n")
    fd.write("\n")
    fd.write(" Cedar Backup Amazon S3 sync tool.\n")
    fd.write("\n")
    fd.write(" This Cedar Backup utility synchronizes a local directory to an Amazon S3\n")
    fd.write(" bucket.  After the sync is complete, a validation step is taken.  An\n")
    fd.write(" error is reported if the contents of the bucket do not match the\n")
    fd.write(" source directory, or if the indicated size for any file differs.\n")
    fd.write(" This tool is a wrapper over the AWS CLI command-line tool.\n")
    fd.write("\n")
    fd.write(" The following arguments are required:\n")
    fd.write("\n")
    fd.write("   sourceDir            The local source directory on disk (must exist)\n")
    fd.write("   s3BucketUrl          The URL to the target Amazon S3 bucket\n")
    fd.write("\n")
    fd.write(" The following switches are accepted:\n")
    fd.write("\n")
    fd.write("   -h, --help           Display this usage/help listing\n")
    fd.write("   -V, --version        Display version information\n")
    fd.write("   -b, --verbose        Print verbose output as well as logging to disk\n")
    fd.write("   -q, --quiet          Run quietly (display no output to the screen)\n")
    fd.write("   -l, --logfile        Path to logfile (default: %s)\n" % DEFAULT_LOGFILE)
    fd.write(
        "   -o, --owner          Logfile ownership, user:group (default: %s:%s)\n" % (DEFAULT_OWNERSHIP[0], DEFAULT_OWNERSHIP[1])
    )
    fd.write("   -m, --mode           Octal logfile permissions mode (default: %o)\n" % DEFAULT_MODE)
    fd.write("   -O, --output         Record some sub-command (i.e. aws) output to the log\n")
    fd.write("   -d, --debug          Write debugging information to the log (implies --output)\n")
    fd.write(
        "   -s, --stack          Dump Python stack trace instead of swallowing exceptions\n"
    )  # exactly 80 characters in width!
    fd.write("   -D, --diagnostics    Print runtime diagnostics to the screen and exit\n")
    fd.write("   -v, --verifyOnly     Only verify the S3 bucket contents, do not make changes\n")
    fd.write("   -u, --uploadOnly     Only upload new data, do not remove files in the S3 bucket\n")
    fd.write("   -w, --ignoreWarnings Ignore warnings about problematic filename encodings\n")
    fd.write("\n")
    fd.write(" Typical usage would be something like:\n")
    fd.write("\n")
    fd.write("   cback3-amazons3-sync /home/myuser s3://example.com-backup/myuser\n")
    fd.write("\n")
    fd.write(" This will sync the contents of /home/myuser into the indicated bucket.\n")
    fd.write("\n")


######################
# _version() function
######################


def _version(fd=sys.stdout):
    """
    Prints version information for the cback3-amazons3-sync script.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write(" Cedar Backup Amazon S3 sync tool.\n")
    fd.write(" Included with Cedar Backup version %s, released %s.\n" % (VERSION, DATE))
    fd.write("\n")
    fd.write(" Copyright (c) %s %s <%s>.\n" % (COPYRIGHT, AUTHOR, EMAIL))
    fd.write(" See CREDITS for a list of included code and other contributors.\n")
    fd.write(" This is free software; there is NO warranty.  See the\n")
    fd.write(" GNU General Public License version 2 for copying conditions.\n")
    fd.write("\n")
    fd.write(" Use the --help option for usage information.\n")
    fd.write("\n")


##########################
# _diagnostics() function
##########################


def _diagnostics(fd=sys.stdout):
    """
    Prints runtime diagnostics information.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write("Diagnostics:\n")
    fd.write("\n")
    Diagnostics().printDiagnostics(fd=fd, prefix="   ")
    fd.write("\n")


############################
# _executeAction() function
############################


def _executeAction(options):
    """
    Implements the guts of the cback3-amazons3-sync tool.

    Args:
       options (Options object): Program command-line options
    Raises:
       Exception: Under many generic error conditions
    """
    sourceFiles = _buildSourceFiles(options.sourceDir)
    if not options.ignoreWarnings:
        _checkSourceFiles(options.sourceDir, sourceFiles)
    if not options.verifyOnly:
        _synchronizeBucket(options.sourceDir, options.s3BucketUrl, options.uploadOnly)
    _verifyBucketContents(options.sourceDir, sourceFiles, options.s3BucketUrl)


################################
# _buildSourceFiles() function
################################


def _buildSourceFiles(sourceDir):
    """
    Build a list of files in a source directory
    Args:
       sourceDir: Local source directory
    Returns:
        FilesystemList with contents of source directory
    """
    if not os.path.isdir(sourceDir):
        raise ValueError("Source directory does not exist on disk.")
    sourceFiles = FilesystemList()
    sourceFiles.addDirContents(sourceDir)
    return sourceFiles


###############################
# _checkSourceFiles() function
###############################

# pylint: disable=W0613
def _checkSourceFiles(sourceDir, sourceFiles):
    """
    Check source files, trying to guess which ones will have encoding problems.
    Args:
       sourceDir: Local source directory
       sourceDir: Local source directory
    @raises ValueError: If a problem file is found
    @see U{http://opensourcehacker.com/2011/09/16/fix-linux-filename-encodings-with-python/}
    @see U{http://serverfault.com/questions/82821/how-to-tell-the-language-encoding-of-a-filename-on-linux}
    @see U{http://randysofia.com/2014/06/06/aws-cli-and-your-locale/}
    """
    with warnings.catch_warnings():
        encoding = Diagnostics().encoding

        # Note: this was difficult to fully test.  As of the original Python 2
        # implementation, I had a bunch of files on disk that had inconsistent
        # encodings, so I was able to prove that the check warned about these
        # files initially, and then didn't warn after I fixed them.  I didn't
        # save off those files for a unit test (ugh) so by the time of the Python
        # 3 conversion -- which is subtly different because of the different way
        # Python 3 handles unicode strings -- I had to contrive some tests.  I
        # think the tests I wrote are consistent with the earlier problems, and I
        # do get the same result for those tests in both CedarBackup 2 and Cedar
        # Backup 3.  However, I can't be certain the implementation is
        # equivalent.  If someone runs into a situation that this code doesn't
        # handle, you may need to revisit the implementation.

        failed = False
        for entry in sourceFiles:
            path = bytes(Path(entry))
            result = chardet.detect(path)
            source = path.decode(result["encoding"])
            try:
                target = path.decode(encoding)
                if source != target:
                    logger.error("Inconsistent encoding for [%s]: got %s, but need %s", path, result["encoding"], encoding)
                    failed = True
            except Exception:
                logger.error("Inconsistent encoding for [%s]: got %s, but need %s", path, result["encoding"], encoding)
                failed = True

        if not failed:
            logger.info("Completed checking source filename encoding (no problems found).")
        else:
            logger.error("Some filenames have inconsistent encodings and will likely cause sync problems.")
            logger.error("You may be able to fix this by setting a more sensible locale in your environment.")
            logger.error("Aternately, you can rename the problem files to be valid in the indicated locale.")
            logger.error("To ignore this warning and proceed anyway, use --ignoreWarnings")
            raise ValueError("Some filenames have inconsistent encodings and will likely cause sync problems.")


################################
# _synchronizeBucket() function
################################


def _synchronizeBucket(sourceDir, s3BucketUrl, uploadOnly):
    """
    Synchronize a local directory to an Amazon S3 bucket.
    Args:
       sourceDir: Local source directory
       s3BucketUrl: Target S3 bucket URL
    """
    # Since at least early 2015, 'aws s3 sync' is always recursive and the
    # --recursive option is useless.  They eventually removed it and now using
    # it causes an error.  See: https://github.com/aws/aws-cli/issues/1170
    logger.info("Synchronizing local source directory up to Amazon S3.")
    args = ["s3", "sync", sourceDir, s3BucketUrl]
    if uploadOnly:
        logger.info("Sync process will only upload new data, never removing files in S3")
    else:
        logger.info("This will be a full sync process, removing any S3 files that do not exist in the source")
        args += ["--delete"]
    result = executeCommand(AWS_COMMAND, args, returnOutput=False)[0]
    if result != 0:
        raise IOError("Error [%d] calling AWS CLI synchronize bucket." % result)


###################################
# _verifyBucketContents() function
###################################


def _verifyBucketContents(sourceDir, sourceFiles, s3BucketUrl):
    """
    Verify that a source directory is equivalent to an Amazon S3 bucket.
    Args:
       sourceDir: Local source directory
       sourceFiles: Filesystem list containing contents of source directory
       s3BucketUrl: Target S3 bucket URL
    """
    # As of this writing, the documentation for the S3 API that we're using
    # below says that up to 1000 elements at a time are returned, and that we
    # have to manually handle pagination by looking for the IsTruncated element.
    # However, in practice, this is not true.  I have been testing with
    # "aws-cli/1.4.4 Python/2.7.3 Linux/3.2.0-4-686-pae", installed through PIP.
    # No matter how many items exist in my bucket and prefix, I get back a
    # single JSON result.  I've tested with buckets containing nearly 6000
    # elements.
    #
    # If I turn on debugging, it's clear that underneath, something in the API
    # is executing multiple list-object requests against AWS, and stiching
    # results together to give me back the final JSON result.  The debug output
    # clearly incldues multiple requests, and each XML response (except for the
    # final one) contains <IsTruncated>true</IsTruncated>.
    #
    # This feature is not mentioned in the offical changelog for any of the
    # releases going back to 1.0.0.  It appears to happen in the botocore
    # library, but I'll admit I can't actually find the code that implements it.
    # For now, all I can do is rely on this behavior and hope that the
    # documentation is out-of-date.  I'm not going to write code that tries to
    # parse out IsTruncated if I can't actually test that code.

    (bucket, prefix) = s3BucketUrl.replace("s3://", "").split("/", 1)

    query = "Contents[].{Key: Key, Size: Size}"
    args = ["s3api", "list-objects", "--bucket", bucket, "--prefix", prefix, "--query", query]
    (result, data) = executeCommand(AWS_COMMAND, args, returnOutput=True)
    if result != 0:
        raise IOError("Error [%d] calling AWS CLI verify bucket contents." % result)

    contents = {}
    for entry in json.loads("".join(data)):
        key = entry["Key"].replace(prefix, "")
        size = int(entry["Size"])
        contents[key] = size

    failed = False
    for entry in sourceFiles:
        if os.path.isfile(entry):
            key = entry.replace(sourceDir, "")
            size = int(os.stat(entry).st_size)
            if key not in contents:
                logger.error("File was apparently not uploaded: [%s]", entry)
                failed = True
            else:
                if size != contents[key]:
                    logger.error("File size differs [%s]: expected %s bytes but got %s bytes", entry, size, contents[key])
                    failed = True

    if not failed:
        logger.info("Completed verifying Amazon S3 bucket contents (no problems found).")
    else:
        logger.error("There were differences between source directory and target S3 bucket.")
        raise ValueError("There were differences between source directory and target S3 bucket.")


#########################################################################
# Main routine
########################################################################

if __name__ == "__main__":
    sys.exit(cli())
