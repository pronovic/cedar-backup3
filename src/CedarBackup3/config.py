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
# Purpose  : Provides configuration-related objects.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides configuration-related objects.

Summary
=======

   Cedar Backup stores all of its configuration in an XML document typically
   called ``cback3.conf``.  The standard location for this document is in
   ``/etc``, but users can specify a different location if they want to.

   The ``Config`` class is a Python object representation of a Cedar Backup XML
   configuration file.  The representation is two-way: XML data can be used to
   create a ``Config`` object, and then changes to the object can be propogated
   back to disk.  A ``Config`` object can even be used to create a configuration
   file from scratch programmatically.

   The ``Config`` class is intended to be the only Python-language interface to
   Cedar Backup configuration on disk.  Cedar Backup will use the class as its
   internal representation of configuration, and applications external to Cedar
   Backup itself (such as a hypothetical third-party configuration tool written
   in Python or a third party extension module) should also use the class when
   they need to read and write configuration files.

Backwards Compatibility
=======================

   The configuration file format has changed between Cedar Backup 1.x and Cedar
   Backup 2.x.  Any Cedar Backup 1.x configuration file is also a valid Cedar
   Backup 2.x configuration file.  However, it doesn't work to go the other
   direction, as the 2.x configuration files contains additional configuration
   is not accepted by older versions of the software.

XML Configuration Structure
===========================

   A ``Config`` object can either be created "empty", or can be created based on
   XML input (either in the form of a string or read in from a file on disk).
   Generally speaking, the XML input *must* result in a ``Config`` object which
   passes the validations laid out below in the *Validation* section.

   An XML configuration file is composed of seven sections:

      - *reference*: specifies reference information about the file (author, revision, etc)
      - *extensions*: specifies mappings to Cedar Backup extensions (external code)
      - *options*: specifies global configuration options
      - *peers*: specifies the set of peers in a master's backup pool
      - *collect*: specifies configuration related to the collect action
      - *stage*: specifies configuration related to the stage action
      - *store*: specifies configuration related to the store action
      - *purge*: specifies configuration related to the purge action

   Each section is represented by an class in this module, and then the overall
   ``Config`` class is a composition of the various other classes.

   Any configuration section that is missing in the XML document (or has not
   been filled into an "empty" document) will just be set to ``None`` in the
   object representation.  The same goes for individual fields within each
   configuration section.  Keep in mind that the document might not be
   completely valid if some sections or fields aren't filled in - but that
   won't matter until validation takes place (see the *Validation* section
   below).

Unicode vs. String Data
=======================

   By default, all string data that comes out of XML documents in Python is
   unicode data (i.e. ``u"whatever"``).  This is fine for many things, but when
   it comes to filesystem paths, it can cause us some problems.  We really want
   strings to be encoded in the filesystem encoding rather than being unicode.
   So, most elements in configuration which represent filesystem paths are
   coverted to plain strings using :any:`util.encodePath`.  The main exception is
   the various ``absoluteExcludePath`` and ``relativeExcludePath`` lists.  These
   are *not* converted, because they are generally only used for filtering,
   not for filesystem operations.

Validation
==========

   There are two main levels of validation in the ``Config`` class and its
   children.  The first is field-level validation.  Field-level validation
   comes into play when a given field in an object is assigned to or updated.
   We use Python's ``property`` functionality to enforce specific validations on
   field values, and in some places we even use customized list classes to
   enforce validations on list members.  You should expect to catch a
   ``ValueError`` exception when making assignments to configuration class
   fields.

   The second level of validation is post-completion validation.  Certain
   validations don't make sense until a document is fully "complete".  We don't
   want these validations to apply all of the time, because it would make
   building up a document from scratch a real pain.  For instance, we might
   have to do things in the right order to keep from throwing exceptions, etc.

   All of these post-completion validations are encapsulated in the
   :any:`Config.validate` method.  This method can be called at any time by a
   client, and will always be called immediately after creating a ``Config``
   object from XML data and before exporting a ``Config`` object to XML.  This
   way, we get decent ease-of-use but we also don't accept or emit invalid
   configuration files.

   The :any:`Config.validate` implementation actually takes two passes to
   completely validate a configuration document.  The first pass at validation
   is to ensure that the proper sections are filled into the document.  There
   are default requirements, but the caller has the opportunity to override
   these defaults.

   The second pass at validation ensures that any filled-in section contains
   valid data.  Any section which is not set to ``None`` is validated according
   to the rules for that section (see below).

   *Reference Validations*

   No validations.

   *Extensions Validations*

   The list of actions may be either ``None`` or an empty list ``[]`` if desired.
   Each extended action must include a name, a module and a function.  Then, an
   extended action must include either an index or dependency information.
   Which one is required depends on which order mode is configured.

   *Options Validations*

   All fields must be filled in except the rsh command.  The rcp and rsh
   commands are used as default values for all remote peers.  Remote peers can
   also rely on the backup user as the default remote user name if they choose.

   *Peers Validations*

   Local peers must be completely filled in, including both name and collect
   directory.  Remote peers must also fill in the name and collect directory,
   but can leave the remote user and rcp command unset.  In this case, the
   remote user is assumed to match the backup user from the options section and
   rcp command is taken directly from the options section.

   *Collect Validations*

   The target directory must be filled in.  The collect mode, archive mode and
   ignore file are all optional.  The list of absolute paths to exclude and
   patterns to exclude may be either ``None`` or an empty list ``[]`` if desired.

   Each collect directory entry must contain an absolute path to collect, and
   then must either be able to take collect mode, archive mode and ignore file
   configuration from the parent ``CollectConfig`` object, or must set each
   value on its own.  The list of absolute paths to exclude, relative paths to
   exclude and patterns to exclude may be either ``None`` or an empty list ``[]``
   if desired.  Any list of absolute paths to exclude or patterns to exclude
   will be combined with the same list in the ``CollectConfig`` object to make
   the complete list for a given directory.

   *Stage Validations*

   The target directory must be filled in.  There must be at least one peer
   (remote or local) between the two lists of peers.  A list with no entries
   can be either ``None`` or an empty list ``[]`` if desired.

   If a set of peers is provided, this configuration completely overrides
   configuration in the peers configuration section, and the same validations
   apply.

   *Store Validations*

   The device type and drive speed are optional, and all other values are
   required (missing booleans will be set to defaults, which is OK).

   The image writer functionality in the ``writer`` module is supposed to be
   able to handle a device speed of ``None``.  Any caller which needs a "real"
   (non-``None``) value for the device type can use ``DEFAULT_DEVICE_TYPE``,
   which is guaranteed to be sensible.

   *Purge Validations*

   The list of purge directories may be either ``None`` or an empty list ``[]``
   if desired.  All purge directories must contain a path and a retain days
   value.

Module Attributes
=================

Attributes:
   DEFAULT_DEVICE_TYPE: The default device type
   DEFAULT_MEDIA_TYPE: The default media type
   VALID_DEVICE_TYPES: List of valid device types
   VALID_MEDIA_TYPES: List of valid media types
   VALID_COLLECT_MODES: List of valid collect modes
   VALID_COMPRESS_MODES: List of valid compress modes
   VALID_ARCHIVE_MODES: List of valid archive modes
   VALID_ORDER_MODES: List of valid extension order modes

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
import re
from functools import total_ordering

from CedarBackup3.util import (
    UNIT_BYTES,
    UNIT_GBYTES,
    UNIT_KBYTES,
    UNIT_MBYTES,
    AbsolutePathList,
    ObjectTypeList,
    RegexList,
    RegexMatchList,
    UnorderedList,
    checkUnique,
    convertSize,
    displayBytes,
    encodePath,
    parseCommaSeparatedString,
)
from CedarBackup3.writers.util import validateDriveSpeed, validateScsiId
from CedarBackup3.xmlutil import (
    addBooleanNode,
    addContainerNode,
    addIntegerNode,
    addStringNode,
    createInputDom,
    createOutputDom,
    isElement,
    readBoolean,
    readChildren,
    readFirstChild,
    readInteger,
    readString,
    readStringList,
    serializeDom,
)

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.config")

DEFAULT_DEVICE_TYPE = "cdwriter"
DEFAULT_MEDIA_TYPE = "cdrw-74"

VALID_DEVICE_TYPES = ["cdwriter", "dvdwriter"]
VALID_CD_MEDIA_TYPES = ["cdr-74", "cdrw-74", "cdr-80", "cdrw-80"]
VALID_DVD_MEDIA_TYPES = ["dvd+r", "dvd+rw"]
VALID_MEDIA_TYPES = VALID_CD_MEDIA_TYPES + VALID_DVD_MEDIA_TYPES
VALID_COLLECT_MODES = ["daily", "weekly", "incr"]
VALID_ARCHIVE_MODES = ["tar", "targz", "tarbz2"]
VALID_COMPRESS_MODES = ["none", "gzip", "bzip2"]
VALID_ORDER_MODES = ["index", "dependency"]
VALID_BLANK_MODES = ["daily", "weekly"]
VALID_BYTE_UNITS = [UNIT_BYTES, UNIT_KBYTES, UNIT_MBYTES, UNIT_GBYTES]
VALID_FAILURE_MODES = ["none", "all", "daily", "weekly"]

REWRITABLE_MEDIA_TYPES = ["cdrw-74", "cdrw-80", "dvd+rw"]

ACTION_NAME_REGEX = r"^[a-z0-9]*$"


########################################################################
# ByteQuantity class definition
########################################################################


@total_ordering
class ByteQuantity(object):

    """
    Class representing a byte quantity.

    A byte quantity has both a quantity and a byte-related unit.  Units are
    maintained using the constants from util.py.  If no units are provided,
    ``UNIT_BYTES`` is assumed.

    The quantity is maintained internally as a string so that issues of
    precision can be avoided.  It really isn't possible to store a floating
    point number here while being able to losslessly translate back and forth
    between XML and object representations.  (Perhaps the Python 2.4 Decimal
    class would have been an option, but I originally wanted to stay compatible
    with Python 2.3.)

    Even though the quantity is maintained as a string, the string must be in a
    valid floating point positive number.  Technically, any floating point
    string format supported by Python is allowble.  However, it does not make
    sense to have a negative quantity of bytes in this context.

    """

    def __init__(self, quantity=None, units=None):
        """
        Constructor for the ``ByteQuantity`` class.

        Args:
           quantity: Quantity of bytes, something interpretable as a float
           units: Unit of bytes, one of VALID_BYTE_UNITS

        Raises:
           ValueError: If one of the values is invalid
        """
        self._quantity = None
        self._units = None
        self.quantity = quantity
        self.units = units

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ByteQuantity(%s, %s)" % (self.quantity, self.units)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return "%s" % displayBytes(self.bytes)

    def __eq__(self, other):
        """Equals operator, implemented in terms of Python 2-style compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of Python 2-style compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of Python 2-style compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Python 2-style comparison operator.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        elif isinstance(other, ByteQuantity):
            if self.bytes != other.bytes:
                if self.bytes < other.bytes:
                    return -1
                else:
                    return 1
            return 0
        else:
            return self.__cmp__(ByteQuantity(other, UNIT_BYTES))  # will fail if other can't be coverted to float

    def _setQuantity(self, value):
        """
        Property target used to set the quantity
        The value must be interpretable as a float if it is not None
        Raises:
           ValueError: If the value is an empty string
           ValueError: If the value is not a valid floating point number
           ValueError: If the value is less than zero
        """
        if value is None:
            self._quantity = None
        else:
            try:
                floatValue = float(value)  # allow integer, float, string, etc.
            except:
                raise ValueError("Quantity must be interpretable as a float")
            if floatValue < 0.0:
                raise ValueError("Quantity cannot be negative.")
            self._quantity = str(value)  # keep around string

    def _getQuantity(self):
        """
        Property target used to get the quantity.
        """
        return self._quantity

    def _setUnits(self, value):
        """
        Property target used to set the units value.
        If not ``None``, the units value must be one of the values in :any:`VALID_BYTE_UNITS`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._units = UNIT_BYTES
        else:
            if value not in VALID_BYTE_UNITS:
                raise ValueError("Units value must be one of %s." % VALID_BYTE_UNITS)
            self._units = value

    def _getUnits(self):
        """
        Property target used to get the units value.
        """
        return self._units

    def _getBytes(self):
        """
        Property target used to return the byte quantity as a floating point number.
        If there is no quantity set, then a value of 0.0 is returned.
        """
        if self.quantity is not None and self.units is not None:
            return convertSize(self.quantity, self.units, UNIT_BYTES)
        return 0.0

    quantity = property(_getQuantity, _setQuantity, None, doc="Byte quantity, as a string")
    units = property(_getUnits, _setUnits, None, doc="Units for byte quantity, for instance UNIT_BYTES")
    bytes = property(_getBytes, None, None, doc="Byte quantity, as a floating point number.")


########################################################################
# ActionDependencies class definition
########################################################################


@total_ordering
class ActionDependencies(object):

    """
    Class representing dependencies associated with an extended action.

    Execution ordering for extended actions is done in one of two ways: either by using
    index values (lower index gets run first) or by having the extended action specify
    dependencies in terms of other named actions.  This class encapsulates the dependency
    information for an extended action.

    The following restrictions exist on data in this class:

       - Any action name must be a non-empty string matching ``ACTION_NAME_REGEX``

    """

    def __init__(self, beforeList=None, afterList=None):
        """
        Constructor for the ``ActionDependencies`` class.

        Args:
           beforeList: List of named actions that this action must be run before
           afterList: List of named actions that this action must be run after

        Raises:
           ValueError: If one of the values is invalid
        """
        self._beforeList = None
        self._afterList = None
        self.beforeList = beforeList
        self.afterList = afterList

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ActionDependencies(%s, %s)" % (self.beforeList, self.afterList)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.beforeList != other.beforeList:
            if self.beforeList < other.beforeList:
                return -1
            else:
                return 1
        if self.afterList != other.afterList:
            if self.afterList < other.afterList:
                return -1
            else:
                return 1
        return 0

    def _setBeforeList(self, value):
        """
        Property target used to set the "run before" list.
        Either the value must be ``None`` or each element must be a string matching ACTION_NAME_REGEX.
        Raises:
           ValueError: If the value does not match the regular expression
        """
        if value is None:
            self._beforeList = None
        else:
            try:
                saved = self._beforeList
                self._beforeList = RegexMatchList(ACTION_NAME_REGEX, emptyAllowed=False, prefix="Action name")
                self._beforeList.extend(value)
            except Exception as e:
                self._beforeList = saved
                raise e

    def _getBeforeList(self):
        """
        Property target used to get the "run before" list.
        """
        return self._beforeList

    def _setAfterList(self, value):
        """
        Property target used to set the "run after" list.
        Either the value must be ``None`` or each element must be a string matching ACTION_NAME_REGEX.
        Raises:
           ValueError: If the value does not match the regular expression
        """
        if value is None:
            self._afterList = None
        else:
            try:
                saved = self._afterList
                self._afterList = RegexMatchList(ACTION_NAME_REGEX, emptyAllowed=False, prefix="Action name")
                self._afterList.extend(value)
            except Exception as e:
                self._afterList = saved
                raise e

    def _getAfterList(self):
        """
        Property target used to get the "run after" list.
        """
        return self._afterList

    beforeList = property(_getBeforeList, _setBeforeList, None, "List of named actions that this action must be run before.")
    afterList = property(_getAfterList, _setAfterList, None, "List of named actions that this action must be run after.")


########################################################################
# ActionHook class definition
########################################################################


@total_ordering
class ActionHook(object):

    """
    Class representing a hook associated with an action.

    A hook associated with an action is a shell command to be executed either
    before or after a named action is executed.

    The following restrictions exist on data in this class:

       - The action name must be a non-empty string matching ``ACTION_NAME_REGEX``
       - The shell command must be a non-empty string.

    The internal ``before`` and ``after`` instance variables are always set to
    False in this parent class.

    """

    def __init__(self, action=None, command=None):
        """
        Constructor for the ``ActionHook`` class.

        Args:
           action: Action this hook is associated with
           command: Shell command to execute

        Raises:
           ValueError: If one of the values is invalid
        """
        self._action = None
        self._command = None
        self._before = False
        self._after = False
        self.action = action
        self.command = command

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ActionHook(%s, %s, %s, %s)" % (self.action, self.command, self.before, self.after)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.action != other.action:
            if str(self.action or "") < str(other.action or ""):
                return -1
            else:
                return 1
        if self.command != other.command:
            if str(self.command or "") < str(other.command or ""):
                return -1
            else:
                return 1
        if self.before != other.before:
            if self.before < other.before:
                return -1
            else:
                return 1
        if self.after != other.after:
            if self.after < other.after:
                return -1
            else:
                return 1
        return 0

    def _setAction(self, value):
        """
        Property target used to set the action name.
        The value must be a non-empty string if it is not ``None``.
        It must also consist only of lower-case letters and digits.
        Raises:
           ValueError: If the value is an empty string
        """
        pattern = re.compile(ACTION_NAME_REGEX)
        if value is not None:
            if len(value) < 1:
                raise ValueError("The action name must be a non-empty string.")
            if not pattern.search(value):
                raise ValueError("The action name must consist of only lower-case letters and digits.")
        self._action = value

    def _getAction(self):
        """
        Property target used to get the action name.
        """
        return self._action

    def _setCommand(self, value):
        """
        Property target used to set the command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The command must be a non-empty string.")
        self._command = value

    def _getCommand(self):
        """
        Property target used to get the command.
        """
        return self._command

    def _getBefore(self):
        """
        Property target used to get the before flag.
        """
        return self._before

    def _getAfter(self):
        """
        Property target used to get the after flag.
        """
        return self._after

    action = property(_getAction, _setAction, None, "Action this hook is associated with.")
    command = property(_getCommand, _setCommand, None, "Shell command to execute.")
    before = property(_getBefore, None, None, "Indicates whether command should be executed before action.")
    after = property(_getAfter, None, None, "Indicates whether command should be executed after action.")


@total_ordering
class PreActionHook(ActionHook):

    """
    Class representing a pre-action hook associated with an action.

    A hook associated with an action is a shell command to be executed either
    before or after a named action is executed.  In this case, a pre-action hook
    is executed before the named action.

    The following restrictions exist on data in this class:

       - The action name must be a non-empty string consisting of lower-case letters and digits.
       - The shell command must be a non-empty string.

    The internal ``before`` instance variable is always set to True in this
    class.

    """

    def __init__(self, action=None, command=None):
        """
        Constructor for the ``PreActionHook`` class.

        Args:
           action: Action this hook is associated with
           command: Shell command to execute

        Raises:
           ValueError: If one of the values is invalid
        """
        ActionHook.__init__(self, action, command)
        self._before = True

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PreActionHook(%s, %s, %s, %s)" % (self.action, self.command, self.before, self.after)


@total_ordering
class PostActionHook(ActionHook):

    """
    Class representing a pre-action hook associated with an action.

    A hook associated with an action is a shell command to be executed either
    before or after a named action is executed.  In this case, a post-action hook
    is executed after the named action.

    The following restrictions exist on data in this class:

       - The action name must be a non-empty string consisting of lower-case letters and digits.
       - The shell command must be a non-empty string.

    The internal ``before`` instance variable is always set to True in this
    class.

    """

    def __init__(self, action=None, command=None):
        """
        Constructor for the ``PostActionHook`` class.

        Args:
           action: Action this hook is associated with
           command: Shell command to execute

        Raises:
           ValueError: If one of the values is invalid
        """
        ActionHook.__init__(self, action, command)
        self._after = True

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PostActionHook(%s, %s, %s, %s)" % (self.action, self.command, self.before, self.after)


########################################################################
# BlankBehavior class definition
########################################################################


@total_ordering
class BlankBehavior(object):

    """
    Class representing optimized store-action media blanking behavior.

    The following restrictions exist on data in this class:

       - The blanking mode must be a one of the values in ``VALID_BLANK_MODES``
       - The blanking factor must be a positive floating point number

    """

    def __init__(self, blankMode=None, blankFactor=None):
        """
        Constructor for the ``BlankBehavior`` class.

        Args:
           blankMode: Blanking mode
           blankFactor: Blanking factor

        Raises:
           ValueError: If one of the values is invalid
        """
        self._blankMode = None
        self._blankFactor = None
        self.blankMode = blankMode
        self.blankFactor = blankFactor

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "BlankBehavior(%s, %s)" % (self.blankMode, self.blankFactor)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.blankMode != other.blankMode:
            if str(self.blankMode or "") < str(other.blankMode or ""):
                return -1
            else:
                return 1
        if self.blankFactor != other.blankFactor:
            if float(self.blankFactor or 0.0) < float(other.blankFactor or 0.0):
                return -1
            else:
                return 1
        return 0

    def _setBlankMode(self, value):
        """
        Property target used to set the blanking mode.
        The value must be one of ``VALID_BLANK_MODES``.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_BLANK_MODES:
                raise ValueError("Blanking mode must be one of %s." % VALID_BLANK_MODES)
        self._blankMode = value

    def _getBlankMode(self):
        """
        Property target used to get the blanking mode.
        """
        return self._blankMode

    def _setBlankFactor(self, value):
        """
        Property target used to set the blanking factor.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
           ValueError: If the value is not a valid floating point number
           ValueError: If the value is less than zero
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Blanking factor must be a non-empty string.")
            floatValue = float(value)
            if floatValue < 0.0:
                raise ValueError("Blanking factor cannot be negative.")
        self._blankFactor = value  # keep around string

    def _getBlankFactor(self):
        """
        Property target used to get the blanking factor.
        """
        return self._blankFactor

    blankMode = property(_getBlankMode, _setBlankMode, None, "Blanking mode")
    blankFactor = property(_getBlankFactor, _setBlankFactor, None, "Blanking factor")


########################################################################
# ExtendedAction class definition
########################################################################


@total_ordering
class ExtendedAction(object):

    """
    Class representing an extended action.

    Essentially, an extended action needs to allow the following to happen::

       exec("from %s import %s" % (module, function))
       exec("%s(action, configPath")" % function)

    The following restrictions exist on data in this class:

       - The action name must be a non-empty string consisting of lower-case letters and digits.
       - The module must be a non-empty string and a valid Python identifier.
       - The function must be an on-empty string and a valid Python identifier.
       - If set, the index must be a positive integer.
       - If set, the dependencies attribute must be an ``ActionDependencies`` object.

    """

    def __init__(self, name=None, module=None, function=None, index=None, dependencies=None):
        """
        Constructor for the ``ExtendedAction`` class.

        Args:
           name: Name of the extended action
           module: Name of the module containing the extended action function
           function: Name of the extended action function
           index: Index of action, used for execution ordering
           dependencies: Dependencies for action, used for execution ordering

        Raises:
           ValueError: If one of the values is invalid
        """
        self._name = None
        self._module = None
        self._function = None
        self._index = None
        self._dependencies = None
        self.name = name
        self.module = module
        self.function = function
        self.index = index
        self.dependencies = dependencies

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ExtendedAction(%s, %s, %s, %s, %s)" % (self.name, self.module, self.function, self.index, self.dependencies)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.name != other.name:
            if str(self.name or "") < str(other.name or ""):
                return -1
            else:
                return 1
        if self.module != other.module:
            if str(self.module or "") < str(other.module or ""):
                return -1
            else:
                return 1
        if self.function != other.function:
            if str(self.function or "") < str(other.function or ""):
                return -1
            else:
                return 1
        if self.index != other.index:
            if int(self.index or 0) < int(other.index or 0):
                return -1
            else:
                return 1
        if self.dependencies != other.dependencies:
            if self.dependencies < other.dependencies:
                return -1
            else:
                return 1
        return 0

    def _setName(self, value):
        """
        Property target used to set the action name.
        The value must be a non-empty string if it is not ``None``.
        It must also consist only of lower-case letters and digits.
        Raises:
           ValueError: If the value is an empty string
        """
        pattern = re.compile(ACTION_NAME_REGEX)
        if value is not None:
            if len(value) < 1:
                raise ValueError("The action name must be a non-empty string.")
            if not pattern.search(value):
                raise ValueError("The action name must consist of only lower-case letters and digits.")
        self._name = value

    def _getName(self):
        """
        Property target used to get the action name.
        """
        return self._name

    def _setModule(self, value):
        """
        Property target used to set the module name.
        The value must be a non-empty string if it is not ``None``.
        It must also be a valid Python identifier.
        Raises:
           ValueError: If the value is an empty string
        """
        pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\.[A-Za-z_][A-Za-z0-9_]*)*$")
        if value is not None:
            if len(value) < 1:
                raise ValueError("The module name must be a non-empty string.")
            if not pattern.search(value):
                raise ValueError("The module name must be a valid Python identifier.")
        self._module = value

    def _getModule(self):
        """
        Property target used to get the module name.
        """
        return self._module

    def _setFunction(self, value):
        """
        Property target used to set the function name.
        The value must be a non-empty string if it is not ``None``.
        It must also be a valid Python identifier.
        Raises:
           ValueError: If the value is an empty string
        """
        pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if value is not None:
            if len(value) < 1:
                raise ValueError("The function name must be a non-empty string.")
            if not pattern.search(value):
                raise ValueError("The function name must be a valid Python identifier.")
        self._function = value

    def _getFunction(self):
        """
        Property target used to get the function name.
        """
        return self._function

    def _setIndex(self, value):
        """
        Property target used to set the action index.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._index = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Action index value must be an integer >= 0.")
            if value < 0:
                raise ValueError("Action index value must be an integer >= 0.")
            self._index = value

    def _getIndex(self):
        """
        Property target used to get the action index.
        """
        return self._index

    def _setDependencies(self, value):
        """
        Property target used to set the action dependencies information.
        If not ``None``, the value must be a ``ActionDependecies`` object.
        Raises:
           ValueError: If the value is not a ``ActionDependencies`` object
        """
        if value is None:
            self._dependencies = None
        else:
            if not isinstance(value, ActionDependencies):
                raise ValueError("Value must be a ``ActionDependencies`` object.")
            self._dependencies = value

    def _getDependencies(self):
        """
        Property target used to get action dependencies information.
        """
        return self._dependencies

    name = property(_getName, _setName, None, "Name of the extended action.")
    module = property(_getModule, _setModule, None, "Name of the module containing the extended action function.")
    function = property(_getFunction, _setFunction, None, "Name of the extended action function.")
    index = property(_getIndex, _setIndex, None, "Index of action, used for execution ordering.")
    dependencies = property(_getDependencies, _setDependencies, None, "Dependencies for action, used for execution ordering.")


########################################################################
# CommandOverride class definition
########################################################################


@total_ordering
class CommandOverride(object):

    """
    Class representing a piece of Cedar Backup command override configuration.

    The following restrictions exist on data in this class:

       - The absolute path must be absolute

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, command=None, absolutePath=None):
        """
        Constructor for the ``CommandOverride`` class.

        Args:
           command: Name of command to be overridden
           absolutePath: Absolute path of the overrridden command

        Raises:
           ValueError: If one of the values is invalid
        """
        self._command = None
        self._absolutePath = None
        self.command = command
        self.absolutePath = absolutePath

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "CommandOverride(%s, %s)" % (self.command, self.absolutePath)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.command != other.command:
            if str(self.command or "") < str(other.command or ""):
                return -1
            else:
                return 1
        if self.absolutePath != other.absolutePath:
            if str(self.absolutePath or "") < str(other.absolutePath or ""):
                return -1
            else:
                return 1
        return 0

    def _setCommand(self, value):
        """
        Property target used to set the command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The command must be a non-empty string.")
        self._command = value

    def _getCommand(self):
        """
        Property target used to get the command.
        """
        return self._command

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
                raise ValueError("Not an absolute path: [%s]" % value)
        self._absolutePath = encodePath(value)

    def _getAbsolutePath(self):
        """
        Property target used to get the absolute path.
        """
        return self._absolutePath

    command = property(_getCommand, _setCommand, None, doc="Name of command to be overridden.")
    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, doc="Absolute path of the overrridden command.")


########################################################################
# CollectFile class definition
########################################################################


@total_ordering
class CollectFile(object):

    """
    Class representing a Cedar Backup collect file.

    The following restrictions exist on data in this class:

       - Absolute paths must be absolute
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The archive mode must be one of the values in :any:`VALID_ARCHIVE_MODES`.

    """

    def __init__(self, absolutePath=None, collectMode=None, archiveMode=None):
        """
        Constructor for the ``CollectFile`` class.

        Args:
           absolutePath: Absolute path of the file to collect
           collectMode: Overridden collect mode for this file
           archiveMode: Overridden archive mode for this file

        Raises:
           ValueError: If one of the values is invalid
        """
        self._absolutePath = None
        self._collectMode = None
        self._archiveMode = None
        self.absolutePath = absolutePath
        self.collectMode = collectMode
        self.archiveMode = archiveMode

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "CollectFile(%s, %s, %s)" % (self.absolutePath, self.collectMode, self.archiveMode)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.archiveMode != other.archiveMode:
            if str(self.archiveMode or "") < str(other.archiveMode or ""):
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
                raise ValueError("Not an absolute path: [%s]" % value)
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

    def _setArchiveMode(self, value):
        """
        Property target used to set the archive mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_ARCHIVE_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_ARCHIVE_MODES:
                raise ValueError("Archive mode must be one of %s." % VALID_ARCHIVE_MODES)
        self._archiveMode = value

    def _getArchiveMode(self):
        """
        Property target used to get the archive mode.
        """
        return self._archiveMode

    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, doc="Absolute path of the file to collect.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this file.")
    archiveMode = property(_getArchiveMode, _setArchiveMode, None, doc="Overridden archive mode for this file.")


########################################################################
# CollectDir class definition
########################################################################


@total_ordering
class CollectDir(object):

    """
    Class representing a Cedar Backup collect directory.

    The following restrictions exist on data in this class:

       - Absolute paths must be absolute
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The archive mode must be one of the values in :any:`VALID_ARCHIVE_MODES`.
       - The ignore file must be a non-empty string.

    For the ``absoluteExcludePaths`` list, validation is accomplished through the
    :any:`util.AbsolutePathList` list implementation that overrides common list
    methods and transparently does the absolute path validation for us.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(
        self,
        absolutePath=None,
        collectMode=None,
        archiveMode=None,
        ignoreFile=None,
        absoluteExcludePaths=None,
        relativeExcludePaths=None,
        excludePatterns=None,
        linkDepth=None,
        dereference=False,
        recursionLevel=None,
    ):
        """
        Constructor for the ``CollectDir`` class.

        Args:
           absolutePath: Absolute path of the directory to collect
           collectMode: Overridden collect mode for this directory
           archiveMode: Overridden archive mode for this directory
           ignoreFile: Overidden ignore file name for this directory
           linkDepth: Maximum at which soft links should be followed
           dereference: Whether to dereference links that are followed
           absoluteExcludePaths: List of absolute paths to exclude
           relativeExcludePaths: List of relative paths to exclude
           excludePatterns: List of regular expression patterns to exclude

        Raises:
           ValueError: If one of the values is invalid
        """
        self._absolutePath = None
        self._collectMode = None
        self._archiveMode = None
        self._ignoreFile = None
        self._linkDepth = None
        self._dereference = None
        self._recursionLevel = None
        self._absoluteExcludePaths = None
        self._relativeExcludePaths = None
        self._excludePatterns = None
        self.absolutePath = absolutePath
        self.collectMode = collectMode
        self.archiveMode = archiveMode
        self.ignoreFile = ignoreFile
        self.linkDepth = linkDepth
        self.dereference = dereference
        self.recursionLevel = recursionLevel
        self.absoluteExcludePaths = absoluteExcludePaths
        self.relativeExcludePaths = relativeExcludePaths
        self.excludePatterns = excludePatterns

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "CollectDir(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.absolutePath,
            self.collectMode,
            self.archiveMode,
            self.ignoreFile,
            self.absoluteExcludePaths,
            self.relativeExcludePaths,
            self.excludePatterns,
            self.linkDepth,
            self.dereference,
            self.recursionLevel,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.archiveMode != other.archiveMode:
            if str(self.archiveMode or "") < str(other.archiveMode or ""):
                return -1
            else:
                return 1
        if self.ignoreFile != other.ignoreFile:
            if str(self.ignoreFile or "") < str(other.ignoreFile or ""):
                return -1
            else:
                return 1
        if self.linkDepth != other.linkDepth:
            if int(self.linkDepth or 0) < int(other.linkDepth or 0):
                return -1
            else:
                return 1
        if self.dereference != other.dereference:
            if self.dereference < other.dereference:
                return -1
            else:
                return 1
        if self.recursionLevel != other.recursionLevel:
            if int(self.recursionLevel or 0) < int(other.recursionLevel or 0):
                return -1
            else:
                return 1
        if self.absoluteExcludePaths != other.absoluteExcludePaths:
            if self.absoluteExcludePaths < other.absoluteExcludePaths:
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
                raise ValueError("Not an absolute path: [%s]" % value)
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

    def _setArchiveMode(self, value):
        """
        Property target used to set the archive mode.
        If not ``None``, the mode must be one of the values in :any:`VALID_ARCHIVE_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_ARCHIVE_MODES:
                raise ValueError("Archive mode must be one of %s." % VALID_ARCHIVE_MODES)
        self._archiveMode = value

    def _getArchiveMode(self):
        """
        Property target used to get the archive mode.
        """
        return self._archiveMode

    def _setIgnoreFile(self, value):
        """
        Property target used to set the ignore file.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The ignore file must be a non-empty string.")
        self._ignoreFile = value

    def _getIgnoreFile(self):
        """
        Property target used to get the ignore file.
        """
        return self._ignoreFile

    def _setLinkDepth(self, value):
        """
        Property target used to set the link depth.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._linkDepth = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Link depth value must be an integer >= 0.")
            if value < 0:
                raise ValueError("Link depth value must be an integer >= 0.")
            self._linkDepth = value

    def _getLinkDepth(self):
        """
        Property target used to get the action linkDepth.
        """
        return self._linkDepth

    def _setDereference(self, value):
        """
        Property target used to set the dereference flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._dereference = True
        else:
            self._dereference = False

    def _getDereference(self):
        """
        Property target used to get the dereference flag.
        """
        return self._dereference

    def _setRecursionLevel(self, value):
        """
        Property target used to set the recursionLevel.
        The value must be an integer.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._recursionLevel = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Recusion level value must be an integer.")
            self._recursionLevel = value

    def _getRecursionLevel(self):
        """
        Property target used to get the action recursionLevel.
        """
        return self._recursionLevel

    def _setAbsoluteExcludePaths(self, value):
        """
        Property target used to set the absolute exclude paths list.
        Either the value must be ``None`` or each element must be an absolute path.
        Elements do not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
        """
        if value is None:
            self._absoluteExcludePaths = None
        else:
            try:
                saved = self._absoluteExcludePaths
                self._absoluteExcludePaths = AbsolutePathList()
                self._absoluteExcludePaths.extend(value)
            except Exception as e:
                self._absoluteExcludePaths = saved
                raise e

    def _getAbsoluteExcludePaths(self):
        """
        Property target used to get the absolute exclude paths list.
        """
        return self._absoluteExcludePaths

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

    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, doc="Absolute path of the directory to collect.")
    collectMode = property(_getCollectMode, _setCollectMode, None, doc="Overridden collect mode for this directory.")
    archiveMode = property(_getArchiveMode, _setArchiveMode, None, doc="Overridden archive mode for this directory.")
    ignoreFile = property(_getIgnoreFile, _setIgnoreFile, None, doc="Overridden ignore file name for this directory.")
    linkDepth = property(_getLinkDepth, _setLinkDepth, None, doc="Maximum at which soft links should be followed.")
    dereference = property(_getDereference, _setDereference, None, doc="Whether to dereference links that are followed.")
    recursionLevel = property(
        _getRecursionLevel, _setRecursionLevel, None, "Recursion level to use for recursive directory collection"
    )
    absoluteExcludePaths = property(_getAbsoluteExcludePaths, _setAbsoluteExcludePaths, None, "List of absolute paths to exclude.")
    relativeExcludePaths = property(_getRelativeExcludePaths, _setRelativeExcludePaths, None, "List of relative paths to exclude.")
    excludePatterns = property(_getExcludePatterns, _setExcludePatterns, None, "List of regular expression patterns to exclude.")


########################################################################
# PurgeDir class definition
########################################################################


@total_ordering
class PurgeDir(object):

    """
    Class representing a Cedar Backup purge directory.

    The following restrictions exist on data in this class:

       - The absolute path must be an absolute path
       - The retain days value must be an integer >= 0.

    """

    def __init__(self, absolutePath=None, retainDays=None):
        """
        Constructor for the ``PurgeDir`` class.

        Args:
           absolutePath: Absolute path of the directory to be purged
           retainDays: Number of days content within directory should be retained

        Raises:
           ValueError: If one of the values is invalid
        """
        self._absolutePath = None
        self._retainDays = None
        self.absolutePath = absolutePath
        self.retainDays = retainDays

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PurgeDir(%s, %s)" % (self.absolutePath, self.retainDays)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.retainDays != other.retainDays:
            if int(self.retainDays or 0) < int(other.retainDays or 0):
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
                raise ValueError("Absolute path must, er, be an absolute path.")
        self._absolutePath = encodePath(value)

    def _getAbsolutePath(self):
        """
        Property target used to get the absolute path.
        """
        return self._absolutePath

    def _setRetainDays(self, value):
        """
        Property target used to set the retain days value.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._retainDays = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Retain days value must be an integer >= 0.")
            if value < 0:
                raise ValueError("Retain days value must be an integer >= 0.")
            self._retainDays = value

    def _getRetainDays(self):
        """
        Property target used to get the absolute path.
        """
        return self._retainDays

    absolutePath = property(_getAbsolutePath, _setAbsolutePath, None, "Absolute path of directory to purge.")
    retainDays = property(_getRetainDays, _setRetainDays, None, "Number of days content within directory should be retained.")


########################################################################
# LocalPeer class definition
########################################################################


@total_ordering
class LocalPeer(object):

    """
    Class representing a Cedar Backup peer.

    The following restrictions exist on data in this class:

       - The peer name must be a non-empty string.
       - The collect directory must be an absolute path.
       - The ignore failure mode must be one of the values in ``VALID_FAILURE_MODES``.

    """

    def __init__(self, name=None, collectDir=None, ignoreFailureMode=None):
        """
        Constructor for the ``LocalPeer`` class.

        Args:
           name: Name of the peer, typically a valid hostname
           collectDir: Collect directory to stage files from on peer
           ignoreFailureMode: Ignore failure mode for peer

        Raises:
           ValueError: If one of the values is invalid
        """
        self._name = None
        self._collectDir = None
        self._ignoreFailureMode = None
        self.name = name
        self.collectDir = collectDir
        self.ignoreFailureMode = ignoreFailureMode

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "LocalPeer(%s, %s, %s)" % (self.name, self.collectDir, self.ignoreFailureMode)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.name != other.name:
            if str(self.name or "") < str(other.name or ""):
                return -1
            else:
                return 1
        if self.collectDir != other.collectDir:
            if str(self.collectDir or "") < str(other.collectDir or ""):
                return -1
            else:
                return 1
        if self.ignoreFailureMode != other.ignoreFailureMode:
            if str(self.ignoreFailureMode or "") < str(other.ignoreFailureMode or ""):
                return -1
            else:
                return 1
        return 0

    def _setName(self, value):
        """
        Property target used to set the peer name.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The peer name must be a non-empty string.")
        self._name = value

    def _getName(self):
        """
        Property target used to get the peer name.
        """
        return self._name

    def _setCollectDir(self, value):
        """
        Property target used to set the collect directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
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

    def _setIgnoreFailureMode(self, value):
        """
        Property target used to set the ignoreFailure mode.
        If not ``None``, the mode must be one of the values in ``VALID_FAILURE_MODES``.
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

    name = property(_getName, _setName, None, "Name of the peer, typically a valid hostname.")
    collectDir = property(_getCollectDir, _setCollectDir, None, "Collect directory to stage files from on peer.")
    ignoreFailureMode = property(_getIgnoreFailureMode, _setIgnoreFailureMode, None, "Ignore failure mode for peer.")


########################################################################
# RemotePeer class definition
########################################################################


@total_ordering
class RemotePeer(object):

    """
    Class representing a Cedar Backup peer.

    The following restrictions exist on data in this class:

       - The peer name must be a non-empty string.
       - The collect directory must be an absolute path.
       - The remote user must be a non-empty string.
       - The rcp command must be a non-empty string.
       - The rsh command must be a non-empty string.
       - The cback command must be a non-empty string.
       - Any managed action name must be a non-empty string matching ``ACTION_NAME_REGEX``
       - The ignore failure mode must be one of the values in ``VALID_FAILURE_MODES``.

    """

    def __init__(
        self,
        name=None,
        collectDir=None,
        remoteUser=None,
        rcpCommand=None,
        rshCommand=None,
        cbackCommand=None,
        managed=False,
        managedActions=None,
        ignoreFailureMode=None,
    ):
        """
        Constructor for the ``RemotePeer`` class.

        Args:
           name: Name of the peer, must be a valid hostname
           collectDir: Collect directory to stage files from on peer
           remoteUser: Name of backup user on remote peer
           rcpCommand: Overridden rcp-compatible copy command for peer
           rshCommand: Overridden rsh-compatible remote shell command for peer
           cbackCommand: Overridden cback-compatible command to use on remote peer
           managed: Indicates whether this is a managed peer
           managedActions: Overridden set of actions that are managed on the peer
           ignoreFailureMode: Ignore failure mode for peer

        Raises:
           ValueError: If one of the values is invalid
        """
        self._name = None
        self._collectDir = None
        self._remoteUser = None
        self._rcpCommand = None
        self._rshCommand = None
        self._cbackCommand = None
        self._managed = None
        self._managedActions = None
        self._ignoreFailureMode = None
        self.name = name
        self.collectDir = collectDir
        self.remoteUser = remoteUser
        self.rcpCommand = rcpCommand
        self.rshCommand = rshCommand
        self.cbackCommand = cbackCommand
        self.managed = managed
        self.managedActions = managedActions
        self.ignoreFailureMode = ignoreFailureMode

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "RemotePeer(%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.name,
            self.collectDir,
            self.remoteUser,
            self.rcpCommand,
            self.rshCommand,
            self.cbackCommand,
            self.managed,
            self.managedActions,
            self.ignoreFailureMode,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.name != other.name:
            if str(self.name or "") < str(other.name or ""):
                return -1
            else:
                return 1
        if self.collectDir != other.collectDir:
            if str(self.collectDir or "") < str(other.collectDir or ""):
                return -1
            else:
                return 1
        if self.remoteUser != other.remoteUser:
            if str(self.remoteUser or "") < str(other.remoteUser or ""):
                return -1
            else:
                return 1
        if self.rcpCommand != other.rcpCommand:
            if str(self.rcpCommand or "") < str(other.rcpCommand or ""):
                return -1
            else:
                return 1
        if self.rshCommand != other.rshCommand:
            if str(self.rshCommand or "") < str(other.rshCommand or ""):
                return -1
            else:
                return 1
        if self.cbackCommand != other.cbackCommand:
            if str(self.cbackCommand or "") < str(other.cbackCommand or ""):
                return -1
            else:
                return 1
        if self.managed != other.managed:
            if str(self.managed or "") < str(other.managed or ""):
                return -1
            else:
                return 1
        if self.managedActions != other.managedActions:
            if self.managedActions < other.managedActions:
                return -1
            else:
                return 1
        if self.ignoreFailureMode != other.ignoreFailureMode:
            if str(self.ignoreFailureMode or "") < str(other.ignoreFailureMode or ""):
                return -1
            else:
                return 1
        return 0

    def _setName(self, value):
        """
        Property target used to set the peer name.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The peer name must be a non-empty string.")
        self._name = value

    def _getName(self):
        """
        Property target used to get the peer name.
        """
        return self._name

    def _setCollectDir(self, value):
        """
        Property target used to set the collect directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
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

    def _setRemoteUser(self, value):
        """
        Property target used to set the remote user.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The remote user must be a non-empty string.")
        self._remoteUser = value

    def _getRemoteUser(self):
        """
        Property target used to get the remote user.
        """
        return self._remoteUser

    def _setRcpCommand(self, value):
        """
        Property target used to set the rcp command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The rcp command must be a non-empty string.")
        self._rcpCommand = value

    def _getRcpCommand(self):
        """
        Property target used to get the rcp command.
        """
        return self._rcpCommand

    def _setRshCommand(self, value):
        """
        Property target used to set the rsh command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The rsh command must be a non-empty string.")
        self._rshCommand = value

    def _getRshCommand(self):
        """
        Property target used to get the rsh command.
        """
        return self._rshCommand

    def _setCbackCommand(self, value):
        """
        Property target used to set the cback command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The cback command must be a non-empty string.")
        self._cbackCommand = value

    def _getCbackCommand(self):
        """
        Property target used to get the cback command.
        """
        return self._cbackCommand

    def _setManaged(self, value):
        """
        Property target used to set the managed flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._managed = True
        else:
            self._managed = False

    def _getManaged(self):
        """
        Property target used to get the managed flag.
        """
        return self._managed

    def _setManagedActions(self, value):
        """
        Property target used to set the managed actions list.
        Elements do not have to exist on disk at the time of assignment.
        """
        if value is None:
            self._managedActions = None
        else:
            try:
                saved = self._managedActions
                self._managedActions = RegexMatchList(ACTION_NAME_REGEX, emptyAllowed=False, prefix="Action name")
                self._managedActions.extend(value)
            except Exception as e:
                self._managedActions = saved
                raise e

    def _getManagedActions(self):
        """
        Property target used to get the managed actions list.
        """
        return self._managedActions

    def _setIgnoreFailureMode(self, value):
        """
        Property target used to set the ignoreFailure mode.
        If not ``None``, the mode must be one of the values in ``VALID_FAILURE_MODES``.
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

    name = property(_getName, _setName, None, "Name of the peer, must be a valid hostname.")
    collectDir = property(_getCollectDir, _setCollectDir, None, "Collect directory to stage files from on peer.")
    remoteUser = property(_getRemoteUser, _setRemoteUser, None, "Name of backup user on remote peer.")
    rcpCommand = property(_getRcpCommand, _setRcpCommand, None, "Overridden rcp-compatible copy command for peer.")
    rshCommand = property(_getRshCommand, _setRshCommand, None, "Overridden rsh-compatible remote shell command for peer.")
    cbackCommand = property(_getCbackCommand, _setCbackCommand, None, "Overridden cback-compatible command to use on remote peer.")
    managed = property(_getManaged, _setManaged, None, "Indicates whether this is a managed peer.")
    managedActions = property(
        _getManagedActions, _setManagedActions, None, "Overridden set of actions that are managed on the peer."
    )
    ignoreFailureMode = property(_getIgnoreFailureMode, _setIgnoreFailureMode, None, "Ignore failure mode for peer.")


########################################################################
# ReferenceConfig class definition
########################################################################


@total_ordering
class ReferenceConfig(object):

    """
    Class representing a Cedar Backup reference configuration.

    The reference information is just used for saving off metadata about
    configuration and exists mostly for backwards-compatibility with Cedar
    Backup 1.x.

    """

    def __init__(self, author=None, revision=None, description=None, generator=None):
        """
        Constructor for the ``ReferenceConfig`` class.

        Args:
           author: Author of the configuration file
           revision: Revision of the configuration file
           description: Description of the configuration file
           generator: Tool that generated the configuration file
        """
        self._author = None
        self._revision = None
        self._description = None
        self._generator = None
        self.author = author
        self.revision = revision
        self.description = description
        self.generator = generator

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ReferenceConfig(%s, %s, %s, %s)" % (self.author, self.revision, self.description, self.generator)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.author != other.author:
            if str(self.author or "") < str(other.author or ""):
                return -1
            else:
                return 1
        if self.revision != other.revision:
            if str(self.revision or "") < str(other.revision or ""):
                return -1
            else:
                return 1
        if self.description != other.description:
            if str(self.description or "") < str(other.description or ""):
                return -1
            else:
                return 1
        if self.generator != other.generator:
            if str(self.generator or "") < str(other.generator or ""):
                return -1
            else:
                return 1
        return 0

    def _setAuthor(self, value):
        """
        Property target used to set the author value.
        No validations.
        """
        self._author = value

    def _getAuthor(self):
        """
        Property target used to get the author value.
        """
        return self._author

    def _setRevision(self, value):
        """
        Property target used to set the revision value.
        No validations.
        """
        self._revision = value

    def _getRevision(self):
        """
        Property target used to get the revision value.
        """
        return self._revision

    def _setDescription(self, value):
        """
        Property target used to set the description value.
        No validations.
        """
        self._description = value

    def _getDescription(self):
        """
        Property target used to get the description value.
        """
        return self._description

    def _setGenerator(self, value):
        """
        Property target used to set the generator value.
        No validations.
        """
        self._generator = value

    def _getGenerator(self):
        """
        Property target used to get the generator value.
        """
        return self._generator

    author = property(_getAuthor, _setAuthor, None, "Author of the configuration file.")
    revision = property(_getRevision, _setRevision, None, "Revision of the configuration file.")
    description = property(_getDescription, _setDescription, None, "Description of the configuration file.")
    generator = property(_getGenerator, _setGenerator, None, "Tool that generated the configuration file.")


########################################################################
# ExtensionsConfig class definition
########################################################################


@total_ordering
class ExtensionsConfig(object):

    """
    Class representing Cedar Backup extensions configuration.

    Extensions configuration is used to specify "extended actions" implemented
    by code external to Cedar Backup.  For instance, a hypothetical third party
    might write extension code to collect database repository data.  If they
    write a properly-formatted extension function, they can use the extension
    configuration to map a command-line Cedar Backup action (i.e. "database")
    to their function.

    The following restrictions exist on data in this class:

       - If set, the order mode must be one of the values in ``VALID_ORDER_MODES``
       - The actions list must be a list of ``ExtendedAction`` objects.

    """

    def __init__(self, actions=None, orderMode=None):
        """
        Constructor for the ``ExtensionsConfig`` class.
        Args:
           actions: List of extended actions
        """
        self._orderMode = None
        self._actions = None
        self.orderMode = orderMode
        self.actions = actions

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "ExtensionsConfig(%s, %s)" % (self.orderMode, self.actions)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.orderMode != other.orderMode:
            if str(self.orderMode or "") < str(other.orderMode or ""):
                return -1
            else:
                return 1
        if self.actions != other.actions:
            if self.actions < other.actions:
                return -1
            else:
                return 1
        return 0

    def _setOrderMode(self, value):
        """
        Property target used to set the order mode.
        The value must be one of :any:`VALID_ORDER_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_ORDER_MODES:
                raise ValueError("Order mode must be one of %s." % VALID_ORDER_MODES)
        self._orderMode = value

    def _getOrderMode(self):
        """
        Property target used to get the order mode.
        """
        return self._orderMode

    def _setActions(self, value):
        """
        Property target used to set the actions list.
        Either the value must be ``None`` or each element must be an ``ExtendedAction``.
        Raises:
           ValueError: If the value is not a ``ExtendedAction``
        """
        if value is None:
            self._actions = None
        else:
            try:
                saved = self._actions
                self._actions = ObjectTypeList(ExtendedAction, "ExtendedAction")
                self._actions.extend(value)
            except Exception as e:
                self._actions = saved
                raise e

    def _getActions(self):
        """
        Property target used to get the actions list.
        """
        return self._actions

    orderMode = property(_getOrderMode, _setOrderMode, None, "Order mode for extensions, to control execution ordering.")
    actions = property(_getActions, _setActions, None, "List of extended actions.")


########################################################################
# OptionsConfig class definition
########################################################################


@total_ordering
class OptionsConfig(object):

    """
    Class representing a Cedar Backup global options configuration.

    The options section is used to store global configuration options and
    defaults that can be applied to other sections.

    The following restrictions exist on data in this class:

       - The working directory must be an absolute path.
       - The starting day must be a day of the week in English, i.e. ``"monday"``, ``"tuesday"``, etc.
       - All of the other values must be non-empty strings if they are set to something other than ``None``.
       - The overrides list must be a list of ``CommandOverride`` objects.
       - The hooks list must be a list of ``ActionHook`` objects.
       - The cback command must be a non-empty string.
       - Any managed action name must be a non-empty string matching ``ACTION_NAME_REGEX``

    """

    def __init__(
        self,
        startingDay=None,
        workingDir=None,
        backupUser=None,
        backupGroup=None,
        rcpCommand=None,
        overrides=None,
        hooks=None,
        rshCommand=None,
        cbackCommand=None,
        managedActions=None,
    ):
        """
        Constructor for the ``OptionsConfig`` class.

        Args:
           startingDay: Day that starts the week
           workingDir: Working (temporary) directory to use for backups
           backupUser: Effective user that backups should run as
           backupGroup: Effective group that backups should run as
           rcpCommand: Default rcp-compatible copy command for staging
           rshCommand: Default rsh-compatible command to use for remote shells
           cbackCommand: Default cback-compatible command to use on managed remote peers
           overrides: List of configured command path overrides, if any
           hooks: List of configured pre- and post-action hooks
           managedActions: Default set of actions that are managed on remote peers

        Raises:
           ValueError: If one of the values is invalid
        """
        self._startingDay = None
        self._workingDir = None
        self._backupUser = None
        self._backupGroup = None
        self._rcpCommand = None
        self._rshCommand = None
        self._cbackCommand = None
        self._overrides = None
        self._hooks = None
        self._managedActions = None
        self.startingDay = startingDay
        self.workingDir = workingDir
        self.backupUser = backupUser
        self.backupGroup = backupGroup
        self.rcpCommand = rcpCommand
        self.rshCommand = rshCommand
        self.cbackCommand = cbackCommand
        self.overrides = overrides
        self.hooks = hooks
        self.managedActions = managedActions

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "OptionsConfig(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.startingDay,
            self.workingDir,
            self.backupUser,
            self.backupGroup,
            self.rcpCommand,
            self.overrides,
            self.hooks,
            self.rshCommand,
            self.cbackCommand,
            self.managedActions,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.startingDay != other.startingDay:
            if str(self.startingDay or "") < str(other.startingDay or ""):
                return -1
            else:
                return 1
        if self.workingDir != other.workingDir:
            if str(self.workingDir or "") < str(other.workingDir or ""):
                return -1
            else:
                return 1
        if self.backupUser != other.backupUser:
            if str(self.backupUser or "") < str(other.backupUser or ""):
                return -1
            else:
                return 1
        if self.backupGroup != other.backupGroup:
            if str(self.backupGroup or "") < str(other.backupGroup or ""):
                return -1
            else:
                return 1
        if self.rcpCommand != other.rcpCommand:
            if str(self.rcpCommand or "") < str(other.rcpCommand or ""):
                return -1
            else:
                return 1
        if self.rshCommand != other.rshCommand:
            if str(self.rshCommand or "") < str(other.rshCommand or ""):
                return -1
            else:
                return 1
        if self.cbackCommand != other.cbackCommand:
            if str(self.cbackCommand or "") < str(other.cbackCommand or ""):
                return -1
            else:
                return 1
        if self.overrides != other.overrides:
            if self.overrides < other.overrides:
                return -1
            else:
                return 1
        if self.hooks != other.hooks:
            if self.hooks < other.hooks:
                return -1
            else:
                return 1
        if self.managedActions != other.managedActions:
            if self.managedActions < other.managedActions:
                return -1
            else:
                return 1
        return 0

    def addOverride(self, command, absolutePath):
        """
        If no override currently exists for the command, add one.
        Args:
           command: Name of command to be overridden
           absolutePath: Absolute path of the overrridden command
        """
        override = CommandOverride(command, absolutePath)
        if self.overrides is None:
            self.overrides = [override]
        else:
            exists = False
            for obj in self.overrides:
                if obj.command == override.command:
                    exists = True
                    break
            if not exists:
                self.overrides.append(override)

    def replaceOverride(self, command, absolutePath):
        """
        If override currently exists for the command, replace it; otherwise add it.
        Args:
           command: Name of command to be overridden
           absolutePath: Absolute path of the overrridden command
        """
        override = CommandOverride(command, absolutePath)
        if self.overrides is None:
            self.overrides = [override]
        else:
            exists = False
            for obj in self.overrides:
                if obj.command == override.command:
                    exists = True
                    obj.absolutePath = override.absolutePath
                    break
            if not exists:
                self.overrides.append(override)

    def _setStartingDay(self, value):
        """
        Property target used to set the starting day.
        If it is not ``None``, the value must be a valid English day of the week,
        one of ``"monday"``, ``"tuesday"``, ``"wednesday"``, etc.
        Raises:
           ValueError: If the value is not a valid day of the week
        """
        if value is not None:
            if value not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                raise ValueError('Starting day must be an English day of the week, i.e. "monday".')
        self._startingDay = value

    def _getStartingDay(self):
        """
        Property target used to get the starting day.
        """
        return self._startingDay

    def _setWorkingDir(self, value):
        """
        Property target used to set the working directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
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

    def _setBackupUser(self, value):
        """
        Property target used to set the backup user.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Backup user must be a non-empty string.")
        self._backupUser = value

    def _getBackupUser(self):
        """
        Property target used to get the backup user.
        """
        return self._backupUser

    def _setBackupGroup(self, value):
        """
        Property target used to set the backup group.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Backup group must be a non-empty string.")
        self._backupGroup = value

    def _getBackupGroup(self):
        """
        Property target used to get the backup group.
        """
        return self._backupGroup

    def _setRcpCommand(self, value):
        """
        Property target used to set the rcp command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The rcp command must be a non-empty string.")
        self._rcpCommand = value

    def _getRcpCommand(self):
        """
        Property target used to get the rcp command.
        """
        return self._rcpCommand

    def _setRshCommand(self, value):
        """
        Property target used to set the rsh command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The rsh command must be a non-empty string.")
        self._rshCommand = value

    def _getRshCommand(self):
        """
        Property target used to get the rsh command.
        """
        return self._rshCommand

    def _setCbackCommand(self, value):
        """
        Property target used to set the cback command.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The cback command must be a non-empty string.")
        self._cbackCommand = value

    def _getCbackCommand(self):
        """
        Property target used to get the cback command.
        """
        return self._cbackCommand

    def _setOverrides(self, value):
        """
        Property target used to set the command path overrides list.
        Either the value must be ``None`` or each element must be a ``CommandOverride``.
        Raises:
           ValueError: If the value is not a ``CommandOverride``
        """
        if value is None:
            self._overrides = None
        else:
            try:
                saved = self._overrides
                self._overrides = ObjectTypeList(CommandOverride, "CommandOverride")
                self._overrides.extend(value)
            except Exception as e:
                self._overrides = saved
                raise e

    def _getOverrides(self):
        """
        Property target used to get the command path overrides list.
        """
        return self._overrides

    def _setHooks(self, value):
        """
        Property target used to set the pre- and post-action hooks list.
        Either the value must be ``None`` or each element must be an ``ActionHook``.
        Raises:
           ValueError: If the value is not a ``CommandOverride``
        """
        if value is None:
            self._hooks = None
        else:
            try:
                saved = self._hooks
                self._hooks = ObjectTypeList(ActionHook, "ActionHook")
                self._hooks.extend(value)
            except Exception as e:
                self._hooks = saved
                raise e

    def _getHooks(self):
        """
        Property target used to get the command path hooks list.
        """
        return self._hooks

    def _setManagedActions(self, value):
        """
        Property target used to set the managed actions list.
        Elements do not have to exist on disk at the time of assignment.
        """
        if value is None:
            self._managedActions = None
        else:
            try:
                saved = self._managedActions
                self._managedActions = RegexMatchList(ACTION_NAME_REGEX, emptyAllowed=False, prefix="Action name")
                self._managedActions.extend(value)
            except Exception as e:
                self._managedActions = saved
                raise e

    def _getManagedActions(self):
        """
        Property target used to get the managed actions list.
        """
        return self._managedActions

    startingDay = property(_getStartingDay, _setStartingDay, None, "Day that starts the week.")
    workingDir = property(_getWorkingDir, _setWorkingDir, None, "Working (temporary) directory to use for backups.")
    backupUser = property(_getBackupUser, _setBackupUser, None, "Effective user that backups should run as.")
    backupGroup = property(_getBackupGroup, _setBackupGroup, None, "Effective group that backups should run as.")
    rcpCommand = property(_getRcpCommand, _setRcpCommand, None, "Default rcp-compatible copy command for staging.")
    rshCommand = property(_getRshCommand, _setRshCommand, None, "Default rsh-compatible command to use for remote shells.")
    cbackCommand = property(
        _getCbackCommand, _setCbackCommand, None, "Default cback-compatible command to use on managed remote peers."
    )
    overrides = property(_getOverrides, _setOverrides, None, "List of configured command path overrides, if any.")
    hooks = property(_getHooks, _setHooks, None, "List of configured pre- and post-action hooks.")
    managedActions = property(
        _getManagedActions, _setManagedActions, None, "Default set of actions that are managed on remote peers."
    )


########################################################################
# PeersConfig class definition
########################################################################


@total_ordering
class PeersConfig(object):

    """
    Class representing Cedar Backup global peer configuration.

    This section contains a list of local and remote peers in a master's backup
    pool.  The section is optional.  If a master does not define this section,
    then all peers are unmanaged, and the stage configuration section must
    explicitly list any peer that is to be staged.  If this section is
    configured, then peers may be managed or unmanaged, and the stage section
    peer configuration (if any) completely overrides this configuration.

    The following restrictions exist on data in this class:

       - The list of local peers must contain only ``LocalPeer`` objects
       - The list of remote peers must contain only ``RemotePeer`` objects

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, localPeers=None, remotePeers=None):
        """
        Constructor for the ``PeersConfig`` class.

        Args:
           localPeers: List of local peers
           remotePeers: List of remote peers

        Raises:
           ValueError: If one of the values is invalid
        """
        self._localPeers = None
        self._remotePeers = None
        self.localPeers = localPeers
        self.remotePeers = remotePeers

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PeersConfig(%s, %s)" % (self.localPeers, self.remotePeers)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.localPeers != other.localPeers:
            if self.localPeers < other.localPeers:
                return -1
            else:
                return 1
        if self.remotePeers != other.remotePeers:
            if self.remotePeers < other.remotePeers:
                return -1
            else:
                return 1
        return 0

    def hasPeers(self):
        """
        Indicates whether any peers are filled into this object.
        Returns:
            Boolean true if any local or remote peers are filled in, false otherwise
        """
        return (self.localPeers is not None and len(self.localPeers) > 0) or (
            self.remotePeers is not None and len(self.remotePeers) > 0
        )

    def _setLocalPeers(self, value):
        """
        Property target used to set the local peers list.
        Either the value must be ``None`` or each element must be a ``LocalPeer``.
        Raises:
           ValueError: If the value is not an absolute path
        """
        if value is None:
            self._localPeers = None
        else:
            try:
                saved = self._localPeers
                self._localPeers = ObjectTypeList(LocalPeer, "LocalPeer")
                self._localPeers.extend(value)
            except Exception as e:
                self._localPeers = saved
                raise e

    def _getLocalPeers(self):
        """
        Property target used to get the local peers list.
        """
        return self._localPeers

    def _setRemotePeers(self, value):
        """
        Property target used to set the remote peers list.
        Either the value must be ``None`` or each element must be a ``RemotePeer``.
        Raises:
           ValueError: If the value is not a ``RemotePeer``
        """
        if value is None:
            self._remotePeers = None
        else:
            try:
                saved = self._remotePeers
                self._remotePeers = ObjectTypeList(RemotePeer, "RemotePeer")
                self._remotePeers.extend(value)
            except Exception as e:
                self._remotePeers = saved
                raise e

    def _getRemotePeers(self):
        """
        Property target used to get the remote peers list.
        """
        return self._remotePeers

    localPeers = property(_getLocalPeers, _setLocalPeers, None, "List of local peers.")
    remotePeers = property(_getRemotePeers, _setRemotePeers, None, "List of remote peers.")


########################################################################
# CollectConfig class definition
########################################################################


@total_ordering
class CollectConfig(object):

    """
    Class representing a Cedar Backup collect configuration.

    The following restrictions exist on data in this class:

       - The target directory must be an absolute path.
       - The collect mode must be one of the values in :any:`VALID_COLLECT_MODES`.
       - The archive mode must be one of the values in :any:`VALID_ARCHIVE_MODES`.
       - The ignore file must be a non-empty string.
       - Each of the paths in ``absoluteExcludePaths`` must be an absolute path
       - The collect file list must be a list of ``CollectFile`` objects.
       - The collect directory list must be a list of ``CollectDir`` objects.

    For the ``absoluteExcludePaths`` list, validation is accomplished through the
    :any:`util.AbsolutePathList` list implementation that overrides common list
    methods and transparently does the absolute path validation for us.

    For the ``collectFiles`` and ``collectDirs`` list, validation is accomplished
    through the :any:`util.ObjectTypeList` list implementation that overrides common
    list methods and transparently ensures that each element has an appropriate
    type.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(
        self,
        targetDir=None,
        collectMode=None,
        archiveMode=None,
        ignoreFile=None,
        absoluteExcludePaths=None,
        excludePatterns=None,
        collectFiles=None,
        collectDirs=None,
    ):
        """
        Constructor for the ``CollectConfig`` class.

        Args:
           targetDir: Directory to collect files into
           collectMode: Default collect mode
           archiveMode: Default archive mode for collect files
           ignoreFile: Default ignore file name
           absoluteExcludePaths: List of absolute paths to exclude
           excludePatterns: List of regular expression patterns to exclude
           collectFiles: List of collect files
           collectDirs: List of collect directories

        Raises:
           ValueError: If one of the values is invalid
        """
        self._targetDir = None
        self._collectMode = None
        self._archiveMode = None
        self._ignoreFile = None
        self._absoluteExcludePaths = None
        self._excludePatterns = None
        self._collectFiles = None
        self._collectDirs = None
        self.targetDir = targetDir
        self.collectMode = collectMode
        self.archiveMode = archiveMode
        self.ignoreFile = ignoreFile
        self.absoluteExcludePaths = absoluteExcludePaths
        self.excludePatterns = excludePatterns
        self.collectFiles = collectFiles
        self.collectDirs = collectDirs

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "CollectConfig(%s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.targetDir,
            self.collectMode,
            self.archiveMode,
            self.ignoreFile,
            self.absoluteExcludePaths,
            self.excludePatterns,
            self.collectFiles,
            self.collectDirs,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.targetDir != other.targetDir:
            if str(self.targetDir or "") < str(other.targetDir or ""):
                return -1
            else:
                return 1
        if self.collectMode != other.collectMode:
            if str(self.collectMode or "") < str(other.collectMode or ""):
                return -1
            else:
                return 1
        if self.archiveMode != other.archiveMode:
            if str(self.archiveMode or "") < str(other.archiveMode or ""):
                return -1
            else:
                return 1
        if self.ignoreFile != other.ignoreFile:
            if str(self.ignoreFile or "") < str(other.ignoreFile or ""):
                return -1
            else:
                return 1
        if self.absoluteExcludePaths != other.absoluteExcludePaths:
            if self.absoluteExcludePaths < other.absoluteExcludePaths:
                return -1
            else:
                return 1
        if self.excludePatterns != other.excludePatterns:
            if self.excludePatterns < other.excludePatterns:
                return -1
            else:
                return 1
        if self.collectFiles != other.collectFiles:
            if self.collectFiles < other.collectFiles:
                return -1
            else:
                return 1
        if self.collectDirs != other.collectDirs:
            if self.collectDirs < other.collectDirs:
                return -1
            else:
                return 1
        return 0

    def _setTargetDir(self, value):
        """
        Property target used to set the target directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Target directory must be an absolute path.")
        self._targetDir = encodePath(value)

    def _getTargetDir(self):
        """
        Property target used to get the target directory.
        """
        return self._targetDir

    def _setCollectMode(self, value):
        """
        Property target used to set the collect mode.
        If not ``None``, the mode must be one of :any:`VALID_COLLECT_MODES`.
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

    def _setArchiveMode(self, value):
        """
        Property target used to set the archive mode.
        If not ``None``, the mode must be one of :any:`VALID_ARCHIVE_MODES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_ARCHIVE_MODES:
                raise ValueError("Archive mode must be one of %s." % VALID_ARCHIVE_MODES)
        self._archiveMode = value

    def _getArchiveMode(self):
        """
        Property target used to get the archive mode.
        """
        return self._archiveMode

    def _setIgnoreFile(self, value):
        """
        Property target used to set the ignore file.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The ignore file must be a non-empty string.")
        self._ignoreFile = encodePath(value)

    def _getIgnoreFile(self):
        """
        Property target used to get the ignore file.
        """
        return self._ignoreFile

    def _setAbsoluteExcludePaths(self, value):
        """
        Property target used to set the absolute exclude paths list.
        Either the value must be ``None`` or each element must be an absolute path.
        Elements do not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
        """
        if value is None:
            self._absoluteExcludePaths = None
        else:
            try:
                saved = self._absoluteExcludePaths
                self._absoluteExcludePaths = AbsolutePathList()
                self._absoluteExcludePaths.extend(value)
            except Exception as e:
                self._absoluteExcludePaths = saved
                raise e

    def _getAbsoluteExcludePaths(self):
        """
        Property target used to get the absolute exclude paths list.
        """
        return self._absoluteExcludePaths

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

    def _setCollectFiles(self, value):
        """
        Property target used to set the collect files list.
        Either the value must be ``None`` or each element must be a ``CollectFile``.
        Raises:
           ValueError: If the value is not a ``CollectFile``
        """
        if value is None:
            self._collectFiles = None
        else:
            try:
                saved = self._collectFiles
                self._collectFiles = ObjectTypeList(CollectFile, "CollectFile")
                self._collectFiles.extend(value)
            except Exception as e:
                self._collectFiles = saved
                raise e

    def _getCollectFiles(self):
        """
        Property target used to get the collect files list.
        """
        return self._collectFiles

    def _setCollectDirs(self, value):
        """
        Property target used to set the collect dirs list.
        Either the value must be ``None`` or each element must be a ``CollectDir``.
        Raises:
           ValueError: If the value is not a ``CollectDir``
        """
        if value is None:
            self._collectDirs = None
        else:
            try:
                saved = self._collectDirs
                self._collectDirs = ObjectTypeList(CollectDir, "CollectDir")
                self._collectDirs.extend(value)
            except Exception as e:
                self._collectDirs = saved
                raise e

    def _getCollectDirs(self):
        """
        Property target used to get the collect dirs list.
        """
        return self._collectDirs

    targetDir = property(_getTargetDir, _setTargetDir, None, "Directory to collect files into.")
    collectMode = property(_getCollectMode, _setCollectMode, None, "Default collect mode.")
    archiveMode = property(_getArchiveMode, _setArchiveMode, None, "Default archive mode for collect files.")
    ignoreFile = property(_getIgnoreFile, _setIgnoreFile, None, "Default ignore file name.")
    absoluteExcludePaths = property(_getAbsoluteExcludePaths, _setAbsoluteExcludePaths, None, "List of absolute paths to exclude.")
    excludePatterns = property(_getExcludePatterns, _setExcludePatterns, None, "List of regular expressions patterns to exclude.")
    collectFiles = property(_getCollectFiles, _setCollectFiles, None, "List of collect files.")
    collectDirs = property(_getCollectDirs, _setCollectDirs, None, "List of collect directories.")


########################################################################
# StageConfig class definition
########################################################################


@total_ordering
class StageConfig(object):

    """
    Class representing a Cedar Backup stage configuration.

    The following restrictions exist on data in this class:

       - The target directory must be an absolute path
       - The list of local peers must contain only ``LocalPeer`` objects
       - The list of remote peers must contain only ``RemotePeer`` objects

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, targetDir=None, localPeers=None, remotePeers=None):
        """
        Constructor for the ``StageConfig`` class.

        Args:
           targetDir: Directory to stage files into, by peer name
           localPeers: List of local peers
           remotePeers: List of remote peers

        Raises:
           ValueError: If one of the values is invalid
        """
        self._targetDir = None
        self._localPeers = None
        self._remotePeers = None
        self.targetDir = targetDir
        self.localPeers = localPeers
        self.remotePeers = remotePeers

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "StageConfig(%s, %s, %s)" % (self.targetDir, self.localPeers, self.remotePeers)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.targetDir != other.targetDir:
            if str(self.targetDir or "") < str(other.targetDir or ""):
                return -1
            else:
                return 1
        if self.localPeers != other.localPeers:
            if self.localPeers < other.localPeers:
                return -1
            else:
                return 1
        if self.remotePeers != other.remotePeers:
            if self.remotePeers < other.remotePeers:
                return -1
            else:
                return 1
        return 0

    def hasPeers(self):
        """
        Indicates whether any peers are filled into this object.
        Returns:
            Boolean true if any local or remote peers are filled in, false otherwise
        """
        return (self.localPeers is not None and len(self.localPeers) > 0) or (
            self.remotePeers is not None and len(self.remotePeers) > 0
        )

    def _setTargetDir(self, value):
        """
        Property target used to set the target directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Target directory must be an absolute path.")
        self._targetDir = encodePath(value)

    def _getTargetDir(self):
        """
        Property target used to get the target directory.
        """
        return self._targetDir

    def _setLocalPeers(self, value):
        """
        Property target used to set the local peers list.
        Either the value must be ``None`` or each element must be a ``LocalPeer``.
        Raises:
           ValueError: If the value is not an absolute path
        """
        if value is None:
            self._localPeers = None
        else:
            try:
                saved = self._localPeers
                self._localPeers = ObjectTypeList(LocalPeer, "LocalPeer")
                self._localPeers.extend(value)
            except Exception as e:
                self._localPeers = saved
                raise e

    def _getLocalPeers(self):
        """
        Property target used to get the local peers list.
        """
        return self._localPeers

    def _setRemotePeers(self, value):
        """
        Property target used to set the remote peers list.
        Either the value must be ``None`` or each element must be a ``RemotePeer``.
        Raises:
           ValueError: If the value is not a ``RemotePeer``
        """
        if value is None:
            self._remotePeers = None
        else:
            try:
                saved = self._remotePeers
                self._remotePeers = ObjectTypeList(RemotePeer, "RemotePeer")
                self._remotePeers.extend(value)
            except Exception as e:
                self._remotePeers = saved
                raise e

    def _getRemotePeers(self):
        """
        Property target used to get the remote peers list.
        """
        return self._remotePeers

    targetDir = property(_getTargetDir, _setTargetDir, None, "Directory to stage files into, by peer name.")
    localPeers = property(_getLocalPeers, _setLocalPeers, None, "List of local peers.")
    remotePeers = property(_getRemotePeers, _setRemotePeers, None, "List of remote peers.")


########################################################################
# StoreConfig class definition
########################################################################


@total_ordering
class StoreConfig(object):

    """
    Class representing a Cedar Backup store configuration.

    The following restrictions exist on data in this class:

       - The source directory must be an absolute path.
       - The media type must be one of the values in :any:`VALID_MEDIA_TYPES`.
       - The device type must be one of the values in :any:`VALID_DEVICE_TYPES`.
       - The device path must be an absolute path.
       - The SCSI id, if provided, must be in the form specified by :any:`validateScsiId`.
       - The drive speed must be an integer >= 1
       - The blanking behavior must be a ``BlankBehavior`` object
       - The refresh media delay must be an integer >= 0
       - The eject delay must be an integer >= 0

    Note that although the blanking factor must be a positive floating point
    number, it is stored as a string. This is done so that we can losslessly go
    back and forth between XML and object representations of configuration.

    """

    def __init__(
        self,
        sourceDir=None,
        mediaType=None,
        deviceType=None,
        devicePath=None,
        deviceScsiId=None,
        driveSpeed=None,
        checkData=False,
        warnMidnite=False,
        noEject=False,
        checkMedia=False,
        blankBehavior=None,
        refreshMediaDelay=None,
        ejectDelay=None,
    ):
        """
        Constructor for the ``StoreConfig`` class.

        Args:
           sourceDir: Directory whose contents should be written to media
           mediaType: Type of the media (see notes above)
           deviceType: Type of the device (optional, see notes above)
           devicePath: Filesystem device name for writer device, i.e. ``/dev/cdrw``
           deviceScsiId: SCSI id for writer device, i.e. ``[<method>:]scsibus,target,lun``
           driveSpeed: Speed of the drive, i.e. ``2`` for 2x drive, etc
           checkData: Whether resulting image should be validated
           checkMedia: Whether media should be checked before being written to
           warnMidnite: Whether to generate warnings for crossing midnite
           noEject: Indicates that the writer device should not be ejected
           blankBehavior: Controls optimized blanking behavior
           refreshMediaDelay: Delay, in seconds, to add after refreshing media
           ejectDelay: Delay, in seconds, to add after ejecting media before closing the tray

        Raises:
           ValueError: If one of the values is invalid
        """
        self._sourceDir = None
        self._mediaType = None
        self._deviceType = None
        self._devicePath = None
        self._deviceScsiId = None
        self._driveSpeed = None
        self._checkData = None
        self._checkMedia = None
        self._warnMidnite = None
        self._noEject = None
        self._blankBehavior = None
        self._refreshMediaDelay = None
        self._ejectDelay = None
        self.sourceDir = sourceDir
        self.mediaType = mediaType
        self.deviceType = deviceType
        self.devicePath = devicePath
        self.deviceScsiId = deviceScsiId
        self.driveSpeed = driveSpeed
        self.checkData = checkData
        self.checkMedia = checkMedia
        self.warnMidnite = warnMidnite
        self.noEject = noEject
        self.blankBehavior = blankBehavior
        self.refreshMediaDelay = refreshMediaDelay
        self.ejectDelay = ejectDelay

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "StoreConfig(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.sourceDir,
            self.mediaType,
            self.deviceType,
            self.devicePath,
            self.deviceScsiId,
            self.driveSpeed,
            self.checkData,
            self.warnMidnite,
            self.noEject,
            self.checkMedia,
            self.blankBehavior,
            self.refreshMediaDelay,
            self.ejectDelay,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.sourceDir != other.sourceDir:
            if str(self.sourceDir or "") < str(other.sourceDir or ""):
                return -1
            else:
                return 1
        if self.mediaType != other.mediaType:
            if str(self.mediaType or "") < str(other.mediaType or ""):
                return -1
            else:
                return 1
        if self.deviceType != other.deviceType:
            if str(self.deviceType or "") < str(other.deviceType or ""):
                return -1
            else:
                return 1
        if self.devicePath != other.devicePath:
            if str(self.devicePath or "") < str(other.devicePath or ""):
                return -1
            else:
                return 1
        if self.deviceScsiId != other.deviceScsiId:
            if str(self.deviceScsiId or "") < str(other.deviceScsiId or ""):
                return -1
            else:
                return 1
        if self.driveSpeed != other.driveSpeed:
            if str(self.driveSpeed or "") < str(other.driveSpeed or ""):
                return -1
            else:
                return 1
        if self.checkData != other.checkData:
            if self.checkData < other.checkData:
                return -1
            else:
                return 1
        if self.checkMedia != other.checkMedia:
            if self.checkMedia < other.checkMedia:
                return -1
            else:
                return 1
        if self.warnMidnite != other.warnMidnite:
            if self.warnMidnite < other.warnMidnite:
                return -1
            else:
                return 1
        if self.noEject != other.noEject:
            if self.noEject < other.noEject:
                return -1
            else:
                return 1
        if self.blankBehavior != other.blankBehavior:
            if str(self.blankBehavior or "") < str(other.blankBehavior or ""):
                return -1
            else:
                return 1
        if self.refreshMediaDelay != other.refreshMediaDelay:
            if int(self.refreshMediaDelay or 0) < int(other.refreshMediaDelay or 0):
                return -1
            else:
                return 1
        if self.ejectDelay != other.ejectDelay:
            if int(self.ejectDelay or 0) < int(other.ejectDelay or 0):
                return -1
            else:
                return 1
        return 0

    def _setSourceDir(self, value):
        """
        Property target used to set the source directory.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Source directory must be an absolute path.")
        self._sourceDir = encodePath(value)

    def _getSourceDir(self):
        """
        Property target used to get the source directory.
        """
        return self._sourceDir

    def _setMediaType(self, value):
        """
        Property target used to set the media type.
        The value must be one of :any:`VALID_MEDIA_TYPES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_MEDIA_TYPES:
                raise ValueError("Media type must be one of %s." % VALID_MEDIA_TYPES)
        self._mediaType = value

    def _getMediaType(self):
        """
        Property target used to get the media type.
        """
        return self._mediaType

    def _setDeviceType(self, value):
        """
        Property target used to set the device type.
        The value must be one of :any:`VALID_DEVICE_TYPES`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is not None:
            if value not in VALID_DEVICE_TYPES:
                raise ValueError("Device type must be one of %s." % VALID_DEVICE_TYPES)
        self._deviceType = value

    def _getDeviceType(self):
        """
        Property target used to get the device type.
        """
        return self._deviceType

    def _setDevicePath(self, value):
        """
        Property target used to set the device path.
        The value must be an absolute path if it is not ``None``.
        It does not have to exist on disk at the time of assignment.
        Raises:
           ValueError: If the value is not an absolute path
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if not os.path.isabs(value):
                raise ValueError("Device path must be an absolute path.")
        self._devicePath = encodePath(value)

    def _getDevicePath(self):
        """
        Property target used to get the device path.
        """
        return self._devicePath

    def _setDeviceScsiId(self, value):
        """
        Property target used to set the SCSI id
        The SCSI id must be valid per :any:`validateScsiId`.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._deviceScsiId = None
        else:
            self._deviceScsiId = validateScsiId(value)

    def _getDeviceScsiId(self):
        """
        Property target used to get the SCSI id.
        """
        return self._deviceScsiId

    def _setDriveSpeed(self, value):
        """
        Property target used to set the drive speed.
        The drive speed must be valid per :any:`validateDriveSpeed`.
        Raises:
           ValueError: If the value is not valid
        """
        self._driveSpeed = validateDriveSpeed(value)

    def _getDriveSpeed(self):
        """
        Property target used to get the drive speed.
        """
        return self._driveSpeed

    def _setCheckData(self, value):
        """
        Property target used to set the check data flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._checkData = True
        else:
            self._checkData = False

    def _getCheckData(self):
        """
        Property target used to get the check data flag.
        """
        return self._checkData

    def _setCheckMedia(self, value):
        """
        Property target used to set the check media flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._checkMedia = True
        else:
            self._checkMedia = False

    def _getCheckMedia(self):
        """
        Property target used to get the check media flag.
        """
        return self._checkMedia

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

    def _setNoEject(self, value):
        """
        Property target used to set the no-eject flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._noEject = True
        else:
            self._noEject = False

    def _getNoEject(self):
        """
        Property target used to get the no-eject flag.
        """
        return self._noEject

    def _setBlankBehavior(self, value):
        """
        Property target used to set blanking behavior configuration.
        If not ``None``, the value must be a ``BlankBehavior`` object.
        Raises:
           ValueError: If the value is not a ``BlankBehavior``
        """
        if value is None:
            self._blankBehavior = None
        else:
            if not isinstance(value, BlankBehavior):
                raise ValueError("Value must be a ``BlankBehavior`` object.")
            self._blankBehavior = value

    def _getBlankBehavior(self):
        """
        Property target used to get the blanking behavior configuration.
        """
        return self._blankBehavior

    def _setRefreshMediaDelay(self, value):
        """
        Property target used to set the refreshMediaDelay.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._refreshMediaDelay = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Action refreshMediaDelay value must be an integer >= 0.")
            if value < 0:
                raise ValueError("Action refreshMediaDelay value must be an integer >= 0.")
            if value == 0:
                value = None  # normalize this out, since it's the default
            self._refreshMediaDelay = value

    def _getRefreshMediaDelay(self):
        """
        Property target used to get the action refreshMediaDelay.
        """
        return self._refreshMediaDelay

    def _setEjectDelay(self, value):
        """
        Property target used to set the ejectDelay.
        The value must be an integer >= 0.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._ejectDelay = None
        else:
            try:
                value = int(value)
            except TypeError:
                raise ValueError("Action ejectDelay value must be an integer >= 0.")
            if value < 0:
                raise ValueError("Action ejectDelay value must be an integer >= 0.")
            if value == 0:
                value = None  # normalize this out, since it's the default
            self._ejectDelay = value

    def _getEjectDelay(self):
        """
        Property target used to get the action ejectDelay.
        """
        return self._ejectDelay

    sourceDir = property(_getSourceDir, _setSourceDir, None, "Directory whose contents should be written to media.")
    mediaType = property(_getMediaType, _setMediaType, None, "Type of the media (see notes above).")
    deviceType = property(_getDeviceType, _setDeviceType, None, "Type of the device (optional, see notes above).")
    devicePath = property(_getDevicePath, _setDevicePath, None, "Filesystem device name for writer device.")
    deviceScsiId = property(_getDeviceScsiId, _setDeviceScsiId, None, "SCSI id for writer device (optional, see notes above).")
    driveSpeed = property(_getDriveSpeed, _setDriveSpeed, None, "Speed of the drive.")
    checkData = property(_getCheckData, _setCheckData, None, "Whether resulting image should be validated.")
    checkMedia = property(_getCheckMedia, _setCheckMedia, None, "Whether media should be checked before being written to.")
    warnMidnite = property(_getWarnMidnite, _setWarnMidnite, None, "Whether to generate warnings for crossing midnite.")
    noEject = property(_getNoEject, _setNoEject, None, "Indicates that the writer device should not be ejected.")
    blankBehavior = property(_getBlankBehavior, _setBlankBehavior, None, "Controls optimized blanking behavior.")
    refreshMediaDelay = property(
        _getRefreshMediaDelay, _setRefreshMediaDelay, None, "Delay, in seconds, to add after refreshing media."
    )
    ejectDelay = property(
        _getEjectDelay, _setEjectDelay, None, "Delay, in seconds, to add after ejecting media before closing the tray"
    )


########################################################################
# PurgeConfig class definition
########################################################################


@total_ordering
class PurgeConfig(object):

    """
    Class representing a Cedar Backup purge configuration.

    The following restrictions exist on data in this class:

       - The purge directory list must be a list of ``PurgeDir`` objects.

    For the ``purgeDirs`` list, validation is accomplished through the
    :any:`util.ObjectTypeList` list implementation that overrides common list
    methods and transparently ensures that each element is a ``PurgeDir``.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    def __init__(self, purgeDirs=None):
        """
        Constructor for the ``Purge`` class.
        Args:
           purgeDirs: List of purge directories
        Raises:
           ValueError: If one of the values is invalid
        """
        self._purgeDirs = None
        self.purgeDirs = purgeDirs

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PurgeConfig(%s)" % self.purgeDirs

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.purgeDirs != other.purgeDirs:
            if self.purgeDirs < other.purgeDirs:
                return -1
            else:
                return 1
        return 0

    def _setPurgeDirs(self, value):
        """
        Property target used to set the purge dirs list.
        Either the value must be ``None`` or each element must be a ``PurgeDir``.
        Raises:
           ValueError: If the value is not a ``PurgeDir``
        """
        if value is None:
            self._purgeDirs = None
        else:
            try:
                saved = self._purgeDirs
                self._purgeDirs = ObjectTypeList(PurgeDir, "PurgeDir")
                self._purgeDirs.extend(value)
            except Exception as e:
                self._purgeDirs = saved
                raise e

    def _getPurgeDirs(self):
        """
        Property target used to get the purge dirs list.
        """
        return self._purgeDirs

    purgeDirs = property(_getPurgeDirs, _setPurgeDirs, None, "List of directories to purge.")


########################################################################
# Config class definition
########################################################################


@total_ordering
class Config(object):

    ######################
    # Class documentation
    ######################

    """
    Class representing a Cedar Backup XML configuration document.

    The ``Config`` class is a Python object representation of a Cedar Backup XML
    configuration file.  It is intended to be the only Python-language interface
    to Cedar Backup configuration on disk for both Cedar Backup itself and for
    external applications.

    The object representation is two-way: XML data can be used to create a
    ``Config`` object, and then changes to the object can be propogated back to
    disk.  A ``Config`` object can even be used to create a configuration file
    from scratch programmatically.

    This class and the classes it is composed from often use Python's
    ``property`` construct to validate input and limit access to values.  Some
    validations can only be done once a document is considered "complete"
    (see module notes for more details).

    Assignments to the various instance variables must match the expected
    type, i.e. ``reference`` must be a ``ReferenceConfig``.  The internal check
    uses the built-in ``isinstance`` function, so it should be OK to use
    subclasses if you want to.

    If an instance variable is not set, its value will be ``None``.  When an
    object is initialized without using an XML document, all of the values
    will be ``None``.  Even when an object is initialized using XML, some of
    the values might be ``None`` because not every section is required.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    ##############
    # Constructor
    ##############

    def __init__(self, xmlData=None, xmlPath=None, validate=True):
        """
        Initializes a configuration object.

        If you initialize the object without passing either ``xmlData`` or
        ``xmlPath``, then configuration will be empty and will be invalid until it
        is filled in properly.

        No reference to the original XML data or original path is saved off by
        this class.  Once the data has been parsed (successfully or not) this
        original information is discarded.

        Unless the ``validate`` argument is ``False``, the :any:`Config.validate`
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
        self._reference = None
        self._extensions = None
        self._options = None
        self._peers = None
        self._collect = None
        self._stage = None
        self._store = None
        self._purge = None
        self.reference = None
        self.extensions = None
        self.options = None
        self.peers = None
        self.collect = None
        self.stage = None
        self.store = None
        self.purge = None
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

    #########################
    # String representations
    #########################

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "Config(%s, %s, %s, %s, %s, %s, %s, %s)" % (
            self.reference,
            self.extensions,
            self.options,
            self.peers,
            self.collect,
            self.stage,
            self.store,
            self.purge,
        )

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    #############################
    # Standard comparison method
    #############################

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
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
        if self.reference != other.reference:
            if self.reference < other.reference:
                return -1
            else:
                return 1
        if self.extensions != other.extensions:
            if self.extensions < other.extensions:
                return -1
            else:
                return 1
        if self.options != other.options:
            if self.options < other.options:
                return -1
            else:
                return 1
        if self.peers != other.peers:
            if self.peers < other.peers:
                return -1
            else:
                return 1
        if self.collect != other.collect:
            if self.collect < other.collect:
                return -1
            else:
                return 1
        if self.stage != other.stage:
            if self.stage < other.stage:
                return -1
            else:
                return 1
        if self.store != other.store:
            if self.store < other.store:
                return -1
            else:
                return 1
        if self.purge != other.purge:
            if self.purge < other.purge:
                return -1
            else:
                return 1
        return 0

    #############
    # Properties
    #############

    def _setReference(self, value):
        """
        Property target used to set the reference configuration value.
        If not ``None``, the value must be a ``ReferenceConfig`` object.
        Raises:
           ValueError: If the value is not a ``ReferenceConfig``
        """
        if value is None:
            self._reference = None
        else:
            if not isinstance(value, ReferenceConfig):
                raise ValueError("Value must be a ``ReferenceConfig`` object.")
            self._reference = value

    def _getReference(self):
        """
        Property target used to get the reference configuration value.
        """
        return self._reference

    def _setExtensions(self, value):
        """
        Property target used to set the extensions configuration value.
        If not ``None``, the value must be a ``ExtensionsConfig`` object.
        Raises:
           ValueError: If the value is not a ``ExtensionsConfig``
        """
        if value is None:
            self._extensions = None
        else:
            if not isinstance(value, ExtensionsConfig):
                raise ValueError("Value must be a ``ExtensionsConfig`` object.")
            self._extensions = value

    def _getExtensions(self):
        """
        Property target used to get the extensions configuration value.
        """
        return self._extensions

    def _setOptions(self, value):
        """
        Property target used to set the options configuration value.
        If not ``None``, the value must be an ``OptionsConfig`` object.
        Raises:
           ValueError: If the value is not a ``OptionsConfig``
        """
        if value is None:
            self._options = None
        else:
            if not isinstance(value, OptionsConfig):
                raise ValueError("Value must be a ``OptionsConfig`` object.")
            self._options = value

    def _getOptions(self):
        """
        Property target used to get the options configuration value.
        """
        return self._options

    def _setPeers(self, value):
        """
        Property target used to set the peers configuration value.
        If not ``None``, the value must be an ``PeersConfig`` object.
        Raises:
           ValueError: If the value is not a ``PeersConfig``
        """
        if value is None:
            self._peers = None
        else:
            if not isinstance(value, PeersConfig):
                raise ValueError("Value must be a ``PeersConfig`` object.")
            self._peers = value

    def _getPeers(self):
        """
        Property target used to get the peers configuration value.
        """
        return self._peers

    def _setCollect(self, value):
        """
        Property target used to set the collect configuration value.
        If not ``None``, the value must be a ``CollectConfig`` object.
        Raises:
           ValueError: If the value is not a ``CollectConfig``
        """
        if value is None:
            self._collect = None
        else:
            if not isinstance(value, CollectConfig):
                raise ValueError("Value must be a ``CollectConfig`` object.")
            self._collect = value

    def _getCollect(self):
        """
        Property target used to get the collect configuration value.
        """
        return self._collect

    def _setStage(self, value):
        """
        Property target used to set the stage configuration value.
        If not ``None``, the value must be a ``StageConfig`` object.
        Raises:
           ValueError: If the value is not a ``StageConfig``
        """
        if value is None:
            self._stage = None
        else:
            if not isinstance(value, StageConfig):
                raise ValueError("Value must be a ``StageConfig`` object.")
            self._stage = value

    def _getStage(self):
        """
        Property target used to get the stage configuration value.
        """
        return self._stage

    def _setStore(self, value):
        """
        Property target used to set the store configuration value.
        If not ``None``, the value must be a ``StoreConfig`` object.
        Raises:
           ValueError: If the value is not a ``StoreConfig``
        """
        if value is None:
            self._store = None
        else:
            if not isinstance(value, StoreConfig):
                raise ValueError("Value must be a ``StoreConfig`` object.")
            self._store = value

    def _getStore(self):
        """
        Property target used to get the store configuration value.
        """
        return self._store

    def _setPurge(self, value):
        """
        Property target used to set the purge configuration value.
        If not ``None``, the value must be a ``PurgeConfig`` object.
        Raises:
           ValueError: If the value is not a ``PurgeConfig``
        """
        if value is None:
            self._purge = None
        else:
            if not isinstance(value, PurgeConfig):
                raise ValueError("Value must be a ``PurgeConfig`` object.")
            self._purge = value

    def _getPurge(self):
        """
        Property target used to get the purge configuration value.
        """
        return self._purge

    reference = property(_getReference, _setReference, None, "Reference configuration in terms of a ``ReferenceConfig`` object.")
    extensions = property(
        _getExtensions, _setExtensions, None, "Extensions configuration in terms of a ``ExtensionsConfig`` object."
    )
    options = property(_getOptions, _setOptions, None, "Options configuration in terms of a ``OptionsConfig`` object.")
    peers = property(_getPeers, _setPeers, None, "Peers configuration in terms of a ``PeersConfig`` object.")
    collect = property(_getCollect, _setCollect, None, "Collect configuration in terms of a ``CollectConfig`` object.")
    stage = property(_getStage, _setStage, None, "Stage configuration in terms of a ``StageConfig`` object.")
    store = property(_getStore, _setStore, None, "Store configuration in terms of a ``StoreConfig`` object.")
    purge = property(_getPurge, _setPurge, None, "Purge configuration in terms of a ``PurgeConfig`` object.")

    #################
    # Public methods
    #################

    def extractXml(self, xmlPath=None, validate=True):
        """
        Extracts configuration into an XML document.

        If ``xmlPath`` is not provided, then the XML document will be returned as
        a string.  If ``xmlPath`` is provided, then the XML document will be written
        to the file and ``None`` will be returned.

        Unless the ``validate`` parameter is ``False``, the :any:`Config.validate`
        method will be called (with its default arguments) against the
        configuration before extracting the XML.  If configuration is not valid,
        then an XML document will not be extracted.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to write an
        invalid configuration file to disk.

        Args:
           xmlPath (Absolute path to a file): Path to an XML file to create on disk
           validate (Boolean true/false): Validate the document before extracting it
        Returns:
            XML string data or ``None`` as described above

        Raises:
           ValueError: If configuration within the object is not valid
           IOError: If there is an error writing to the file
           OSError: If there is an error writing to the file
        """
        if validate:
            self.validate()
        xmlData = self._extractXml()
        if xmlPath is not None:
            with open(xmlPath, "w") as f:
                f.write(xmlData)
            return None
        else:
            return xmlData

    def validate(
        self,
        requireOneAction=True,
        requireReference=False,
        requireExtensions=False,
        requireOptions=True,
        requireCollect=False,
        requireStage=False,
        requireStore=False,
        requirePurge=False,
        requirePeers=False,
    ):
        """
        Validates configuration represented by the object.

        This method encapsulates all of the validations that should apply to a
        fully "complete" document but are not already taken care of by earlier
        validations.  It also provides some extra convenience functionality which
        might be useful to some people.  The process of validation is laid out in
        the *Validation* section in the class notes (above).

        Args:
           requireOneAction: Require at least one of the collect, stage, store or purge sections
           requireReference: Require the reference section
           requireExtensions: Require the extensions section
           requireOptions: Require the options section
           requirePeers: Require the peers section
           requireCollect: Require the collect section
           requireStage: Require the stage section
           requireStore: Require the store section
           requirePurge: Require the purge section

        Raises:
           ValueError: If one of the validations fails
        """
        if requireOneAction and (self.collect, self.stage, self.store, self.purge) == (None, None, None, None):
            raise ValueError("At least one of the collect, stage, store and purge sections is required.")
        if requireReference and self.reference is None:
            raise ValueError("The reference is section is required.")
        if requireExtensions and self.extensions is None:
            raise ValueError("The extensions is section is required.")
        if requireOptions and self.options is None:
            raise ValueError("The options is section is required.")
        if requirePeers and self.peers is None:
            raise ValueError("The peers is section is required.")
        if requireCollect and self.collect is None:
            raise ValueError("The collect is section is required.")
        if requireStage and self.stage is None:
            raise ValueError("The stage is section is required.")
        if requireStore and self.store is None:
            raise ValueError("The store is section is required.")
        if requirePurge and self.purge is None:
            raise ValueError("The purge is section is required.")
        self._validateContents()

    #####################################
    # High-level methods for parsing XML
    #####################################

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls individual static methods to parse each of the individual
        configuration sections.

        Most of the validation we do here has to do with whether the document can
        be parsed and whether any values which exist are valid.  We don't do much
        validation as to whether required elements actually exist unless we have
        to to make sense of the document (instead, that's the job of the
        :any:`validate` method).

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._reference = Config._parseReference(parentNode)
        self._extensions = Config._parseExtensions(parentNode)
        self._options = Config._parseOptions(parentNode)
        self._peers = Config._parsePeers(parentNode)
        self._collect = Config._parseCollect(parentNode)
        self._stage = Config._parseStage(parentNode)
        self._store = Config._parseStore(parentNode)
        self._purge = Config._parsePurge(parentNode)

    @staticmethod
    def _parseReference(parentNode):
        """
        Parses a reference configuration section.

        We read the following fields::

           author         //cb_config/reference/author
           revision       //cb_config/reference/revision
           description    //cb_config/reference/description
           generator      //cb_config/reference/generator

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``ReferenceConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        reference = None
        sectionNode = readFirstChild(parentNode, "reference")
        if sectionNode is not None:
            reference = ReferenceConfig()
            reference.author = readString(sectionNode, "author")
            reference.revision = readString(sectionNode, "revision")
            reference.description = readString(sectionNode, "description")
            reference.generator = readString(sectionNode, "generator")
        return reference

    @staticmethod
    def _parseExtensions(parentNode):
        """
        Parses an extensions configuration section.

        We read the following fields::

           orderMode            //cb_config/extensions/order_mode

        We also read groups of the following items, one list element per item::

           name                 //cb_config/extensions/action/name
           module               //cb_config/extensions/action/module
           function             //cb_config/extensions/action/function
           index                //cb_config/extensions/action/index
           dependencies         //cb_config/extensions/action/depends

        The extended actions are parsed by :any:`_parseExtendedActions`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``ExtensionsConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        extensions = None
        sectionNode = readFirstChild(parentNode, "extensions")
        if sectionNode is not None:
            extensions = ExtensionsConfig()
            extensions.orderMode = readString(sectionNode, "order_mode")
            extensions.actions = Config._parseExtendedActions(sectionNode)
        return extensions

    @staticmethod
    def _parseOptions(parentNode):
        """
        Parses a options configuration section.

        We read the following fields::

           startingDay    //cb_config/options/starting_day
           workingDir     //cb_config/options/working_dir
           backupUser     //cb_config/options/backup_user
           backupGroup    //cb_config/options/backup_group
           rcpCommand     //cb_config/options/rcp_command
           rshCommand     //cb_config/options/rsh_command
           cbackCommand   //cb_config/options/cback_command
           managedActions //cb_config/options/managed_actions

        The list of managed actions is a comma-separated list of action names.

        We also read groups of the following items, one list element per
        item::

           overrides      //cb_config/options/override
           hooks          //cb_config/options/hook

        The overrides are parsed by :any:`_parseOverrides` and the hooks are parsed
        by :any:`_parseHooks`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``OptionsConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        options = None
        sectionNode = readFirstChild(parentNode, "options")
        if sectionNode is not None:
            options = OptionsConfig()
            options.startingDay = readString(sectionNode, "starting_day")
            options.workingDir = readString(sectionNode, "working_dir")
            options.backupUser = readString(sectionNode, "backup_user")
            options.backupGroup = readString(sectionNode, "backup_group")
            options.rcpCommand = readString(sectionNode, "rcp_command")
            options.rshCommand = readString(sectionNode, "rsh_command")
            options.cbackCommand = readString(sectionNode, "cback_command")
            options.overrides = Config._parseOverrides(sectionNode)
            options.hooks = Config._parseHooks(sectionNode)
            managedActions = readString(sectionNode, "managed_actions")
            options.managedActions = parseCommaSeparatedString(managedActions)
        return options

    @staticmethod
    def _parsePeers(parentNode):
        """
        Parses a peers configuration section.

        We read groups of the following items, one list element per
        item::

           localPeers     //cb_config/stage/peer
           remotePeers    //cb_config/stage/peer

        The individual peer entries are parsed by :any:`_parsePeerList`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``StageConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        peers = None
        sectionNode = readFirstChild(parentNode, "peers")
        if sectionNode is not None:
            peers = PeersConfig()
            (peers.localPeers, peers.remotePeers) = Config._parsePeerList(sectionNode)
        return peers

    @staticmethod
    def _parseCollect(parentNode):
        """
        Parses a collect configuration section.

        We read the following individual fields::

           targetDir            //cb_config/collect/collect_dir
           collectMode          //cb_config/collect/collect_mode
           archiveMode          //cb_config/collect/archive_mode
           ignoreFile           //cb_config/collect/ignore_file

        We also read groups of the following items, one list element per
        item::

           absoluteExcludePaths //cb_config/collect/exclude/abs_path
           excludePatterns      //cb_config/collect/exclude/pattern
           collectFiles         //cb_config/collect/file
           collectDirs          //cb_config/collect/dir

        The exclusions are parsed by :any:`_parseExclusions`, the collect files are
        parsed by :any:`_parseCollectFiles`, and the directories are parsed by
        :any:`_parseCollectDirs`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``CollectConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        collect = None
        sectionNode = readFirstChild(parentNode, "collect")
        if sectionNode is not None:
            collect = CollectConfig()
            collect.targetDir = readString(sectionNode, "collect_dir")
            collect.collectMode = readString(sectionNode, "collect_mode")
            collect.archiveMode = readString(sectionNode, "archive_mode")
            collect.ignoreFile = readString(sectionNode, "ignore_file")
            (collect.absoluteExcludePaths, unused, collect.excludePatterns) = Config._parseExclusions(sectionNode)
            collect.collectFiles = Config._parseCollectFiles(sectionNode)
            collect.collectDirs = Config._parseCollectDirs(sectionNode)
        return collect

    @staticmethod
    def _parseStage(parentNode):
        """
        Parses a stage configuration section.

        We read the following individual fields::

           targetDir      //cb_config/stage/staging_dir

        We also read groups of the following items, one list element per
        item::

           localPeers     //cb_config/stage/peer
           remotePeers    //cb_config/stage/peer

        The individual peer entries are parsed by :any:`_parsePeerList`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``StageConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        stage = None
        sectionNode = readFirstChild(parentNode, "stage")
        if sectionNode is not None:
            stage = StageConfig()
            stage.targetDir = readString(sectionNode, "staging_dir")
            (stage.localPeers, stage.remotePeers) = Config._parsePeerList(sectionNode)
        return stage

    @staticmethod
    def _parseStore(parentNode):
        """
        Parses a store configuration section.

        We read the following fields::

           sourceDir         //cb_config/store/source_dir
           mediaType         //cb_config/store/media_type
           deviceType        //cb_config/store/device_type
           devicePath        //cb_config/store/target_device
           deviceScsiId      //cb_config/store/target_scsi_id
           driveSpeed        //cb_config/store/drive_speed
           checkData         //cb_config/store/check_data
           checkMedia        //cb_config/store/check_media
           warnMidnite       //cb_config/store/warn_midnite
           noEject           //cb_config/store/no_eject

        Blanking behavior configuration is parsed by the ``_parseBlankBehavior``
        method.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``StoreConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        store = None
        sectionNode = readFirstChild(parentNode, "store")
        if sectionNode is not None:
            store = StoreConfig()
            store.sourceDir = readString(sectionNode, "source_dir")
            store.mediaType = readString(sectionNode, "media_type")
            store.deviceType = readString(sectionNode, "device_type")
            store.devicePath = readString(sectionNode, "target_device")
            store.deviceScsiId = readString(sectionNode, "target_scsi_id")
            store.driveSpeed = readInteger(sectionNode, "drive_speed")
            store.checkData = readBoolean(sectionNode, "check_data")
            store.checkMedia = readBoolean(sectionNode, "check_media")
            store.warnMidnite = readBoolean(sectionNode, "warn_midnite")
            store.noEject = readBoolean(sectionNode, "no_eject")
            store.blankBehavior = Config._parseBlankBehavior(sectionNode)
            store.refreshMediaDelay = readInteger(sectionNode, "refresh_media_delay")
            store.ejectDelay = readInteger(sectionNode, "eject_delay")
        return store

    @staticmethod
    def _parsePurge(parentNode):
        """
        Parses a purge configuration section.

        We read groups of the following items, one list element per
        item::

           purgeDirs     //cb_config/purge/dir

        The individual directory entries are parsed by :any:`_parsePurgeDirs`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``PurgeConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        purge = None
        sectionNode = readFirstChild(parentNode, "purge")
        if sectionNode is not None:
            purge = PurgeConfig()
            purge.purgeDirs = Config._parsePurgeDirs(sectionNode)
        return purge

    @staticmethod
    def _parseExtendedActions(parentNode):
        """
        Reads extended actions data from immediately beneath the parent.

        We read the following individual fields from each extended action::

           name           name
           module         module
           function       function
           index          index
           dependencies   depends

        Dependency information is parsed by the ``_parseDependencies`` method.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of extended actions
        Raises:
           ValueError: If the data at the location can't be read
        """
        lst = []
        for entry in readChildren(parentNode, "action"):
            if isElement(entry):
                action = ExtendedAction()
                action.name = readString(entry, "name")
                action.module = readString(entry, "module")
                action.function = readString(entry, "function")
                action.index = readInteger(entry, "index")
                action.dependencies = Config._parseDependencies(entry)
                lst.append(action)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseExclusions(parentNode):
        """
        Reads exclusions data from immediately beneath the parent.

        We read groups of the following items, one list element per item::

           absolute    exclude/abs_path
           relative    exclude/rel_path
           patterns    exclude/pattern

        If there are none of some pattern (i.e. no relative path items) then
        ``None`` will be returned for that item in the tuple.

        This method can be used to parse exclusions on both the collect
        configuration level and on the collect directory level within collect
        configuration.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            Tuple of (absolute, relative, patterns) exclusions
        """
        sectionNode = readFirstChild(parentNode, "exclude")
        if sectionNode is None:
            return (None, None, None)
        else:
            absolute = readStringList(sectionNode, "abs_path")
            relative = readStringList(sectionNode, "rel_path")
            patterns = readStringList(sectionNode, "pattern")
            return (absolute, relative, patterns)

    @staticmethod
    def _parseOverrides(parentNode):
        """
        Reads a list of ``CommandOverride`` objects from immediately beneath the parent.

        We read the following individual fields::

           command                 command
           absolutePath            abs_path

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of ``CommandOverride`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parentNode, "override"):
            if isElement(entry):
                override = CommandOverride()
                override.command = readString(entry, "command")
                override.absolutePath = readString(entry, "abs_path")
                lst.append(override)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseHooks(parentNode):
        """
        Reads a list of ``ActionHook`` objects from immediately beneath the parent.

        We read the following individual fields::

           action                  action
           command                 command

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of ``ActionHook`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parentNode, "pre_action_hook"):
            if isElement(entry):
                hook = PreActionHook()
                hook.action = readString(entry, "action")
                hook.command = readString(entry, "command")
                lst.append(hook)
        for entry in readChildren(parentNode, "post_action_hook"):
            if isElement(entry):
                hook = PostActionHook()
                hook.action = readString(entry, "action")
                hook.command = readString(entry, "command")
                lst.append(hook)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseCollectFiles(parentNode):
        """
        Reads a list of ``CollectFile`` objects from immediately beneath the parent.

        We read the following individual fields::

           absolutePath            abs_path
           collectMode             mode *or* collect_mode
           archiveMode             archive_mode

        The collect mode is a special case.  Just a ``mode`` tag is accepted, but
        we prefer ``collect_mode`` for consistency with the rest of the config
        file and to avoid confusion with the archive mode.  If both are provided,
        only ``mode`` will be used.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of ``CollectFile`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parentNode, "file"):
            if isElement(entry):
                cfile = CollectFile()
                cfile.absolutePath = readString(entry, "abs_path")
                cfile.collectMode = readString(entry, "mode")
                if cfile.collectMode is None:
                    cfile.collectMode = readString(entry, "collect_mode")
                cfile.archiveMode = readString(entry, "archive_mode")
                lst.append(cfile)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parseCollectDirs(parentNode):
        """
        Reads a list of ``CollectDir`` objects from immediately beneath the parent.

        We read the following individual fields::

           absolutePath            abs_path
           collectMode             mode *or* collect_mode
           archiveMode             archive_mode
           ignoreFile              ignore_file
           linkDepth               link_depth
           dereference             dereference
           recursionLevel          recursion_level

        The collect mode is a special case.  Just a ``mode`` tag is accepted for
        backwards compatibility, but we prefer ``collect_mode`` for consistency
        with the rest of the config file and to avoid confusion with the archive
        mode.  If both are provided, only ``mode`` will be used.

        We also read groups of the following items, one list element per
        item::

           absoluteExcludePaths    exclude/abs_path
           relativeExcludePaths    exclude/rel_path
           excludePatterns         exclude/pattern

        The exclusions are parsed by :any:`_parseExclusions`.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of ``CollectDir`` objects or ``None`` if none are found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        lst = []
        for entry in readChildren(parentNode, "dir"):
            if isElement(entry):
                cdir = CollectDir()
                cdir.absolutePath = readString(entry, "abs_path")
                cdir.collectMode = readString(entry, "mode")
                if cdir.collectMode is None:
                    cdir.collectMode = readString(entry, "collect_mode")
                cdir.archiveMode = readString(entry, "archive_mode")
                cdir.ignoreFile = readString(entry, "ignore_file")
                cdir.linkDepth = readInteger(entry, "link_depth")
                cdir.dereference = readBoolean(entry, "dereference")
                cdir.recursionLevel = readInteger(entry, "recursion_level")
                (cdir.absoluteExcludePaths, cdir.relativeExcludePaths, cdir.excludePatterns) = Config._parseExclusions(entry)
                lst.append(cdir)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parsePurgeDirs(parentNode):
        """
        Reads a list of ``PurgeDir`` objects from immediately beneath the parent.

        We read the following individual fields::

           absolutePath            <baseExpr>/abs_path
           retainDays              <baseExpr>/retain_days

        Args:
           parentNode: Parent node to search beneath

        Returns:
            List of ``PurgeDir`` objects or ``None`` if none are found
        Raises:
           ValueError: If the data at the location can't be read
        """
        lst = []
        for entry in readChildren(parentNode, "dir"):
            if isElement(entry):
                cdir = PurgeDir()
                cdir.absolutePath = readString(entry, "abs_path")
                cdir.retainDays = readInteger(entry, "retain_days")
                lst.append(cdir)
        if lst == []:
            lst = None
        return lst

    @staticmethod
    def _parsePeerList(parentNode):
        """
        Reads remote and local peer data from immediately beneath the parent.

        We read the following individual fields for both remote
        and local peers::

           name        name
           collectDir  collect_dir

        We also read the following individual fields for remote peers
        only::

           remoteUser     backup_user
           rcpCommand     rcp_command
           rshCommand     rsh_command
           cbackCommand   cback_command
           managed        managed
           managedActions managed_actions

        Additionally, the value in the ``type`` field is used to determine whether
        this entry is a remote peer.  If the type is ``"remote"``, it's a remote
        peer, and if the type is ``"local"``, it's a remote peer.

        If there are none of one type of peer (i.e. no local peers) then ``None``
        will be returned for that item in the tuple.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            Tuple of (local, remote) peer lists
        Raises:
           ValueError: If the data at the location can't be read
        """
        localPeers = []
        remotePeers = []
        for entry in readChildren(parentNode, "peer"):
            if isElement(entry):
                peerType = readString(entry, "type")
                if peerType == "local":
                    localPeer = LocalPeer()
                    localPeer.name = readString(entry, "name")
                    localPeer.collectDir = readString(entry, "collect_dir")
                    localPeer.ignoreFailureMode = readString(entry, "ignore_failures")
                    localPeers.append(localPeer)
                elif peerType == "remote":
                    remotePeer = RemotePeer()
                    remotePeer.name = readString(entry, "name")
                    remotePeer.collectDir = readString(entry, "collect_dir")
                    remotePeer.remoteUser = readString(entry, "backup_user")
                    remotePeer.rcpCommand = readString(entry, "rcp_command")
                    remotePeer.rshCommand = readString(entry, "rsh_command")
                    remotePeer.cbackCommand = readString(entry, "cback_command")
                    remotePeer.ignoreFailureMode = readString(entry, "ignore_failures")
                    remotePeer.managed = readBoolean(entry, "managed")
                    managedActions = readString(entry, "managed_actions")
                    remotePeer.managedActions = parseCommaSeparatedString(managedActions)
                    remotePeers.append(remotePeer)
        if localPeers == []:
            localPeers = None
        if remotePeers == []:
            remotePeers = None
        return (localPeers, remotePeers)

    @staticmethod
    def _parseDependencies(parentNode):
        """
        Reads extended action dependency information from a parent node.

        We read the following individual fields::

           runBefore   depends/run_before
           runAfter    depends/run_after

        Each of these fields is a comma-separated list of action names.

        The result is placed into an ``ActionDependencies`` object.

        If the dependencies parent node does not exist, ``None`` will be returned.
        Otherwise, an ``ActionDependencies`` object will always be created, even
        if it does not contain any actual dependencies in it.

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``ActionDependencies`` object or ``None``
        Raises:
           ValueError: If the data at the location can't be read
        """
        sectionNode = readFirstChild(parentNode, "depends")
        if sectionNode is None:
            return None
        else:
            runBefore = readString(sectionNode, "run_before")
            runAfter = readString(sectionNode, "run_after")
            beforeList = parseCommaSeparatedString(runBefore)
            afterList = parseCommaSeparatedString(runAfter)
            return ActionDependencies(beforeList, afterList)

    @staticmethod
    def _parseBlankBehavior(parentNode):
        """
        Reads a single ``BlankBehavior`` object from immediately beneath the parent.

        We read the following individual fields::

           blankMode     blank_behavior/mode
           blankFactor   blank_behavior/factor

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``BlankBehavior`` object or ``None`` if none if the section is not found
        Raises:
           ValueError: If some filled-in value is invalid
        """
        blankBehavior = None
        sectionNode = readFirstChild(parentNode, "blank_behavior")
        if sectionNode is not None:
            blankBehavior = BlankBehavior()
            blankBehavior.blankMode = readString(sectionNode, "mode")
            blankBehavior.blankFactor = readString(sectionNode, "factor")
        return blankBehavior

    ########################################
    # High-level methods for generating XML
    ########################################

    def _extractXml(self):
        """
        Internal method to extract configuration into an XML string.

        This method assumes that the internal :any:`validate` method has been called
        prior to extracting the XML, if the caller cares.  No validation will be
        done internally.

        As a general rule, fields that are set to ``None`` will be extracted into
        the document as empty tags.  The same goes for container tags that are
        filled based on lists - if the list is empty or ``None``, the container
        tag will be empty.
        """
        (xmlDom, parentNode) = createOutputDom()
        Config._addReference(xmlDom, parentNode, self.reference)
        Config._addExtensions(xmlDom, parentNode, self.extensions)
        Config._addOptions(xmlDom, parentNode, self.options)
        Config._addPeers(xmlDom, parentNode, self.peers)
        Config._addCollect(xmlDom, parentNode, self.collect)
        Config._addStage(xmlDom, parentNode, self.stage)
        Config._addStore(xmlDom, parentNode, self.store)
        Config._addPurge(xmlDom, parentNode, self.purge)
        xmlData = serializeDom(xmlDom)
        xmlDom.unlink()
        return xmlData

    @staticmethod
    def _addReference(xmlDom, parentNode, referenceConfig):
        """
        Adds a <reference> configuration section as the next child of a parent.

        We add the following fields to the document::

           author         //cb_config/reference/author
           revision       //cb_config/reference/revision
           description    //cb_config/reference/description
           generator      //cb_config/reference/generator

        If ``referenceConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           referenceConfig: Reference configuration section to be added to the document
        """
        if referenceConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "reference")
            addStringNode(xmlDom, sectionNode, "author", referenceConfig.author)
            addStringNode(xmlDom, sectionNode, "revision", referenceConfig.revision)
            addStringNode(xmlDom, sectionNode, "description", referenceConfig.description)
            addStringNode(xmlDom, sectionNode, "generator", referenceConfig.generator)

    @staticmethod
    def _addExtensions(xmlDom, parentNode, extensionsConfig):
        """
        Adds an <extensions> configuration section as the next child of a parent.

        We add the following fields to the document::

           order_mode     //cb_config/extensions/order_mode

        We also add groups of the following items, one list element per item::

           actions        //cb_config/extensions/action

        The extended action entries are added by :any:`_addExtendedAction`.

        If ``extensionsConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           extensionsConfig: Extensions configuration section to be added to the document
        """
        if extensionsConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "extensions")
            addStringNode(xmlDom, sectionNode, "order_mode", extensionsConfig.orderMode)
            if extensionsConfig.actions is not None:
                for action in extensionsConfig.actions:
                    Config._addExtendedAction(xmlDom, sectionNode, action)

    @staticmethod
    def _addOptions(xmlDom, parentNode, optionsConfig):
        """
        Adds a <options> configuration section as the next child of a parent.

        We add the following fields to the document::

           startingDay    //cb_config/options/starting_day
           workingDir     //cb_config/options/working_dir
           backupUser     //cb_config/options/backup_user
           backupGroup    //cb_config/options/backup_group
           rcpCommand     //cb_config/options/rcp_command
           rshCommand     //cb_config/options/rsh_command
           cbackCommand   //cb_config/options/cback_command
           managedActions //cb_config/options/managed_actions

        We also add groups of the following items, one list element per
        item::

           overrides      //cb_config/options/override
           hooks          //cb_config/options/pre_action_hook
           hooks          //cb_config/options/post_action_hook

        The individual override items are added by :any:`_addOverride`.  The
        individual hook items are added by :any:`_addHook`.

        If ``optionsConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           optionsConfig: Options configuration section to be added to the document
        """
        if optionsConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "options")
            addStringNode(xmlDom, sectionNode, "starting_day", optionsConfig.startingDay)
            addStringNode(xmlDom, sectionNode, "working_dir", optionsConfig.workingDir)
            addStringNode(xmlDom, sectionNode, "backup_user", optionsConfig.backupUser)
            addStringNode(xmlDom, sectionNode, "backup_group", optionsConfig.backupGroup)
            addStringNode(xmlDom, sectionNode, "rcp_command", optionsConfig.rcpCommand)
            addStringNode(xmlDom, sectionNode, "rsh_command", optionsConfig.rshCommand)
            addStringNode(xmlDom, sectionNode, "cback_command", optionsConfig.cbackCommand)
            managedActions = Config._buildCommaSeparatedString(optionsConfig.managedActions)
            addStringNode(xmlDom, sectionNode, "managed_actions", managedActions)
            if optionsConfig.overrides is not None:
                for override in optionsConfig.overrides:
                    Config._addOverride(xmlDom, sectionNode, override)
            if optionsConfig.hooks is not None:
                for hook in optionsConfig.hooks:
                    Config._addHook(xmlDom, sectionNode, hook)

    @staticmethod
    def _addPeers(xmlDom, parentNode, peersConfig):
        """
        Adds a <peers> configuration section as the next child of a parent.

        We add groups of the following items, one list element per
        item::

           localPeers     //cb_config/peers/peer
           remotePeers    //cb_config/peers/peer

        The individual local and remote peer entries are added by
        :any:`_addLocalPeer` and :any:`_addRemotePeer`, respectively.

        If ``peersConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           peersConfig: Peers configuration section to be added to the document
        """
        if peersConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "peers")
            if peersConfig.localPeers is not None:
                for localPeer in peersConfig.localPeers:
                    Config._addLocalPeer(xmlDom, sectionNode, localPeer)
            if peersConfig.remotePeers is not None:
                for remotePeer in peersConfig.remotePeers:
                    Config._addRemotePeer(xmlDom, sectionNode, remotePeer)

    @staticmethod
    def _addCollect(xmlDom, parentNode, collectConfig):
        """
        Adds a <collect> configuration section as the next child of a parent.

        We add the following fields to the document::

           targetDir            //cb_config/collect/collect_dir
           collectMode          //cb_config/collect/collect_mode
           archiveMode          //cb_config/collect/archive_mode
           ignoreFile           //cb_config/collect/ignore_file

        We also add groups of the following items, one list element per
        item::

           absoluteExcludePaths //cb_config/collect/exclude/abs_path
           excludePatterns      //cb_config/collect/exclude/pattern
           collectFiles         //cb_config/collect/file
           collectDirs          //cb_config/collect/dir

        The individual collect files are added by :any:`_addCollectFile` and
        individual collect directories are added by :any:`_addCollectDir`.

        If ``collectConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           collectConfig: Collect configuration section to be added to the document
        """
        if collectConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "collect")
            addStringNode(xmlDom, sectionNode, "collect_dir", collectConfig.targetDir)
            addStringNode(xmlDom, sectionNode, "collect_mode", collectConfig.collectMode)
            addStringNode(xmlDom, sectionNode, "archive_mode", collectConfig.archiveMode)
            addStringNode(xmlDom, sectionNode, "ignore_file", collectConfig.ignoreFile)
            if (collectConfig.absoluteExcludePaths is not None and collectConfig.absoluteExcludePaths != []) or (
                collectConfig.excludePatterns is not None and collectConfig.excludePatterns != []
            ):
                excludeNode = addContainerNode(xmlDom, sectionNode, "exclude")
                if collectConfig.absoluteExcludePaths is not None:
                    for absolutePath in collectConfig.absoluteExcludePaths:
                        addStringNode(xmlDom, excludeNode, "abs_path", absolutePath)
                if collectConfig.excludePatterns is not None:
                    for pattern in collectConfig.excludePatterns:
                        addStringNode(xmlDom, excludeNode, "pattern", pattern)
            if collectConfig.collectFiles is not None:
                for collectFile in collectConfig.collectFiles:
                    Config._addCollectFile(xmlDom, sectionNode, collectFile)
            if collectConfig.collectDirs is not None:
                for collectDir in collectConfig.collectDirs:
                    Config._addCollectDir(xmlDom, sectionNode, collectDir)

    @staticmethod
    def _addStage(xmlDom, parentNode, stageConfig):
        """
        Adds a <stage> configuration section as the next child of a parent.

        We add the following fields to the document::

           targetDir      //cb_config/stage/staging_dir

        We also add groups of the following items, one list element per
        item::

           localPeers     //cb_config/stage/peer
           remotePeers    //cb_config/stage/peer

        The individual local and remote peer entries are added by
        :any:`_addLocalPeer` and :any:`_addRemotePeer`, respectively.

        If ``stageConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           stageConfig: Stage configuration section to be added to the document
        """
        if stageConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "stage")
            addStringNode(xmlDom, sectionNode, "staging_dir", stageConfig.targetDir)
            if stageConfig.localPeers is not None:
                for localPeer in stageConfig.localPeers:
                    Config._addLocalPeer(xmlDom, sectionNode, localPeer)
            if stageConfig.remotePeers is not None:
                for remotePeer in stageConfig.remotePeers:
                    Config._addRemotePeer(xmlDom, sectionNode, remotePeer)

    @staticmethod
    def _addStore(xmlDom, parentNode, storeConfig):
        """
        Adds a <store> configuration section as the next child of a parent.

        We add the following fields to the document::

           sourceDir         //cb_config/store/source_dir
           mediaType         //cb_config/store/media_type
           deviceType        //cb_config/store/device_type
           devicePath        //cb_config/store/target_device
           deviceScsiId      //cb_config/store/target_scsi_id
           driveSpeed        //cb_config/store/drive_speed
           checkData         //cb_config/store/check_data
           checkMedia        //cb_config/store/check_media
           warnMidnite       //cb_config/store/warn_midnite
           noEject           //cb_config/store/no_eject
           refreshMediaDelay //cb_config/store/refresh_media_delay
           ejectDelay        //cb_config/store/eject_delay

        Blanking behavior configuration is added by the :any:`_addBlankBehavior`
        method.

        If ``storeConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           storeConfig: Store configuration section to be added to the document
        """
        if storeConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "store")
            addStringNode(xmlDom, sectionNode, "source_dir", storeConfig.sourceDir)
            addStringNode(xmlDom, sectionNode, "media_type", storeConfig.mediaType)
            addStringNode(xmlDom, sectionNode, "device_type", storeConfig.deviceType)
            addStringNode(xmlDom, sectionNode, "target_device", storeConfig.devicePath)
            addStringNode(xmlDom, sectionNode, "target_scsi_id", storeConfig.deviceScsiId)
            addIntegerNode(xmlDom, sectionNode, "drive_speed", storeConfig.driveSpeed)
            addBooleanNode(xmlDom, sectionNode, "check_data", storeConfig.checkData)
            addBooleanNode(xmlDom, sectionNode, "check_media", storeConfig.checkMedia)
            addBooleanNode(xmlDom, sectionNode, "warn_midnite", storeConfig.warnMidnite)
            addBooleanNode(xmlDom, sectionNode, "no_eject", storeConfig.noEject)
            addIntegerNode(xmlDom, sectionNode, "refresh_media_delay", storeConfig.refreshMediaDelay)
            addIntegerNode(xmlDom, sectionNode, "eject_delay", storeConfig.ejectDelay)
            Config._addBlankBehavior(xmlDom, sectionNode, storeConfig.blankBehavior)

    @staticmethod
    def _addPurge(xmlDom, parentNode, purgeConfig):
        """
        Adds a <purge> configuration section as the next child of a parent.

        We add the following fields to the document::

           purgeDirs     //cb_config/purge/dir

        The individual directory entries are added by :any:`_addPurgeDir`.

        If ``purgeConfig`` is ``None``, then no container will be added.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           purgeConfig: Purge configuration section to be added to the document
        """
        if purgeConfig is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "purge")
            if purgeConfig.purgeDirs is not None:
                for purgeDir in purgeConfig.purgeDirs:
                    Config._addPurgeDir(xmlDom, sectionNode, purgeDir)

    @staticmethod
    def _addExtendedAction(xmlDom, parentNode, action):
        """
        Adds an extended action container as the next child of a parent.

        We add the following fields to the document::

           name           action/name
           module         action/module
           function       action/function
           index          action/index
           dependencies   action/depends

        Dependencies are added by the :any:`_addDependencies` method.

        The <action> node itself is created as the next child of the parent node.
        This method only adds one action node.  The parent must loop for each action
        in the ``ExtensionsConfig`` object.

        If ``action`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           action: Purge directory to be added to the document
        """
        if action is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "action")
            addStringNode(xmlDom, sectionNode, "name", action.name)
            addStringNode(xmlDom, sectionNode, "module", action.module)
            addStringNode(xmlDom, sectionNode, "function", action.function)
            addIntegerNode(xmlDom, sectionNode, "index", action.index)
            Config._addDependencies(xmlDom, sectionNode, action.dependencies)

    @staticmethod
    def _addOverride(xmlDom, parentNode, override):
        """
        Adds a command override container as the next child of a parent.

        We add the following fields to the document::

           command                 override/command
           absolutePath            override/abs_path

        The <override> node itself is created as the next child of the parent
        node.  This method only adds one override node.  The parent must loop for
        each override in the ``OptionsConfig`` object.

        If ``override`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           override: Command override to be added to the document
        """
        if override is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "override")
            addStringNode(xmlDom, sectionNode, "command", override.command)
            addStringNode(xmlDom, sectionNode, "abs_path", override.absolutePath)

    @staticmethod
    def _addHook(xmlDom, parentNode, hook):
        """
        Adds an action hook container as the next child of a parent.

        The behavior varies depending on the value of the ``before`` and ``after``
        flags on the hook.  If the ``before`` flag is set, it's a pre-action hook,
        and we'll add the following fields::

           action                  pre_action_hook/action
           command                 pre_action_hook/command

        If the ``after`` flag is set, it's a post-action hook, and we'll add the
        following fields::

           action                  post_action_hook/action
           command                 post_action_hook/command

        The <pre_action_hook> or <post_action_hook> node itself is created as the
        next child of the parent node.  This method only adds one hook node.  The
        parent must loop for each hook in the ``OptionsConfig`` object.

        If ``hook`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           hook: Command hook to be added to the document
        """
        if hook is not None:
            if hook.before:
                sectionNode = addContainerNode(xmlDom, parentNode, "pre_action_hook")
            else:
                sectionNode = addContainerNode(xmlDom, parentNode, "post_action_hook")
            addStringNode(xmlDom, sectionNode, "action", hook.action)
            addStringNode(xmlDom, sectionNode, "command", hook.command)

    @staticmethod
    def _addCollectFile(xmlDom, parentNode, collectFile):
        """
        Adds a collect file container as the next child of a parent.

        We add the following fields to the document::

           absolutePath            dir/abs_path
           collectMode             dir/collect_mode
           archiveMode             dir/archive_mode

        Note that for consistency with collect directory handling we'll only emit
        the preferred ``collect_mode`` tag.

        The <file> node itself is created as the next child of the parent node.
        This method only adds one collect file node.  The parent must loop
        for each collect file in the ``CollectConfig`` object.

        If ``collectFile`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           collectFile: Collect file to be added to the document
        """
        if collectFile is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "file")
            addStringNode(xmlDom, sectionNode, "abs_path", collectFile.absolutePath)
            addStringNode(xmlDom, sectionNode, "collect_mode", collectFile.collectMode)
            addStringNode(xmlDom, sectionNode, "archive_mode", collectFile.archiveMode)

    @staticmethod
    def _addCollectDir(xmlDom, parentNode, collectDir):
        """
        Adds a collect directory container as the next child of a parent.

        We add the following fields to the document::

           absolutePath            dir/abs_path
           collectMode             dir/collect_mode
           archiveMode             dir/archive_mode
           ignoreFile              dir/ignore_file
           linkDepth               dir/link_depth
           dereference             dir/dereference
           recursionLevel          dir/recursion_level

        Note that an original XML document might have listed the collect mode
        using the ``mode`` tag, since we accept both ``collect_mode`` and ``mode``.
        However, here we'll only emit the preferred ``collect_mode`` tag.

        We also add groups of the following items, one list element per item::

           absoluteExcludePaths    dir/exclude/abs_path
           relativeExcludePaths    dir/exclude/rel_path
           excludePatterns         dir/exclude/pattern

        The <dir> node itself is created as the next child of the parent node.
        This method only adds one collect directory node.  The parent must loop
        for each collect directory in the ``CollectConfig`` object.

        If ``collectDir`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           collectDir: Collect directory to be added to the document
        """
        if collectDir is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "dir")
            addStringNode(xmlDom, sectionNode, "abs_path", collectDir.absolutePath)
            addStringNode(xmlDom, sectionNode, "collect_mode", collectDir.collectMode)
            addStringNode(xmlDom, sectionNode, "archive_mode", collectDir.archiveMode)
            addStringNode(xmlDom, sectionNode, "ignore_file", collectDir.ignoreFile)
            addIntegerNode(xmlDom, sectionNode, "link_depth", collectDir.linkDepth)
            addBooleanNode(xmlDom, sectionNode, "dereference", collectDir.dereference)
            addIntegerNode(xmlDom, sectionNode, "recursion_level", collectDir.recursionLevel)
            if (
                (collectDir.absoluteExcludePaths is not None and collectDir.absoluteExcludePaths != [])
                or (collectDir.relativeExcludePaths is not None and collectDir.relativeExcludePaths != [])
                or (collectDir.excludePatterns is not None and collectDir.excludePatterns != [])
            ):
                excludeNode = addContainerNode(xmlDom, sectionNode, "exclude")
                if collectDir.absoluteExcludePaths is not None:
                    for absolutePath in collectDir.absoluteExcludePaths:
                        addStringNode(xmlDom, excludeNode, "abs_path", absolutePath)
                if collectDir.relativeExcludePaths is not None:
                    for relativePath in collectDir.relativeExcludePaths:
                        addStringNode(xmlDom, excludeNode, "rel_path", relativePath)
                if collectDir.excludePatterns is not None:
                    for pattern in collectDir.excludePatterns:
                        addStringNode(xmlDom, excludeNode, "pattern", pattern)

    @staticmethod
    def _addLocalPeer(xmlDom, parentNode, localPeer):
        """
        Adds a local peer container as the next child of a parent.

        We add the following fields to the document::

           name                peer/name
           collectDir          peer/collect_dir
           ignoreFailureMode   peer/ignore_failures

        Additionally, ``peer/type`` is filled in with ``"local"``, since this is a
        local peer.

        The <peer> node itself is created as the next child of the parent node.
        This method only adds one peer node.  The parent must loop for each peer
        in the ``StageConfig`` object.

        If ``localPeer`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           localPeer: Purge directory to be added to the document
        """
        if localPeer is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "peer")
            addStringNode(xmlDom, sectionNode, "name", localPeer.name)
            addStringNode(xmlDom, sectionNode, "type", "local")
            addStringNode(xmlDom, sectionNode, "collect_dir", localPeer.collectDir)
            addStringNode(xmlDom, sectionNode, "ignore_failures", localPeer.ignoreFailureMode)

    @staticmethod
    def _addRemotePeer(xmlDom, parentNode, remotePeer):
        """
        Adds a remote peer container as the next child of a parent.

        We add the following fields to the document::

           name                peer/name
           collectDir          peer/collect_dir
           remoteUser          peer/backup_user
           rcpCommand          peer/rcp_command
           rcpCommand          peer/rcp_command
           rshCommand          peer/rsh_command
           cbackCommand        peer/cback_command
           ignoreFailureMode   peer/ignore_failures
           managed             peer/managed
           managedActions      peer/managed_actions

        Additionally, ``peer/type`` is filled in with ``"remote"``, since this is a
        remote peer.

        The <peer> node itself is created as the next child of the parent node.
        This method only adds one peer node.  The parent must loop for each peer
        in the ``StageConfig`` object.

        If ``remotePeer`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           remotePeer: Purge directory to be added to the document
        """
        if remotePeer is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "peer")
            addStringNode(xmlDom, sectionNode, "name", remotePeer.name)
            addStringNode(xmlDom, sectionNode, "type", "remote")
            addStringNode(xmlDom, sectionNode, "collect_dir", remotePeer.collectDir)
            addStringNode(xmlDom, sectionNode, "backup_user", remotePeer.remoteUser)
            addStringNode(xmlDom, sectionNode, "rcp_command", remotePeer.rcpCommand)
            addStringNode(xmlDom, sectionNode, "rsh_command", remotePeer.rshCommand)
            addStringNode(xmlDom, sectionNode, "cback_command", remotePeer.cbackCommand)
            addStringNode(xmlDom, sectionNode, "ignore_failures", remotePeer.ignoreFailureMode)
            addBooleanNode(xmlDom, sectionNode, "managed", remotePeer.managed)
            managedActions = Config._buildCommaSeparatedString(remotePeer.managedActions)
            addStringNode(xmlDom, sectionNode, "managed_actions", managedActions)

    @staticmethod
    def _addPurgeDir(xmlDom, parentNode, purgeDir):
        """
        Adds a purge directory container as the next child of a parent.

        We add the following fields to the document::

           absolutePath            dir/abs_path
           retainDays              dir/retain_days

        The <dir> node itself is created as the next child of the parent node.
        This method only adds one purge directory node.  The parent must loop for
        each purge directory in the ``PurgeConfig`` object.

        If ``purgeDir`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           purgeDir: Purge directory to be added to the document
        """
        if purgeDir is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "dir")
            addStringNode(xmlDom, sectionNode, "abs_path", purgeDir.absolutePath)
            addIntegerNode(xmlDom, sectionNode, "retain_days", purgeDir.retainDays)

    @staticmethod
    def _addDependencies(xmlDom, parentNode, dependencies):
        """
        Adds a extended action dependencies to parent node.

        We add the following fields to the document::

           runBefore      depends/run_before
           runAfter       depends/run_after

        If ``dependencies`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           dependencies: ``ActionDependencies`` object to be added to the document
        """
        if dependencies is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "depends")
            runBefore = Config._buildCommaSeparatedString(dependencies.beforeList)
            runAfter = Config._buildCommaSeparatedString(dependencies.afterList)
            addStringNode(xmlDom, sectionNode, "run_before", runBefore)
            addStringNode(xmlDom, sectionNode, "run_after", runAfter)

    @staticmethod
    def _buildCommaSeparatedString(valueList):
        """
        Creates a comma-separated string from a list of values.

        As a special case, if ``valueList`` is ``None``, then ``None`` will be
        returned.

        Args:
           valueList: List of values to be placed into a string

        Returns:
            Values from valueList as a comma-separated string
        """
        if valueList is None:
            return None
        return ",".join(valueList)

    @staticmethod
    def _addBlankBehavior(xmlDom, parentNode, blankBehavior):
        """
        Adds a blanking behavior container as the next child of a parent.

        We add the following fields to the document::

           blankMode    blank_behavior/mode
           blankFactor  blank_behavior/factor

        The <blank_behavior> node itself is created as the next child of the
        parent node.

        If ``blankBehavior`` is ``None``, this method call will be a no-op.

        Args:
           xmlDom: DOM tree as from :any:`createOutputDom`
           parentNode: Parent that the section should be appended to
           blankBehavior: Blanking behavior to be added to the document
        """
        if blankBehavior is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "blank_behavior")
            addStringNode(xmlDom, sectionNode, "mode", blankBehavior.blankMode)
            addStringNode(xmlDom, sectionNode, "factor", blankBehavior.blankFactor)

    #################################################
    # High-level methods used for validating content
    #################################################

    def _validateContents(self):
        """
        Validates configuration contents per rules discussed in module
        documentation.

        This is the second pass at validation.  It ensures that any filled-in
        section contains valid data.  Any sections which is not set to ``None`` is
        validated per the rules for that section, laid out in the module
        documentation (above).

        Raises:
           ValueError: If configuration is invalid
        """
        self._validateReference()
        self._validateExtensions()
        self._validateOptions()
        self._validatePeers()
        self._validateCollect()
        self._validateStage()
        self._validateStore()
        self._validatePurge()

    def _validateReference(self):
        """
        Validates reference configuration.
        There are currently no reference-related validations.
        Raises:
           ValueError: If reference configuration is invalid
        """
        pass

    def _validateExtensions(self):
        """
        Validates extensions configuration.

        The list of actions may be either ``None`` or an empty list ``[]`` if
        desired.  Each extended action must include a name, a module, and a
        function.

        Then, if the order mode is None or "index", an index is required; and if
        the order mode is "dependency", dependency information is required.

        Raises:
           ValueError: If reference configuration is invalid
        """
        if self.extensions is not None:
            if self.extensions.actions is not None:
                names = []
                for action in self.extensions.actions:
                    if action.name is None:
                        raise ValueError("Each extended action must set a name.")
                    names.append(action.name)
                    if action.module is None:
                        raise ValueError("Each extended action must set a module.")
                    if action.function is None:
                        raise ValueError("Each extended action must set a function.")
                    if self.extensions.orderMode is None or self.extensions.orderMode == "index":
                        if action.index is None:
                            raise ValueError("Each extended action must set an index, based on order mode.")
                    elif self.extensions.orderMode == "dependency":
                        if action.dependencies is None:
                            raise ValueError("Each extended action must set dependency information, based on order mode.")
                checkUnique("Duplicate extension names exist:", names)

    def _validateOptions(self):
        """
        Validates options configuration.

        All fields must be filled in except the rsh command.  The rcp and rsh
        commands are used as default values for all remote peers.  Remote peers
        can also rely on the backup user as the default remote user name if they
        choose.

        Raises:
           ValueError: If reference configuration is invalid
        """
        if self.options is not None:
            if self.options.startingDay is None:
                raise ValueError("Options section starting day must be filled in.")
            if self.options.workingDir is None:
                raise ValueError("Options section working directory must be filled in.")
            if self.options.backupUser is None:
                raise ValueError("Options section backup user must be filled in.")
            if self.options.backupGroup is None:
                raise ValueError("Options section backup group must be filled in.")
            if self.options.rcpCommand is None:
                raise ValueError("Options section remote copy command must be filled in.")

    def _validatePeers(self):
        """
        Validates peers configuration per rules in :any:`_validatePeerList`.
        Raises:
           ValueError: If peers configuration is invalid
        """
        if self.peers is not None:
            self._validatePeerList(self.peers.localPeers, self.peers.remotePeers)

    def _validateCollect(self):
        """
        Validates collect configuration.

        The target directory must be filled in.  The collect mode, archive mode,
        ignore file, and recursion level are all optional.  The list of absolute
        paths to exclude and patterns to exclude may be either ``None`` or an
        empty list ``[]`` if desired.

        Each collect directory entry must contain an absolute path to collect,
        and then must either be able to take collect mode, archive mode and
        ignore file configuration from the parent ``CollectConfig`` object, or
        must set each value on its own.  The list of absolute paths to exclude,
        relative paths to exclude and patterns to exclude may be either ``None``
        or an empty list ``[]`` if desired.  Any list of absolute paths to exclude
        or patterns to exclude will be combined with the same list in the
        ``CollectConfig`` object to make the complete list for a given directory.

        Raises:
           ValueError: If collect configuration is invalid
        """
        if self.collect is not None:
            if self.collect.targetDir is None:
                raise ValueError("Collect section target directory must be filled in.")
            if self.collect.collectFiles is not None:
                for collectFile in self.collect.collectFiles:
                    if collectFile.absolutePath is None:
                        raise ValueError("Each collect file must set an absolute path.")
                    if self.collect.collectMode is None and collectFile.collectMode is None:
                        raise ValueError("Collect mode must either be set in parent collect section or individual collect file.")
                    if self.collect.archiveMode is None and collectFile.archiveMode is None:
                        raise ValueError("Archive mode must either be set in parent collect section or individual collect file.")
            if self.collect.collectDirs is not None:
                for collectDir in self.collect.collectDirs:
                    if collectDir.absolutePath is None:
                        raise ValueError("Each collect directory must set an absolute path.")
                    if self.collect.collectMode is None and collectDir.collectMode is None:
                        raise ValueError(
                            "Collect mode must either be set in parent collect section or individual collect directory."
                        )
                    if self.collect.archiveMode is None and collectDir.archiveMode is None:
                        raise ValueError(
                            "Archive mode must either be set in parent collect section or individual collect directory."
                        )
                    if self.collect.ignoreFile is None and collectDir.ignoreFile is None:
                        raise ValueError(
                            "Ignore file must either be set in parent collect section or individual collect directory."
                        )
                    if (collectDir.linkDepth is None or collectDir.linkDepth < 1) and collectDir.dereference:
                        raise ValueError("Dereference flag is only valid when a non-zero link depth is in use.")

    def _validateStage(self):
        """
        Validates stage configuration.

        The target directory must be filled in, and the peers are
        also validated.

        Peers are only required in this section if the peers configuration
        section is not filled in.  However, if any peers are filled in
        here, they override the peers configuration and must meet the
        validation criteria in :any:`_validatePeerList`.

        Raises:
           ValueError: If stage configuration is invalid
        """
        if self.stage is not None:
            if self.stage.targetDir is None:
                raise ValueError("Stage section target directory must be filled in.")
            if self.peers is None:
                # In this case, stage configuration is our only configuration and must be valid.
                self._validatePeerList(self.stage.localPeers, self.stage.remotePeers)
            else:
                # In this case, peers configuration is the default and stage configuration overrides.
                # Validation is only needed if it's stage configuration is actually filled in.
                if self.stage.hasPeers():
                    self._validatePeerList(self.stage.localPeers, self.stage.remotePeers)

    def _validateStore(self):
        """
        Validates store configuration.

        The device type, drive speed, and blanking behavior are optional.  All
        other values are required. Missing booleans will be set to defaults.

        If blanking behavior is provided, then both a blanking mode and a
        blanking factor are required.

        The image writer functionality in the ``writer`` module is supposed to be
        able to handle a device speed of ``None``.

        Any caller which needs a "real" (non-``None``) value for the device type
        can use ``DEFAULT_DEVICE_TYPE``, which is guaranteed to be sensible.

        This is also where we make sure that the media type -- which is already a
        valid type -- matches up properly with the device type.

        Raises:
           ValueError: If store configuration is invalid
        """
        if self.store is not None:
            if self.store.sourceDir is None:
                raise ValueError("Store section source directory must be filled in.")
            if self.store.mediaType is None:
                raise ValueError("Store section media type must be filled in.")
            if self.store.devicePath is None:
                raise ValueError("Store section device path must be filled in.")
            if self.store.deviceType is None or self.store.deviceType == "cdwriter":
                if self.store.mediaType not in VALID_CD_MEDIA_TYPES:
                    raise ValueError("Media type must match device type.")
            elif self.store.deviceType == "dvdwriter":
                if self.store.mediaType not in VALID_DVD_MEDIA_TYPES:
                    raise ValueError("Media type must match device type.")
            if self.store.blankBehavior is not None:
                if self.store.blankBehavior.blankMode is None and self.store.blankBehavior.blankFactor is None:
                    raise ValueError("If blanking behavior is provided, all values must be filled in.")

    def _validatePurge(self):
        """
        Validates purge configuration.

        The list of purge directories may be either ``None`` or an empty list
        ``[]`` if desired.  All purge directories must contain a path and a retain
        days value.

        Raises:
           ValueError: If purge configuration is invalid
        """
        if self.purge is not None:
            if self.purge.purgeDirs is not None:
                for purgeDir in self.purge.purgeDirs:
                    if purgeDir.absolutePath is None:
                        raise ValueError("Each purge directory must set an absolute path.")
                    if purgeDir.retainDays is None:
                        raise ValueError("Each purge directory must set a retain days value.")

    def _validatePeerList(self, localPeers, remotePeers):
        """
        Validates the set of local and remote peers.

        Local peers must be completely filled in, including both name and collect
        directory.  Remote peers must also fill in the name and collect
        directory, but can leave the remote user and rcp command unset.  In this
        case, the remote user is assumed to match the backup user from the
        options section and rcp command is taken directly from the options
        section.

        Args:
           localPeers: List of local peers
           remotePeers: List of remote peers

        Raises:
           ValueError: If stage configuration is invalid
        """
        if localPeers is None and remotePeers is None:
            raise ValueError("Peer list must contain at least one backup peer.")
        if localPeers is None and remotePeers is not None:
            if len(remotePeers) < 1:
                raise ValueError("Peer list must contain at least one backup peer.")
        elif localPeers is not None and remotePeers is None:
            if len(localPeers) < 1:
                raise ValueError("Peer list must contain at least one backup peer.")
        elif localPeers is not None and remotePeers is not None:
            if len(localPeers) + len(remotePeers) < 1:
                raise ValueError("Peer list must contain at least one backup peer.")
        names = []
        if localPeers is not None:
            for localPeer in localPeers:
                if localPeer.name is None:
                    raise ValueError("Local peers must set a name.")
                names.append(localPeer.name)
                if localPeer.collectDir is None:
                    raise ValueError("Local peers must set a collect directory.")
        if remotePeers is not None:
            for remotePeer in remotePeers:
                if remotePeer.name is None:
                    raise ValueError("Remote peers must set a name.")
                names.append(remotePeer.name)
                if remotePeer.collectDir is None:
                    raise ValueError("Remote peers must set a collect directory.")
                if (self.options is None or self.options.backupUser is None) and remotePeer.remoteUser is None:
                    raise ValueError("Remote user must either be set in options section or individual remote peer.")
                if (self.options is None or self.options.rcpCommand is None) and remotePeer.rcpCommand is None:
                    raise ValueError("Remote copy command must either be set in options section or individual remote peer.")
                if remotePeer.managed:
                    if (self.options is None or self.options.rshCommand is None) and remotePeer.rshCommand is None:
                        raise ValueError("Remote shell command must either be set in options section or individual remote peer.")
                    if (self.options is None or self.options.cbackCommand is None) and remotePeer.cbackCommand is None:
                        raise ValueError("Remote cback command must either be set in options section or individual remote peer.")
                    if (self.options is None or self.options.managedActions is None or len(self.options.managedActions) < 1) and (
                        remotePeer.managedActions is None or len(remotePeer.managedActions) < 1
                    ):
                        raise ValueError("Managed actions list must be set in options section or individual remote peer.")
        checkUnique("Duplicate peer names exist:", names)


########################################################################
# General utility functions
########################################################################


def readByteQuantity(parent, name):
    """
    Read a byte size value from an XML document.

    A byte size value is an interpreted string value.  If the string value
    ends with "MB" or "GB", then the string before that is interpreted as
    megabytes or gigabytes.  Otherwise, it is intepreted as bytes.

    Args:
       parent: Parent node to search beneath
       name: Name of node to search for

    Returns:
        ByteQuantity parsed from XML document
    """
    data = readString(parent, name)
    if data is None:
        return None
    data = data.strip()
    if data.endswith("KB"):
        quantity = data[0 : data.rfind("KB")].strip()
        units = UNIT_KBYTES
    elif data.endswith("MB"):
        quantity = data[0 : data.rfind("MB")].strip()
        units = UNIT_MBYTES
    elif data.endswith("GB"):
        quantity = data[0 : data.rfind("GB")].strip()
        units = UNIT_GBYTES
    else:
        quantity = data.strip()
        units = UNIT_BYTES
    return ByteQuantity(quantity, units)


def addByteQuantityNode(xmlDom, parentNode, nodeName, byteQuantity):
    """
    Adds a text node as the next child of a parent, to contain a byte size.

    If the ``byteQuantity`` is None, then the node will be created, but will
    be empty (i.e. will contain no text node child).

    The size in bytes will be normalized.  If it is larger than 1.0 GB, it will
    be shown in GB ("1.0 GB").  If it is larger than 1.0 MB ("1.0 MB"), it will
    be shown in MB.  Otherwise, it will be shown in bytes ("423413").

    Args:
       xmlDom: DOM tree as from ``impl.createDocument()``
       parentNode: Parent node to create child for
       nodeName: Name of the new container node
       byteQuantity: ByteQuantity object to put into the XML document

    Returns:
        Reference to the newly-created node
    """
    if byteQuantity is None:
        byteString = None
    elif byteQuantity.units == UNIT_KBYTES:
        byteString = "%s KB" % byteQuantity.quantity
    elif byteQuantity.units == UNIT_MBYTES:
        byteString = "%s MB" % byteQuantity.quantity
    elif byteQuantity.units == UNIT_GBYTES:
        byteString = "%s GB" % byteQuantity.quantity
    else:
        byteString = byteQuantity.quantity
    return addStringNode(xmlDom, parentNode, nodeName, byteString)
