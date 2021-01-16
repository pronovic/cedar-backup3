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
# Purpose  : Tests capacity extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/capacity.py.

Code Coverage
=============

   This module contains individual tests for the the public classes implemented
   in extend/capacity.py.

Naming Conventions
==================

   I prefer to avoid large unit tests which validate more than one piece of
   functionality, and I prefer to avoid using overly descriptive (read: long)
   test names, as well.  Instead, I use lots of very small tests that each
   validate one specific thing.  These small tests are then named with an index
   number, yielding something like ``testAddDir_001`` or ``testValidate_010``.
   Each method has a docstring describing what it's supposed to accomplish.  I
   feel that this makes it easier to judge how important a given failure is,
   and also makes it somewhat easier to diagnose and fix individual problems.

Testing XML Extraction
======================

   It's difficult to validated that generated XML is exactly "right",
   especially when dealing with pretty-printed XML.  We can't just provide a
   constant string and say "the result must match this".  Instead, what we do
   is extract a node, build some XML from it, and then feed that XML back into
   another object's constructor.  If that parse process succeeds and the old
   object is equal to the new object, we assume that the extract was
   successful.

   It would arguably be better if we could do a completely independent check -
   but implementing that check would be equivalent to re-implementing all of
   the existing functionality that we're validating here!  After all, the most
   important thing is that data can move seamlessly from object to XML document
   and back to object.

Full vs. Reduced Tests
======================

   All of the tests in this module are considered safe to be run in an average
   build environment.  There is a no need to use a CAPACITYTESTS_FULL
   environment variable to provide a "reduced feature set" test suite as for
   some of the other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.extend.capacity import ByteQuantity, CapacityConfig, LocalConfig, PercentageQuantity
from CedarBackup3.testutil import configureLogging, failUnlessAssignRaises, findResources
from CedarBackup3.util import UNIT_BYTES, UNIT_GBYTES, UNIT_KBYTES, UNIT_MBYTES
from CedarBackup3.xmlutil import createOutputDom, serializeDom

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "capacity.conf.1",
    "capacity.conf.2",
    "capacity.conf.3",
    "capacity.conf.4",
]


#######################################################################
# Test Case Classes
#######################################################################

###############################
# TestPercentageQuantity class
###############################


class TestPercentageQuantity(unittest.TestCase):

    """Tests for the PercentageQuantity class."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    ##################
    # Utility methods
    ##################

    def failUnlessAssignRaises(self, exception, obj, prop, value):
        """Equivalent of :any:`failUnlessRaises`, but used for property assignments instead."""
        failUnlessAssignRaises(self, exception, obj, prop, value)

    ############################
    # Test __repr__ and __str__
    ############################

    def testStringFuncs_001(self):
        """
        Just make sure that the string functions don't have errors (i.e. bad variable names).
        """
        obj = PercentageQuantity()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(0.0, quantity.percentage)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        quantity = PercentageQuantity("6")
        self.assertEqual("6", quantity.quantity)
        self.assertEqual(6.0, quantity.percentage)

    def testConstructor_003(self):
        """
        Test assignment of quantity attribute, None value.
        """
        quantity = PercentageQuantity(quantity="1.0")
        self.assertEqual("1.0", quantity.quantity)
        self.assertEqual(1.0, quantity.percentage)
        quantity.quantity = None
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(0.0, quantity.percentage)

    def testConstructor_004(self):
        """
        Test assignment of quantity attribute, valid values.
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(0.0, quantity.percentage)
        quantity.quantity = "1.0"
        self.assertEqual("1.0", quantity.quantity)
        self.assertEqual(1.0, quantity.percentage)
        quantity.quantity = ".1"
        self.assertEqual(".1", quantity.quantity)
        self.assertEqual(0.1, quantity.percentage)
        quantity.quantity = "12"
        self.assertEqual("12", quantity.quantity)
        self.assertEqual(12.0, quantity.percentage)
        quantity.quantity = "0.5"
        self.assertEqual("0.5", quantity.quantity)
        self.assertEqual(0.5, quantity.percentage)
        quantity.quantity = "0.25E2"
        self.assertEqual("0.25E2", quantity.quantity)
        self.assertEqual(0.25e2, quantity.percentage)

    def testConstructor_005(self):
        """
        Test assignment of quantity attribute, invalid value (empty).
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "")
        self.assertEqual(None, quantity.quantity)

    def testConstructor_006(self):
        """
        Test assignment of quantity attribute, invalid value (not a floating point number).
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "blech")
        self.assertEqual(None, quantity.quantity)

    def testConstructor_007(self):
        """
        Test assignment of quantity attribute, invalid value (negative number).
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "-3")
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "-6.8")
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "-0.2")
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "-.1")
        self.assertEqual(None, quantity.quantity)

    def testConstructor_008(self):
        """
        Test assignment of quantity attribute, invalid value (larger than 100%).
        """
        quantity = PercentageQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "100.0001")
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "101")
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "1e6")
        self.assertEqual(None, quantity.quantity)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        quantity1 = PercentageQuantity()
        quantity2 = PercentageQuantity()
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        quantity1 = PercentageQuantity("12")
        quantity2 = PercentageQuantity("12")
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, quantity differs (one None).
        """
        quantity1 = PercentageQuantity()
        quantity2 = PercentageQuantity(quantity="12")
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, quantity differs.
        """
        quantity1 = PercentageQuantity("10")
        quantity2 = PercentageQuantity("12")
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)


##########################
# TestCapacityConfig class
##########################


class TestCapacityConfig(unittest.TestCase):

    """Tests for the CapacityConfig class."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    ##################
    # Utility methods
    ##################

    def failUnlessAssignRaises(self, exception, obj, prop, value):
        """Equivalent of :any:`failUnlessRaises`, but used for property assignments instead."""
        failUnlessAssignRaises(self, exception, obj, prop, value)

    ############################
    # Test __repr__ and __str__
    ############################

    def testStringFuncs_001(self):
        """
        Just make sure that the string functions don't have errors (i.e. bad variable names).
        """
        obj = CapacityConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.maxPercentage)
        self.assertEqual(None, capacity.minBytes)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        capacity = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("2.0", UNIT_KBYTES))
        self.assertEqual(PercentageQuantity("63.2"), capacity.maxPercentage)
        self.assertEqual(ByteQuantity("2.0", UNIT_KBYTES), capacity.minBytes)

    def testConstructor_003(self):
        """
        Test assignment of maxPercentage attribute, None value.
        """
        capacity = CapacityConfig(maxPercentage=PercentageQuantity("63.2"))
        self.assertEqual(PercentageQuantity("63.2"), capacity.maxPercentage)
        capacity.maxPercentage = None
        self.assertEqual(None, capacity.maxPercentage)

    def testConstructor_004(self):
        """
        Test assignment of maxPercentage attribute, valid value.
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.maxPercentage)
        capacity.maxPercentage = PercentageQuantity("63.2")
        self.assertEqual(PercentageQuantity("63.2"), capacity.maxPercentage)

    def testConstructor_005(self):
        """
        Test assignment of maxPercentage attribute, invalid value (empty).
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.maxPercentage)
        self.failUnlessAssignRaises(ValueError, capacity, "maxPercentage", "")
        self.assertEqual(None, capacity.maxPercentage)

    def testConstructor_006(self):
        """
        Test assignment of maxPercentage attribute, invalid value (not a PercentageQuantity).
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.maxPercentage)
        self.failUnlessAssignRaises(ValueError, capacity, "maxPercentage", "1.0 GB")
        self.assertEqual(None, capacity.maxPercentage)

    def testConstructor_007(self):
        """
        Test assignment of minBytes attribute, None value.
        """
        capacity = CapacityConfig(minBytes=ByteQuantity("1.00", UNIT_KBYTES))
        self.assertEqual(ByteQuantity("1.00", UNIT_KBYTES), capacity.minBytes)
        capacity.minBytes = None
        self.assertEqual(None, capacity.minBytes)

    def testConstructor_008(self):
        """
        Test assignment of minBytes attribute, valid value.
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.minBytes)
        capacity.minBytes = ByteQuantity("1.00", UNIT_KBYTES)
        self.assertEqual(ByteQuantity("1.00", UNIT_KBYTES), capacity.minBytes)

    def testConstructor_009(self):
        """
        Test assignment of minBytes attribute, invalid value (empty).
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.minBytes)
        self.failUnlessAssignRaises(ValueError, capacity, "minBytes", "")
        self.assertEqual(None, capacity.minBytes)

    def testConstructor_010(self):
        """
        Test assignment of minBytes attribute, invalid value (not a ByteQuantity).
        """
        capacity = CapacityConfig()
        self.assertEqual(None, capacity.minBytes)
        self.failUnlessAssignRaises(ValueError, capacity, "minBytes", 12)
        self.assertEqual(None, capacity.minBytes)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        capacity1 = CapacityConfig()
        capacity2 = CapacityConfig()
        self.assertEqual(capacity1, capacity2)
        self.assertTrue(capacity1 == capacity2)
        self.assertTrue(not capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(capacity1 >= capacity2)
        self.assertTrue(not capacity1 != capacity2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        capacity1 = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("1.00", UNIT_MBYTES))
        capacity2 = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertEqual(capacity1, capacity2)
        self.assertTrue(capacity1 == capacity2)
        self.assertTrue(not capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(capacity1 >= capacity2)
        self.assertTrue(not capacity1 != capacity2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, maxPercentage differs (one None).
        """
        capacity1 = CapacityConfig()
        capacity2 = CapacityConfig(maxPercentage=PercentageQuantity("63.2"))
        self.assertNotEqual(capacity1, capacity2)
        self.assertTrue(not capacity1 == capacity2)
        self.assertTrue(capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(not capacity1 >= capacity2)
        self.assertTrue(capacity1 != capacity2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, maxPercentage differs.
        """
        capacity1 = CapacityConfig(PercentageQuantity("15.0"), ByteQuantity("1.00", UNIT_MBYTES))
        capacity2 = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(capacity1, capacity2)
        self.assertTrue(not capacity1 == capacity2)
        self.assertTrue(capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(not capacity1 >= capacity2)
        self.assertTrue(capacity1 != capacity2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, minBytes differs (one None).
        """
        capacity1 = CapacityConfig()
        capacity2 = CapacityConfig(minBytes=ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(capacity1, capacity2)
        self.assertTrue(not capacity1 == capacity2)
        self.assertTrue(capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(not capacity1 >= capacity2)
        self.assertTrue(capacity1 != capacity2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, minBytes differs.
        """
        capacity1 = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("0.5", UNIT_MBYTES))
        capacity2 = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(capacity1, capacity2)
        self.assertTrue(not capacity1 == capacity2)
        self.assertTrue(capacity1 < capacity2)
        self.assertTrue(capacity1 <= capacity2)
        self.assertTrue(not capacity1 > capacity2)
        self.assertTrue(not capacity1 >= capacity2)
        self.assertTrue(capacity1 != capacity2)


########################
# TestLocalConfig class
########################


class TestLocalConfig(unittest.TestCase):

    """Tests for the LocalConfig class."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    ################
    # Setup methods
    ################

    def setUp(self):
        try:
            self.resources = findResources(RESOURCES, DATA_DIRS)
        except Exception as e:
            self.fail(e)

    def tearDown(self):
        pass

    ##################
    # Utility methods
    ##################

    def failUnlessAssignRaises(self, exception, obj, prop, value):
        """Equivalent of :any:`failUnlessRaises`, but used for property assignments instead."""
        failUnlessAssignRaises(self, exception, obj, prop, value)

    def validateAddConfig(self, origConfig):
        """
        Validates that document dumped from ``LocalConfig.addConfig`` results in
        identical object.

        We dump a document containing just the capacity configuration, and then
        make sure that if we push that document back into the ``LocalConfig``
        object, that the resulting object matches the original.

        The ``self.failUnlessEqual`` method is used for the validation, so if the
        method call returns normally, everything is OK.

        Args:
           origConfig: Original configuration
        """
        (xmlDom, parentNode) = createOutputDom()
        origConfig.addConfig(xmlDom, parentNode)
        xmlData = serializeDom(xmlDom)
        newConfig = LocalConfig(xmlData=xmlData, validate=False)
        self.assertEqual(origConfig, newConfig)

    ############################
    # Test __repr__ and __str__
    ############################

    def testStringFuncs_001(self):
        """
        Just make sure that the string functions don't have errors (i.e. bad variable names).
        """
        obj = LocalConfig()
        obj.__repr__()
        obj.__str__()

    #####################################################
    # Test basic constructor and attribute functionality
    #####################################################

    def testConstructor_001(self):
        """
        Test empty constructor, validate=False.
        """
        config = LocalConfig(validate=False)
        self.assertEqual(None, config.capacity)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.capacity)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["capacity.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of capacity attribute, None value.
        """
        config = LocalConfig()
        config.capacity = None
        self.assertEqual(None, config.capacity)

    def testConstructor_005(self):
        """
        Test assignment of capacity attribute, valid value.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig()
        self.assertEqual(CapacityConfig(), config.capacity)

    def testConstructor_006(self):
        """
        Test assignment of capacity attribute, invalid value (not CapacityConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "capacity", "STRING!")

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        config1 = LocalConfig()
        config1.capacity = CapacityConfig()

        config2 = LocalConfig()
        config2.capacity = CapacityConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, capacity differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.capacity = CapacityConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, capacity differs.
        """
        config1 = LocalConfig()
        config1.capacity = CapacityConfig(minBytes=ByteQuantity("0.1", UNIT_MBYTES))

        config2 = LocalConfig()
        config2.capacity = CapacityConfig(minBytes=ByteQuantity("1.00", UNIT_MBYTES))

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    ######################
    # Test validate logic
    ######################

    def testValidate_001(self):
        """
        Test validate on a None capacity section.
        """
        config = LocalConfig()
        config.capacity = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty capacity section.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty capacity section with no values filled in.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig(None, None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_004(self):
        """
        Test validate on a non-empty capacity section with both max percentage and min bytes filled in.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig(PercentageQuantity("63.2"), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty capacity section with only max percentage filled in.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig(maxPercentage=PercentageQuantity("63.2"))
        config.validate()

    def testValidate_006(self):
        """
        Test validate on a non-empty capacity section with only min bytes filled in.
        """
        config = LocalConfig()
        config.capacity = CapacityConfig(minBytes=ByteQuantity("1.00", UNIT_MBYTES))
        config.validate()

    ############################
    # Test parsing of documents
    ############################
    # Some of the byte-size parsing logic is tested more fully in test_split.py.
    # I decided not to duplicate it here, since it's shared from config.py.

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["capacity.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.capacity)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.capacity)

    def testParse_002(self):
        """
        Parse config document that configures max percentage.
        """
        path = self.resources["capacity.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(PercentageQuantity("63.2"), config.capacity.maxPercentage)
        self.assertEqual(None, config.capacity.minBytes)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(PercentageQuantity("63.2"), config.capacity.maxPercentage)
        self.assertEqual(None, config.capacity.minBytes)

    def testParse_003(self):
        """
        Parse config document that configures min bytes, size in bytes.
        """
        path = self.resources["capacity.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(None, config.capacity.maxPercentage)
        self.assertEqual(ByteQuantity("18", UNIT_BYTES), config.capacity.minBytes)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(None, config.capacity.maxPercentage)
        self.assertEqual(ByteQuantity("18", UNIT_BYTES), config.capacity.minBytes)

    def testParse_004(self):
        """
        Parse config document with filled-in values, size in KB.
        """
        path = self.resources["capacity.conf.4"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(None, config.capacity.maxPercentage)
        self.assertEqual(ByteQuantity("1.25", UNIT_KBYTES), config.capacity.minBytes)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.capacity)
        self.assertEqual(None, config.capacity.maxPercentage)
        self.assertEqual(ByteQuantity("1.25", UNIT_KBYTES), config.capacity.minBytes)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        capacity = CapacityConfig()
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with max percentage value set.
        """
        capacity = CapacityConfig(maxPercentage=PercentageQuantity("63.29128310980123"))
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)

    def testAddConfig_003(self):
        """
        Test with min bytes value set, byte values.
        """
        capacity = CapacityConfig(minBytes=ByteQuantity("121231", UNIT_BYTES))
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)

    def testAddConfig_004(self):
        """
        Test with min bytes value set, KB values.
        """
        capacity = CapacityConfig(minBytes=ByteQuantity("63352", UNIT_KBYTES))
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)

    def testAddConfig_005(self):
        """
        Test with min bytes value set, MB values.
        """
        capacity = CapacityConfig(minBytes=ByteQuantity("63352", UNIT_MBYTES))
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)

    def testAddConfig_006(self):
        """
        Test with min bytes value set, GB values.
        """
        capacity = CapacityConfig(minBytes=ByteQuantity("63352", UNIT_GBYTES))
        config = LocalConfig()
        config.capacity = capacity
        self.validateAddConfig(config)
