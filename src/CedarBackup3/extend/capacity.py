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
# Copyright (c) 2008,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides an extension to check remaining media capacity.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides an extension to check remaining media capacity.

Some users have asked for advance warning that their media is beginning to fill
up.  This is an extension that checks the current capacity of the media in the
writer, and prints a warning if the media is more than X% full, or has fewer
than X bytes of capacity remaining.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import logging
from functools import total_ordering

from CedarBackup3.actions.util import checkMediaState, createWriter
from CedarBackup3.config import ByteQuantity, addByteQuantityNode, readByteQuantity
from CedarBackup3.util import displayBytes
from CedarBackup3.xmlutil import addContainerNode, addStringNode, createInputDom, readFirstChild, readString

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.extend.capacity")


########################################################################
# Percentage class definition
########################################################################


@total_ordering
class PercentageQuantity(object):

    """
    Class representing a percentage quantity.

    The percentage is maintained internally as a string so that issues of
    precision can be avoided.  It really isn't possible to store a floating
    point number here while being able to losslessly translate back and forth
    between XML and object representations.  (Perhaps the Python 2.4 Decimal
    class would have been an option, but I originally wanted to stay compatible
    with Python 2.3.)

    Even though the quantity is maintained as a string, the string must be in a
    valid floating point positive number.  Technically, any floating point
    string format supported by Python is allowble.  However, it does not make
    sense to have a negative percentage in this context.

    """

    def __init__(self, quantity=None):
        """
        Constructor for the ``PercentageQuantity`` class.
        Args:
           quantity: Percentage quantity, as a string (i.e. "99.9" or "12")
        Raises:
           ValueError: If the quantity value is invaid
        """
        self._quantity = None
        self.quantity = quantity

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "PercentageQuantity(%s)" % (self.quantity)

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
        if self.quantity != other.quantity:
            if float(self.quantity or 0.0) < float(other.quantity or 0.0):
                return -1
            else:
                return 1
        return 0

    def _setQuantity(self, value):
        """
        Property target used to set the quantity
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
           ValueError: If the value is not a valid floating point number
           ValueError: If the value is less than zero
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("Percentage must be a non-empty string.")
            floatValue = float(value)
            if floatValue < 0.0 or floatValue > 100.0:
                raise ValueError("Percentage must be a positive value from 0.0 to 100.0")
        self._quantity = value  # keep around string

    def _getQuantity(self):
        """
        Property target used to get the quantity.
        """
        return self._quantity

    def _getPercentage(self):
        """
        Property target used to get the quantity as a floating point number.
        If there is no quantity set, then a value of 0.0 is returned.
        """
        if self.quantity is not None:
            return float(self.quantity)
        return 0.0

    quantity = property(_getQuantity, _setQuantity, None, doc="Percentage value, as a string")
    percentage = property(_getPercentage, None, None, "Percentage value, as a floating point number.")


########################################################################
# CapacityConfig class definition
########################################################################


@total_ordering
class CapacityConfig(object):

    """
    Class representing capacity configuration.

    The following restrictions exist on data in this class:

       - The maximum percentage utilized must be a PercentageQuantity
       - The minimum bytes remaining must be a ByteQuantity

    """

    def __init__(self, maxPercentage=None, minBytes=None):
        """
        Constructor for the ``CapacityConfig`` class.

        Args:
           maxPercentage: Maximum percentage of the media that may be utilized
           minBytes: Minimum number of free bytes that must be available
        """
        self._maxPercentage = None
        self._minBytes = None
        self.maxPercentage = maxPercentage
        self.minBytes = minBytes

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "CapacityConfig(%s, %s)" % (self.maxPercentage, self.minBytes)

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
        if self.maxPercentage != other.maxPercentage:
            if (self.maxPercentage or PercentageQuantity()) < (other.maxPercentage or PercentageQuantity()):
                return -1
            else:
                return 1
        if self.minBytes != other.minBytes:
            if (self.minBytes or ByteQuantity()) < (other.minBytes or ByteQuantity()):
                return -1
            else:
                return 1
        return 0

    def _setMaxPercentage(self, value):
        """
        Property target used to set the maxPercentage value.
        If not ``None``, the value must be a ``PercentageQuantity`` object.
        Raises:
           ValueError: If the value is not a ``PercentageQuantity``
        """
        if value is None:
            self._maxPercentage = None
        else:
            if not isinstance(value, PercentageQuantity):
                raise ValueError("Value must be a ``PercentageQuantity`` object.")
            self._maxPercentage = value

    def _getMaxPercentage(self):
        """
        Property target used to get the maxPercentage value
        """
        return self._maxPercentage

    def _setMinBytes(self, value):
        """
        Property target used to set the bytes utilized value.
        If not ``None``, the value must be a ``ByteQuantity`` object.
        Raises:
           ValueError: If the value is not a ``ByteQuantity``
        """
        if value is None:
            self._minBytes = None
        else:
            if not isinstance(value, ByteQuantity):
                raise ValueError("Value must be a ``ByteQuantity`` object.")
            self._minBytes = value

    def _getMinBytes(self):
        """
        Property target used to get the bytes remaining value.
        """
        return self._minBytes

    maxPercentage = property(_getMaxPercentage, _setMaxPercentage, None, "Maximum percentage of the media that may be utilized.")
    minBytes = property(_getMinBytes, _setMinBytes, None, "Minimum number of free bytes that must be available.")


########################################################################
# LocalConfig class definition
########################################################################


@total_ordering
class LocalConfig(object):

    """
    Class representing this extension's configuration document.

    This is not a general-purpose configuration object like the main Cedar
    Backup configuration object.  Instead, it just knows how to parse and emit
    specific configuration values to this extension.  Third parties who need to
    read and write configuration related to this extension should access it
    through the constructor, ``validate`` and ``addConfig`` methods.

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
        self._capacity = None
        self.capacity = None
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
        return "LocalConfig(%s)" % (self.capacity)

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
        if self.capacity != other.capacity:
            if self.capacity < other.capacity:
                return -1
            else:
                return 1
        return 0

    def _setCapacity(self, value):
        """
        Property target used to set the capacity configuration value.
        If not ``None``, the value must be a ``CapacityConfig`` object.
        Raises:
           ValueError: If the value is not a ``CapacityConfig``
        """
        if value is None:
            self._capacity = None
        else:
            if not isinstance(value, CapacityConfig):
                raise ValueError("Value must be a ``CapacityConfig`` object.")
            self._capacity = value

    def _getCapacity(self):
        """
        Property target used to get the capacity configuration value.
        """
        return self._capacity

    capacity = property(_getCapacity, _setCapacity, None, "Capacity configuration in terms of a ``CapacityConfig`` object.")

    def validate(self):
        """
        Validates configuration represented by the object.
        THere must be either a percentage, or a byte capacity, but not both.
        Raises:
           ValueError: If one of the validations fails
        """
        if self.capacity is None:
            raise ValueError("Capacity section is required.")
        if self.capacity.maxPercentage is None and self.capacity.minBytes is None:
            raise ValueError("Must provide either max percentage or min bytes.")
        if self.capacity.maxPercentage is not None and self.capacity.minBytes is not None:
            raise ValueError("Must provide either max percentage or min bytes, but not both.")

    def addConfig(self, xmlDom, parentNode):
        """
        Adds a <capacity> configuration section as the next child of a parent.

        Third parties should use this function to write configuration related to
        this extension.

        We add the following fields to the document::

           maxPercentage  //cb_config/capacity/max_percentage
           minBytes       //cb_config/capacity/min_bytes

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent that the section should be appended to
        """
        if self.capacity is not None:
            sectionNode = addContainerNode(xmlDom, parentNode, "capacity")
            LocalConfig._addPercentageQuantity(xmlDom, sectionNode, "max_percentage", self.capacity.maxPercentage)
            if self.capacity.minBytes is not None:  # because utility function fills in empty section on None
                addByteQuantityNode(xmlDom, sectionNode, "min_bytes", self.capacity.minBytes)

    def _parseXmlData(self, xmlData):
        """
        Internal method to parse an XML string into the object.

        This method parses the XML document into a DOM tree (``xmlDom``) and then
        calls a static method to parse the capacity configuration section.

        Args:
           xmlData (String data): XML data to be parsed
        Raises:
           ValueError: If the XML cannot be successfully parsed
        """
        (xmlDom, parentNode) = createInputDom(xmlData)
        self._capacity = LocalConfig._parseCapacity(parentNode)

    @staticmethod
    def _parseCapacity(parentNode):
        """
        Parses a capacity configuration section.

        We read the following fields::

           maxPercentage  //cb_config/capacity/max_percentage
           minBytes       //cb_config/capacity/min_bytes

        Args:
           parentNode: Parent node to search beneath

        Returns:
            ``CapacityConfig`` object or ``None`` if the section does not exist
        Raises:
           ValueError: If some filled-in value is invalid
        """
        capacity = None
        section = readFirstChild(parentNode, "capacity")
        if section is not None:
            capacity = CapacityConfig()
            capacity.maxPercentage = LocalConfig._readPercentageQuantity(section, "max_percentage")
            capacity.minBytes = readByteQuantity(section, "min_bytes")
        return capacity

    @staticmethod
    def _readPercentageQuantity(parent, name):
        """
        Read a percentage quantity value from an XML document.
        Args:
           parent: Parent node to search beneath
           name: Name of node to search for
        Returns:
            Percentage quantity parsed from XML document
        """
        quantity = readString(parent, name)
        if quantity is None:
            return None
        return PercentageQuantity(quantity)

    @staticmethod
    def _addPercentageQuantity(xmlDom, parentNode, nodeName, percentageQuantity):
        """
        Adds a text node as the next child of a parent, to contain a percentage quantity.

        If the ``percentageQuantity`` is None, then no node will be created.

        Args:
           xmlDom: DOM tree as from ``impl.createDocument()``
           parentNode: Parent node to create child for
           nodeName: Name of the new container node
           percentageQuantity: PercentageQuantity object to put into the XML document

        Returns:
            Reference to the newly-created node
        """
        if percentageQuantity is not None:
            addStringNode(xmlDom, parentNode, nodeName, percentageQuantity.quantity)


########################################################################
# Public functions
########################################################################

###########################
# executeAction() function
###########################

# pylint: disable=W0613
def executeAction(configPath, options, config):
    """
    Executes the capacity action.

    Args:
       configPath (String representing a path on disk): Path to configuration file on disk
       options (Options object): Program command-line options
       config (Config object): Program configuration
    Raises:
       ValueError: Under many generic error conditions
       IOError: If there are I/O problems reading or writing files
    """
    logger.debug("Executing capacity extended action.")
    if config.options is None or config.store is None:
        raise ValueError("Cedar Backup configuration is not properly filled in.")
    local = LocalConfig(xmlPath=configPath)
    if config.store.checkMedia:
        checkMediaState(config.store)  # raises exception if media is not initialized
    capacity = createWriter(config).retrieveCapacity()
    logger.debug("Media capacity: %s", capacity)
    if local.capacity.maxPercentage is not None:
        if capacity.utilized > local.capacity.maxPercentage.percentage:
            logger.error(
                "Media has reached capacity limit of %s%%: %.2f%% utilized",
                local.capacity.maxPercentage.quantity,
                capacity.utilized,
            )
    else:
        if capacity.bytesAvailable < local.capacity.minBytes:
            logger.error(
                "Media has reached capacity limit of %s: only %s available",
                local.capacity.minBytes,
                displayBytes(capacity.bytesAvailable),
            )
    logger.info("Executed the capacity extended action successfully.")
