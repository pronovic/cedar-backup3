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
# Copyright (c) 2004-2008,2010,2011,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests configuration functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/config.py.

Code Coverage
=============

   This module contains individual tests for the public functions and classes
   implemented in config.py.

   I usually prefer to test only the public interface to a class, because that
   way the regression tests don't depend on the internal implementation.  In
   this case, I've decided to test some of the private methods, because their
   "privateness" is more a matter of presenting a clean external interface than
   anything else.  In particular, this is the case with the private validation
   functions (I use the private functions so I can test just the validations
   for one specific case, even if the public interface only exposes one broad
   validation).

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
   is extract the XML and then feed it back into another object's constructor.
   If that parse process succeeds and the old object is equal to the new
   object, we assume that the extract was successful.

   It would arguably be better if we could do a completely independent check -
   but implementing that check would be equivalent to re-implementing all of
   the existing functionality that we're validating here!  After all, the most
   important thing is that data can move seamlessly from object to XML document
   and back to object.

Full vs. Reduced Tests
======================

   All of the tests in this module are considered safe to be run in an average
   build environment.  There is a no need to use a CONFIGTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.config import (
    ActionDependencies,
    ActionHook,
    BlankBehavior,
    ByteQuantity,
    CollectConfig,
    CollectDir,
    CollectFile,
    CommandOverride,
    Config,
    ExtendedAction,
    ExtensionsConfig,
    LocalPeer,
    OptionsConfig,
    PeersConfig,
    PostActionHook,
    PreActionHook,
    PurgeConfig,
    PurgeDir,
    ReferenceConfig,
    RemotePeer,
    StageConfig,
    StoreConfig,
)
from CedarBackup3.testutil import configureLogging, failUnlessAssignRaises, findResources
from CedarBackup3.util import UNIT_BYTES, UNIT_GBYTES, UNIT_KBYTES, UNIT_MBYTES

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "cback.conf.1",
    "cback.conf.2",
    "cback.conf.3",
    "cback.conf.4",
    "cback.conf.5",
    "cback.conf.6",
    "cback.conf.7",
    "cback.conf.8",
    "cback.conf.9",
    "cback.conf.10",
    "cback.conf.11",
    "cback.conf.12",
    "cback.conf.13",
    "cback.conf.14",
    "cback.conf.15",
    "cback.conf.16",
    "cback.conf.17",
    "cback.conf.18",
    "cback.conf.19",
    "cback.conf.20",
    "cback.conf.21",
    "cback.conf.22",
    "cback.conf.23",
]


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestByteQuantity class
##########################


# noinspection PyTypeChecker
class TestByteQuantity(unittest.TestCase):

    """Tests for the ByteQuantity class."""

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
        obj = ByteQuantity()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        quantity = ByteQuantity()
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(0.0, quantity.bytes)

    def testConstructor_002a(self):
        """
        Test constructor with all values filled in, with valid string quantity.
        """
        quantity = ByteQuantity("6", UNIT_BYTES)
        self.assertEqual("6", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(6.0, quantity.bytes)

        quantity = ByteQuantity("2684354560", UNIT_BYTES)
        self.assertEqual("2684354560", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(2684354560.0, quantity.bytes)

        quantity = ByteQuantity("629145600", UNIT_BYTES)
        self.assertEqual("629145600", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

        quantity = ByteQuantity("2.5", UNIT_GBYTES)
        self.assertEqual("2.5", quantity.quantity)
        self.assertEqual(UNIT_GBYTES, quantity.units)
        self.assertEqual(2684354560.0, quantity.bytes)

        quantity = ByteQuantity("600", UNIT_MBYTES)
        self.assertEqual("600", quantity.quantity)
        self.assertEqual(UNIT_MBYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

    def testConstructor_002b(self):
        """
        Test constructor with all values filled in, with valid integer quantity.
        """
        quantity = ByteQuantity(6, UNIT_BYTES)
        self.assertEqual("6", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(6.0, quantity.bytes)

        quantity = ByteQuantity(2684354560, UNIT_BYTES)
        self.assertEqual("2684354560", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(2684354560.0, quantity.bytes)

        quantity = ByteQuantity(629145600, UNIT_BYTES)
        self.assertEqual("629145600", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

        quantity = ByteQuantity(600, UNIT_MBYTES)
        self.assertEqual("600", quantity.quantity)
        self.assertEqual(UNIT_MBYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

    def testConstructor_002c(self):
        """
        Test constructor with all values filled in, with valid float quantity.
        """
        quantity = ByteQuantity(6.0, UNIT_BYTES)
        self.assertEqual("6.0", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(6.0, quantity.bytes)

        quantity = ByteQuantity(2684354560.0, UNIT_BYTES)
        self.assertEqual("2684354560.0", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(2684354560.0, quantity.bytes)

        quantity = ByteQuantity(629145600.0, UNIT_BYTES)
        self.assertEqual("629145600.0", quantity.quantity)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

        quantity = ByteQuantity(2.5, UNIT_GBYTES)
        self.assertEqual("2.5", quantity.quantity)
        self.assertEqual(UNIT_GBYTES, quantity.units)
        self.assertEqual(2684354560.0, quantity.bytes)

        quantity = ByteQuantity(600.0, UNIT_MBYTES)
        self.assertEqual("600.0", quantity.quantity)
        self.assertEqual(UNIT_MBYTES, quantity.units)
        self.assertEqual(629145600.0, quantity.bytes)

    def testConstructor_003(self):
        """
        Test assignment of quantity attribute, None value.
        """
        quantity = ByteQuantity(quantity="1.0")
        self.assertEqual("1.0", quantity.quantity)
        self.assertEqual(1.0, quantity.bytes)
        quantity.quantity = None
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(0.0, quantity.bytes)

    def testConstructor_004a(self):
        """
        Test assignment of quantity attribute, valid string values.
        """
        quantity = ByteQuantity()
        quantity.units = UNIT_BYTES  # so we can test the bytes attribute
        self.assertEqual(None, quantity.quantity)
        self.assertEqual(0.0, quantity.bytes)
        quantity.quantity = "1.0"
        self.assertEqual("1.0", quantity.quantity)
        self.assertEqual(1.0, quantity.bytes)
        quantity.quantity = ".1"
        self.assertEqual(".1", quantity.quantity)
        self.assertEqual(0.1, quantity.bytes)
        quantity.quantity = "12"
        self.assertEqual("12", quantity.quantity)
        self.assertEqual(12.0, quantity.bytes)
        quantity.quantity = "0.5"
        self.assertEqual("0.5", quantity.quantity)
        self.assertEqual(0.5, quantity.bytes)
        quantity.quantity = "181281"
        self.assertEqual("181281", quantity.quantity)
        self.assertEqual(181281.0, quantity.bytes)
        quantity.quantity = "1E6"
        self.assertEqual("1E6", quantity.quantity)
        self.assertEqual(1.0e6, quantity.bytes)
        quantity.quantity = "0.25E2"
        self.assertEqual("0.25E2", quantity.quantity)
        self.assertEqual(0.25e2, quantity.bytes)

    def testConstructor_004b(self):
        """
        Test assignment of quantity attribute, valid integer values.
        """
        quantity = ByteQuantity()
        quantity.units = UNIT_BYTES  # so we can test the bytes attribute
        quantity.quantity = 1
        self.assertEqual("1", quantity.quantity)
        self.assertEqual(1.0, quantity.bytes)
        quantity.quantity = 12
        self.assertEqual("12", quantity.quantity)
        self.assertEqual(12.0, quantity.bytes)
        quantity.quantity = 181281
        self.assertEqual("181281", quantity.quantity)
        self.assertEqual(181281.0, quantity.bytes)

    def testConstructor_004c(self):
        """
        Test assignment of quantity attribute, valid float values.
        """
        quantity = ByteQuantity()
        quantity.units = UNIT_BYTES  # so we can test the bytes attribute
        quantity.quantity = 1.0
        self.assertEqual("1.0", quantity.quantity)
        self.assertEqual(1.0, quantity.bytes)
        quantity.quantity = 0.1
        self.assertEqual("0.1", quantity.quantity)
        self.assertEqual(0.1, quantity.bytes)
        quantity.quantity = "12.0"
        self.assertEqual("12.0", quantity.quantity)
        self.assertEqual(12.0, quantity.bytes)
        quantity.quantity = 0.5
        self.assertEqual("0.5", quantity.quantity)
        self.assertEqual(0.5, quantity.bytes)
        quantity.quantity = "181281.0"
        self.assertEqual("181281.0", quantity.quantity)
        self.assertEqual(181281.0, quantity.bytes)
        quantity.quantity = 1e6
        self.assertEqual("1000000.0", quantity.quantity)
        self.assertEqual(1.0e6, quantity.bytes)
        quantity.quantity = 0.25e2
        self.assertEqual("25.0", quantity.quantity)
        self.assertEqual(0.25e2, quantity.bytes)

    def testConstructor_005(self):
        """
        Test assignment of quantity attribute, invalid value (empty).
        """
        quantity = ByteQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "")
        self.assertEqual(None, quantity.quantity)

    def testConstructor_006(self):
        """
        Test assignment of quantity attribute, invalid value (not interpretable as a float).
        """
        quantity = ByteQuantity()
        self.assertEqual(None, quantity.quantity)
        self.failUnlessAssignRaises(ValueError, quantity, "quantity", "blech")
        self.assertEqual(None, quantity.quantity)

    def testConstructor_007(self):
        """
        Test assignment of quantity attribute, invalid value (negative number).
        """
        quantity = ByteQuantity()
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
        Test assignment of units attribute, None value.
        """
        quantity = ByteQuantity(units=UNIT_MBYTES)
        self.assertEqual(UNIT_MBYTES, quantity.units)
        quantity.units = None
        self.assertEqual(UNIT_BYTES, quantity.units)

    def testConstructor_009(self):
        """
        Test assignment of units attribute, valid values.
        """
        quantity = ByteQuantity()
        self.assertEqual(UNIT_BYTES, quantity.units)
        quantity.units = UNIT_KBYTES
        self.assertEqual(UNIT_KBYTES, quantity.units)
        quantity.units = UNIT_MBYTES
        self.assertEqual(UNIT_MBYTES, quantity.units)
        quantity.units = UNIT_GBYTES
        self.assertEqual(UNIT_GBYTES, quantity.units)
        quantity.units = UNIT_BYTES
        self.assertEqual(UNIT_BYTES, quantity.units)

    def testConstructor_010(self):
        """
        Test assignment of units attribute, invalid value (empty).
        """
        quantity = ByteQuantity()
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "")
        self.assertEqual(UNIT_BYTES, quantity.units)

    def testConstructor_011(self):
        """
        Test assignment of units attribute, invalid value (not a valid unit).
        """
        quantity = ByteQuantity()
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", 16)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", -2)
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "bytes")
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "B")
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "KB")
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "MB")
        self.assertEqual(UNIT_BYTES, quantity.units)
        self.failUnlessAssignRaises(ValueError, quantity, "units", "GB")
        self.assertEqual(UNIT_BYTES, quantity.units)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        quantity1 = ByteQuantity()
        quantity2 = ByteQuantity()
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
        quantity1 = ByteQuantity("12", UNIT_BYTES)
        quantity2 = ByteQuantity("12", UNIT_BYTES)
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
        quantity1 = ByteQuantity()
        quantity2 = ByteQuantity(quantity="12")
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004a(self):
        """
        Test comparison of two differing objects, quantity differs (same units).
        """
        quantity1 = ByteQuantity("10", UNIT_BYTES)
        quantity2 = ByteQuantity("12", UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004b(self):
        """
        Test comparison of two differing objects, quantity differs (different units).
        """
        quantity1 = ByteQuantity("10", UNIT_BYTES)
        quantity2 = ByteQuantity("12", UNIT_KBYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004c(self):
        """
        Test comparison of two differing objects, quantity differs (implied UNIT_BYTES).
        """
        quantity1 = ByteQuantity("10")
        quantity2 = ByteQuantity("12", UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004d(self):
        """
        Test comparison of two differing objects, quantity differs (implied UNIT_BYTES).
        """
        quantity1 = ByteQuantity("10", UNIT_BYTES)
        quantity2 = ByteQuantity("12")
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_004e(self):
        """
        Test comparison of two differing objects, quantity differs (implied UNIT_BYTES).
        """
        quantity1 = ByteQuantity("10")
        quantity2 = ByteQuantity("12")
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, units differs (one None).
        """
        quantity1 = ByteQuantity()
        quantity2 = ByteQuantity(units=UNIT_MBYTES)
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, units differs.
        """
        quantity1 = ByteQuantity("12", UNIT_BYTES)
        quantity2 = ByteQuantity("12", UNIT_KBYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_007a(self):
        """
        Test comparison of byte quantity to integer bytes, equivalent
        """
        quantity1 = 12
        quantity2 = ByteQuantity(quantity="12", units=UNIT_BYTES)
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_007b(self):
        """
        Test comparison of byte quantity to integer bytes, equivalent
        """
        quantity1 = 629145600
        quantity2 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_007c(self):
        """
        Test comparison of byte quantity to integer bytes, equivalent
        """
        quantity1 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        quantity2 = 629145600
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_008a(self):
        """
        Test comparison of byte quantity to integer bytes, integer smaller
        """
        quantity1 = 11
        quantity2 = ByteQuantity(quantity="12", units=UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_008b(self):
        """
        Test comparison of byte quantity to integer bytes, integer smaller
        """
        quantity1 = 130390425
        quantity2 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_009a(self):
        """
        Test comparison of byte quantity to integer bytes, integer larger
        """
        quantity1 = 13
        quantity2 = ByteQuantity(quantity="12", units=UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(not quantity1 <= quantity2)
        self.assertTrue(quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_009b(self):
        """
        Test comparison of byte quantity to integer bytes, integer larger
        """
        quantity1 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        quantity2 = 629145610
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_010a(self):
        """
        Test comparison of byte quantity to float bytes, equivalent
        """
        quantity1 = 12.0
        quantity2 = ByteQuantity(quantity="12.0", units=UNIT_BYTES)
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_010b(self):
        """
        Test comparison of byte quantity to float bytes, equivalent
        """
        quantity1 = 629145600.0
        quantity2 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        self.assertEqual(quantity1, quantity2)
        self.assertTrue(quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(not quantity1 != quantity2)

    def testComparison_011a(self):
        """
        Test comparison of byte quantity to float bytes, float smaller
        """
        quantity1 = 11.0
        quantity2 = ByteQuantity(quantity="12.0", units=UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_011b(self):
        """
        Test comparison of byte quantity to float bytes, float smaller
        """
        quantity1 = 130390425.0
        quantity2 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_012a(self):
        """
        Test comparison of byte quantity to float bytes, float larger
        """
        quantity1 = 13.0
        quantity2 = ByteQuantity(quantity="12.0", units=UNIT_BYTES)
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(not quantity1 < quantity2)
        self.assertTrue(not quantity1 <= quantity2)
        self.assertTrue(quantity1 > quantity2)
        self.assertTrue(quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)

    def testComparison_012b(self):
        """
        Test comparison of byte quantity to float bytes, float larger
        """
        quantity1 = ByteQuantity(quantity="600", units=UNIT_MBYTES)
        quantity2 = 629145610.0
        self.assertNotEqual(quantity1, quantity2)
        self.assertTrue(not quantity1 == quantity2)
        self.assertTrue(quantity1 < quantity2)
        self.assertTrue(quantity1 <= quantity2)
        self.assertTrue(not quantity1 > quantity2)
        self.assertTrue(not quantity1 >= quantity2)
        self.assertTrue(quantity1 != quantity2)


###############################
# TestActionDependencies class
###############################


class TestActionDependencies(unittest.TestCase):

    """Tests for the ActionDependencies class."""

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
        obj = ActionDependencies()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.beforeList)
        self.assertEqual(None, dependencies.afterList)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        dependencies = ActionDependencies(["b"], ["a"])
        self.assertEqual(["b"], dependencies.beforeList)
        self.assertEqual(["a"], dependencies.afterList)

    def testConstructor_003(self):
        """
        Test assignment of beforeList attribute, None value.
        """
        dependencies = ActionDependencies(beforeList=[])
        self.assertEqual([], dependencies.beforeList)
        dependencies.beforeList = None
        self.assertEqual(None, dependencies.beforeList)

    def testConstructor_004(self):
        """
        Test assignment of beforeList attribute, empty list.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.beforeList)
        dependencies.beforeList = []
        self.assertEqual([], dependencies.beforeList)

    def testConstructor_005(self):
        """
        Test assignment of beforeList attribute, non-empty list, valid values.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.beforeList)
        dependencies.beforeList = [
            "a",
            "b",
        ]
        self.assertEqual(["a", "b"], dependencies.beforeList)

    def testConstructor_006(self):
        """
        Test assignment of beforeList attribute, non-empty list, invalid value.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", ["KEN"])
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", ["hello, world"])
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", ["dash-word"])
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", [""])
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", [None])
        self.assertEqual(None, dependencies.beforeList)

    def testConstructor_007(self):
        """
        Test assignment of beforeList attribute, non-empty list, mixed values.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.beforeList)
        self.failUnlessAssignRaises(ValueError, dependencies, "beforeList", ["ken", "dash-word"])

    def testConstructor_008(self):
        """
        Test assignment of afterList attribute, None value.
        """
        dependencies = ActionDependencies(afterList=[])
        self.assertEqual([], dependencies.afterList)
        dependencies.afterList = None
        self.assertEqual(None, dependencies.afterList)

    def testConstructor_009(self):
        """
        Test assignment of afterList attribute, non-empty list, valid values.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.afterList)
        dependencies.afterList = [
            "a",
            "b",
        ]
        self.assertEqual(["a", "b"], dependencies.afterList)

    def testConstructor_010(self):
        """
        Test assignment of afterList attribute, non-empty list, invalid values.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.afterList)

    def testConstructor_011(self):
        """
        Test assignment of afterList attribute, non-empty list, mixed values.
        """
        dependencies = ActionDependencies()
        self.assertEqual(None, dependencies.afterList)
        self.failUnlessAssignRaises(ValueError, dependencies, "afterList", ["KEN"])
        self.assertEqual(None, dependencies.afterList)
        self.failUnlessAssignRaises(ValueError, dependencies, "afterList", ["hello, world"])
        self.assertEqual(None, dependencies.afterList)
        self.failUnlessAssignRaises(ValueError, dependencies, "afterList", ["dash-word"])
        self.assertEqual(None, dependencies.afterList)
        self.failUnlessAssignRaises(ValueError, dependencies, "afterList", [""])
        self.assertEqual(None, dependencies.afterList)
        self.failUnlessAssignRaises(ValueError, dependencies, "afterList", [None])
        self.assertEqual(None, dependencies.afterList)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        dependencies1 = ActionDependencies()
        dependencies2 = ActionDependencies()
        self.assertEqual(dependencies1, dependencies2)
        self.assertTrue(dependencies1 == dependencies2)
        self.assertTrue(not dependencies1 < dependencies2)
        self.assertTrue(dependencies1 <= dependencies2)
        self.assertTrue(not dependencies1 > dependencies2)
        self.assertTrue(dependencies1 >= dependencies2)
        self.assertTrue(not dependencies1 != dependencies2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        dependencies1 = ActionDependencies(beforeList=["a"], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=["b"])
        self.assertEqual(dependencies1, dependencies2)
        self.assertTrue(dependencies1 == dependencies2)
        self.assertTrue(not dependencies1 < dependencies2)
        self.assertTrue(dependencies1 <= dependencies2)
        self.assertTrue(not dependencies1 > dependencies2)
        self.assertTrue(dependencies1 >= dependencies2)
        self.assertTrue(not dependencies1 != dependencies2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, beforeList differs (one None).
        """
        dependencies1 = ActionDependencies(beforeList=None, afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=["b"])
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(dependencies1 < dependencies2)
        self.assertTrue(dependencies1 <= dependencies2)
        self.assertTrue(not dependencies1 > dependencies2)
        self.assertTrue(not dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, beforeList differs (one empty).
        """
        dependencies1 = ActionDependencies(beforeList=[], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=["b"])
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(dependencies1 < dependencies2)
        self.assertTrue(dependencies1 <= dependencies2)
        self.assertTrue(not dependencies1 > dependencies2)
        self.assertTrue(not dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, beforeList differs.
        """
        dependencies1 = ActionDependencies(beforeList=["a"], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["b"], afterList=["b"])
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(dependencies1 < dependencies2)
        self.assertTrue(dependencies1 <= dependencies2)
        self.assertTrue(not dependencies1 > dependencies2)
        self.assertTrue(not dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, afterList differs (one None).
        """
        dependencies1 = ActionDependencies(beforeList=["a"], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=None)
        self.assertNotEqual(dependencies1, dependencies2)
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(not dependencies1 < dependencies2)
        self.assertTrue(not dependencies1 <= dependencies2)
        self.assertTrue(dependencies1 > dependencies2)
        self.assertTrue(dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, afterList differs (one empty).
        """
        dependencies1 = ActionDependencies(beforeList=["a"], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=[])
        self.assertNotEqual(dependencies1, dependencies2)
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(not dependencies1 < dependencies2)
        self.assertTrue(not dependencies1 <= dependencies2)
        self.assertTrue(dependencies1 > dependencies2)
        self.assertTrue(dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, afterList differs.
        """
        dependencies1 = ActionDependencies(beforeList=["a"], afterList=["b"])
        dependencies2 = ActionDependencies(beforeList=["a"], afterList=["a"])
        self.assertNotEqual(dependencies1, dependencies2)
        self.assertTrue(not dependencies1 == dependencies2)
        self.assertTrue(not dependencies1 < dependencies2)
        self.assertTrue(not dependencies1 <= dependencies2)
        self.assertTrue(dependencies1 > dependencies2)
        self.assertTrue(dependencies1 >= dependencies2)
        self.assertTrue(dependencies1 != dependencies2)


#######################
# TestActionHook class
#######################


class TestActionHook(unittest.TestCase):

    """Tests for the ActionHook class."""

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
        obj = ActionHook()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        hook = ActionHook()
        self.assertEqual(False, hook._before)
        self.assertEqual(False, hook._after)
        self.assertEqual(None, hook.action)
        self.assertEqual(None, hook.command)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        hook = ActionHook(action="action", command="command")
        self.assertEqual(False, hook._before)
        self.assertEqual(False, hook._after)
        self.assertEqual("action", hook.action)
        self.assertEqual("command", hook.command)

    def testConstructor_003(self):
        """
        Test assignment of action attribute, None value.
        """
        hook = ActionHook(action="action")
        self.assertEqual("action", hook.action)
        hook.action = None
        self.assertEqual(None, hook.action)

    def testConstructor_004(self):
        """
        Test assignment of action attribute, valid value.
        """
        hook = ActionHook()
        self.assertEqual(None, hook.action)
        hook.action = "action"
        self.assertEqual("action", hook.action)

    def testConstructor_005(self):
        """
        Test assignment of action attribute, invalid value.
        """
        hook = ActionHook()
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "KEN")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "dash-word")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "hello, world")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "")
        self.assertEqual(None, hook.action)

    def testConstructor_006(self):
        """
        Test assignment of command attribute, None value.
        """
        hook = ActionHook(command="command")
        self.assertEqual("command", hook.command)
        hook.command = None
        self.assertEqual(None, hook.command)

    def testConstructor_007(self):
        """
        Test assignment of command attribute, valid valid.
        """
        hook = ActionHook()
        self.assertEqual(None, hook.command)
        hook.command = "command"
        self.assertEqual("command", hook.command)

    def testConstructor_008(self):
        """
        Test assignment of command attribute, invalid valid.
        """
        hook = ActionHook()
        self.assertEqual(None, hook.command)
        self.failUnlessAssignRaises(ValueError, hook, "command", "")
        self.assertEqual(None, hook.command)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        hook1 = ActionHook()
        hook2 = ActionHook()
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        hook1 = ActionHook(action="action", command="command")
        hook2 = ActionHook(action="action", command="command")
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_003(self):
        """
        Test comparison of two different objects, action differs (one None).
        """
        hook1 = ActionHook(action="action", command="command")
        hook2 = ActionHook(action=None, command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_004(self):
        """
        Test comparison of two different objects, action differs.
        """
        hook1 = ActionHook(action="action2", command="command")
        hook2 = ActionHook(action="action1", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_005(self):
        """
        Test comparison of two different objects, command differs (one None).
        """
        hook1 = ActionHook(action="action", command=None)
        hook2 = ActionHook(action="action", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_006(self):
        """
        Test comparison of two different objects, command differs.
        """
        hook1 = ActionHook(action="action", command="command1")
        hook2 = ActionHook(action="action", command="command2")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)


##########################
# TestPreActionHook class
##########################


class TestPreActionHook(unittest.TestCase):

    """Tests for the PreActionHook class."""

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
        obj = PreActionHook()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        hook = PreActionHook()
        self.assertEqual(True, hook._before)
        self.assertEqual(False, hook._after)
        self.assertEqual(None, hook.action)
        self.assertEqual(None, hook.command)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        hook = PreActionHook(action="action", command="command")
        self.assertEqual(True, hook._before)
        self.assertEqual(False, hook._after)
        self.assertEqual("action", hook.action)
        self.assertEqual("command", hook.command)

    def testConstructor_003(self):
        """
        Test assignment of action attribute, None value.
        """
        hook = PreActionHook(action="action")
        self.assertEqual("action", hook.action)
        hook.action = None
        self.assertEqual(None, hook.action)

    def testConstructor_004(self):
        """
        Test assignment of action attribute, valid value.
        """
        hook = PreActionHook()
        self.assertEqual(None, hook.action)
        hook.action = "action"
        self.assertEqual("action", hook.action)

    def testConstructor_005(self):
        """
        Test assignment of action attribute, invalid value.
        """
        hook = PreActionHook()
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "KEN")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "dash-word")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "hello, world")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "")
        self.assertEqual(None, hook.action)

    def testConstructor_006(self):
        """
        Test assignment of command attribute, None value.
        """
        hook = PreActionHook(command="command")
        self.assertEqual("command", hook.command)
        hook.command = None
        self.assertEqual(None, hook.command)

    def testConstructor_007(self):
        """
        Test assignment of command attribute, valid valid.
        """
        hook = PreActionHook()
        self.assertEqual(None, hook.command)
        hook.command = "command"
        self.assertEqual("command", hook.command)

    def testConstructor_008(self):
        """
        Test assignment of command attribute, invalid valid.
        """
        hook = PreActionHook()
        self.assertEqual(None, hook.command)
        self.failUnlessAssignRaises(ValueError, hook, "command", "")
        self.assertEqual(None, hook.command)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        hook1 = PreActionHook()
        hook2 = PreActionHook()
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        hook1 = PreActionHook(action="action", command="command")
        hook2 = PreActionHook(action="action", command="command")
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_003(self):
        """
        Test comparison of two different objects, action differs (one None).
        """
        hook1 = PreActionHook(action="action", command="command")
        hook2 = PreActionHook(action=None, command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_004(self):
        """
        Test comparison of two different objects, action differs.
        """
        hook1 = PreActionHook(action="action2", command="command")
        hook2 = PreActionHook(action="action1", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_005(self):
        """
        Test comparison of two different objects, command differs (one None).
        """
        hook1 = PreActionHook(action="action", command=None)
        hook2 = PreActionHook(action="action", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_006(self):
        """
        Test comparison of two different objects, command differs.
        """
        hook1 = PreActionHook(action="action", command="command1")
        hook2 = PreActionHook(action="action", command="command2")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)


###########################
# TestPostActionHook class
###########################


class TestPostActionHook(unittest.TestCase):

    """Tests for the PostActionHook class."""

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
        obj = PostActionHook()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        hook = PostActionHook()
        self.assertEqual(False, hook._before)
        self.assertEqual(True, hook._after)
        self.assertEqual(None, hook.action)
        self.assertEqual(None, hook.command)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        hook = PostActionHook(action="action", command="command")
        self.assertEqual(False, hook._before)
        self.assertEqual(True, hook._after)
        self.assertEqual("action", hook.action)
        self.assertEqual("command", hook.command)

    def testConstructor_003(self):
        """
        Test assignment of action attribute, None value.
        """
        hook = PostActionHook(action="action")
        self.assertEqual("action", hook.action)
        hook.action = None
        self.assertEqual(None, hook.action)

    def testConstructor_004(self):
        """
        Test assignment of action attribute, valid value.
        """
        hook = PostActionHook()
        self.assertEqual(None, hook.action)
        hook.action = "action"
        self.assertEqual("action", hook.action)

    def testConstructor_005(self):
        """
        Test assignment of action attribute, invalid value.
        """
        hook = PostActionHook()
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "KEN")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "dash-word")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "hello, world")
        self.assertEqual(None, hook.action)
        self.failUnlessAssignRaises(ValueError, hook, "action", "")
        self.assertEqual(None, hook.action)

    def testConstructor_006(self):
        """
        Test assignment of command attribute, None value.
        """
        hook = PostActionHook(command="command")
        self.assertEqual("command", hook.command)
        hook.command = None
        self.assertEqual(None, hook.command)

    def testConstructor_007(self):
        """
        Test assignment of command attribute, valid valid.
        """
        hook = PostActionHook()
        self.assertEqual(None, hook.command)
        hook.command = "command"
        self.assertEqual("command", hook.command)

    def testConstructor_008(self):
        """
        Test assignment of command attribute, invalid valid.
        """
        hook = PostActionHook()
        self.assertEqual(None, hook.command)
        self.failUnlessAssignRaises(ValueError, hook, "command", "")
        self.assertEqual(None, hook.command)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        hook1 = PostActionHook()
        hook2 = PostActionHook()
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        hook1 = PostActionHook(action="action", command="command")
        hook2 = PostActionHook(action="action", command="command")
        self.assertEqual(hook1, hook2)
        self.assertTrue(hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(not hook1 != hook2)

    def testComparison_003(self):
        """
        Test comparison of two different objects, action differs (one None).
        """
        hook1 = PostActionHook(action="action", command="command")
        hook2 = PostActionHook(action=None, command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_004(self):
        """
        Test comparison of two different objects, action differs.
        """
        hook1 = PostActionHook(action="action2", command="command")
        hook2 = PostActionHook(action="action1", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(not hook1 < hook2)
        self.assertTrue(not hook1 <= hook2)
        self.assertTrue(hook1 > hook2)
        self.assertTrue(hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_005(self):
        """
        Test comparison of two different objects, command differs (one None).
        """
        hook1 = PostActionHook(action="action", command=None)
        hook2 = PostActionHook(action="action", command="command")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)

    def testComparison_006(self):
        """
        Test comparison of two different objects, command differs.
        """
        hook1 = PostActionHook(action="action", command="command1")
        hook2 = PostActionHook(action="action", command="command2")
        self.assertTrue(not hook1 == hook2)
        self.assertTrue(hook1 < hook2)
        self.assertTrue(hook1 <= hook2)
        self.assertTrue(not hook1 > hook2)
        self.assertTrue(not hook1 >= hook2)
        self.assertTrue(hook1 != hook2)


##########################
# TestBlankBehavior class
##########################


class TestBlankBehavior(unittest.TestCase):

    """Tests for the BlankBehavior class."""

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
        obj = BlankBehavior()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankMode)
        self.assertEqual(None, behavior.blankFactor)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        behavior = BlankBehavior(blankMode="daily", blankFactor="1.0")
        self.assertEqual("daily", behavior.blankMode)
        self.assertEqual("1.0", behavior.blankFactor)

    def testConstructor_003(self):
        """
        Test assignment of blankMode, None value.
        """
        behavior = BlankBehavior(blankMode="daily")
        self.assertEqual("daily", behavior.blankMode)
        behavior.blankMode = None
        self.assertEqual(None, behavior.blankMode)

    def testConstructor_004(self):
        """
        Test assignment of blankMode attribute, valid value.
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankMode)
        behavior.blankMode = "daily"
        self.assertEqual("daily", behavior.blankMode)
        behavior.blankMode = "weekly"
        self.assertEqual("weekly", behavior.blankMode)

    def testConstructor_005(self):
        """
        Test assignment of blankFactor attribute, None value.
        """
        behavior = BlankBehavior(blankFactor="1.3")
        self.assertEqual("1.3", behavior.blankFactor)
        behavior.blankFactor = None
        self.assertEqual(None, behavior.blankFactor)

    def testConstructor_006(self):
        """
        Test assignment of blankFactor attribute, valid values.
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankFactor)
        behavior.blankFactor = "1.0"
        self.assertEqual("1.0", behavior.blankFactor)
        behavior.blankFactor = ".1"
        self.assertEqual(".1", behavior.blankFactor)
        behavior.blankFactor = "12"
        self.assertEqual("12", behavior.blankFactor)
        behavior.blankFactor = "0.5"
        self.assertEqual("0.5", behavior.blankFactor)
        behavior.blankFactor = "181281"
        self.assertEqual("181281", behavior.blankFactor)
        behavior.blankFactor = "1E6"
        self.assertEqual("1E6", behavior.blankFactor)
        behavior.blankFactor = "0.25E2"
        self.assertEqual("0.25E2", behavior.blankFactor)

    def testConstructor_007(self):
        """
        Test assignment of blankFactor attribute, invalid value (empty).
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "")
        self.assertEqual(None, behavior.blankFactor)

    def testConstructor_008(self):
        """
        Test assignment of blankFactor attribute, invalid value (not a floating point number).
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "blech")
        self.assertEqual(None, behavior.blankFactor)

    def testConstructor_009(self):
        """
        Test assignment of blankFactor store attribute, invalid value (negative number).
        """
        behavior = BlankBehavior()
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "-3")
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "-6.8")
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "-0.2")
        self.assertEqual(None, behavior.blankFactor)
        self.failUnlessAssignRaises(ValueError, behavior, "blankFactor", "-.1")
        self.assertEqual(None, behavior.blankFactor)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        behavior1 = BlankBehavior()
        behavior2 = BlankBehavior()
        self.assertEqual(behavior1, behavior2)
        self.assertTrue(behavior1 == behavior2)
        self.assertTrue(not behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(behavior1 >= behavior2)
        self.assertTrue(not behavior1 != behavior2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        behavior1 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        behavior2 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        self.assertEqual(behavior1, behavior2)
        self.assertTrue(behavior1 == behavior2)
        self.assertTrue(not behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(behavior1 >= behavior2)
        self.assertTrue(not behavior1 != behavior2)

    def testComparison_003(self):
        """
        Test comparison of two different objects, blankMode differs (one None).
        """
        behavior1 = BlankBehavior(None, blankFactor="1.0")
        behavior2 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        self.assertTrue(not behavior1 == behavior2)
        self.assertTrue(behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(not behavior1 >= behavior2)
        self.assertTrue(behavior1 != behavior2)

    def testComparison_004(self):
        """
        Test comparison of two different objects, blankMode differs.
        """
        behavior1 = BlankBehavior(blankMode="daily", blankFactor="1.0")
        behavior2 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        self.assertTrue(not behavior1 == behavior2)
        self.assertTrue(behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(not behavior1 >= behavior2)
        self.assertTrue(behavior1 != behavior2)

    def testComparison_005(self):
        """
        Test comparison of two different objects, blankFactor differs (one None).
        """
        behavior1 = BlankBehavior(blankMode="weekly", blankFactor=None)
        behavior2 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        self.assertTrue(not behavior1 == behavior2)
        self.assertTrue(behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(not behavior1 >= behavior2)
        self.assertTrue(behavior1 != behavior2)

    def testComparison_006(self):
        """
        Test comparison of two different objects, blankFactor differs.
        """
        behavior1 = BlankBehavior(blankMode="weekly", blankFactor="0.0")
        behavior2 = BlankBehavior(blankMode="weekly", blankFactor="1.0")
        self.assertTrue(not behavior1 == behavior2)
        self.assertTrue(behavior1 < behavior2)
        self.assertTrue(behavior1 <= behavior2)
        self.assertTrue(not behavior1 > behavior2)
        self.assertTrue(not behavior1 >= behavior2)
        self.assertTrue(behavior1 != behavior2)


###########################
# TestExtendedAction class
###########################


class TestExtendedAction(unittest.TestCase):

    """Tests for the ExtendedAction class."""

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
        obj = ExtendedAction()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.name)
        self.assertEqual(None, action.module)
        self.assertEqual(None, action.function)
        self.assertEqual(None, action.index)
        self.assertEqual(None, action.dependencies)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        action = ExtendedAction("one", "two", "three", 4, ActionDependencies())
        self.assertEqual("one", action.name)
        self.assertEqual("two", action.module)
        self.assertEqual("three", action.function)
        self.assertEqual(4, action.index)
        self.assertEqual(ActionDependencies(), action.dependencies)

    def testConstructor_003(self):
        """
        Test assignment of name attribute, None value.
        """
        action = ExtendedAction(name="name")
        self.assertEqual("name", action.name)
        action.name = None
        self.assertEqual(None, action.name)

    def testConstructor_004(self):
        """
        Test assignment of name attribute, valid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.name)
        action.name = "name"
        self.assertEqual("name", action.name)
        action.name = "9"
        self.assertEqual("9", action.name)
        action.name = "name99name"
        self.assertEqual("name99name", action.name)
        action.name = "12action"
        self.assertEqual("12action", action.name)

    def testConstructor_005(self):
        """
        Test assignment of name attribute, invalid value (empty).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "")
        self.assertEqual(None, action.name)

    def testConstructor_006(self):
        """
        Test assignment of name attribute, invalid value (does not match valid pattern).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "Something")
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "what_ever")
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "_BOGUS")
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "stuff-here")
        self.assertEqual(None, action.name)
        self.failUnlessAssignRaises(ValueError, action, "name", "/more/stuff")
        self.assertEqual(None, action.name)

    def testConstructor_007(self):
        """
        Test assignment of module attribute, None value.
        """
        action = ExtendedAction(module="module")
        self.assertEqual("module", action.module)
        action.module = None
        self.assertEqual(None, action.module)

    def testConstructor_008(self):
        """
        Test assignment of module attribute, valid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.module)
        action.module = "module"
        self.assertEqual("module", action.module)
        action.module = "stuff"
        self.assertEqual("stuff", action.module)
        action.module = "stuff.something"
        self.assertEqual("stuff.something", action.module)
        action.module = "_identifier.__another.one_more__"
        self.assertEqual("_identifier.__another.one_more__", action.module)

    def testConstructor_009(self):
        """
        Test assignment of module attribute, invalid value (empty).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "")
        self.assertEqual(None, action.module)

    def testConstructor_010(self):
        """
        Test assignment of module attribute, invalid value (does not match valid pattern).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "9something")
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "_bogus.")
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "-bogus")
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "/BOGUS")
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", "really._really__.___really.long.bad.path.")
        self.assertEqual(None, action.module)
        self.failUnlessAssignRaises(ValueError, action, "module", ".really._really__.___really.long.bad.path")
        self.assertEqual(None, action.module)

    def testConstructor_011(self):
        """
        Test assignment of function attribute, None value.
        """
        action = ExtendedAction(function="function")
        self.assertEqual("function", action.function)
        action.function = None
        self.assertEqual(None, action.function)

    def testConstructor_012(self):
        """
        Test assignment of function attribute, valid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.function)
        action.function = "function"
        self.assertEqual("function", action.function)
        action.function = "_stuff"
        self.assertEqual("_stuff", action.function)
        action.function = "moreStuff9"
        self.assertEqual("moreStuff9", action.function)
        action.function = "__identifier__"
        self.assertEqual("__identifier__", action.function)

    def testConstructor_013(self):
        """
        Test assignment of function attribute, invalid value (empty).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.function)
        self.failUnlessAssignRaises(ValueError, action, "function", "")
        self.assertEqual(None, action.function)

    def testConstructor_014(self):
        """
        Test assignment of function attribute, invalid value (does not match valid pattern).
        """
        action = ExtendedAction()
        self.assertEqual(None, action.function)
        self.failUnlessAssignRaises(ValueError, action, "function", "9something")
        self.assertEqual(None, action.function)
        self.failUnlessAssignRaises(ValueError, action, "function", "one.two")
        self.assertEqual(None, action.function)
        self.failUnlessAssignRaises(ValueError, action, "function", "-bogus")
        self.assertEqual(None, action.function)
        self.failUnlessAssignRaises(ValueError, action, "function", "/BOGUS")
        self.assertEqual(None, action.function)

    def testConstructor_015(self):
        """
        Test assignment of index attribute, None value.
        """
        action = ExtendedAction(index=1)
        self.assertEqual(1, action.index)
        action.index = None
        self.assertEqual(None, action.index)

    def testConstructor_016(self):
        """
        Test assignment of index attribute, valid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.index)
        action.index = 1
        self.assertEqual(1, action.index)

    def testConstructor_017(self):
        """
        Test assignment of index attribute, invalid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.index)
        self.failUnlessAssignRaises(ValueError, action, "index", "ken")
        self.assertEqual(None, action.index)

    def testConstructor_018(self):
        """
        Test assignment of dependencies attribute, None value.
        """
        action = ExtendedAction(dependencies=ActionDependencies())
        self.assertEqual(ActionDependencies(), action.dependencies)
        action.dependencies = None
        self.assertEqual(None, action.dependencies)

    def testConstructor_019(self):
        """
        Test assignment of dependencies attribute, valid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.dependencies)
        action.dependencies = ActionDependencies()
        self.assertEqual(ActionDependencies(), action.dependencies)

    def testConstructor_020(self):
        """
        Test assignment of dependencies attribute, invalid value.
        """
        action = ExtendedAction()
        self.assertEqual(None, action.dependencies)
        self.failUnlessAssignRaises(ValueError, action, "dependencies", "ken")
        self.assertEqual(None, action.dependencies)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        action1 = ExtendedAction()
        action2 = ExtendedAction()
        self.assertEqual(action1, action2)
        self.assertTrue(action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(not action1 != action2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        action1 = ExtendedAction("one", "two", "three", 4, ActionDependencies())
        action2 = ExtendedAction("one", "two", "three", 4, ActionDependencies())
        self.assertTrue(action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(not action1 != action2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, name differs (one None).
        """
        action1 = ExtendedAction(name="name")
        action2 = ExtendedAction()
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(not action1 <= action2)
        self.assertTrue(action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, name differs.
        """
        action1 = ExtendedAction("name2", "two", "three", 4)
        action2 = ExtendedAction("name1", "two", "three", 4)
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(not action1 <= action2)
        self.assertTrue(action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, module differs (one None).
        """
        action1 = ExtendedAction(module="whatever")
        action2 = ExtendedAction()
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(not action1 <= action2)
        self.assertTrue(action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, module differs.
        """
        action1 = ExtendedAction("one", "MODULE", "three", 4)
        action2 = ExtendedAction("one", "two", "three", 4)
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(not action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, function differs (one None).
        """
        action1 = ExtendedAction(function="func1")
        action2 = ExtendedAction()
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(not action1 <= action2)
        self.assertTrue(action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, function differs.
        """
        action1 = ExtendedAction("one", "two", "func1", 4)
        action2 = ExtendedAction("one", "two", "func2", 4)
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(not action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, index differs (one None).
        """
        action1 = ExtendedAction()
        action2 = ExtendedAction(index=42)
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(not action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, index differs.
        """
        action1 = ExtendedAction("one", "two", "three", 99)
        action2 = ExtendedAction("one", "two", "three", 12)
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(not action1 < action2)
        self.assertTrue(not action1 <= action2)
        self.assertTrue(action1 > action2)
        self.assertTrue(action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, dependencies differs (one None).
        """
        action1 = ExtendedAction()
        action2 = ExtendedAction(dependencies=ActionDependencies())
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(not action1 >= action2)
        self.assertTrue(action1 != action2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, dependencies differs.
        """
        action1 = ExtendedAction("one", "two", "three", 99, ActionDependencies(beforeList=[]))
        action2 = ExtendedAction("one", "two", "three", 99, ActionDependencies(beforeList=["ken"]))
        self.assertNotEqual(action1, action2)
        self.assertTrue(not action1 == action2)
        self.assertTrue(action1 < action2)
        self.assertTrue(action1 <= action2)
        self.assertTrue(not action1 > action2)
        self.assertTrue(not action1 >= action2)
        self.assertTrue(action1 != action2)


############################
# TestCommandOverride class
############################


class TestCommandOverride(unittest.TestCase):

    """Tests for the CommandOverride class."""

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
        obj = CommandOverride()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        override = CommandOverride()
        self.assertEqual(None, override.command)
        self.assertEqual(None, override.absolutePath)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        override = CommandOverride(command="command", absolutePath="/path/to/something")
        self.assertEqual("command", override.command)
        self.assertEqual("/path/to/something", override.absolutePath)

    def testConstructor_003(self):
        """
        Test assignment of command attribute, None value.
        """
        override = CommandOverride(command="command")
        self.assertEqual("command", override.command)
        override.command = None
        self.assertEqual(None, override.command)

    def testConstructor_004(self):
        """
        Test assignment of command attribute, valid value.
        """
        override = CommandOverride()
        self.assertEqual(None, override.command)
        override.command = "command"
        self.assertEqual("command", override.command)

    def testConstructor_005(self):
        """
        Test assignment of command attribute, invalid value.
        """
        override = CommandOverride()
        override.command = None
        self.failUnlessAssignRaises(ValueError, override, "command", "")
        override.command = None

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        override = CommandOverride(absolutePath="/path/to/something")
        self.assertEqual("/path/to/something", override.absolutePath)
        override.absolutePath = None
        self.assertEqual(None, override.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        override = CommandOverride()
        self.assertEqual(None, override.absolutePath)
        override.absolutePath = "/path/to/something"
        self.assertEqual("/path/to/something", override.absolutePath)

    def testConstructor_008(self):
        """
        Test assignment of absolutePath attribute, invalid value.
        """
        override = CommandOverride()
        override.command = None
        self.failUnlessAssignRaises(ValueError, override, "absolutePath", "path/to/something/relative")
        override.command = None
        self.failUnlessAssignRaises(ValueError, override, "absolutePath", "")
        override.command = None

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        override1 = CommandOverride()
        override2 = CommandOverride()
        self.assertEqual(override1, override2)
        self.assertTrue(override1 == override2)
        self.assertTrue(not override1 < override2)
        self.assertTrue(override1 <= override2)
        self.assertTrue(not override1 > override2)
        self.assertTrue(override1 >= override2)
        self.assertTrue(not override1 != override2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        override1 = CommandOverride(command="command", absolutePath="/path/to/something")
        override2 = CommandOverride(command="command", absolutePath="/path/to/something")
        self.assertEqual(override1, override2)
        self.assertTrue(override1 == override2)
        self.assertTrue(not override1 < override2)
        self.assertTrue(override1 <= override2)
        self.assertTrue(not override1 > override2)
        self.assertTrue(override1 >= override2)
        self.assertTrue(not override1 != override2)

    def testComparison_003(self):
        """
        Test comparison of differing objects, command differs (one None).
        """
        override1 = CommandOverride(command=None, absolutePath="/path/to/something")
        override2 = CommandOverride(command="command", absolutePath="/path/to/something")
        self.assertTrue(not override1 == override2)
        self.assertTrue(override1 < override2)
        self.assertTrue(override1 <= override2)
        self.assertTrue(not override1 > override2)
        self.assertTrue(not override1 >= override2)
        self.assertTrue(override1 != override2)

    def testComparison_004(self):
        """
        Test comparison of differing objects, command differs.
        """
        override1 = CommandOverride(command="command2", absolutePath="/path/to/something")
        override2 = CommandOverride(command="command1", absolutePath="/path/to/something")
        self.assertTrue(not override1 == override2)
        self.assertTrue(not override1 < override2)
        self.assertTrue(not override1 <= override2)
        self.assertTrue(override1 > override2)
        self.assertTrue(override1 >= override2)
        self.assertTrue(override1 != override2)

    def testComparison_005(self):
        """
        Test comparison of differing objects, absolutePath differs (one None).
        """
        override1 = CommandOverride(command="command", absolutePath="/path/to/something")
        override2 = CommandOverride(command="command", absolutePath=None)
        self.assertTrue(not override1 == override2)
        self.assertTrue(not override1 < override2)
        self.assertTrue(not override1 <= override2)
        self.assertTrue(override1 > override2)
        self.assertTrue(override1 >= override2)
        self.assertTrue(override1 != override2)

    def testComparison_006(self):
        """
        Test comparison of differing objects, absolutePath differs.
        """
        override1 = CommandOverride(command="command", absolutePath="/path/to/something1")
        override2 = CommandOverride(command="command", absolutePath="/path/to/something2")
        self.assertTrue(not override1 == override2)
        self.assertTrue(override1 < override2)
        self.assertTrue(override1 <= override2)
        self.assertTrue(not override1 > override2)
        self.assertTrue(not override1 >= override2)
        self.assertTrue(override1 != override2)


########################
# TestCollectFile class
########################


class TestCollectFile(unittest.TestCase):

    """Tests for the CollectFile class."""

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
        obj = CollectFile()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.absolutePath)
        self.assertEqual(None, collectFile.collectMode)
        self.assertEqual(None, collectFile.archiveMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        collectFile = CollectFile("/etc/whatever", "incr", "tar")
        self.assertEqual("/etc/whatever", collectFile.absolutePath)
        self.assertEqual("incr", collectFile.collectMode)
        self.assertEqual("tar", collectFile.archiveMode)

    def testConstructor_003(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        collectFile = CollectFile(absolutePath="/whatever")
        self.assertEqual("/whatever", collectFile.absolutePath)
        collectFile.absolutePath = None
        self.assertEqual(None, collectFile.absolutePath)

    def testConstructor_004(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.absolutePath)
        collectFile.absolutePath = "/etc/whatever"
        self.assertEqual("/etc/whatever", collectFile.absolutePath)

    def testConstructor_005(self):
        """
        Test assignment of absolutePath attribute, invalid value (empty).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.absolutePath)
        self.failUnlessAssignRaises(ValueError, collectFile, "absolutePath", "")
        self.assertEqual(None, collectFile.absolutePath)

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, invalid value (non-absolute).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.absolutePath)
        self.failUnlessAssignRaises(ValueError, collectFile, "absolutePath", "whatever")
        self.assertEqual(None, collectFile.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        collectFile = CollectFile(collectMode="incr")
        self.assertEqual("incr", collectFile.collectMode)
        collectFile.collectMode = None
        self.assertEqual(None, collectFile.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.collectMode)
        collectFile.collectMode = "daily"
        self.assertEqual("daily", collectFile.collectMode)
        collectFile.collectMode = "weekly"
        self.assertEqual("weekly", collectFile.collectMode)
        collectFile.collectMode = "incr"
        self.assertEqual("incr", collectFile.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.collectMode)
        self.failUnlessAssignRaises(ValueError, collectFile, "collectMode", "")
        self.assertEqual(None, collectFile.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.collectMode)
        self.failUnlessAssignRaises(ValueError, collectFile, "collectMode", "bogus")
        self.assertEqual(None, collectFile.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of archiveMode attribute, None value.
        """
        collectFile = CollectFile(archiveMode="tar")
        self.assertEqual("tar", collectFile.archiveMode)
        collectFile.archiveMode = None
        self.assertEqual(None, collectFile.archiveMode)

    def testConstructor_012(self):
        """
        Test assignment of archiveMode attribute, valid value.
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.archiveMode)
        collectFile.archiveMode = "tar"
        self.assertEqual("tar", collectFile.archiveMode)
        collectFile.archiveMode = "targz"
        self.assertEqual("targz", collectFile.archiveMode)
        collectFile.archiveMode = "tarbz2"
        self.assertEqual("tarbz2", collectFile.archiveMode)

    def testConstructor_013(self):
        """
        Test assignment of archiveMode attribute, invalid value (empty).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.archiveMode)
        self.failUnlessAssignRaises(ValueError, collectFile, "archiveMode", "")
        self.assertEqual(None, collectFile.archiveMode)

    def testConstructor_014(self):
        """
        Test assignment of archiveMode attribute, invalid value (not in list).
        """
        collectFile = CollectFile()
        self.assertEqual(None, collectFile.archiveMode)
        self.failUnlessAssignRaises(ValueError, collectFile, "archiveMode", "bogus")
        self.assertEqual(None, collectFile.archiveMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        collectFile1 = CollectFile()
        collectFile2 = CollectFile()
        self.assertEqual(collectFile1, collectFile2)
        self.assertTrue(collectFile1 == collectFile2)
        self.assertTrue(not collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(collectFile1 >= collectFile2)
        self.assertTrue(not collectFile1 != collectFile2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        collectFile1 = CollectFile("/etc/whatever", "incr", "tar")
        collectFile2 = CollectFile("/etc/whatever", "incr", "tar")
        self.assertTrue(collectFile1 == collectFile2)
        self.assertTrue(not collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(collectFile1 >= collectFile2)
        self.assertTrue(not collectFile1 != collectFile2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, absolutePath differs (one None).
        """
        collectFile1 = CollectFile()
        collectFile2 = CollectFile(absolutePath="/whatever")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(not collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, absolutePath differs.
        """
        collectFile1 = CollectFile("/etc/whatever", "incr", "tar")
        collectFile2 = CollectFile("/stuff", "incr", "tar")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(not collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        collectFile1 = CollectFile()
        collectFile2 = CollectFile(collectMode="incr")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(not collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        collectFile1 = CollectFile("/etc/whatever", "incr", "tar")
        collectFile2 = CollectFile("/etc/whatever", "daily", "tar")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(not collectFile1 < collectFile2)
        self.assertTrue(not collectFile1 <= collectFile2)
        self.assertTrue(collectFile1 > collectFile2)
        self.assertTrue(collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, archiveMode differs (one None).
        """
        collectFile1 = CollectFile()
        collectFile2 = CollectFile(archiveMode="tar")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(collectFile1 < collectFile2)
        self.assertTrue(collectFile1 <= collectFile2)
        self.assertTrue(not collectFile1 > collectFile2)
        self.assertTrue(not collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, archiveMode differs.
        """
        collectFile1 = CollectFile("/etc/whatever", "incr", "targz")
        collectFile2 = CollectFile("/etc/whatever", "incr", "tar")
        self.assertNotEqual(collectFile1, collectFile2)
        self.assertTrue(not collectFile1 == collectFile2)
        self.assertTrue(not collectFile1 < collectFile2)
        self.assertTrue(not collectFile1 <= collectFile2)
        self.assertTrue(collectFile1 > collectFile2)
        self.assertTrue(collectFile1 >= collectFile2)
        self.assertTrue(collectFile1 != collectFile2)


#######################
# TestCollectDir class
#######################


class TestCollectDir(unittest.TestCase):

    """Tests for the CollectDir class."""

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
        obj = CollectDir()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absolutePath)
        self.assertEqual(None, collectDir.collectMode)
        self.assertEqual(None, collectDir.archiveMode)
        self.assertEqual(None, collectDir.ignoreFile)
        self.assertEqual(None, collectDir.linkDepth)
        self.assertEqual(False, collectDir.dereference)
        self.assertEqual(None, collectDir.recursionLevel)
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        self.assertEqual(None, collectDir.relativeExcludePaths)
        self.assertEqual(None, collectDir.excludePatterns)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        collectDir = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 2, True, 6)
        self.assertEqual("/etc/whatever", collectDir.absolutePath)
        self.assertEqual("incr", collectDir.collectMode)
        self.assertEqual("tar", collectDir.archiveMode)
        self.assertEqual(".ignore", collectDir.ignoreFile)
        self.assertEqual(2, collectDir.linkDepth)
        self.assertEqual(True, collectDir.dereference)
        self.assertEqual(6, collectDir.recursionLevel)
        self.assertEqual([], collectDir.absoluteExcludePaths)
        self.assertEqual([], collectDir.relativeExcludePaths)
        self.assertEqual([], collectDir.excludePatterns)

    def testConstructor_003(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        collectDir = CollectDir(absolutePath="/whatever")
        self.assertEqual("/whatever", collectDir.absolutePath)
        collectDir.absolutePath = None
        self.assertEqual(None, collectDir.absolutePath)

    def testConstructor_004(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absolutePath)
        collectDir.absolutePath = "/etc/whatever"
        self.assertEqual("/etc/whatever", collectDir.absolutePath)

    def testConstructor_005(self):
        """
        Test assignment of absolutePath attribute, invalid value (empty).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, collectDir, "absolutePath", "")
        self.assertEqual(None, collectDir.absolutePath)

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, invalid value (non-absolute).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, collectDir, "absolutePath", "whatever")
        self.assertEqual(None, collectDir.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        collectDir = CollectDir(collectMode="incr")
        self.assertEqual("incr", collectDir.collectMode)
        collectDir.collectMode = None
        self.assertEqual(None, collectDir.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.collectMode)
        collectDir.collectMode = "daily"
        self.assertEqual("daily", collectDir.collectMode)
        collectDir.collectMode = "weekly"
        self.assertEqual("weekly", collectDir.collectMode)
        collectDir.collectMode = "incr"
        self.assertEqual("incr", collectDir.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.collectMode)
        self.failUnlessAssignRaises(ValueError, collectDir, "collectMode", "")
        self.assertEqual(None, collectDir.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.collectMode)
        self.failUnlessAssignRaises(ValueError, collectDir, "collectMode", "bogus")
        self.assertEqual(None, collectDir.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of archiveMode attribute, None value.
        """
        collectDir = CollectDir(archiveMode="tar")
        self.assertEqual("tar", collectDir.archiveMode)
        collectDir.archiveMode = None
        self.assertEqual(None, collectDir.archiveMode)

    def testConstructor_012(self):
        """
        Test assignment of archiveMode attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.archiveMode)
        collectDir.archiveMode = "tar"
        self.assertEqual("tar", collectDir.archiveMode)
        collectDir.archiveMode = "targz"
        self.assertEqual("targz", collectDir.archiveMode)
        collectDir.archiveMode = "tarbz2"
        self.assertEqual("tarbz2", collectDir.archiveMode)

    def testConstructor_013(self):
        """
        Test assignment of archiveMode attribute, invalid value (empty).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.archiveMode)
        self.failUnlessAssignRaises(ValueError, collectDir, "archiveMode", "")
        self.assertEqual(None, collectDir.archiveMode)

    def testConstructor_014(self):
        """
        Test assignment of archiveMode attribute, invalid value (not in list).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.archiveMode)
        self.failUnlessAssignRaises(ValueError, collectDir, "archiveMode", "bogus")
        self.assertEqual(None, collectDir.archiveMode)

    def testConstructor_015(self):
        """
        Test assignment of ignoreFile attribute, None value.
        """
        collectDir = CollectDir(ignoreFile="ignore")
        self.assertEqual("ignore", collectDir.ignoreFile)
        collectDir.ignoreFile = None
        self.assertEqual(None, collectDir.ignoreFile)

    def testConstructor_016(self):
        """
        Test assignment of ignoreFile attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.ignoreFile)
        collectDir.ignoreFile = "ignorefile"
        self.assertEqual("ignorefile", collectDir.ignoreFile)

    def testConstructor_017(self):
        """
        Test assignment of ignoreFile attribute, invalid value (empty).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.ignoreFile)
        self.failUnlessAssignRaises(ValueError, collectDir, "ignoreFile", "")
        self.assertEqual(None, collectDir.ignoreFile)

    def testConstructor_018(self):
        """
        Test assignment of absoluteExcludePaths attribute, None value.
        """
        collectDir = CollectDir(absoluteExcludePaths=[])
        self.assertEqual([], collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths = None
        self.assertEqual(None, collectDir.absoluteExcludePaths)

    def testConstructor_019(self):
        """
        Test assignment of absoluteExcludePaths attribute, [] value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths = []
        self.assertEqual([], collectDir.absoluteExcludePaths)

    def testConstructor_020(self):
        """
        Test assignment of absoluteExcludePaths attribute, single valid entry.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths = [
            "/whatever",
        ]
        self.assertEqual(["/whatever"], collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths.append("/stuff")
        self.assertEqual(["/whatever", "/stuff"], collectDir.absoluteExcludePaths)

    def testConstructor_021(self):
        """
        Test assignment of absoluteExcludePaths attribute, multiple valid
        entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths = [
            "/whatever",
            "/stuff",
        ]
        self.assertEqual(["/whatever", "/stuff"], collectDir.absoluteExcludePaths)
        collectDir.absoluteExcludePaths.append("/etc/X11")
        self.assertEqual(["/whatever", "/stuff", "/etc/X11"], collectDir.absoluteExcludePaths)

    def testConstructor_022(self):
        """
        Test assignment of absoluteExcludePaths attribute, single invalid entry
        (empty).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collectDir, "absoluteExcludePaths", [""])
        self.assertEqual(None, collectDir.absoluteExcludePaths)

    def testConstructor_023(self):
        """
        Test assignment of absoluteExcludePaths attribute, single invalid entry
        (not absolute).
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collectDir, "absoluteExcludePaths", ["notabsolute"])
        self.assertEqual(None, collectDir.absoluteExcludePaths)

    def testConstructor_024(self):
        """
        Test assignment of absoluteExcludePaths attribute, mixed valid and
        invalid entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collectDir, "absoluteExcludePaths", ["/good", "bad", "/alsogood"])
        self.assertEqual(None, collectDir.absoluteExcludePaths)

    def testConstructor_025(self):
        """
        Test assignment of relativeExcludePaths attribute, None value.
        """
        collectDir = CollectDir(relativeExcludePaths=[])
        self.assertEqual([], collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths = None
        self.assertEqual(None, collectDir.relativeExcludePaths)

    def testConstructor_026(self):
        """
        Test assignment of relativeExcludePaths attribute, [] value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths = []
        self.assertEqual([], collectDir.relativeExcludePaths)

    def testConstructor_027(self):
        """
        Test assignment of relativeExcludePaths attribute, single valid entry.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths = [
            "stuff",
        ]
        self.assertEqual(["stuff"], collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths.insert(0, "bogus")
        self.assertEqual(["bogus", "stuff"], collectDir.relativeExcludePaths)

    def testConstructor_028(self):
        """
        Test assignment of relativeExcludePaths attribute, multiple valid
        entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths = [
            "bogus",
            "stuff",
        ]
        self.assertEqual(["bogus", "stuff"], collectDir.relativeExcludePaths)
        collectDir.relativeExcludePaths.append("more")
        self.assertEqual(["bogus", "stuff", "more"], collectDir.relativeExcludePaths)

    def testConstructor_029(self):
        """
        Test assignment of excludePatterns attribute, None value.
        """
        collectDir = CollectDir(excludePatterns=[])
        self.assertEqual([], collectDir.excludePatterns)
        collectDir.excludePatterns = None
        self.assertEqual(None, collectDir.excludePatterns)

    def testConstructor_030(self):
        """
        Test assignment of excludePatterns attribute, [] value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        collectDir.excludePatterns = []
        self.assertEqual([], collectDir.excludePatterns)

    def testConstructor_031(self):
        """
        Test assignment of excludePatterns attribute, single valid entry.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        collectDir.excludePatterns = [
            "valid",
        ]
        self.assertEqual(["valid"], collectDir.excludePatterns)
        collectDir.excludePatterns.append("more")
        self.assertEqual(["valid", "more"], collectDir.excludePatterns)

    def testConstructor_032(self):
        """
        Test assignment of excludePatterns attribute, multiple valid entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        collectDir.excludePatterns = [
            "valid",
            "more",
        ]
        self.assertEqual(["valid", "more"], collectDir.excludePatterns)
        collectDir.excludePatterns.insert(1, "bogus")
        self.assertEqual(["valid", "bogus", "more"], collectDir.excludePatterns)

    def testConstructor_033(self):
        """
        Test assignment of excludePatterns attribute, single invalid entry.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collectDir, "excludePatterns", ["*.jpg"])
        self.assertEqual(None, collectDir.excludePatterns)

    def testConstructor_034(self):
        """
        Test assignment of excludePatterns attribute, multiple invalid entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collectDir, "excludePatterns", ["*.jpg", "*"])
        self.assertEqual(None, collectDir.excludePatterns)

    def testConstructor_035(self):
        """
        Test assignment of excludePatterns attribute, mixed valid and invalid
        entries.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collectDir, "excludePatterns", ["*.jpg", "valid"])
        self.assertEqual(None, collectDir.excludePatterns)

    def testConstructor_036(self):
        """
        Test assignment of linkDepth attribute, None value.
        """
        collectDir = CollectDir(linkDepth=1)
        self.assertEqual(1, collectDir.linkDepth)
        collectDir.linkDepth = None
        self.assertEqual(None, collectDir.linkDepth)

    def testConstructor_037(self):
        """
        Test assignment of linkDepth attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.linkDepth)
        collectDir.linkDepth = 1
        self.assertEqual(1, collectDir.linkDepth)

    def testConstructor_038(self):
        """
        Test assignment of linkDepth attribute, invalid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.linkDepth)
        self.failUnlessAssignRaises(ValueError, collectDir, "linkDepth", "ken")
        self.assertEqual(None, collectDir.linkDepth)

    def testConstructor_039(self):
        """
        Test assignment of dereference attribute, None value.
        """
        collectDir = CollectDir(dereference=True)
        self.assertEqual(True, collectDir.dereference)
        collectDir.dereference = None
        self.assertEqual(False, collectDir.dereference)

    def testConstructor_040(self):
        """
        Test assignment of dereference attribute, valid value (real boolean).
        """
        collectDir = CollectDir()
        self.assertEqual(False, collectDir.dereference)
        collectDir.dereference = True
        self.assertEqual(True, collectDir.dereference)
        collectDir.dereference = False
        self.assertEqual(False, collectDir.dereference)

    def testConstructor_041(self):
        """
        Test assignment of dereference attribute, valid value (expression).
        """
        collectDir = CollectDir()
        self.assertEqual(False, collectDir.dereference)
        collectDir.dereference = 0
        self.assertEqual(False, collectDir.dereference)
        collectDir.dereference = []
        self.assertEqual(False, collectDir.dereference)
        collectDir.dereference = None
        self.assertEqual(False, collectDir.dereference)
        collectDir.dereference = ["a"]
        self.assertEqual(True, collectDir.dereference)
        collectDir.dereference = 3
        self.assertEqual(True, collectDir.dereference)

    def testConstructor_042(self):
        """
        Test assignment of recursionLevel attribute, None value.
        """
        collectDir = CollectDir(recursionLevel=1)
        self.assertEqual(1, collectDir.recursionLevel)
        collectDir.recursionLevel = None
        self.assertEqual(None, collectDir.recursionLevel)

    def testConstructor_043(self):
        """
        Test assignment of recursionLevel attribute, valid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.recursionLevel)
        collectDir.recursionLevel = 1
        self.assertEqual(1, collectDir.recursionLevel)

    def testConstructor_044(self):
        """
        Test assignment of recursionLevel attribute, invalid value.
        """
        collectDir = CollectDir()
        self.assertEqual(None, collectDir.recursionLevel)
        self.failUnlessAssignRaises(ValueError, collectDir, "recursionLevel", "ken")
        self.assertEqual(None, collectDir.recursionLevel)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir()
        self.assertEqual(collectDir1, collectDir2)
        self.assertTrue(collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(not collectDir1 != collectDir2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None (empty
        lists).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertTrue(collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(not collectDir1 != collectDir2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None
        (non-empty lists).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", ["/one"], ["two"], ["three"], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", ["/one"], ["two"], ["three"], 1, True, 6)
        self.assertTrue(collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(not collectDir1 != collectDir2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, absolutePath differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(absolutePath="/whatever")
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, absolutePath differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/stuff", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(collectMode="incr")
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "daily", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, archiveMode differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(archiveMode="tar")
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, archiveMode differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "targz", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, ignoreFile differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(ignoreFile="ignore")
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, ignoreFile differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one None, one empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(absoluteExcludePaths=[])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one None, one not empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(absoluteExcludePaths=["/whatever"])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one empty, one not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", ["/whatever"], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (both not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", ["/stuff"], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", ["/stuff", "/something"], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)  # note: different than standard due to unsorted list
        self.assertTrue(not collectDir1 <= collectDir2)  # note: different than standard due to unsorted list
        self.assertTrue(collectDir1 > collectDir2)  # note: different than standard due to unsorted list
        self.assertTrue(collectDir1 >= collectDir2)  # note: different than standard due to unsorted list
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one None, one empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(relativeExcludePaths=[])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one None, one not empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(relativeExcludePaths=["stuff", "other"])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one empty, one not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], ["one"], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (both not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], ["one"], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], ["two"], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_020(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(excludePatterns=[])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_021(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one not empty).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(excludePatterns=["one", "two", "three"])
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_022(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        empty, one not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], ["pattern"], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_023(self):
        """
        Test comparison of two differing objects, excludePatterns differs (both
        not empty).
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], ["p1"], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", ".ignore", [], [], ["p2"], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_024(self):
        """
        Test comparison of two differing objects, linkDepth differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(linkDepth=1)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_025(self):
        """
        Test comparison of two differing objects, linkDepth differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 2, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, True, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_026(self):
        """
        Test comparison of two differing objects, dereference differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(dereference=True)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_027(self):
        """
        Test comparison of two differing objects, dereference differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, False, 6)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_028(self):
        """
        Test comparison of two differing objects, recursionLevel differs (one None).
        """
        collectDir1 = CollectDir()
        collectDir2 = CollectDir(recursionLevel=1)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(collectDir1 < collectDir2)
        self.assertTrue(collectDir1 <= collectDir2)
        self.assertTrue(not collectDir1 > collectDir2)
        self.assertTrue(not collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)

    def testComparison_029(self):
        """
        Test comparison of two differing objects, recursionLevel differs.
        """
        collectDir1 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, True, 6)
        collectDir2 = CollectDir("/etc/whatever", "incr", "tar", "ignore", [], [], [], 1, True, 5)
        self.assertNotEqual(collectDir1, collectDir2)
        self.assertTrue(not collectDir1 == collectDir2)
        self.assertTrue(not collectDir1 < collectDir2)
        self.assertTrue(not collectDir1 <= collectDir2)
        self.assertTrue(collectDir1 > collectDir2)
        self.assertTrue(collectDir1 >= collectDir2)
        self.assertTrue(collectDir1 != collectDir2)


#####################
# TestPurgeDir class
#####################


class TestPurgeDir(unittest.TestCase):

    """Tests for the PurgeDir class."""

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
        obj = PurgeDir()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.absolutePath)
        self.assertEqual(None, purgeDir.retainDays)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        purgeDir = PurgeDir("/whatever", 0)
        self.assertEqual("/whatever", purgeDir.absolutePath)
        self.assertEqual(0, purgeDir.retainDays)

    def testConstructor_003(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        purgeDir = PurgeDir(absolutePath="/whatever")
        self.assertEqual("/whatever", purgeDir.absolutePath)
        purgeDir.absolutePath = None
        self.assertEqual(None, purgeDir.absolutePath)

    def testConstructor_004(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.absolutePath)
        purgeDir.absolutePath = "/etc/whatever"
        self.assertEqual("/etc/whatever", purgeDir.absolutePath)

    def testConstructor_005(self):
        """
        Test assignment of absolutePath attribute, invalid value (empty).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, purgeDir, "absolutePath", "")
        self.assertEqual(None, purgeDir.absolutePath)

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, invalid value (non-absolute).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, purgeDir, "absolutePath", "bogus")
        self.assertEqual(None, purgeDir.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of retainDays attribute, None value.
        """
        purgeDir = PurgeDir(retainDays=12)
        self.assertEqual(12, purgeDir.retainDays)
        purgeDir.retainDays = None
        self.assertEqual(None, purgeDir.retainDays)

    def testConstructor_008(self):
        """
        Test assignment of retainDays attribute, valid value (integer).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.retainDays)
        purgeDir.retainDays = 12
        self.assertEqual(12, purgeDir.retainDays)

    def testConstructor_009(self):
        """
        Test assignment of retainDays attribute, valid value (string representing integer).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.retainDays)
        purgeDir.retainDays = "12"
        self.assertEqual(12, purgeDir.retainDays)

    def testConstructor_010(self):
        """
        Test assignment of retainDays attribute, invalid value (empty string).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.retainDays)
        self.failUnlessAssignRaises(ValueError, purgeDir, "retainDays", "")
        self.assertEqual(None, purgeDir.retainDays)

    def testConstructor_011(self):
        """
        Test assignment of retainDays attribute, invalid value (non-integer, like a list).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.retainDays)
        self.failUnlessAssignRaises(ValueError, purgeDir, "retainDays", [])
        self.assertEqual(None, purgeDir.retainDays)

    def testConstructor_012(self):
        """
        Test assignment of retainDays attribute, invalid value (string representing non-integer).
        """
        purgeDir = PurgeDir()
        self.assertEqual(None, purgeDir.retainDays)
        self.failUnlessAssignRaises(ValueError, purgeDir, "retainDays", "blech")
        self.assertEqual(None, purgeDir.retainDays)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        purgeDir1 = PurgeDir()
        purgeDir2 = PurgeDir()
        self.assertEqual(purgeDir1, purgeDir2)
        self.assertTrue(purgeDir1 == purgeDir2)
        self.assertTrue(not purgeDir1 < purgeDir2)
        self.assertTrue(purgeDir1 <= purgeDir2)
        self.assertTrue(not purgeDir1 > purgeDir2)
        self.assertTrue(purgeDir1 >= purgeDir2)
        self.assertTrue(not purgeDir1 != purgeDir2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        purgeDir1 = PurgeDir("/etc/whatever", 12)
        purgeDir2 = PurgeDir("/etc/whatever", 12)
        self.assertTrue(purgeDir1 == purgeDir2)
        self.assertTrue(not purgeDir1 < purgeDir2)
        self.assertTrue(purgeDir1 <= purgeDir2)
        self.assertTrue(not purgeDir1 > purgeDir2)
        self.assertTrue(purgeDir1 >= purgeDir2)
        self.assertTrue(not purgeDir1 != purgeDir2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, absolutePath differs (one None).
        """
        purgeDir1 = PurgeDir()
        purgeDir2 = PurgeDir(absolutePath="/whatever")
        self.assertNotEqual(purgeDir1, purgeDir2)
        self.assertTrue(not purgeDir1 == purgeDir2)
        self.assertTrue(purgeDir1 < purgeDir2)
        self.assertTrue(purgeDir1 <= purgeDir2)
        self.assertTrue(not purgeDir1 > purgeDir2)
        self.assertTrue(not purgeDir1 >= purgeDir2)
        self.assertTrue(purgeDir1 != purgeDir2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, absolutePath differs.
        """
        purgeDir1 = PurgeDir("/etc/blech", 12)
        purgeDir2 = PurgeDir("/etc/whatever", 12)
        self.assertNotEqual(purgeDir1, purgeDir2)
        self.assertTrue(not purgeDir1 == purgeDir2)
        self.assertTrue(purgeDir1 < purgeDir2)
        self.assertTrue(purgeDir1 <= purgeDir2)
        self.assertTrue(not purgeDir1 > purgeDir2)
        self.assertTrue(not purgeDir1 >= purgeDir2)
        self.assertTrue(purgeDir1 != purgeDir2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, retainDays differs (one None).
        """
        purgeDir1 = PurgeDir()
        purgeDir2 = PurgeDir(retainDays=365)
        self.assertNotEqual(purgeDir1, purgeDir2)
        self.assertTrue(not purgeDir1 == purgeDir2)
        self.assertTrue(purgeDir1 < purgeDir2)
        self.assertTrue(purgeDir1 <= purgeDir2)
        self.assertTrue(not purgeDir1 > purgeDir2)
        self.assertTrue(not purgeDir1 >= purgeDir2)
        self.assertTrue(purgeDir1 != purgeDir2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, retainDays differs.
        """
        purgeDir1 = PurgeDir("/etc/whatever", 365)
        purgeDir2 = PurgeDir("/etc/whatever", 12)
        self.assertNotEqual(purgeDir1, purgeDir2)
        self.assertTrue(not purgeDir1 == purgeDir2)
        self.assertTrue(not purgeDir1 < purgeDir2)
        self.assertTrue(not purgeDir1 <= purgeDir2)
        self.assertTrue(purgeDir1 > purgeDir2)
        self.assertTrue(purgeDir1 >= purgeDir2)
        self.assertTrue(purgeDir1 != purgeDir2)


######################
# TestLocalPeer class
######################


class TestLocalPeer(unittest.TestCase):

    """Tests for the LocalPeer class."""

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
        obj = LocalPeer()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.name)
        self.assertEqual(None, localPeer.collectDir)
        self.assertEqual(None, localPeer.ignoreFailureMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        localPeer = LocalPeer("myname", "/whatever", "all")
        self.assertEqual("myname", localPeer.name)
        self.assertEqual("/whatever", localPeer.collectDir)
        self.assertEqual("all", localPeer.ignoreFailureMode)

    def testConstructor_003(self):
        """
        Test assignment of name attribute, None value.
        """
        localPeer = LocalPeer(name="myname")
        self.assertEqual("myname", localPeer.name)
        localPeer.name = None
        self.assertEqual(None, localPeer.name)

    def testConstructor_004(self):
        """
        Test assignment of name attribute, valid value.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.name)
        localPeer.name = "myname"
        self.assertEqual("myname", localPeer.name)

    def testConstructor_005(self):
        """
        Test assignment of name attribute, invalid value (empty).
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.name)
        self.failUnlessAssignRaises(ValueError, localPeer, "name", "")
        self.assertEqual(None, localPeer.name)

    def testConstructor_006(self):
        """
        Test assignment of collectDir attribute, None value.
        """
        localPeer = LocalPeer(collectDir="/whatever")
        self.assertEqual("/whatever", localPeer.collectDir)
        localPeer.collectDir = None
        self.assertEqual(None, localPeer.collectDir)

    def testConstructor_007(self):
        """
        Test assignment of collectDir attribute, valid value.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.collectDir)
        localPeer.collectDir = "/etc/stuff"
        self.assertEqual("/etc/stuff", localPeer.collectDir)

    def testConstructor_008(self):
        """
        Test assignment of collectDir attribute, invalid value (empty).
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.collectDir)
        self.failUnlessAssignRaises(ValueError, localPeer, "collectDir", "")
        self.assertEqual(None, localPeer.collectDir)

    def testConstructor_009(self):
        """
        Test assignment of collectDir attribute, invalid value (non-absolute).
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.collectDir)
        self.failUnlessAssignRaises(ValueError, localPeer, "collectDir", "bogus")
        self.assertEqual(None, localPeer.collectDir)

    def testConstructor_010(self):
        """
        Test assignment of ignoreFailureMode attribute, valid values.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.ignoreFailureMode)
        localPeer.ignoreFailureMode = "none"
        self.assertEqual("none", localPeer.ignoreFailureMode)
        localPeer.ignoreFailureMode = "all"
        self.assertEqual("all", localPeer.ignoreFailureMode)
        localPeer.ignoreFailureMode = "daily"
        self.assertEqual("daily", localPeer.ignoreFailureMode)
        localPeer.ignoreFailureMode = "weekly"
        self.assertEqual("weekly", localPeer.ignoreFailureMode)

    def testConstructor_011(self):
        """
        Test assignment of ignoreFailureMode attribute, invalid value.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.ignoreFailureMode)
        self.failUnlessAssignRaises(ValueError, localPeer, "ignoreFailureMode", "bogus")

    def testConstructor_012(self):
        """
        Test assignment of ignoreFailureMode attribute, None value.
        """
        localPeer = LocalPeer()
        self.assertEqual(None, localPeer.ignoreFailureMode)
        localPeer.ignoreFailureMode = None
        self.assertEqual(None, localPeer.ignoreFailureMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        localPeer1 = LocalPeer()
        localPeer2 = LocalPeer()
        self.assertEqual(localPeer1, localPeer2)
        self.assertTrue(localPeer1 == localPeer2)
        self.assertTrue(not localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(localPeer1 >= localPeer2)
        self.assertTrue(not localPeer1 != localPeer2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        localPeer1 = LocalPeer("myname", "/etc/stuff", "all")
        localPeer2 = LocalPeer("myname", "/etc/stuff", "all")
        self.assertTrue(localPeer1 == localPeer2)
        self.assertTrue(not localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(localPeer1 >= localPeer2)
        self.assertTrue(not localPeer1 != localPeer2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, name differs (one None).
        """
        localPeer1 = LocalPeer()
        localPeer2 = LocalPeer(name="blech")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(not localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, name differs.
        """
        localPeer1 = LocalPeer("name", "/etc/stuff", "all")
        localPeer2 = LocalPeer("name", "/etc/whatever", "all")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(not localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectDir differs (one None).
        """
        localPeer1 = LocalPeer()
        localPeer2 = LocalPeer(collectDir="/etc/whatever")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(not localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectDir differs.
        """
        localPeer1 = LocalPeer("name2", "/etc/stuff", "all")
        localPeer2 = LocalPeer("name1", "/etc/stuff", "all")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(not localPeer1 < localPeer2)
        self.assertTrue(not localPeer1 <= localPeer2)
        self.assertTrue(localPeer1 > localPeer2)
        self.assertTrue(localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, ignoreFailureMode differs (one None).
        """
        localPeer1 = LocalPeer()
        localPeer2 = LocalPeer(ignoreFailureMode="all")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(localPeer1 < localPeer2)
        self.assertTrue(localPeer1 <= localPeer2)
        self.assertTrue(not localPeer1 > localPeer2)
        self.assertTrue(not localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, collectDir differs.
        """
        localPeer1 = LocalPeer("name1", "/etc/stuff", "none")
        localPeer2 = LocalPeer("name1", "/etc/stuff", "all")
        self.assertNotEqual(localPeer1, localPeer2)
        self.assertTrue(not localPeer1 == localPeer2)
        self.assertTrue(not localPeer1 < localPeer2)
        self.assertTrue(not localPeer1 <= localPeer2)
        self.assertTrue(localPeer1 > localPeer2)
        self.assertTrue(localPeer1 >= localPeer2)
        self.assertTrue(localPeer1 != localPeer2)


#######################
# TestRemotePeer class
#######################


class TestRemotePeer(unittest.TestCase):

    """Tests for the RemotePeer class."""

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
        obj = RemotePeer()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.name)
        self.assertEqual(None, remotePeer.collectDir)
        self.assertEqual(None, remotePeer.remoteUser)
        self.assertEqual(None, remotePeer.rcpCommand)
        self.assertEqual(None, remotePeer.rshCommand)
        self.assertEqual(None, remotePeer.cbackCommand)
        self.assertEqual(False, remotePeer.managed)
        self.assertEqual(None, remotePeer.managedActions)
        self.assertEqual(None, remotePeer.ignoreFailureMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        remotePeer = RemotePeer("myname", "/stuff", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertEqual("myname", remotePeer.name)
        self.assertEqual("/stuff", remotePeer.collectDir)
        self.assertEqual("backup", remotePeer.remoteUser)
        self.assertEqual("scp -1 -B", remotePeer.rcpCommand)
        self.assertEqual("ssh", remotePeer.rshCommand)
        self.assertEqual("cback", remotePeer.cbackCommand)
        self.assertEqual(True, remotePeer.managed)
        self.assertEqual(["collect"], remotePeer.managedActions)
        self.assertEqual("all", remotePeer.ignoreFailureMode)

    def testConstructor_003(self):
        """
        Test assignment of name attribute, None value.
        """
        remotePeer = RemotePeer(name="myname")
        self.assertEqual("myname", remotePeer.name)
        remotePeer.name = None
        self.assertEqual(None, remotePeer.name)

    def testConstructor_004(self):
        """
        Test assignment of name attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.name)
        remotePeer.name = "namename"
        self.assertEqual("namename", remotePeer.name)

    def testConstructor_005(self):
        """
        Test assignment of name attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.name)
        self.failUnlessAssignRaises(ValueError, remotePeer, "name", "")
        self.assertEqual(None, remotePeer.name)

    def testConstructor_006(self):
        """
        Test assignment of collectDir attribute, None value.
        """
        remotePeer = RemotePeer(collectDir="/etc/stuff")
        self.assertEqual("/etc/stuff", remotePeer.collectDir)
        remotePeer.collectDir = None
        self.assertEqual(None, remotePeer.collectDir)

    def testConstructor_007(self):
        """
        Test assignment of collectDir attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.collectDir)
        remotePeer.collectDir = "/tmp"
        self.assertEqual("/tmp", remotePeer.collectDir)

    def testConstructor_008(self):
        """
        Test assignment of collectDir attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.collectDir)
        self.failUnlessAssignRaises(ValueError, remotePeer, "collectDir", "")
        self.assertEqual(None, remotePeer.collectDir)

    def testConstructor_009(self):
        """
        Test assignment of collectDir attribute, invalid value (non-absolute).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.collectDir)
        self.failUnlessAssignRaises(ValueError, remotePeer, "collectDir", "bogus/stuff/there")
        self.assertEqual(None, remotePeer.collectDir)

    def testConstructor_010(self):
        """
        Test assignment of remoteUser attribute, None value.
        """
        remotePeer = RemotePeer(remoteUser="spot")
        self.assertEqual("spot", remotePeer.remoteUser)
        remotePeer.remoteUser = None
        self.assertEqual(None, remotePeer.remoteUser)

    def testConstructor_011(self):
        """
        Test assignment of remoteUser attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.remoteUser)
        remotePeer.remoteUser = "spot"
        self.assertEqual("spot", remotePeer.remoteUser)

    def testConstructor_012(self):
        """
        Test assignment of remoteUser attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.remoteUser)
        self.failUnlessAssignRaises(ValueError, remotePeer, "remoteUser", "")
        self.assertEqual(None, remotePeer.remoteUser)

    def testConstructor_013(self):
        """
        Test assignment of rcpCommand attribute, None value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.rcpCommand)
        remotePeer.rcpCommand = "scp"
        self.assertEqual("scp", remotePeer.rcpCommand)

    def testConstructor_014(self):
        """
        Test assignment of rcpCommand attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.rcpCommand)
        remotePeer.rcpCommand = "scp"
        self.assertEqual("scp", remotePeer.rcpCommand)

    def testConstructor_015(self):
        """
        Test assignment of rcpCommand attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.rcpCommand)
        self.failUnlessAssignRaises(ValueError, remotePeer, "rcpCommand", "")
        self.assertEqual(None, remotePeer.rcpCommand)

    def testConstructor_016(self):
        """
        Test assignment of rshCommand attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.rshCommand)
        remotePeer.rshCommand = "scp"
        self.assertEqual("scp", remotePeer.rshCommand)

    def testConstructor_017(self):
        """
        Test assignment of rshCommand attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.rshCommand)
        self.failUnlessAssignRaises(ValueError, remotePeer, "rshCommand", "")
        self.assertEqual(None, remotePeer.rshCommand)

    def testConstructor_018(self):
        """
        Test assignment of cbackCommand attribute, valid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.cbackCommand)
        remotePeer.cbackCommand = "scp"
        self.assertEqual("scp", remotePeer.cbackCommand)

    def testConstructor_019(self):
        """
        Test assignment of cbackCommand attribute, invalid value (empty).
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.cbackCommand)
        self.failUnlessAssignRaises(ValueError, remotePeer, "cbackCommand", "")
        self.assertEqual(None, remotePeer.cbackCommand)

    def testConstructor_021(self):
        """
        Test assignment of managed attribute, None value.
        """
        remotePeer = RemotePeer(managed=True)
        self.assertEqual(True, remotePeer.managed)
        remotePeer.managed = None
        self.assertEqual(False, remotePeer.managed)

    def testConstructor_022(self):
        """
        Test assignment of managed attribute, valid value (real boolean).
        """
        remotePeer = RemotePeer()
        self.assertEqual(False, remotePeer.managed)
        remotePeer.managed = True
        self.assertEqual(True, remotePeer.managed)
        remotePeer.managed = False
        self.assertEqual(False, remotePeer.managed)

    def testConstructor_023(self):
        """
        Test assignment of managed attribute, valid value (expression).
        """
        remotePeer = RemotePeer()
        self.assertEqual(False, remotePeer.managed)
        remotePeer.managed = 0
        self.assertEqual(False, remotePeer.managed)
        remotePeer.managed = []
        self.assertEqual(False, remotePeer.managed)
        remotePeer.managed = None
        self.assertEqual(False, remotePeer.managed)
        remotePeer.managed = ["a"]
        self.assertEqual(True, remotePeer.managed)
        remotePeer.managed = 3
        self.assertEqual(True, remotePeer.managed)

    def testConstructor_024(self):
        """
        Test assignment of managedActions attribute, None value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.managedActions)
        remotePeer.managedActions = None
        self.assertEqual(None, remotePeer.managedActions)

    def testConstructor_025(self):
        """
        Test assignment of managedActions attribute, empty list.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.managedActions)
        remotePeer.managedActions = []
        self.assertEqual([], remotePeer.managedActions)

    def testConstructor_026(self):
        """
        Test assignment of managedActions attribute, non-empty list, valid values.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.managedActions)
        remotePeer.managedActions = [
            "a",
            "b",
        ]
        self.assertEqual(["a", "b"], remotePeer.managedActions)

    def testConstructor_027(self):
        """
        Test assignment of managedActions attribute, non-empty list, invalid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", ["KEN"])
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", ["hello, world"])
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", ["dash-word"])
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", [""])
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", [None])
        self.assertEqual(None, remotePeer.managedActions)

    def testConstructor_028(self):
        """
        Test assignment of managedActions attribute, non-empty list, mixed values.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.managedActions)
        self.failUnlessAssignRaises(ValueError, remotePeer, "managedActions", ["ken", "dash-word"])

    def testConstructor_029(self):
        """
        Test assignment of ignoreFailureMode attribute, valid values.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.ignoreFailureMode)
        remotePeer.ignoreFailureMode = "none"
        self.assertEqual("none", remotePeer.ignoreFailureMode)
        remotePeer.ignoreFailureMode = "all"
        self.assertEqual("all", remotePeer.ignoreFailureMode)
        remotePeer.ignoreFailureMode = "daily"
        self.assertEqual("daily", remotePeer.ignoreFailureMode)
        remotePeer.ignoreFailureMode = "weekly"
        self.assertEqual("weekly", remotePeer.ignoreFailureMode)

    def testConstructor_030(self):
        """
        Test assignment of ignoreFailureMode attribute, invalid value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.ignoreFailureMode)
        self.failUnlessAssignRaises(ValueError, remotePeer, "ignoreFailureMode", "bogus")

    def testConstructor_031(self):
        """
        Test assignment of ignoreFailureMode attribute, None value.
        """
        remotePeer = RemotePeer()
        self.assertEqual(None, remotePeer.ignoreFailureMode)
        remotePeer.ignoreFailureMode = None
        self.assertEqual(None, remotePeer.ignoreFailureMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer()
        self.assertEqual(remotePeer1, remotePeer2)
        self.assertTrue(remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(not remotePeer1 != remotePeer2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertTrue(remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(not remotePeer1 != remotePeer2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, name differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(name="name")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, name differs.
        """
        remotePeer1 = RemotePeer("name1", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name2", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectDir differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(collectDir="/tmp")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectDir differs.
        """
        remotePeer1 = RemotePeer("name", "/etc", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, remoteUser differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(remoteUser="spot")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, remoteUser differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "spot", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(not remotePeer1 <= remotePeer2)
        self.assertTrue(remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, rcpCommand differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(rcpCommand="scp")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, rcpCommand differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -2 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(not remotePeer1 <= remotePeer2)
        self.assertTrue(remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, rshCommand differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(rshCommand="ssh")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, rshCommand differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh2", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh1", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(not remotePeer1 <= remotePeer2)
        self.assertTrue(remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, cbackCommand differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(cbackCommand="cback")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, cbackCommand differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback2", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback1", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(not remotePeer1 <= remotePeer2)
        self.assertTrue(remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, managed differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(managed=True)
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, managed differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", False, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        None, one empty).
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, None, "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, [], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        None, one not empty).
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, None, "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        empty, one not empty).
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, [], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_020(self):
        """
        Test comparison of two differing objects, managedActions differs (both
        not empty).
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["purge"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(not remotePeer1 < remotePeer2)
        self.assertTrue(not remotePeer1 <= remotePeer2)
        self.assertTrue(remotePeer1 > remotePeer2)
        self.assertTrue(remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_021(self):
        """
        Test comparison of two differing objects, ignoreFailureMode differs (one None).
        """
        remotePeer1 = RemotePeer()
        remotePeer2 = RemotePeer(ignoreFailureMode="all")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)

    def testComparison_022(self):
        """
        Test comparison of two differing objects, ignoreFailureMode differs.
        """
        remotePeer1 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "all")
        remotePeer2 = RemotePeer("name", "/etc/stuff/tmp/X11", "backup", "scp -1 -B", "ssh", "cback", True, ["collect"], "none")
        self.assertNotEqual(remotePeer1, remotePeer2)
        self.assertTrue(not remotePeer1 == remotePeer2)
        self.assertTrue(remotePeer1 < remotePeer2)
        self.assertTrue(remotePeer1 <= remotePeer2)
        self.assertTrue(not remotePeer1 > remotePeer2)
        self.assertTrue(not remotePeer1 >= remotePeer2)
        self.assertTrue(remotePeer1 != remotePeer2)


############################
# TestReferenceConfig class
############################


class TestReferenceConfig(unittest.TestCase):

    """Tests for the ReferenceConfig class."""

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
        obj = ReferenceConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.author)
        self.assertEqual(None, reference.revision)
        self.assertEqual(None, reference.description)
        self.assertEqual(None, reference.generator)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        reference = ReferenceConfig("one", "two", "three", "four")
        self.assertEqual("one", reference.author)
        self.assertEqual("two", reference.revision)
        self.assertEqual("three", reference.description)
        self.assertEqual("four", reference.generator)

    def testConstructor_003(self):
        """
        Test assignment of author attribute, None value.
        """
        reference = ReferenceConfig(author="one")
        self.assertEqual("one", reference.author)
        reference.author = None
        self.assertEqual(None, reference.author)

    def testConstructor_004(self):
        """
        Test assignment of author attribute, valid value.
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.author)
        reference.author = "one"
        self.assertEqual("one", reference.author)

    def testConstructor_005(self):
        """
        Test assignment of author attribute, valid value (empty).
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.author)
        reference.author = ""
        self.assertEqual("", reference.author)

    def testConstructor_006(self):
        """
        Test assignment of revision attribute, None value.
        """
        reference = ReferenceConfig(revision="one")
        self.assertEqual("one", reference.revision)
        reference.revision = None
        self.assertEqual(None, reference.revision)

    def testConstructor_007(self):
        """
        Test assignment of revision attribute, valid value.
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.revision)
        reference.revision = "one"
        self.assertEqual("one", reference.revision)

    def testConstructor_008(self):
        """
        Test assignment of revision attribute, valid value (empty).
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.revision)
        reference.revision = ""
        self.assertEqual("", reference.revision)

    def testConstructor_009(self):
        """
        Test assignment of description attribute, None value.
        """
        reference = ReferenceConfig(description="one")
        self.assertEqual("one", reference.description)
        reference.description = None
        self.assertEqual(None, reference.description)

    def testConstructor_010(self):
        """
        Test assignment of description attribute, valid value.
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.description)
        reference.description = "one"
        self.assertEqual("one", reference.description)

    def testConstructor_011(self):
        """
        Test assignment of description attribute, valid value (empty).
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.description)
        reference.description = ""
        self.assertEqual("", reference.description)

    def testConstructor_012(self):
        """
        Test assignment of generator attribute, None value.
        """
        reference = ReferenceConfig(generator="one")
        self.assertEqual("one", reference.generator)
        reference.generator = None
        self.assertEqual(None, reference.generator)

    def testConstructor_013(self):
        """
        Test assignment of generator attribute, valid value.
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.generator)
        reference.generator = "one"
        self.assertEqual("one", reference.generator)

    def testConstructor_014(self):
        """
        Test assignment of generator attribute, valid value (empty).
        """
        reference = ReferenceConfig()
        self.assertEqual(None, reference.generator)
        reference.generator = ""
        self.assertEqual("", reference.generator)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        reference1 = ReferenceConfig()
        reference2 = ReferenceConfig()
        self.assertEqual(reference1, reference2)
        self.assertTrue(reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(not reference1 != reference2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("one", "two", "three", "four")
        self.assertTrue(reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(not reference1 != reference2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, author differs (one None).
        """
        reference1 = ReferenceConfig()
        reference2 = ReferenceConfig(author="one")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, author differs (one empty).
        """
        reference1 = ReferenceConfig("", "two", "three", "four")
        reference2 = ReferenceConfig("one", "two", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, author differs.
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("author", "two", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(not reference1 <= reference2)
        self.assertTrue(reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, revision differs (one None).
        """
        reference1 = ReferenceConfig()
        reference2 = ReferenceConfig(revision="one")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, revision differs (one empty).
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("one", "", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(not reference1 <= reference2)
        self.assertTrue(reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, revision differs.
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("one", "revision", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(not reference1 <= reference2)
        self.assertTrue(reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, description differs (one None).
        """
        reference1 = ReferenceConfig()
        reference2 = ReferenceConfig(description="one")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, description differs (one empty).
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("one", "two", "", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(not reference1 < reference2)
        self.assertTrue(not reference1 <= reference2)
        self.assertTrue(reference1 > reference2)
        self.assertTrue(reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, description differs.
        """
        reference1 = ReferenceConfig("one", "two", "description", "four")
        reference2 = ReferenceConfig("one", "two", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, generator differs (one None).
        """
        reference1 = ReferenceConfig()
        reference2 = ReferenceConfig(generator="one")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, generator differs (one empty).
        """
        reference1 = ReferenceConfig("one", "two", "three", "")
        reference2 = ReferenceConfig("one", "two", "three", "four")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, generator differs.
        """
        reference1 = ReferenceConfig("one", "two", "three", "four")
        reference2 = ReferenceConfig("one", "two", "three", "generator")
        self.assertNotEqual(reference1, reference2)
        self.assertTrue(not reference1 == reference2)
        self.assertTrue(reference1 < reference2)
        self.assertTrue(reference1 <= reference2)
        self.assertTrue(not reference1 > reference2)
        self.assertTrue(not reference1 >= reference2)
        self.assertTrue(reference1 != reference2)


#############################
# TestExtensionsConfig class
#############################


class TestExtensionsConfig(unittest.TestCase):

    """Tests for the ExtensionsConfig class."""

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
        obj = ExtensionsConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (empty list), positional arguments.
        """
        extensions = ExtensionsConfig([], None)
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual([], extensions.actions)
        extensions = ExtensionsConfig([], "index")
        self.assertEqual("index", extensions.orderMode)
        self.assertEqual([], extensions.actions)
        extensions = ExtensionsConfig([], "dependency")
        self.assertEqual("dependency", extensions.orderMode)
        self.assertEqual([], extensions.actions)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values (non-empty list), named arguments.
        """
        extensions = ExtensionsConfig(orderMode=None, actions=[ExtendedAction()])
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual([ExtendedAction()], extensions.actions)
        extensions = ExtensionsConfig(orderMode="index", actions=[ExtendedAction()])
        self.assertEqual("index", extensions.orderMode)
        self.assertEqual([ExtendedAction()], extensions.actions)
        extensions = ExtensionsConfig(orderMode="dependency", actions=[ExtendedAction()])
        self.assertEqual("dependency", extensions.orderMode)
        self.assertEqual([ExtendedAction()], extensions.actions)

    def testConstructor_004(self):
        """
        Test assignment of actions attribute, None value.
        """
        extensions = ExtensionsConfig([])
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual([], extensions.actions)
        extensions.actions = None
        self.assertEqual(None, extensions.actions)

    def testConstructor_005(self):
        """
        Test assignment of actions attribute, [] value.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        extensions.actions = []
        self.assertEqual([], extensions.actions)

    def testConstructor_006(self):
        """
        Test assignment of actions attribute, single valid entry.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        extensions.actions = [
            ExtendedAction(),
        ]
        self.assertEqual([ExtendedAction()], extensions.actions)

    def testConstructor_007(self):
        """
        Test assignment of actions attribute, multiple valid entries.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        extensions.actions = [
            ExtendedAction("a", "b", "c", 1),
            ExtendedAction("d", "e", "f", 2),
        ]
        self.assertEqual([ExtendedAction("a", "b", "c", 1), ExtendedAction("d", "e", "f", 2)], extensions.actions)

    def testConstructor_009(self):
        """
        Test assignment of actions attribute, single invalid entry (not an
        ExtendedAction).
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        self.failUnlessAssignRaises(ValueError, extensions, "actions", [RemotePeer()])
        self.assertEqual(None, extensions.actions)

    def testConstructor_010(self):
        """
        Test assignment of actions attribute, mixed valid and invalid entries.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        self.failUnlessAssignRaises(ValueError, extensions, "actions", [ExtendedAction(), RemotePeer()])
        self.assertEqual(None, extensions.actions)

    def testConstructor_011(self):
        """
        Test assignment of orderMode attribute, None value.
        """
        extensions = ExtensionsConfig(orderMode="index")
        self.assertEqual("index", extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        extensions.orderMode = None
        self.assertEqual(None, extensions.orderMode)

    def testConstructor_012(self):
        """
        Test assignment of orderMode attribute, valid values.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        extensions.orderMode = "index"
        self.assertEqual("index", extensions.orderMode)
        extensions.orderMode = "dependency"
        self.assertEqual("dependency", extensions.orderMode)

    def testConstructor_013(self):
        """
        Test assignment of orderMode attribute, invalid values.
        """
        extensions = ExtensionsConfig()
        self.assertEqual(None, extensions.orderMode)
        self.assertEqual(None, extensions.actions)
        self.failUnlessAssignRaises(ValueError, extensions, "orderMode", "")
        self.failUnlessAssignRaises(ValueError, extensions, "orderMode", "bogus")
        self.failUnlessAssignRaises(ValueError, extensions, "orderMode", "indexes")
        self.failUnlessAssignRaises(ValueError, extensions, "orderMode", "indices")
        self.failUnlessAssignRaises(ValueError, extensions, "orderMode", "dependencies")

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        extensions1 = ExtensionsConfig()
        extensions2 = ExtensionsConfig()
        self.assertEqual(extensions1, extensions2)
        self.assertTrue(extensions1 == extensions2)
        self.assertTrue(not extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(extensions1 >= extensions2)
        self.assertTrue(not extensions1 != extensions2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None (empty
        lists).
        """
        extensions1 = ExtensionsConfig([], "index")
        extensions2 = ExtensionsConfig([], "index")
        self.assertEqual(extensions1, extensions2)
        self.assertTrue(extensions1 == extensions2)
        self.assertTrue(not extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(extensions1 >= extensions2)
        self.assertTrue(not extensions1 != extensions2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None
        (non-empty lists).
        """
        extensions1 = ExtensionsConfig([ExtendedAction()], "index")
        extensions2 = ExtensionsConfig([ExtendedAction()], "index")
        self.assertEqual(extensions1, extensions2)
        self.assertTrue(extensions1 == extensions2)
        self.assertTrue(not extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(extensions1 >= extensions2)
        self.assertTrue(not extensions1 != extensions2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, actions differs (one None,
        one empty).
        """
        extensions1 = ExtensionsConfig(None)
        extensions2 = ExtensionsConfig([])
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, actions differs (one None,
        one not empty).
        """
        extensions1 = ExtensionsConfig(None)
        extensions2 = ExtensionsConfig([ExtendedAction()])
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, actions differs (one empty,
        one not empty).
        """
        extensions1 = ExtensionsConfig([])
        extensions2 = ExtensionsConfig([ExtendedAction()])
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, actions differs (both not
        empty).
        """
        extensions1 = ExtensionsConfig([ExtendedAction(name="one")])
        extensions2 = ExtensionsConfig([ExtendedAction(name="two")])
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)

    def testComparison_008(self):
        """
        Test comparison of differing objects, orderMode differs (one None).
        """
        extensions1 = ExtensionsConfig([], None)
        extensions2 = ExtensionsConfig([], "index")
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)

    def testComparison_009(self):
        """
        Test comparison of differing objects, orderMode differs.
        """
        extensions1 = ExtensionsConfig([], "dependency")
        extensions2 = ExtensionsConfig([], "index")
        self.assertNotEqual(extensions1, extensions2)
        self.assertTrue(not extensions1 == extensions2)
        self.assertTrue(extensions1 < extensions2)
        self.assertTrue(extensions1 <= extensions2)
        self.assertTrue(not extensions1 > extensions2)
        self.assertTrue(not extensions1 >= extensions2)
        self.assertTrue(extensions1 != extensions2)


##########################
# TestOptionsConfig class
##########################


class TestOptionsConfig(unittest.TestCase):

    """Tests for the OptionsConfig class."""

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
        obj = OptionsConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.startingDay)
        self.assertEqual(None, options.workingDir)
        self.assertEqual(None, options.backupUser)
        self.assertEqual(None, options.backupGroup)
        self.assertEqual(None, options.rcpCommand)
        self.assertEqual(None, options.rshCommand)
        self.assertEqual(None, options.cbackCommand)
        self.assertEqual(None, options.overrides)
        self.assertEqual(None, options.hooks)
        self.assertEqual(None, options.managedActions)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (lists empty).
        """
        options = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", [], [], "ssh", "cback", [])
        self.assertEqual("monday", options.startingDay)
        self.assertEqual("/tmp", options.workingDir)
        self.assertEqual("user", options.backupUser)
        self.assertEqual("group", options.backupGroup)
        self.assertEqual("scp -1 -B", options.rcpCommand)
        self.assertEqual("ssh", options.rshCommand)
        self.assertEqual("cback", options.cbackCommand)
        self.assertEqual([], options.overrides)
        self.assertEqual([], options.hooks)
        self.assertEqual([], options.managedActions)

    def testConstructor_003(self):
        """
        Test assignment of startingDay attribute, None value.
        """
        options = OptionsConfig(startingDay="monday")
        self.assertEqual("monday", options.startingDay)
        options.startingDay = None
        self.assertEqual(None, options.startingDay)

    def testConstructor_004(self):
        """
        Test assignment of startingDay attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.startingDay)
        options.startingDay = "monday"
        self.assertEqual("monday", options.startingDay)
        options.startingDay = "tuesday"
        self.assertEqual("tuesday", options.startingDay)
        options.startingDay = "wednesday"
        self.assertEqual("wednesday", options.startingDay)
        options.startingDay = "thursday"
        self.assertEqual("thursday", options.startingDay)
        options.startingDay = "friday"
        self.assertEqual("friday", options.startingDay)
        options.startingDay = "saturday"
        self.assertEqual("saturday", options.startingDay)
        options.startingDay = "sunday"
        self.assertEqual("sunday", options.startingDay)

    def testConstructor_005(self):
        """
        Test assignment of startingDay attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.startingDay)
        self.failUnlessAssignRaises(ValueError, options, "startingDay", "")
        self.assertEqual(None, options.startingDay)

    def testConstructor_006(self):
        """
        Test assignment of startingDay attribute, invalid value (not in list).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.startingDay)
        self.failUnlessAssignRaises(ValueError, options, "startingDay", "dienstag")  # ha, ha, pretend I'm German
        self.assertEqual(None, options.startingDay)

    def testConstructor_007(self):
        """
        Test assignment of workingDir attribute, None value.
        """
        options = OptionsConfig(workingDir="/tmp")
        self.assertEqual("/tmp", options.workingDir)
        options.workingDir = None
        self.assertEqual(None, options.workingDir)

    def testConstructor_008(self):
        """
        Test assignment of workingDir attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.workingDir)
        options.workingDir = "/tmp"
        self.assertEqual("/tmp", options.workingDir)

    def testConstructor_009(self):
        """
        Test assignment of workingDir attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.workingDir)
        self.failUnlessAssignRaises(ValueError, options, "workingDir", "")
        self.assertEqual(None, options.workingDir)

    def testConstructor_010(self):
        """
        Test assignment of workingDir attribute, invalid value (non-absolute).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.workingDir)
        self.failUnlessAssignRaises(ValueError, options, "workingDir", "stuff")
        self.assertEqual(None, options.workingDir)

    def testConstructor_011(self):
        """
        Test assignment of backupUser attribute, None value.
        """
        options = OptionsConfig(backupUser="user")
        self.assertEqual("user", options.backupUser)
        options.backupUser = None
        self.assertEqual(None, options.backupUser)

    def testConstructor_012(self):
        """
        Test assignment of backupUser attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.backupUser)
        options.backupUser = "user"
        self.assertEqual("user", options.backupUser)

    def testConstructor_013(self):
        """
        Test assignment of backupUser attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.backupUser)
        self.failUnlessAssignRaises(ValueError, options, "backupUser", "")
        self.assertEqual(None, options.backupUser)

    def testConstructor_014(self):
        """
        Test assignment of backupGroup attribute, None value.
        """
        options = OptionsConfig(backupGroup="group")
        self.assertEqual("group", options.backupGroup)
        options.backupGroup = None
        self.assertEqual(None, options.backupGroup)

    def testConstructor_015(self):
        """
        Test assignment of backupGroup attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.backupGroup)
        options.backupGroup = "group"
        self.assertEqual("group", options.backupGroup)

    def testConstructor_016(self):
        """
        Test assignment of backupGroup attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.backupGroup)
        self.failUnlessAssignRaises(ValueError, options, "backupGroup", "")
        self.assertEqual(None, options.backupGroup)

    def testConstructor_017(self):
        """
        Test assignment of rcpCommand attribute, None value.
        """
        options = OptionsConfig(rcpCommand="command")
        self.assertEqual("command", options.rcpCommand)
        options.rcpCommand = None
        self.assertEqual(None, options.rcpCommand)

    def testConstructor_018(self):
        """
        Test assignment of rcpCommand attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.rcpCommand)
        options.rcpCommand = "command"
        self.assertEqual("command", options.rcpCommand)

    def testConstructor_019(self):
        """
        Test assignment of rcpCommand attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.rcpCommand)
        self.failUnlessAssignRaises(ValueError, options, "rcpCommand", "")
        self.assertEqual(None, options.rcpCommand)

    def testConstructor_020(self):
        """
        Test constructor with all values filled in, with valid values (lists not empty).
        """
        overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
        ]
        hooks = [
            PreActionHook("collect", "ls -l"),
        ]
        managedActions = [
            "collect",
            "purge",
        ]
        options = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertEqual("monday", options.startingDay)
        self.assertEqual("/tmp", options.workingDir)
        self.assertEqual("user", options.backupUser)
        self.assertEqual("group", options.backupGroup)
        self.assertEqual("scp -1 -B", options.rcpCommand)
        self.assertEqual("ssh", options.rshCommand)
        self.assertEqual("cback", options.cbackCommand)
        self.assertEqual(overrides, options.overrides)
        self.assertEqual(hooks, options.hooks)
        self.assertEqual(managedActions, options.managedActions)

    def testConstructor_021(self):
        """
        Test assignment of overrides attribute, None value.
        """
        collect = OptionsConfig(overrides=[])
        self.assertEqual([], collect.overrides)
        collect.overrides = None
        self.assertEqual(None, collect.overrides)

    def testConstructor_022(self):
        """
        Test assignment of overrides attribute, [] value.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        collect.overrides = []
        self.assertEqual([], collect.overrides)

    def testConstructor_023(self):
        """
        Test assignment of overrides attribute, single valid entry.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        collect.overrides = [
            CommandOverride("one", "/one"),
        ]
        self.assertEqual([CommandOverride("one", "/one")], collect.overrides)

    def testConstructor_024(self):
        """
        Test assignment of overrides attribute, multiple valid
        entries.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        collect.overrides = [
            CommandOverride("one", "/one"),
            CommandOverride("two", "/two"),
        ]
        self.assertEqual([CommandOverride("one", "/one"), CommandOverride("two", "/two")], collect.overrides)

    def testConstructor_025(self):
        """
        Test assignment of overrides attribute, single invalid entry
        (None).
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        self.failUnlessAssignRaises(ValueError, collect, "overrides", [None])
        self.assertEqual(None, collect.overrides)

    def testConstructor_026(self):
        """
        Test assignment of overrides attribute, single invalid entry
        (not a CommandOverride).
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        self.failUnlessAssignRaises(ValueError, collect, "overrides", ["hello"])
        self.assertEqual(None, collect.overrides)

    def testConstructor_027(self):
        """
        Test assignment of overrides attribute, mixed valid and
        invalid entries.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.overrides)
        self.failUnlessAssignRaises(ValueError, collect, "overrides", ["hello", CommandOverride("one", "/one")])
        self.assertEqual(None, collect.overrides)

    def testConstructor_028(self):
        """
        Test assignment of hooks attribute, None value.
        """
        collect = OptionsConfig(hooks=[])
        self.assertEqual([], collect.hooks)
        collect.hooks = None
        self.assertEqual(None, collect.hooks)

    def testConstructor_029(self):
        """
        Test assignment of hooks attribute, [] value.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        collect.hooks = []
        self.assertEqual([], collect.hooks)

    def testConstructor_030(self):
        """
        Test assignment of hooks attribute, single valid entry.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        collect.hooks = [
            PreActionHook("stage", "df -k"),
        ]
        self.assertEqual([PreActionHook("stage", "df -k")], collect.hooks)

    def testConstructor_031(self):
        """
        Test assignment of hooks attribute, multiple valid
        entries.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        collect.hooks = [
            PreActionHook("stage", "df -k"),
            PostActionHook("collect", "ls -l"),
        ]
        self.assertEqual([PreActionHook("stage", "df -k"), PostActionHook("collect", "ls -l")], collect.hooks)

    def testConstructor_032(self):
        """
        Test assignment of hooks attribute, single invalid entry
        (None).
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        self.failUnlessAssignRaises(ValueError, collect, "hooks", [None])
        self.assertEqual(None, collect.hooks)

    def testConstructor_033(self):
        """
        Test assignment of hooks attribute, single invalid entry
        (not a ActionHook).
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        self.failUnlessAssignRaises(ValueError, collect, "hooks", ["hello"])
        self.assertEqual(None, collect.hooks)

    def testConstructor_034(self):
        """
        Test assignment of hooks attribute, mixed valid and
        invalid entries.
        """
        collect = OptionsConfig()
        self.assertEqual(None, collect.hooks)
        self.failUnlessAssignRaises(ValueError, collect, "hooks", ["hello", PreActionHook("stage", "df -k")])
        self.assertEqual(None, collect.hooks)

    def testConstructor_035(self):
        """
        Test assignment of rshCommand attribute, None value.
        """
        options = OptionsConfig(rshCommand="command")
        self.assertEqual("command", options.rshCommand)
        options.rshCommand = None
        self.assertEqual(None, options.rshCommand)

    def testConstructor_036(self):
        """
        Test assignment of rshCommand attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.rshCommand)
        options.rshCommand = "command"
        self.assertEqual("command", options.rshCommand)

    def testConstructor_037(self):
        """
        Test assignment of rshCommand attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.rshCommand)
        self.failUnlessAssignRaises(ValueError, options, "rshCommand", "")
        self.assertEqual(None, options.rshCommand)

    def testConstructor_038(self):
        """
        Test assignment of cbackCommand attribute, None value.
        """
        options = OptionsConfig(cbackCommand="command")
        self.assertEqual("command", options.cbackCommand)
        options.cbackCommand = None
        self.assertEqual(None, options.cbackCommand)

    def testConstructor_039(self):
        """
        Test assignment of cbackCommand attribute, valid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.cbackCommand)
        options.cbackCommand = "command"
        self.assertEqual("command", options.cbackCommand)

    def testConstructor_040(self):
        """
        Test assignment of cbackCommand attribute, invalid value (empty).
        """
        options = OptionsConfig()
        self.assertEqual(None, options.cbackCommand)
        self.failUnlessAssignRaises(ValueError, options, "cbackCommand", "")
        self.assertEqual(None, options.cbackCommand)

    def testConstructor_041(self):
        """
        Test assignment of managedActions attribute, None value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.managedActions)
        options.managedActions = None
        self.assertEqual(None, options.managedActions)

    def testConstructor_042(self):
        """
        Test assignment of managedActions attribute, empty list.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.managedActions)
        options.managedActions = []
        self.assertEqual([], options.managedActions)

    def testConstructor_043(self):
        """
        Test assignment of managedActions attribute, non-empty list, valid values.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.managedActions)
        options.managedActions = [
            "a",
            "b",
        ]
        self.assertEqual(["a", "b"], options.managedActions)

    def testConstructor_044(self):
        """
        Test assignment of managedActions attribute, non-empty list, invalid value.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", ["KEN"])
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", ["hello, world"])
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", ["dash-word"])
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", [""])
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", [None])
        self.assertEqual(None, options.managedActions)

    def testConstructor_045(self):
        """
        Test assignment of managedActions attribute, non-empty list, mixed values.
        """
        options = OptionsConfig()
        self.assertEqual(None, options.managedActions)
        self.failUnlessAssignRaises(ValueError, options, "managedActions", ["ken", "dash-word"])

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig()
        self.assertEqual(options1, options2)
        self.assertTrue(options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(not options1 != options2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertEqual(options1, options2)
        self.assertTrue(options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(not options1 != options2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, startingDay differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(startingDay="monday")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, startingDay differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("tuesday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, workingDir differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(workingDir="/tmp")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, workingDir differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig(
            "monday", "/tmp/whatever", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions
        )
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, backupUser differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(backupUser="user")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, backupUser differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user2", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user1", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, backupGroup differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(backupGroup="group")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, backupGroup differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group1", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group2", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, rcpCommand differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(rcpCommand="command")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, rcpCommand differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -2 -B", overrides, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, overrides differs (one
        None, one empty).
        """
        overrides1 = None
        overrides2 = []
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides1, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides2, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, overrides differs (one
        None, one not empty).
        """
        overrides1 = None
        overrides2 = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides1, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides2, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2, "ssh")
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, overrides differs (one
        empty, one not empty).
        """
        overrides1 = [
            CommandOverride("one", "/one"),
        ]
        overrides2 = []
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides1, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides2, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, overrides differs (both
        not empty).
        """
        overrides1 = [
            CommandOverride("one", "/one"),
        ]
        overrides2 = [
            CommandOverride(),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides1, hooks, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides2, hooks, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, hooks differs (one
        None, one empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks1 = None
        hooks2 = []
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks1, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks2, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, hooks differs (one
        None, one not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks1 = [PreActionHook("collect", "ls -l ")]
        hooks2 = [PostActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks1, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks2, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 != options2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, hooks differs (one
        empty, one not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks1 = [PreActionHook("collect", "ls -l ")]
        hooks2 = [PreActionHook("stage", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks1, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks2, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(options1 != options2)

    def testComparison_020(self):
        """
        Test comparison of two differing objects, hooks differs (both
        not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks1 = [PreActionHook("collect", "ls -l ")]
        hooks2 = [PostActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks1, "ssh", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks2, "ssh", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_021(self):
        """
        Test comparison of two differing objects, rshCommand differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(rshCommand="command")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_022(self):
        """
        Test comparison of two differing objects, rshCommand differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh2", "cback", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh1", "cback", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_023(self):
        """
        Test comparison of two differing objects, cbackCommand differs (one None).
        """
        options1 = OptionsConfig()
        options2 = OptionsConfig(rshCommand="command")
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_024(self):
        """
        Test comparison of two differing objects, cbackCommand differs.
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions = [
            "collect",
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback1", managedActions)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback2", managedActions)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_025(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        None, one empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions1 = None
        managedActions2 = []
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions1)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions2)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_026(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        None, one not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions1 = None
        managedActions2 = [
            "collect",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions1)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions2)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(options1 != options2)

    def testComparison_027(self):
        """
        Test comparison of two differing objects, managedActions differs (one
        empty, one not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions1 = []
        managedActions2 = [
            "collect",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions1)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions2)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(options1 != options2)

    def testComparison_028(self):
        """
        Test comparison of two differing objects, managedActions differs (both
        not empty).
        """
        overrides = [
            CommandOverride("one", "/one"),
        ]
        hooks = [PreActionHook("collect", "ls -l ")]
        managedActions1 = [
            "collect",
        ]
        managedActions2 = [
            "purge",
        ]
        options1 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions1)
        options2 = OptionsConfig("monday", "/tmp", "user", "group", "scp -1 -B", overrides, hooks, "ssh", "cback", managedActions2)
        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    ####################################
    # Test add and replace of overrides
    ####################################

    def testOverrides_001(self):
        """
        Test addOverride() with no existing overrides.
        """
        options = OptionsConfig()
        options.addOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("cdrecord", "/usr/bin/wodim")], options.overrides)

    def testOverrides_002(self):
        """
        Test addOverride() with no existing override that matches.
        """
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("one", "/one"),
        ]
        options.addOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("one", "/one"), CommandOverride("cdrecord", "/usr/bin/wodim")], options.overrides)

    def testOverrides_003(self):
        """
        Test addOverride(), with existing override that matches.
        """
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/one"),
        ]
        options.addOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("cdrecord", "/one")], options.overrides)

    def testOverrides_004(self):
        """
        Test replaceOverride() with no existing overrides.
        """
        options = OptionsConfig()
        options.replaceOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("cdrecord", "/usr/bin/wodim")], options.overrides)

    def testOverrides_005(self):
        """
        Test replaceOverride() with no existing override that matches.
        """
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("one", "/one"),
        ]
        options.replaceOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("one", "/one"), CommandOverride("cdrecord", "/usr/bin/wodim")], options.overrides)

    def testOverrides_006(self):
        """
        Test replaceOverride(), with existing override that matches.
        """
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/one"),
        ]
        options.replaceOverride("cdrecord", "/usr/bin/wodim")
        self.assertEqual([CommandOverride("cdrecord", "/usr/bin/wodim")], options.overrides)


########################
# TestPeersConfig class
########################


class TestPeersConfig(unittest.TestCase):

    """Tests for the PeersConfig class."""

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
        obj = PeersConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        self.assertEqual(None, peers.remotePeers)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (empty lists).
        """
        peers = PeersConfig([], [])
        self.assertEqual([], peers.localPeers)
        self.assertEqual([], peers.remotePeers)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values (non-empty lists).
        """
        peers = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertEqual([LocalPeer()], peers.localPeers)
        self.assertEqual([RemotePeer()], peers.remotePeers)

    def testConstructor_004(self):
        """
        Test assignment of localPeers attribute, None value.
        """
        peers = PeersConfig(localPeers=[])
        self.assertEqual([], peers.localPeers)
        peers.localPeers = None
        self.assertEqual(None, peers.localPeers)

    def testConstructor_005(self):
        """
        Test assignment of localPeers attribute, empty list.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        peers.localPeers = []
        self.assertEqual([], peers.localPeers)

    def testConstructor_006(self):
        """
        Test assignment of localPeers attribute, single valid entry.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        peers.localPeers = [
            LocalPeer(),
        ]
        self.assertEqual([LocalPeer()], peers.localPeers)

    def testConstructor_007(self):
        """
        Test assignment of localPeers attribute, multiple valid
        entries.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        peers.localPeers = [
            LocalPeer(name="one"),
            LocalPeer(name="two"),
        ]
        self.assertEqual([LocalPeer(name="one"), LocalPeer(name="two")], peers.localPeers)

    def testConstructor_008(self):
        """
        Test assignment of localPeers attribute, single invalid entry
        (None).
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        self.failUnlessAssignRaises(ValueError, peers, "localPeers", [None])
        self.assertEqual(None, peers.localPeers)

    def testConstructor_009(self):
        """
        Test assignment of localPeers attribute, single invalid entry
        (not a LocalPeer).
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        self.failUnlessAssignRaises(ValueError, peers, "localPeers", [RemotePeer()])
        self.assertEqual(None, peers.localPeers)

    def testConstructor_010(self):
        """
        Test assignment of localPeers attribute, mixed valid and
        invalid entries.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.localPeers)
        self.failUnlessAssignRaises(ValueError, peers, "localPeers", [LocalPeer(), RemotePeer()])
        self.assertEqual(None, peers.localPeers)

    def testConstructor_011(self):
        """
        Test assignment of remotePeers attribute, None value.
        """
        peers = PeersConfig(remotePeers=[])
        self.assertEqual([], peers.remotePeers)
        peers.remotePeers = None
        self.assertEqual(None, peers.remotePeers)

    def testConstructor_012(self):
        """
        Test assignment of remotePeers attribute, empty list.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        peers.remotePeers = []
        self.assertEqual([], peers.remotePeers)

    def testConstructor_013(self):
        """
        Test assignment of remotePeers attribute, single valid entry.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        peers.remotePeers = [
            RemotePeer(name="one"),
        ]
        self.assertEqual([RemotePeer(name="one")], peers.remotePeers)

    def testConstructor_014(self):
        """
        Test assignment of remotePeers attribute, multiple valid
        entries.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        peers.remotePeers = [
            RemotePeer(name="one"),
            RemotePeer(name="two"),
        ]
        self.assertEqual([RemotePeer(name="one"), RemotePeer(name="two")], peers.remotePeers)

    def testConstructor_015(self):
        """
        Test assignment of remotePeers attribute, single invalid entry
        (None).
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        self.failUnlessAssignRaises(ValueError, peers, "remotePeers", [None])
        self.assertEqual(None, peers.remotePeers)

    def testConstructor_016(self):
        """
        Test assignment of remotePeers attribute, single invalid entry
        (not a RemotePeer).
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        self.failUnlessAssignRaises(ValueError, peers, "remotePeers", [LocalPeer()])
        self.assertEqual(None, peers.remotePeers)

    def testConstructor_017(self):
        """
        Test assignment of remotePeers attribute, mixed valid and
        invalid entries.
        """
        peers = PeersConfig()
        self.assertEqual(None, peers.remotePeers)
        self.failUnlessAssignRaises(ValueError, peers, "remotePeers", [LocalPeer(), RemotePeer()])
        self.assertEqual(None, peers.remotePeers)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        peers1 = PeersConfig()
        peers2 = PeersConfig()
        self.assertEqual(peers1, peers2)
        self.assertTrue(peers1 == peers2)
        self.assertTrue(not peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(peers1 >= peers2)
        self.assertTrue(not peers1 != peers2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None (empty lists).
        """
        peers1 = PeersConfig([], [])
        peers2 = PeersConfig([], [])
        self.assertEqual(peers1, peers2)
        self.assertTrue(peers1 == peers2)
        self.assertTrue(not peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(peers1 >= peers2)
        self.assertTrue(not peers1 != peers2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None (non-empty lists).
        """
        peers1 = PeersConfig([LocalPeer()], [RemotePeer()])
        peers2 = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertEqual(peers1, peers2)
        self.assertTrue(peers1 == peers2)
        self.assertTrue(not peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(peers1 >= peers2)
        self.assertTrue(not peers1 != peers2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, localPeers differs (one None,
        one empty).
        """
        peers1 = PeersConfig(None, [RemotePeer()])
        peers2 = PeersConfig([], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, localPeers differs (one None,
        one not empty).
        """
        peers1 = PeersConfig(None, [RemotePeer()])
        peers2 = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, localPeers differs (one empty,
        one not empty).
        """
        peers1 = PeersConfig([], [RemotePeer()])
        peers2 = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, localPeers differs (both not
        empty).
        """
        peers1 = PeersConfig([LocalPeer(name="one")], [RemotePeer()])
        peers2 = PeersConfig([LocalPeer(name="two")], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, remotePeers differs (one None,
        one empty).
        """
        peers1 = PeersConfig([LocalPeer()], None)
        peers2 = PeersConfig([LocalPeer()], [])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, remotePeers differs (one None,
        one not empty).
        """
        peers1 = PeersConfig([LocalPeer()], None)
        peers2 = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, remotePeers differs (one empty,
        one not empty).
        """
        peers1 = PeersConfig([LocalPeer()], [])
        peers2 = PeersConfig([LocalPeer()], [RemotePeer()])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(peers1 < peers2)
        self.assertTrue(peers1 <= peers2)
        self.assertTrue(not peers1 > peers2)
        self.assertTrue(not peers1 >= peers2)
        self.assertTrue(peers1 != peers2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, remotePeers differs (both not
        empty).
        """
        peers1 = PeersConfig([LocalPeer()], [RemotePeer(name="two")])
        peers2 = PeersConfig([LocalPeer()], [RemotePeer(name="one")])
        self.assertNotEqual(peers1, peers2)
        self.assertTrue(not peers1 == peers2)
        self.assertTrue(not peers1 < peers2)
        self.assertTrue(not peers1 <= peers2)
        self.assertTrue(peers1 > peers2)
        self.assertTrue(peers1 >= peers2)
        self.assertTrue(peers1 != peers2)


##########################
# TestCollectConfig class
##########################


class TestCollectConfig(unittest.TestCase):

    """Tests for the CollectConfig class."""

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
        obj = CollectConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.targetDir)
        self.assertEqual(None, collect.collectMode)
        self.assertEqual(None, collect.archiveMode)
        self.assertEqual(None, collect.ignoreFile)
        self.assertEqual(None, collect.absoluteExcludePaths)
        self.assertEqual(None, collect.excludePatterns)
        self.assertEqual(None, collect.collectDirs)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (lists empty).
        """
        collect = CollectConfig("/target", "incr", "tar", "ignore", [], [], [], [])
        self.assertEqual("/target", collect.targetDir)
        self.assertEqual("incr", collect.collectMode)
        self.assertEqual("tar", collect.archiveMode)
        self.assertEqual("ignore", collect.ignoreFile)
        self.assertEqual([], collect.absoluteExcludePaths)
        self.assertEqual([], collect.excludePatterns)
        self.assertEqual([], collect.collectDirs)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values (lists not empty).
        """
        collect = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertEqual("/target", collect.targetDir)
        self.assertEqual("incr", collect.collectMode)
        self.assertEqual("tar", collect.archiveMode)
        self.assertEqual("ignore", collect.ignoreFile)
        self.assertEqual(["/path"], collect.absoluteExcludePaths)
        self.assertEqual(["pattern"], collect.excludePatterns)
        self.assertEqual([CollectFile()], collect.collectFiles)
        self.assertEqual([CollectDir()], collect.collectDirs)

    def testConstructor_004(self):
        """
        Test assignment of targetDir attribute, None value.
        """
        collect = CollectConfig(targetDir="/whatever")
        self.assertEqual("/whatever", collect.targetDir)
        collect.targetDir = None
        self.assertEqual(None, collect.targetDir)

    def testConstructor_005(self):
        """
        Test assignment of targetDir attribute, valid value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.targetDir)
        collect.targetDir = "/whatever"
        self.assertEqual("/whatever", collect.targetDir)

    def testConstructor_006(self):
        """
        Test assignment of targetDir attribute, invalid value (empty).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.targetDir)
        self.failUnlessAssignRaises(ValueError, collect, "targetDir", "")
        self.assertEqual(None, collect.targetDir)

    def testConstructor_007(self):
        """
        Test assignment of targetDir attribute, invalid value (non-absolute).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.targetDir)
        self.failUnlessAssignRaises(ValueError, collect, "targetDir", "bogus")
        self.assertEqual(None, collect.targetDir)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        collect = CollectConfig(collectMode="incr")
        self.assertEqual("incr", collect.collectMode)
        collect.collectMode = None
        self.assertEqual(None, collect.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectMode)
        collect.collectMode = "daily"
        self.assertEqual("daily", collect.collectMode)
        collect.collectMode = "weekly"
        self.assertEqual("weekly", collect.collectMode)
        collect.collectMode = "incr"
        self.assertEqual("incr", collect.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectMode)
        self.failUnlessAssignRaises(ValueError, collect, "collectMode", "")
        self.assertEqual(None, collect.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectMode)
        self.failUnlessAssignRaises(ValueError, collect, "collectMode", "periodic")
        self.assertEqual(None, collect.collectMode)

    def testConstructor_012(self):
        """
        Test assignment of archiveMode attribute, None value.
        """
        collect = CollectConfig(archiveMode="tar")
        self.assertEqual("tar", collect.archiveMode)
        collect.archiveMode = None
        self.assertEqual(None, collect.archiveMode)

    def testConstructor_013(self):
        """
        Test assignment of archiveMode attribute, valid value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.archiveMode)
        collect.archiveMode = "tar"
        self.assertEqual("tar", collect.archiveMode)
        collect.archiveMode = "targz"
        self.assertEqual("targz", collect.archiveMode)
        collect.archiveMode = "tarbz2"
        self.assertEqual("tarbz2", collect.archiveMode)

    def testConstructor_014(self):
        """
        Test assignment of archiveMode attribute, invalid value (empty).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.archiveMode)
        self.failUnlessAssignRaises(ValueError, collect, "archiveMode", "")
        self.assertEqual(None, collect.archiveMode)

    def testConstructor_015(self):
        """
        Test assignment of archiveMode attribute, invalid value (not in list).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.archiveMode)
        self.failUnlessAssignRaises(ValueError, collect, "archiveMode", "tarz")
        self.assertEqual(None, collect.archiveMode)

    def testConstructor_016(self):
        """
        Test assignment of ignoreFile attribute, None value.
        """
        collect = CollectConfig(ignoreFile="ignore")
        self.assertEqual("ignore", collect.ignoreFile)
        collect.ignoreFile = None
        self.assertEqual(None, collect.ignoreFile)

    def testConstructor_017(self):
        """
        Test assignment of ignoreFile attribute, valid value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.ignoreFile)
        collect.ignoreFile = "ignore"
        self.assertEqual("ignore", collect.ignoreFile)

    def testConstructor_018(self):
        """
        Test assignment of ignoreFile attribute, invalid value (empty).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.ignoreFile)
        self.failUnlessAssignRaises(ValueError, collect, "ignoreFile", "")
        self.assertEqual(None, collect.ignoreFile)

    def testConstructor_019(self):
        """
        Test assignment of absoluteExcludePaths attribute, None value.
        """
        collect = CollectConfig(absoluteExcludePaths=[])
        self.assertEqual([], collect.absoluteExcludePaths)
        collect.absoluteExcludePaths = None
        self.assertEqual(None, collect.absoluteExcludePaths)

    def testConstructor_020(self):
        """
        Test assignment of absoluteExcludePaths attribute, [] value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        collect.absoluteExcludePaths = []
        self.assertEqual([], collect.absoluteExcludePaths)

    def testConstructor_021(self):
        """
        Test assignment of absoluteExcludePaths attribute, single valid entry.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        collect.absoluteExcludePaths = [
            "/whatever",
        ]
        self.assertEqual(["/whatever"], collect.absoluteExcludePaths)

    def testConstructor_022(self):
        """
        Test assignment of absoluteExcludePaths attribute, multiple valid
        entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        collect.absoluteExcludePaths = [
            "/one",
            "/two",
            "/three",
        ]
        self.assertEqual(["/one", "/two", "/three"], collect.absoluteExcludePaths)

    def testConstructor_023(self):
        """
        Test assignment of absoluteExcludePaths attribute, single invalid entry
        (empty).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collect, "absoluteExcludePaths", [""])
        self.assertEqual(None, collect.absoluteExcludePaths)

    def testConstructor_024(self):
        """
        Test assignment of absoluteExcludePaths attribute, single invalid entry
        (not absolute).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collect, "absoluteExcludePaths", ["one"])
        self.assertEqual(None, collect.absoluteExcludePaths)

    def testConstructor_025(self):
        """
        Test assignment of absoluteExcludePaths attribute, mixed valid and
        invalid entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.absoluteExcludePaths)
        self.failUnlessAssignRaises(ValueError, collect, "absoluteExcludePaths", ["one", "/two"])
        self.assertEqual(None, collect.absoluteExcludePaths)

    def testConstructor_026(self):
        """
        Test assignment of excludePatterns attribute, None value.
        """
        collect = CollectConfig(excludePatterns=[])
        self.assertEqual([], collect.excludePatterns)
        collect.excludePatterns = None
        self.assertEqual(None, collect.excludePatterns)

    def testConstructor_027(self):
        """
        Test assignment of excludePatterns attribute, [] value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        collect.excludePatterns = []
        self.assertEqual([], collect.excludePatterns)

    def testConstructor_028(self):
        """
        Test assignment of excludePatterns attribute, single valid entry.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        collect.excludePatterns = [
            "pattern",
        ]
        self.assertEqual(["pattern"], collect.excludePatterns)

    def testConstructor_029(self):
        """
        Test assignment of excludePatterns attribute, multiple valid entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        collect.excludePatterns = [
            "pattern1",
            "pattern2",
        ]
        self.assertEqual(["pattern1", "pattern2"], collect.excludePatterns)

    def testConstructor_029a(self):
        """
        Test assignment of excludePatterns attribute, single invalid entry.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collect, "excludePatterns", ["*.jpg"])
        self.assertEqual(None, collect.excludePatterns)

    def testConstructor_029b(self):
        """
        Test assignment of excludePatterns attribute, multiple invalid entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collect, "excludePatterns", ["*.jpg", "*"])
        self.assertEqual(None, collect.excludePatterns)

    def testConstructor_029c(self):
        """
        Test assignment of excludePatterns attribute, mixed valid and invalid
        entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.excludePatterns)
        self.failUnlessAssignRaises(ValueError, collect, "excludePatterns", ["*.jpg", "valid"])
        self.assertEqual(None, collect.excludePatterns)

    def testConstructor_030(self):
        """
        Test assignment of collectDirs attribute, None value.
        """
        collect = CollectConfig(collectDirs=[])
        self.assertEqual([], collect.collectDirs)
        collect.collectDirs = None
        self.assertEqual(None, collect.collectDirs)

    def testConstructor_031(self):
        """
        Test assignment of collectDirs attribute, [] value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        collect.collectDirs = []
        self.assertEqual([], collect.collectDirs)

    def testConstructor_032(self):
        """
        Test assignment of collectDirs attribute, single valid entry.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        collect.collectDirs = [
            CollectDir(absolutePath="/one"),
        ]
        self.assertEqual([CollectDir(absolutePath="/one")], collect.collectDirs)

    def testConstructor_033(self):
        """
        Test assignment of collectDirs attribute, multiple valid
        entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        collect.collectDirs = [
            CollectDir(absolutePath="/one"),
            CollectDir(absolutePath="/two"),
        ]
        self.assertEqual([CollectDir(absolutePath="/one"), CollectDir(absolutePath="/two")], collect.collectDirs)

    def testConstructor_034(self):
        """
        Test assignment of collectDirs attribute, single invalid entry
        (None).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        self.failUnlessAssignRaises(ValueError, collect, "collectDirs", [None])
        self.assertEqual(None, collect.collectDirs)

    def testConstructor_035(self):
        """
        Test assignment of collectDirs attribute, single invalid entry
        (not a CollectDir).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        self.failUnlessAssignRaises(ValueError, collect, "collectDirs", ["hello"])
        self.assertEqual(None, collect.collectDirs)

    def testConstructor_036(self):
        """
        Test assignment of collectDirs attribute, mixed valid and
        invalid entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectDirs)
        self.failUnlessAssignRaises(ValueError, collect, "collectDirs", ["hello", CollectDir()])
        self.assertEqual(None, collect.collectDirs)

    def testConstructor_037(self):
        """
        Test assignment of collectFiles attribute, None value.
        """
        collect = CollectConfig(collectFiles=[])
        self.assertEqual([], collect.collectFiles)
        collect.collectFiles = None
        self.assertEqual(None, collect.collectFiles)

    def testConstructor_038(self):
        """
        Test assignment of collectFiles attribute, [] value.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        collect.collectFiles = []
        self.assertEqual([], collect.collectFiles)

    def testConstructor_039(self):
        """
        Test assignment of collectFiles attribute, single valid entry.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        collect.collectFiles = [
            CollectFile(absolutePath="/one"),
        ]
        self.assertEqual([CollectFile(absolutePath="/one")], collect.collectFiles)

    def testConstructor_040(self):
        """
        Test assignment of collectFiles attribute, multiple valid
        entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        collect.collectFiles = [
            CollectFile(absolutePath="/one"),
            CollectFile(absolutePath="/two"),
        ]
        self.assertEqual([CollectFile(absolutePath="/one"), CollectFile(absolutePath="/two")], collect.collectFiles)

    def testConstructor_041(self):
        """
        Test assignment of collectFiles attribute, single invalid entry
        (None).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        self.failUnlessAssignRaises(ValueError, collect, "collectFiles", [None])
        self.assertEqual(None, collect.collectFiles)

    def testConstructor_042(self):
        """
        Test assignment of collectFiles attribute, single invalid entry
        (not a CollectFile).
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        self.failUnlessAssignRaises(ValueError, collect, "collectFiles", ["hello"])
        self.assertEqual(None, collect.collectFiles)

    def testConstructor_043(self):
        """
        Test assignment of collectFiles attribute, mixed valid and
        invalid entries.
        """
        collect = CollectConfig()
        self.assertEqual(None, collect.collectFiles)
        self.failUnlessAssignRaises(ValueError, collect, "collectFiles", ["hello", CollectFile()])
        self.assertEqual(None, collect.collectFiles)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        collect1 = CollectConfig()
        collect2 = CollectConfig()
        self.assertEqual(collect1, collect2)
        self.assertTrue(collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(not collect1 != collect2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertEqual(collect1, collect2)
        self.assertTrue(collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(not collect1 != collect2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, targetDir differs (one None).
        """
        collect1 = CollectConfig(None, "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target2", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, targetDir differs.
        """
        collect1 = CollectConfig("/target1", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target2", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", None, "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        collect1 = CollectConfig("/target", "daily", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, archiveMode differs (one None).
        """
        collect1 = CollectConfig("/target", "incr", None, "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, archiveMode differs.
        """
        collect1 = CollectConfig("/target", "incr", "targz", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tarbz2", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, ignoreFile differs (one None).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", None, ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, ignoreFile differs.
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore1", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore2", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one None, one empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", None, ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", [], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one None, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", None, ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (one empty, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", [], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, absoluteExcludePaths differs
        (both not empty).
        """
        collect1 = CollectConfig(
            "/target", "incr", "tar", "ignore", ["/path", "/path2"], ["pattern"], [CollectFile()], [CollectDir()]
        )
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], None, [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], [], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], None, [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        empty, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], [], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, excludePatterns differs (both
        not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig(
            "/target", "incr", "tar", "ignore", ["/path"], ["pattern", "bogus"], [CollectFile()], [CollectDir()]
        )
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, collectDirs differs (one
        None, one empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], None)
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_020(self):
        """
        Test comparison of two differing objects, collectDirs differs (one
        None, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], None)
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_021(self):
        """
        Test comparison of two differing objects, collectDirs differs (one
        empty, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_022(self):
        """
        Test comparison of two differing objects, collectDirs differs (both
        not empty).
        """
        collect1 = CollectConfig(
            "/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir(), CollectDir()]
        )
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_023(self):
        """
        Test comparison of two differing objects, collectFiles differs (one
        None, one empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], None, [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_024(self):
        """
        Test comparison of two differing objects, collectFiles differs (one
        None, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], None, [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(collect1 < collect2)
        self.assertTrue(collect1 <= collect2)
        self.assertTrue(not collect1 > collect2)
        self.assertTrue(not collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_025(self):
        """
        Test comparison of two differing objects, collectFiles differs (one
        empty, one not empty).
        """
        collect1 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)

    def testComparison_026(self):
        """
        Test comparison of two differing objects, collectFiles differs (both
        not empty).
        """
        collect1 = CollectConfig(
            "/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile(), CollectFile()], [CollectDir()]
        )
        collect2 = CollectConfig("/target", "incr", "tar", "ignore", ["/path"], ["pattern"], [CollectFile()], [CollectDir()])
        self.assertNotEqual(collect1, collect2)
        self.assertTrue(not collect1 == collect2)
        self.assertTrue(not collect1 < collect2)
        self.assertTrue(not collect1 <= collect2)
        self.assertTrue(collect1 > collect2)
        self.assertTrue(collect1 >= collect2)
        self.assertTrue(collect1 != collect2)


########################
# TestStageConfig class
########################


class TestStageConfig(unittest.TestCase):

    """Tests for the StageConfig class."""

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
        obj = StageConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.targetDir)
        self.assertEqual(None, stage.localPeers)
        self.assertEqual(None, stage.remotePeers)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (empty lists).
        """
        stage = StageConfig("/whatever", [], [])
        self.assertEqual("/whatever", stage.targetDir)
        self.assertEqual([], stage.localPeers)
        self.assertEqual([], stage.remotePeers)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values (non-empty lists).
        """
        stage = StageConfig("/whatever", [LocalPeer()], [RemotePeer()])
        self.assertEqual("/whatever", stage.targetDir)
        self.assertEqual([LocalPeer()], stage.localPeers)
        self.assertEqual([RemotePeer()], stage.remotePeers)

    def testConstructor_004(self):
        """
        Test assignment of targetDir attribute, None value.
        """
        stage = StageConfig(targetDir="/whatever")
        self.assertEqual("/whatever", stage.targetDir)
        stage.targetDir = None
        self.assertEqual(None, stage.targetDir)

    def testConstructor_005(self):
        """
        Test assignment of targetDir attribute, valid value.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.targetDir)
        stage.targetDir = "/whatever"
        self.assertEqual("/whatever", stage.targetDir)

    def testConstructor_006(self):
        """
        Test assignment of targetDir attribute, invalid value (empty).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.targetDir)
        self.failUnlessAssignRaises(ValueError, stage, "targetDir", "")
        self.assertEqual(None, stage.targetDir)

    def testConstructor_007(self):
        """
        Test assignment of targetDir attribute, invalid value (non-absolute).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.targetDir)
        self.failUnlessAssignRaises(ValueError, stage, "targetDir", "stuff")
        self.assertEqual(None, stage.targetDir)

    def testConstructor_008(self):
        """
        Test assignment of localPeers attribute, None value.
        """
        stage = StageConfig(localPeers=[])
        self.assertEqual([], stage.localPeers)
        stage.localPeers = None
        self.assertEqual(None, stage.localPeers)

    def testConstructor_009(self):
        """
        Test assignment of localPeers attribute, empty list.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        stage.localPeers = []
        self.assertEqual([], stage.localPeers)

    def testConstructor_010(self):
        """
        Test assignment of localPeers attribute, single valid entry.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        stage.localPeers = [
            LocalPeer(),
        ]
        self.assertEqual([LocalPeer()], stage.localPeers)

    def testConstructor_011(self):
        """
        Test assignment of localPeers attribute, multiple valid
        entries.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        stage.localPeers = [
            LocalPeer(name="one"),
            LocalPeer(name="two"),
        ]
        self.assertEqual([LocalPeer(name="one"), LocalPeer(name="two")], stage.localPeers)

    def testConstructor_012(self):
        """
        Test assignment of localPeers attribute, single invalid entry
        (None).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        self.failUnlessAssignRaises(ValueError, stage, "localPeers", [None])
        self.assertEqual(None, stage.localPeers)

    def testConstructor_013(self):
        """
        Test assignment of localPeers attribute, single invalid entry
        (not a LocalPeer).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        self.failUnlessAssignRaises(ValueError, stage, "localPeers", [RemotePeer()])
        self.assertEqual(None, stage.localPeers)

    def testConstructor_014(self):
        """
        Test assignment of localPeers attribute, mixed valid and
        invalid entries.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.localPeers)
        self.failUnlessAssignRaises(ValueError, stage, "localPeers", [LocalPeer(), RemotePeer()])
        self.assertEqual(None, stage.localPeers)

    def testConstructor_015(self):
        """
        Test assignment of remotePeers attribute, None value.
        """
        stage = StageConfig(remotePeers=[])
        self.assertEqual([], stage.remotePeers)
        stage.remotePeers = None
        self.assertEqual(None, stage.remotePeers)

    def testConstructor_016(self):
        """
        Test assignment of remotePeers attribute, empty list.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        stage.remotePeers = []
        self.assertEqual([], stage.remotePeers)

    def testConstructor_017(self):
        """
        Test assignment of remotePeers attribute, single valid entry.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        stage.remotePeers = [
            RemotePeer(name="one"),
        ]
        self.assertEqual([RemotePeer(name="one")], stage.remotePeers)

    def testConstructor_018(self):
        """
        Test assignment of remotePeers attribute, multiple valid
        entries.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        stage.remotePeers = [
            RemotePeer(name="one"),
            RemotePeer(name="two"),
        ]
        self.assertEqual([RemotePeer(name="one"), RemotePeer(name="two")], stage.remotePeers)

    def testConstructor_019(self):
        """
        Test assignment of remotePeers attribute, single invalid entry
        (None).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        self.failUnlessAssignRaises(ValueError, stage, "remotePeers", [None])
        self.assertEqual(None, stage.remotePeers)

    def testConstructor_020(self):
        """
        Test assignment of remotePeers attribute, single invalid entry
        (not a RemotePeer).
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        self.failUnlessAssignRaises(ValueError, stage, "remotePeers", [LocalPeer()])
        self.assertEqual(None, stage.remotePeers)

    def testConstructor_021(self):
        """
        Test assignment of remotePeers attribute, mixed valid and
        invalid entries.
        """
        stage = StageConfig()
        self.assertEqual(None, stage.remotePeers)
        self.failUnlessAssignRaises(ValueError, stage, "remotePeers", [LocalPeer(), RemotePeer()])
        self.assertEqual(None, stage.remotePeers)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        stage1 = StageConfig()
        stage2 = StageConfig()
        self.assertEqual(stage1, stage2)
        self.assertTrue(stage1 == stage2)
        self.assertTrue(not stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(stage1 >= stage2)
        self.assertTrue(not stage1 != stage2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None (empty lists).
        """
        stage1 = StageConfig("/target", [], [])
        stage2 = StageConfig("/target", [], [])
        self.assertEqual(stage1, stage2)
        self.assertTrue(stage1 == stage2)
        self.assertTrue(not stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(stage1 >= stage2)
        self.assertTrue(not stage1 != stage2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None (non-empty lists).
        """
        stage1 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        self.assertEqual(stage1, stage2)
        self.assertTrue(stage1 == stage2)
        self.assertTrue(not stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(stage1 >= stage2)
        self.assertTrue(not stage1 != stage2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, targetDir differs (one None).
        """
        stage1 = StageConfig()
        stage2 = StageConfig(targetDir="/whatever")
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, targetDir differs.
        """
        stage1 = StageConfig("/target1", [LocalPeer()], [RemotePeer()])
        stage2 = StageConfig("/target2", [LocalPeer()], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, localPeers differs (one None,
        one empty).
        """
        stage1 = StageConfig("/target", None, [RemotePeer()])
        stage2 = StageConfig("/target", [], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, localPeers differs (one None,
        one not empty).
        """
        stage1 = StageConfig("/target", None, [RemotePeer()])
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, localPeers differs (one empty,
        one not empty).
        """
        stage1 = StageConfig("/target", [], [RemotePeer()])
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, localPeers differs (both not
        empty).
        """
        stage1 = StageConfig("/target", [LocalPeer(name="one")], [RemotePeer()])
        stage2 = StageConfig("/target", [LocalPeer(name="two")], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, remotePeers differs (one None,
        one empty).
        """
        stage1 = StageConfig("/target", [LocalPeer()], None)
        stage2 = StageConfig("/target", [LocalPeer()], [])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, remotePeers differs (one None,
        one not empty).
        """
        stage1 = StageConfig("/target", [LocalPeer()], None)
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, remotePeers differs (one empty,
        one not empty).
        """
        stage1 = StageConfig("/target", [LocalPeer()], [])
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer()])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(stage1 < stage2)
        self.assertTrue(stage1 <= stage2)
        self.assertTrue(not stage1 > stage2)
        self.assertTrue(not stage1 >= stage2)
        self.assertTrue(stage1 != stage2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, remotePeers differs (both not
        empty).
        """
        stage1 = StageConfig("/target", [LocalPeer()], [RemotePeer(name="two")])
        stage2 = StageConfig("/target", [LocalPeer()], [RemotePeer(name="one")])
        self.assertNotEqual(stage1, stage2)
        self.assertTrue(not stage1 == stage2)
        self.assertTrue(not stage1 < stage2)
        self.assertTrue(not stage1 <= stage2)
        self.assertTrue(stage1 > stage2)
        self.assertTrue(stage1 >= stage2)
        self.assertTrue(stage1 != stage2)


########################
# TestStoreConfig class
########################


class TestStoreConfig(unittest.TestCase):

    """Tests for the StoreConfig class."""

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
        obj = StoreConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        store = StoreConfig()
        self.assertEqual(None, store.sourceDir)
        self.assertEqual(None, store.mediaType)
        self.assertEqual(None, store.deviceType)
        self.assertEqual(None, store.devicePath)
        self.assertEqual(None, store.deviceScsiId)
        self.assertEqual(None, store.driveSpeed)
        self.assertEqual(False, store.checkData)
        self.assertEqual(False, store.checkMedia)
        self.assertEqual(False, store.warnMidnite)
        self.assertEqual(False, store.noEject)
        self.assertEqual(None, store.blankBehavior)
        self.assertEqual(None, store.refreshMediaDelay)
        self.assertEqual(None, store.ejectDelay)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        behavior = BlankBehavior("weekly", "1.3")
        store = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior, 12, 13)
        self.assertEqual("/source", store.sourceDir)
        self.assertEqual("cdr-74", store.mediaType)
        self.assertEqual("cdwriter", store.deviceType)
        self.assertEqual("/dev/cdrw", store.devicePath)
        self.assertEqual("0,0,0", store.deviceScsiId)
        self.assertEqual(4, store.driveSpeed)
        self.assertEqual(True, store.checkData)
        self.assertEqual(True, store.checkMedia)
        self.assertEqual(True, store.warnMidnite)
        self.assertEqual(True, store.noEject)
        self.assertEqual(behavior, store.blankBehavior)
        self.assertEqual(12, store.refreshMediaDelay)
        self.assertEqual(13, store.ejectDelay)

    def testConstructor_003(self):
        """
        Test assignment of sourceDir attribute, None value.
        """
        store = StoreConfig(sourceDir="/whatever")
        self.assertEqual("/whatever", store.sourceDir)
        store.sourceDir = None
        self.assertEqual(None, store.sourceDir)

    def testConstructor_004(self):
        """
        Test assignment of sourceDir attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.sourceDir)
        store.sourceDir = "/whatever"
        self.assertEqual("/whatever", store.sourceDir)

    def testConstructor_005(self):
        """
        Test assignment of sourceDir attribute, invalid value (empty).
        """
        store = StoreConfig()
        self.assertEqual(None, store.sourceDir)
        self.failUnlessAssignRaises(ValueError, store, "sourceDir", "")
        self.assertEqual(None, store.sourceDir)

    def testConstructor_006(self):
        """
        Test assignment of sourceDir attribute, invalid value (non-absolute).
        """
        store = StoreConfig()
        self.assertEqual(None, store.sourceDir)
        self.failUnlessAssignRaises(ValueError, store, "sourceDir", "bogus")
        self.assertEqual(None, store.sourceDir)

    def testConstructor_007(self):
        """
        Test assignment of mediaType attribute, None value.
        """
        store = StoreConfig(mediaType="cdr-74")
        self.assertEqual("cdr-74", store.mediaType)
        store.mediaType = None
        self.assertEqual(None, store.mediaType)

    def testConstructor_008(self):
        """
        Test assignment of mediaType attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.mediaType)
        store.mediaType = "cdr-74"
        self.assertEqual("cdr-74", store.mediaType)
        store.mediaType = "cdrw-74"
        self.assertEqual("cdrw-74", store.mediaType)
        store.mediaType = "cdr-80"
        self.assertEqual("cdr-80", store.mediaType)
        store.mediaType = "cdrw-80"
        self.assertEqual("cdrw-80", store.mediaType)
        store.mediaType = "dvd+r"
        self.assertEqual("dvd+r", store.mediaType)
        store.mediaType = "dvd+rw"
        self.assertEqual("dvd+rw", store.mediaType)

    def testConstructor_009(self):
        """
        Test assignment of mediaType attribute, invalid value (empty).
        """
        store = StoreConfig()
        self.assertEqual(None, store.mediaType)
        self.failUnlessAssignRaises(ValueError, store, "mediaType", "")
        self.assertEqual(None, store.mediaType)

    def testConstructor_010(self):
        """
        Test assignment of mediaType attribute, invalid value (not in list).
        """
        store = StoreConfig()
        self.assertEqual(None, store.mediaType)
        self.failUnlessAssignRaises(ValueError, store, "mediaType", "floppy")
        self.assertEqual(None, store.mediaType)

    def testConstructor_011(self):
        """
        Test assignment of deviceType attribute, None value.
        """
        store = StoreConfig(deviceType="cdwriter")
        self.assertEqual("cdwriter", store.deviceType)
        store.deviceType = None
        self.assertEqual(None, store.deviceType)

    def testConstructor_012(self):
        """
        Test assignment of deviceType attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceType)
        store.deviceType = "cdwriter"
        self.assertEqual("cdwriter", store.deviceType)
        store.deviceType = "dvdwriter"
        self.assertEqual("dvdwriter", store.deviceType)

    def testConstructor_013(self):
        """
        Test assignment of deviceType attribute, invalid value (empty).
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceType)
        self.failUnlessAssignRaises(ValueError, store, "deviceType", "")
        self.assertEqual(None, store.deviceType)

    def testConstructor_014(self):
        """
        Test assignment of deviceType attribute, invalid value (not in list).
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceType)
        self.failUnlessAssignRaises(ValueError, store, "deviceType", "ftape")
        self.assertEqual(None, store.deviceType)

    def testConstructor_015(self):
        """
        Test assignment of devicePath attribute, None value.
        """
        store = StoreConfig(devicePath="/dev/cdrw")
        self.assertEqual("/dev/cdrw", store.devicePath)
        store.devicePath = None
        self.assertEqual(None, store.devicePath)

    def testConstructor_016(self):
        """
        Test assignment of devicePath attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.devicePath)
        store.devicePath = "/dev/cdrw"
        self.assertEqual("/dev/cdrw", store.devicePath)

    def testConstructor_017(self):
        """
        Test assignment of devicePath attribute, invalid value (empty).
        """
        store = StoreConfig()
        self.assertEqual(None, store.devicePath)
        self.failUnlessAssignRaises(ValueError, store, "devicePath", "")
        self.assertEqual(None, store.devicePath)

    def testConstructor_018(self):
        """
        Test assignment of devicePath attribute, invalid value (non-absolute).
        """
        store = StoreConfig()
        self.assertEqual(None, store.devicePath)
        self.failUnlessAssignRaises(ValueError, store, "devicePath", "dev/cdrw")
        self.assertEqual(None, store.devicePath)

    def testConstructor_019(self):
        """
        Test assignment of deviceScsiId attribute, None value.
        """
        store = StoreConfig(deviceScsiId="0,0,0")
        self.assertEqual("0,0,0", store.deviceScsiId)
        store.deviceScsiId = None
        self.assertEqual(None, store.deviceScsiId)

    def testConstructor_020(self):
        """
        Test assignment of deviceScsiId attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceScsiId)
        store.deviceScsiId = "0,0,0"
        self.assertEqual("0,0,0", store.deviceScsiId)
        store.deviceScsiId = "ATA:0,0,0"
        self.assertEqual("ATA:0,0,0", store.deviceScsiId)

    def testConstructor_021(self):
        """
        Test assignment of deviceScsiId attribute, invalid value (empty).
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceScsiId)
        self.failUnlessAssignRaises(ValueError, store, "deviceScsiId", "")
        self.assertEqual(None, store.deviceScsiId)

    def testConstructor_022(self):
        """
        Test assignment of deviceScsiId attribute, invalid value (invalid id).
        """
        store = StoreConfig()
        self.assertEqual(None, store.deviceScsiId)
        self.failUnlessAssignRaises(ValueError, store, "deviceScsiId", "ATA;0,0,0")
        self.assertEqual(None, store.deviceScsiId)
        self.failUnlessAssignRaises(ValueError, store, "deviceScsiId", "ATAPI-0,0,0")
        self.assertEqual(None, store.deviceScsiId)
        self.failUnlessAssignRaises(ValueError, store, "deviceScsiId", "1:2:3")
        self.assertEqual(None, store.deviceScsiId)

    def testConstructor_023(self):
        """
        Test assignment of driveSpeed attribute, None value.
        """
        store = StoreConfig(driveSpeed=4)
        self.assertEqual(4, store.driveSpeed)
        store.driveSpeed = None
        self.assertEqual(None, store.driveSpeed)

    def testConstructor_024(self):
        """
        Test assignment of driveSpeed attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.driveSpeed)
        store.driveSpeed = 4
        self.assertEqual(4, store.driveSpeed)
        store.driveSpeed = "12"
        self.assertEqual(12, store.driveSpeed)

    def testConstructor_025(self):
        """
        Test assignment of driveSpeed attribute, invalid value (not an integer).
        """
        store = StoreConfig()
        self.assertEqual(None, store.driveSpeed)
        self.failUnlessAssignRaises(ValueError, store, "driveSpeed", "blech")
        self.assertEqual(None, store.driveSpeed)
        self.failUnlessAssignRaises(ValueError, store, "driveSpeed", CollectDir())
        self.assertEqual(None, store.driveSpeed)

    def testConstructor_026(self):
        """
        Test assignment of checkData attribute, None value.
        """
        store = StoreConfig(checkData=True)
        self.assertEqual(True, store.checkData)
        store.checkData = None
        self.assertEqual(False, store.checkData)

    def testConstructor_027(self):
        """
        Test assignment of checkData attribute, valid value (real boolean).
        """
        store = StoreConfig()
        self.assertEqual(False, store.checkData)
        store.checkData = True
        self.assertEqual(True, store.checkData)
        store.checkData = False
        self.assertEqual(False, store.checkData)

    def testConstructor_028(self):
        """
        Test assignment of checkData attribute, valid value (expression).
        """
        store = StoreConfig()
        self.assertEqual(False, store.checkData)
        store.checkData = 0
        self.assertEqual(False, store.checkData)
        store.checkData = []
        self.assertEqual(False, store.checkData)
        store.checkData = None
        self.assertEqual(False, store.checkData)
        store.checkData = ["a"]
        self.assertEqual(True, store.checkData)
        store.checkData = 3
        self.assertEqual(True, store.checkData)

    def testConstructor_029(self):
        """
        Test assignment of warnMidnite attribute, None value.
        """
        store = StoreConfig(warnMidnite=True)
        self.assertEqual(True, store.warnMidnite)
        store.warnMidnite = None
        self.assertEqual(False, store.warnMidnite)

    def testConstructor_030(self):
        """
        Test assignment of warnMidnite attribute, valid value (real boolean).
        """
        store = StoreConfig()
        self.assertEqual(False, store.warnMidnite)
        store.warnMidnite = True
        self.assertEqual(True, store.warnMidnite)
        store.warnMidnite = False
        self.assertEqual(False, store.warnMidnite)

    def testConstructor_031(self):
        """
        Test assignment of warnMidnite attribute, valid value (expression).
        """
        store = StoreConfig()
        self.assertEqual(False, store.warnMidnite)
        store.warnMidnite = 0
        self.assertEqual(False, store.warnMidnite)
        store.warnMidnite = []
        self.assertEqual(False, store.warnMidnite)
        store.warnMidnite = None
        self.assertEqual(False, store.warnMidnite)
        store.warnMidnite = ["a"]
        self.assertEqual(True, store.warnMidnite)
        store.warnMidnite = 3
        self.assertEqual(True, store.warnMidnite)

    def testConstructor_032(self):
        """
        Test assignment of noEject attribute, None value.
        """
        store = StoreConfig(noEject=True)
        self.assertEqual(True, store.noEject)
        store.noEject = None
        self.assertEqual(False, store.noEject)

    def testConstructor_033(self):
        """
        Test assignment of noEject attribute, valid value (real boolean).
        """
        store = StoreConfig()
        self.assertEqual(False, store.noEject)
        store.noEject = True
        self.assertEqual(True, store.noEject)
        store.noEject = False
        self.assertEqual(False, store.noEject)

    def testConstructor_034(self):
        """
        Test assignment of noEject attribute, valid value (expression).
        """
        store = StoreConfig()
        self.assertEqual(False, store.noEject)
        store.noEject = 0
        self.assertEqual(False, store.noEject)
        store.noEject = []
        self.assertEqual(False, store.noEject)
        store.noEject = None
        self.assertEqual(False, store.noEject)
        store.noEject = ["a"]
        self.assertEqual(True, store.noEject)
        store.noEject = 3
        self.assertEqual(True, store.noEject)

    def testConstructor_035(self):
        """
        Test assignment of checkMedia attribute, None value.
        """
        store = StoreConfig(checkMedia=True)
        self.assertEqual(True, store.checkMedia)
        store.checkMedia = None
        self.assertEqual(False, store.checkMedia)

    def testConstructor_036(self):
        """
        Test assignment of checkMedia attribute, valid value (real boolean).
        """
        store = StoreConfig()
        self.assertEqual(False, store.checkMedia)
        store.checkMedia = True
        self.assertEqual(True, store.checkMedia)
        store.checkMedia = False
        self.assertEqual(False, store.checkMedia)

    def testConstructor_037(self):
        """
        Test assignment of checkMedia attribute, valid value (expression).
        """
        store = StoreConfig()
        self.assertEqual(False, store.checkMedia)
        store.checkMedia = 0
        self.assertEqual(False, store.checkMedia)
        store.checkMedia = []
        self.assertEqual(False, store.checkMedia)
        store.checkMedia = None
        self.assertEqual(False, store.checkMedia)
        store.checkMedia = ["a"]
        self.assertEqual(True, store.checkMedia)
        store.checkMedia = 3
        self.assertEqual(True, store.checkMedia)

    def testConstructor_038(self):
        """
        Test assignment of blankBehavior attribute, None value.
        """
        store = StoreConfig()
        store.blankBehavior = None
        self.assertEqual(None, store.blankBehavior)

    def testConstructor_039(self):
        """
        Test assignment of blankBehavior store attribute, valid value.
        """
        store = StoreConfig()
        store.blankBehavior = BlankBehavior()
        self.assertEqual(BlankBehavior(), store.blankBehavior)

    def testConstructor_040(self):
        """
        Test assignment of blankBehavior store attribute, invalid value (not BlankBehavior).
        """
        store = StoreConfig()
        self.failUnlessAssignRaises(ValueError, store, "blankBehavior", CollectDir())

    def testConstructor_041(self):
        """
        Test assignment of refreshMediaDelay attribute, None value.
        """
        store = StoreConfig(refreshMediaDelay=4)
        self.assertEqual(4, store.refreshMediaDelay)
        store.refreshMediaDelay = None
        self.assertEqual(None, store.refreshMediaDelay)

    def testConstructor_042(self):
        """
        Test assignment of refreshMediaDelay attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.refreshMediaDelay)
        store.refreshMediaDelay = 4
        self.assertEqual(4, store.refreshMediaDelay)
        store.refreshMediaDelay = "12"
        self.assertEqual(12, store.refreshMediaDelay)
        store.refreshMediaDelay = "0"
        self.assertEqual(None, store.refreshMediaDelay)
        store.refreshMediaDelay = 0
        self.assertEqual(None, store.refreshMediaDelay)

    def testConstructor_043(self):
        """
        Test assignment of refreshMediaDelay attribute, invalid value (not an integer).
        """
        store = StoreConfig()
        self.assertEqual(None, store.refreshMediaDelay)
        self.failUnlessAssignRaises(ValueError, store, "refreshMediaDelay", "blech")
        self.assertEqual(None, store.refreshMediaDelay)
        self.failUnlessAssignRaises(ValueError, store, "refreshMediaDelay", CollectDir())
        self.assertEqual(None, store.refreshMediaDelay)

    def testConstructor_044(self):
        """
        Test assignment of ejectDelay attribute, None value.
        """
        store = StoreConfig(ejectDelay=4)
        self.assertEqual(4, store.ejectDelay)
        store.ejectDelay = None
        self.assertEqual(None, store.ejectDelay)

    def testConstructor_045(self):
        """
        Test assignment of ejectDelay attribute, valid value.
        """
        store = StoreConfig()
        self.assertEqual(None, store.ejectDelay)
        store.ejectDelay = 4
        self.assertEqual(4, store.ejectDelay)
        store.ejectDelay = "12"
        self.assertEqual(12, store.ejectDelay)
        store.ejectDelay = "0"
        self.assertEqual(None, store.ejectDelay)
        store.ejectDelay = 0
        self.assertEqual(None, store.ejectDelay)

    def testConstructor_046(self):
        """
        Test assignment of ejectDelay attribute, invalid value (not an integer).
        """
        store = StoreConfig()
        self.assertEqual(None, store.ejectDelay)
        self.failUnlessAssignRaises(ValueError, store, "ejectDelay", "blech")
        self.assertEqual(None, store.ejectDelay)
        self.failUnlessAssignRaises(ValueError, store, "ejectDelay", CollectDir())
        self.assertEqual(None, store.ejectDelay)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        store1 = StoreConfig()
        store2 = StoreConfig()
        self.assertEqual(store1, store2)
        self.assertTrue(store1 == store2)
        self.assertTrue(not store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(store1 >= store2)
        self.assertTrue(not store1 != store2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertEqual(store1, store2)
        self.assertTrue(store1 == store2)
        self.assertTrue(not store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(store1 >= store2)
        self.assertTrue(not store1 != store2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, sourceDir differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(sourceDir="/whatever")
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, sourceDir differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source1", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source2", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, mediaType differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(mediaType="cdr-74")
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, mediaType differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdrw-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(not store1 < store2)
        self.assertTrue(not store1 <= store2)
        self.assertTrue(store1 > store2)
        self.assertTrue(store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, deviceType differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(deviceType="cdwriter")
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, devicePath differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(devicePath="/dev/cdrw")
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, devicePath differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/hdd", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, deviceScsiId differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(deviceScsiId="0,0,0")
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, deviceScsiId differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "ATA:0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, driveSpeed differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(driveSpeed=3)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, driveSpeed differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 1, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, checkData differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, False, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, warnMidnite differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, False, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, noEject differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, False, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, checkMedia differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, False, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, blankBehavior differs (one None).
        """
        behavior = BlankBehavior()
        store1 = StoreConfig()
        store2 = StoreConfig(blankBehavior=behavior)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, blankBehavior differs.
        """
        behavior1 = BlankBehavior("daily", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior1, 4, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 4, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_020(self):
        """
        Test comparison of two differing objects, refreshMediaDelay differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(refreshMediaDelay=3)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_021(self):
        """
        Test comparison of two differing objects, refreshMediaDelay differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 1, True, True, True, True, behavior1, 1, 5)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 1, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_022(self):
        """
        Test comparison of two differing objects, ejectDelay differs (one None).
        """
        store1 = StoreConfig()
        store2 = StoreConfig(ejectDelay=3)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)

    def testComparison_023(self):
        """
        Test comparison of two differing objects, ejectDelay differs.
        """
        behavior1 = BlankBehavior("weekly", "1.3")
        behavior2 = BlankBehavior("weekly", "1.3")
        store1 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 1, True, True, True, True, behavior1, 4, 1)
        store2 = StoreConfig("/source", "cdr-74", "cdwriter", "/dev/cdrw", "0,0,0", 1, True, True, True, True, behavior2, 4, 5)
        self.assertNotEqual(store1, store2)
        self.assertTrue(not store1 == store2)
        self.assertTrue(store1 < store2)
        self.assertTrue(store1 <= store2)
        self.assertTrue(not store1 > store2)
        self.assertTrue(not store1 >= store2)
        self.assertTrue(store1 != store2)


########################
# TestPurgeConfig class
########################


class TestPurgeConfig(unittest.TestCase):

    """Tests for the PurgeConfig class."""

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
        obj = PurgeConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values (empty list).
        """
        purge = PurgeConfig([])
        self.assertEqual([], purge.purgeDirs)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values (non-empty list).
        """
        purge = PurgeConfig([PurgeDir()])
        self.assertEqual([PurgeDir()], purge.purgeDirs)

    def testConstructor_004(self):
        """
        Test assignment of purgeDirs attribute, None value.
        """
        purge = PurgeConfig([])
        self.assertEqual([], purge.purgeDirs)
        purge.purgeDirs = None
        self.assertEqual(None, purge.purgeDirs)

    def testConstructor_005(self):
        """
        Test assignment of purgeDirs attribute, [] value.
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)
        purge.purgeDirs = []
        self.assertEqual([], purge.purgeDirs)

    def testConstructor_006(self):
        """
        Test assignment of purgeDirs attribute, single valid entry.
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)
        purge.purgeDirs = [
            PurgeDir(),
        ]
        self.assertEqual([PurgeDir()], purge.purgeDirs)

    def testConstructor_007(self):
        """
        Test assignment of purgeDirs attribute, multiple valid entries.
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)
        purge.purgeDirs = [
            PurgeDir("/one"),
            PurgeDir("/two"),
        ]
        self.assertEqual([PurgeDir("/one"), PurgeDir("/two")], purge.purgeDirs)

    def testConstructor_009(self):
        """
        Test assignment of purgeDirs attribute, single invalid entry (not a
        PurgeDir).
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)
        self.failUnlessAssignRaises(ValueError, purge, "purgeDirs", [RemotePeer()])
        self.assertEqual(None, purge.purgeDirs)

    def testConstructor_010(self):
        """
        Test assignment of purgeDirs attribute, mixed valid and invalid entries.
        """
        purge = PurgeConfig()
        self.assertEqual(None, purge.purgeDirs)
        self.failUnlessAssignRaises(ValueError, purge, "purgeDirs", [PurgeDir(), RemotePeer()])
        self.assertEqual(None, purge.purgeDirs)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        purge1 = PurgeConfig()
        purge2 = PurgeConfig()
        self.assertEqual(purge1, purge2)
        self.assertTrue(purge1 == purge2)
        self.assertTrue(not purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(purge1 >= purge2)
        self.assertTrue(not purge1 != purge2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None (empty
        lists).
        """
        purge1 = PurgeConfig([])
        purge2 = PurgeConfig([])
        self.assertEqual(purge1, purge2)
        self.assertTrue(purge1 == purge2)
        self.assertTrue(not purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(purge1 >= purge2)
        self.assertTrue(not purge1 != purge2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None
        (non-empty lists).
        """
        purge1 = PurgeConfig([PurgeDir()])
        purge2 = PurgeConfig([PurgeDir()])
        self.assertEqual(purge1, purge2)
        self.assertTrue(purge1 == purge2)
        self.assertTrue(not purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(purge1 >= purge2)
        self.assertTrue(not purge1 != purge2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, purgeDirs differs (one None,
        one empty).
        """
        purge1 = PurgeConfig(None)
        purge2 = PurgeConfig([])
        self.assertNotEqual(purge1, purge2)
        self.assertTrue(not purge1 == purge2)
        self.assertTrue(purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(not purge1 >= purge2)
        self.assertTrue(purge1 != purge2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, purgeDirs differs (one None,
        one not empty).
        """
        purge1 = PurgeConfig(None)
        purge2 = PurgeConfig([PurgeDir()])
        self.assertNotEqual(purge1, purge2)
        self.assertTrue(not purge1 == purge2)
        self.assertTrue(purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(not purge1 >= purge2)
        self.assertTrue(purge1 != purge2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, purgeDirs differs (one empty,
        one not empty).
        """
        purge1 = PurgeConfig([])
        purge2 = PurgeConfig([PurgeDir()])
        self.assertNotEqual(purge1, purge2)
        self.assertTrue(not purge1 == purge2)
        self.assertTrue(purge1 < purge2)
        self.assertTrue(purge1 <= purge2)
        self.assertTrue(not purge1 > purge2)
        self.assertTrue(not purge1 >= purge2)
        self.assertTrue(purge1 != purge2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, purgeDirs differs (both not
        empty).
        """
        purge1 = PurgeConfig([PurgeDir("/two")])
        purge2 = PurgeConfig([PurgeDir("/one")])
        self.assertNotEqual(purge1, purge2)
        self.assertTrue(not purge1 == purge2)
        self.assertTrue(not purge1 < purge2)
        self.assertTrue(not purge1 <= purge2)
        self.assertTrue(purge1 > purge2)
        self.assertTrue(purge1 >= purge2)
        self.assertTrue(purge1 != purge2)


###################
# TestConfig class
###################


class TestConfig(unittest.TestCase):

    """Tests for the Config class."""

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

    ############################
    # Test __repr__ and __str__
    ############################

    def testStringFuncs_001(self):
        """
        Just make sure that the string functions don't have errors (i.e. bad variable names).
        """
        obj = Config()
        obj.__repr__()
        obj.__str__()

    #####################################################
    # Test basic constructor and attribute functionality
    #####################################################

    def testConstructor_001(self):
        """
        Test empty constructor, validate=False.
        """
        config = Config(validate=False)
        self.assertEqual(None, config.reference)
        self.assertEqual(None, config.extensions)
        self.assertEqual(None, config.options)
        self.assertEqual(None, config.peers)
        self.assertEqual(None, config.collect)
        self.assertEqual(None, config.stage)
        self.assertEqual(None, config.store)
        self.assertEqual(None, config.purge)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = Config(validate=True)
        self.assertEqual(None, config.reference)
        self.assertEqual(None, config.extensions)
        self.assertEqual(None, config.options)
        self.assertEqual(None, config.peers)
        self.assertEqual(None, config.collect)
        self.assertEqual(None, config.stage)
        self.assertEqual(None, config.store)
        self.assertEqual(None, config.purge)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["cback.conf.2"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, Config, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test with empty config document as data, validate=False.
        """
        path = self.resources["cback.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = Config(xmlData=contents, validate=False)
        self.assertEqual(None, config.reference)
        self.assertEqual(None, config.extensions)
        self.assertEqual(None, config.options)
        self.assertEqual(None, config.peers)
        self.assertEqual(None, config.collect)
        self.assertEqual(None, config.stage)
        self.assertEqual(None, config.store)
        self.assertEqual(None, config.purge)

    def testConstructor_005(self):
        """
        Test with empty config document in a file, validate=False.
        """
        path = self.resources["cback.conf.2"]
        config = Config(xmlPath=path, validate=False)
        self.assertEqual(None, config.reference)
        self.assertEqual(None, config.extensions)
        self.assertEqual(None, config.options)
        self.assertEqual(None, config.peers)
        self.assertEqual(None, config.collect)
        self.assertEqual(None, config.stage)
        self.assertEqual(None, config.store)
        self.assertEqual(None, config.purge)

    def testConstructor_006(self):
        """
        Test assignment of reference attribute, None value.
        """
        config = Config()
        config.reference = None
        self.assertEqual(None, config.reference)

    def testConstructor_007(self):
        """
        Test assignment of reference attribute, valid value.
        """
        config = Config()
        config.reference = ReferenceConfig()
        self.assertEqual(ReferenceConfig(), config.reference)

    def testConstructor_008(self):
        """
        Test assignment of reference attribute, invalid value (not ReferenceConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "reference", CollectDir())

    def testConstructor_009(self):
        """
        Test assignment of extensions attribute, None value.
        """
        config = Config()
        config.extensions = None
        self.assertEqual(None, config.extensions)

    def testConstructor_010(self):
        """
        Test assignment of extensions attribute, valid value.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        self.assertEqual(ExtensionsConfig(), config.extensions)

    def testConstructor_011(self):
        """
        Test assignment of extensions attribute, invalid value (not ExtensionsConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "extensions", CollectDir())

    def testConstructor_012(self):
        """
        Test assignment of options attribute, None value.
        """
        config = Config()
        config.options = None
        self.assertEqual(None, config.options)

    def testConstructor_013(self):
        """
        Test assignment of options attribute, valid value.
        """
        config = Config()
        config.options = OptionsConfig()
        self.assertEqual(OptionsConfig(), config.options)

    def testConstructor_014(self):
        """
        Test assignment of options attribute, invalid value (not OptionsConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "options", CollectDir())

    def testConstructor_015(self):
        """
        Test assignment of collect attribute, None value.
        """
        config = Config()
        config.collect = None
        self.assertEqual(None, config.collect)

    def testConstructor_016(self):
        """
        Test assignment of collect attribute, valid value.
        """
        config = Config()
        config.collect = CollectConfig()
        self.assertEqual(CollectConfig(), config.collect)

    def testConstructor_017(self):
        """
        Test assignment of collect attribute, invalid value (not CollectConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "collect", CollectDir())

    def testConstructor_018(self):
        """
        Test assignment of stage attribute, None value.
        """
        config = Config()
        config.stage = None
        self.assertEqual(None, config.stage)

    def testConstructor_019(self):
        """
        Test assignment of stage attribute, valid value.
        """
        config = Config()
        config.stage = StageConfig()
        self.assertEqual(StageConfig(), config.stage)

    def testConstructor_020(self):
        """
        Test assignment of stage attribute, invalid value (not StageConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "stage", CollectDir())

    def testConstructor_021(self):
        """
        Test assignment of store attribute, None value.
        """
        config = Config()
        config.store = None
        self.assertEqual(None, config.store)

    def testConstructor_022(self):
        """
        Test assignment of store attribute, valid value.
        """
        config = Config()
        config.store = StoreConfig()
        self.assertEqual(StoreConfig(), config.store)

    def testConstructor_023(self):
        """
        Test assignment of store attribute, invalid value (not StoreConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "store", CollectDir())

    def testConstructor_024(self):
        """
        Test assignment of purge attribute, None value.
        """
        config = Config()
        config.purge = None
        self.assertEqual(None, config.purge)

    def testConstructor_025(self):
        """
        Test assignment of purge attribute, valid value.
        """
        config = Config()
        config.purge = PurgeConfig()
        self.assertEqual(PurgeConfig(), config.purge)

    def testConstructor_026(self):
        """
        Test assignment of purge attribute, invalid value (not PurgeConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "purge", CollectDir())

    def testConstructor_027(self):
        """
        Test assignment of peers attribute, None value.
        """
        config = Config()
        config.peers = None
        self.assertEqual(None, config.peers)

    def testConstructor_028(self):
        """
        Test assignment of peers attribute, valid value.
        """
        config = Config()
        config.peers = PeersConfig()
        self.assertEqual(PeersConfig(), config.peers)

    def testConstructor_029(self):
        """
        Test assignment of peers attribute, invalid value (not PeersConfig).
        """
        config = Config()
        self.failUnlessAssignRaises(ValueError, config, "peers", CollectDir())

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        config1 = Config()
        config2 = Config()
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
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.extensions = ExtensionsConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.extensions = ExtensionsConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, reference differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.reference = ReferenceConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, reference differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig(author="one")
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig(author="two")
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, extensions differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.extensions = ExtensionsConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, extensions differs (one list empty, one None).
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.extensions = ExtensionsConfig(None)
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.extensions = ExtensionsConfig([])
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, extensions differs (one list empty, one not empty).
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.extensions = ExtensionsConfig([])
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.extensions = ExtensionsConfig([ExtendedAction("one", "two", "three")])
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, extensions differs (both lists not empty).
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.extensions = ExtensionsConfig([ExtendedAction("one", "two", "three")])
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.extensions = ExtensionsConfig([ExtendedAction("one", "two", "four")])
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(not config1 <= config2)
        self.assertTrue(config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, options differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.options = OptionsConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, options differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.options = OptionsConfig(startingDay="tuesday")
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.options = OptionsConfig(startingDay="monday")
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(not config1 <= config2)
        self.assertTrue(config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, collect differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.collect = CollectConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, collect differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig(collectMode="daily")
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig(collectMode="incr")
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, stage differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.stage = StageConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, stage differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig(targetDir="/something")
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig(targetDir="/whatever")
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, store differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.store = StoreConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, store differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig(deviceScsiId="ATA:0,0,0")
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig(deviceScsiId="0,0,0")
        config2.purge = PurgeConfig()

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(not config1 <= config2)
        self.assertTrue(config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_017(self):
        """
        Test comparison of two differing objects, purge differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.purge = PurgeConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_018(self):
        """
        Test comparison of two differing objects, purge differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig(purgeDirs=None)

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig()
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig(purgeDirs=[])

        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_019(self):
        """
        Test comparison of two differing objects, peers differs (one None).
        """
        config1 = Config()
        config2 = Config()
        config2.peers = PeersConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_020(self):
        """
        Test comparison of two identical objects, peers differs.
        """
        config1 = Config()
        config1.reference = ReferenceConfig()
        config1.extensions = ExtensionsConfig()
        config1.options = OptionsConfig()
        config1.peers = PeersConfig()
        config1.collect = CollectConfig()
        config1.stage = StageConfig()
        config1.store = StoreConfig()
        config1.purge = PurgeConfig()

        config2 = Config()
        config2.reference = ReferenceConfig()
        config2.extensions = ExtensionsConfig()
        config2.options = OptionsConfig()
        config2.peers = PeersConfig(localPeers=[LocalPeer()])
        config2.collect = CollectConfig()
        config2.stage = StageConfig()
        config2.store = StoreConfig()
        config2.purge = PurgeConfig()

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
        Test validate on an empty reference section.
        """
        config = Config()
        config.reference = ReferenceConfig()
        config._validateReference()

    def testValidate_002(self):
        """
        Test validate on a non-empty reference section, with everything filled in.
        """
        config = Config()
        config.reference = ReferenceConfig("author", "revision", "description", "generator")
        config._validateReference()

    def testValidate_003(self):
        """
        Test validate on an empty extensions section, with a None list.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = None
        config._validateExtensions()

    def testValidate_004(self):
        """
        Test validate on an empty extensions section, with [] for the list.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = []
        config._validateExtensions()

    def testValidate_005(self):
        """
        Test validate on an a extensions section, with one empty extended action.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction(),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_006(self):
        """
        Test validate on an a extensions section, with one extended action that
        has only a name.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction(name="name"),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_007(self):
        """
        Test validate on an a extensions section, with one extended action that
        has only a module.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction(module="module"),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_008(self):
        """
        Test validate on an a extensions section, with one extended action that
        has only a function.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction(function="function"),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_009(self):
        """
        Test validate on an a extensions section, with one extended action that
        has only an index.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction(index=12),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_010(self):
        """
        Test validate on an a extensions section, with one extended action that
        makes sense, index order mode.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "index"
        config.extensions.actions = [ExtendedAction("one", "two", "three", 100)]
        config._validateExtensions()

    def testValidate_011(self):
        """
        Test validate on an a extensions section, with one extended action that
        makes sense, dependency order mode.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "dependency"
        config.extensions.actions = [ExtendedAction("one", "two", "three", dependencies=ActionDependencies())]
        config._validateExtensions()

    def testValidate_012(self):
        """
        Test validate on an a extensions section, with several extended actions
        that make sense for various kinds of order modes.
        """
        config = Config()

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", 1),
            ExtendedAction("e", "f", "g", 10),
        ]
        config._validateExtensions()

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "index"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", 1),
            ExtendedAction("e", "f", "g", 10),
        ]
        config._validateExtensions()

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "dependency"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("e", "f", "g", dependencies=ActionDependencies()),
        ]
        config._validateExtensions()

    def testValidate_012a(self):
        """
        Test validate on an a extensions section, with several extended actions
        that don't have the proper ordering modes.
        """
        config = Config()

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = None
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("e", "f", "g", dependencies=ActionDependencies()),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "index"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("e", "f", "g", dependencies=ActionDependencies()),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "dependency"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", 100),
            ExtendedAction("e", "f", "g", 12),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "index"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", 12),
            ExtendedAction("e", "f", "g", dependencies=ActionDependencies()),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "dependency"
        config.extensions.actions = [
            ExtendedAction("a", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("e", "f", "g", 12),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_013(self):
        """
        Test validate on an empty options section.
        """
        config = Config()
        config.options = OptionsConfig()
        self.assertRaises(ValueError, config._validateOptions)

    def testValidate_014(self):
        """
        Test validate on a non-empty options section, with everything filled in.
        """
        config = Config()
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config._validateOptions()

    def testValidate_015(self):
        """
        Test validate on a non-empty options section, with individual items missing.
        """
        config = Config()
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config._validateOptions()
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config.options.startingDay = None
        self.assertRaises(ValueError, config._validateOptions)
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config.options.workingDir = None
        self.assertRaises(ValueError, config._validateOptions)
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config.options.backupUser = None
        self.assertRaises(ValueError, config._validateOptions)
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config.options.backupGroup = None
        self.assertRaises(ValueError, config._validateOptions)
        config.options = OptionsConfig("monday", "/whatever", "user", "group", "command")
        config.options.rcpCommand = None
        self.assertRaises(ValueError, config._validateOptions)

    def testValidate_016(self):
        """
        Test validate on an empty collect section.
        """
        config = Config()
        config.collect = CollectConfig()
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_017(self):
        """
        Test validate on collect section containing only targetDir.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config._validateCollect()  # we no longer validate that at least one file or dir is required here

    def testValidate_018(self):
        """
        Test validate on collect section containing only targetDir and one
        collectDirs entry that is empty.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_018a(self):
        """
        Test validate on collect section containing only targetDir and one
        collectFiles entry that is empty.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectFiles = [
            CollectFile(),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_019(self):
        """
        Test validate on collect section containing only targetDir and one
        collectDirs entry with only a path.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff"),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_019a(self):
        """
        Test validate on collect section containing only targetDir and one
        collectFiles entry with only a path.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectFiles = [
            CollectFile(absolutePath="/stuff"),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_020(self):
        """
        Test validate on collect section containing only targetDir and one
        collectDirs entry with path, collect mode, archive mode and ignore file.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i"),
        ]
        config._validateCollect()

    def testValidate_020a(self):
        """
        Test validate on collect section containing only targetDir and one
        collectFiles entry with path, collect mode and archive mode.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectFiles = [
            CollectFile(absolutePath="/stuff", collectMode="incr", archiveMode="tar"),
        ]
        config._validateCollect()

    def testValidate_021(self):
        """
        Test validate on collect section containing targetDir, collect mode,
        archive mode and ignore file, and one collectDirs entry with only a path.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectMode = "incr"
        config.collect.archiveMode = "tar"
        config.collect.ignoreFile = "ignore"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff"),
        ]
        config._validateCollect()

    def testValidate_021a(self):
        """
        Test validate on collect section containing targetDir, collect mode,
        archive mode and ignore file, and one collectFiles entry with only a path.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectMode = "incr"
        config.collect.archiveMode = "tar"
        config.collect.ignoreFile = "ignore"
        config.collect.collectFiles = [
            CollectFile(absolutePath="/stuff"),
        ]
        config._validateCollect()

    def testValidate_022(self):
        """
        Test validate on collect section containing targetDir, but with collect mode,
        archive mode and ignore file mixed between main section and directories.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.archiveMode = "tar"
        config.collect.ignoreFile = "ignore"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff", collectMode="incr", ignoreFile="i"),
        ]
        config._validateCollect()
        config.collect.collectDirs.append(CollectDir(absolutePath="/stuff2"))
        self.assertRaises(ValueError, config._validateCollect)
        config.collect.collectDirs[-1].collectMode = "daily"
        config._validateCollect()

    def testValidate_022a(self):
        """
        Test validate on collect section containing targetDir, but with collect mode,
        and archive mode mixed between main section and directories.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.archiveMode = "tar"
        config.collect.collectFiles = [
            CollectFile(absolutePath="/stuff", collectMode="incr", archiveMode="targz"),
        ]
        config._validateCollect()
        config.collect.collectFiles.append(CollectFile(absolutePath="/stuff2"))
        self.assertRaises(ValueError, config._validateCollect)
        config.collect.collectFiles[-1].collectMode = "daily"
        config._validateCollect()

    def testValidate_023(self):
        """
        Test validate on an empty stage section.
        """
        config = Config()
        config.stage = StageConfig()
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_024(self):
        """
        Test validate on stage section containing only targetDir and None for the
        lists.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = None
        config.stage.remotePeers = None
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_025(self):
        """
        Test validate on stage section containing only targetDir and [] for the
        lists.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = []
        config.stage.remotePeers = []
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_026(self):
        """
        Test validate on stage section containing targetDir and one local peer
        that is empty.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_027(self):
        """
        Test validate on stage section containing targetDir and one local peer
        with only a name.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(name="name"),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_028(self):
        """
        Test validate on stage section containing targetDir and one local peer
        with a name and path, None for remote list.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(name="name", collectDir="/somewhere"),
        ]
        config.stage.remotePeers = None
        config._validateStage()

    def testValidate_029(self):
        """
        Test validate on stage section containing targetDir and one local peer
        with a name and path, [] for remote list.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(name="name", collectDir="/somewhere"),
        ]
        config.stage.remotePeers = []
        config._validateStage()

    def testValidate_030(self):
        """
        Test validate on stage section containing targetDir and one remote peer
        that is empty.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.remotePeers = [
            RemotePeer(),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_031(self):
        """
        Test validate on stage section containing targetDir and one remote peer
        with only a name.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.remotePeers = [
            RemotePeer(name="blech"),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_032(self):
        """
        Test validate on stage section containing targetDir and one remote peer
        with a name and path, None for local list.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = None
        config.stage.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validateStage)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validateStage()
        config.options = None
        self.assertRaises(ValueError, config._validateStage)
        config.stage.remotePeers[-1].remoteUser = "remote"
        config.stage.remotePeers[-1].rcpCommand = "command"
        config._validateStage()

    def testValidate_033(self):
        """
        Test validate on stage section containing targetDir and one remote peer
        with a name and path, [] for local list.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = []
        config.stage.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validateStage)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validateStage()
        config.options = None
        self.assertRaises(ValueError, config._validateStage)
        config.stage.remotePeers[-1].remoteUser = "remote"
        config.stage.remotePeers[-1].rcpCommand = "command"
        config._validateStage()

    def testValidate_034(self):
        """
        Test validate on stage section containing targetDir and one remote and
        one local peer.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(name="metoo", collectDir="/nowhere"),
        ]
        config.stage.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validateStage)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validateStage()
        config.options = None
        self.assertRaises(ValueError, config._validateStage)
        config.stage.remotePeers[-1].remoteUser = "remote"
        config.stage.remotePeers[-1].rcpCommand = "command"
        config._validateStage()

    def testValidate_035(self):
        """
        Test validate on stage section containing targetDir multiple remote and
        local peers.
        """
        config = Config()
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(name="metoo", collectDir="/nowhere"),
            LocalPeer("one", "/two"),
            LocalPeer("a", "/b"),
        ]
        config.stage.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
            RemotePeer("c", "/d"),
        ]
        self.assertRaises(ValueError, config._validateStage)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validateStage()
        config.options = None
        self.assertRaises(ValueError, config._validateStage)
        config.stage.remotePeers[-1].remoteUser = "remote"
        config.stage.remotePeers[-1].rcpCommand = "command"
        self.assertRaises(ValueError, config._validateStage)
        config.stage.remotePeers[0].remoteUser = "remote"
        config.stage.remotePeers[0].rcpCommand = "command"
        config._validateStage()

    def testValidate_036(self):
        """
        Test validate on an empty store section.
        """
        config = Config()
        config.store = StoreConfig()
        self.assertRaises(ValueError, config._validateStore)

    def testValidate_037(self):
        """
        Test validate on store section with everything filled in.
        """
        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdrw-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-80"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdrw-80"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "dvd+r"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "dvd+rw"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

    def testValidate_038(self):
        """
        Test validate on store section missing one each of required fields.
        """
        config = Config()
        config.store = StoreConfig()
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

    def testValidate_039(self):
        """
        Test validate on store section missing one each of device type, drive
        speed and capacity mode and the booleans.
        """
        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        config._validateStore()

    def testValidate_039a(self):
        """
        Test validate on store section with everything filled in, but mismatch device/media.
        """
        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-74"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdrw-74"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdr-80"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "cdrw-80"
        config.store.deviceType = "dvdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "dvd+rw"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

        config = Config()
        config.store = StoreConfig()
        config.store.sourceDir = "/source"
        config.store.mediaType = "dvd+r"
        config.store.deviceType = "cdwriter"
        config.store.devicePath = "/dev/cdrw"
        config.store.deviceScsiId = "0,0,0"
        config.store.driveSpeed = 4
        config.store.checkData = True
        config.store.checkMedia = True
        config.store.warnMidnite = True
        config.store.noEject = True
        self.assertRaises(ValueError, config._validateStore)

    def testValidate_040(self):
        """
        Test validate on an empty purge section, with a None list.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = None
        config._validatePurge()

    def testValidate_041(self):
        """
        Test validate on an empty purge section, with [] for the list.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = []
        config._validatePurge()

    def testValidate_042(self):
        """
        Test validate on an a purge section, with one empty purge dir.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = [
            PurgeDir(),
        ]
        self.assertRaises(ValueError, config._validatePurge)

    def testValidate_043(self):
        """
        Test validate on an a purge section, with one purge dir that has only a
        path.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = [
            PurgeDir(absolutePath="/whatever"),
        ]
        self.assertRaises(ValueError, config._validatePurge)

    def testValidate_044(self):
        """
        Test validate on an a purge section, with one purge dir that has only
        retain days.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = [
            PurgeDir(retainDays=3),
        ]
        self.assertRaises(ValueError, config._validatePurge)

    def testValidate_045(self):
        """
        Test validate on an a purge section, with one purge dir that makes sense.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = [
            PurgeDir(absolutePath="/whatever", retainDays=4),
        ]
        config._validatePurge()

    def testValidate_046(self):
        """
        Test validate on an a purge section, with several purge dirs that make
        sense.
        """
        config = Config()
        config.purge = PurgeConfig()
        config.purge.purgeDirs = [
            PurgeDir("/whatever", 4),
            PurgeDir("/etc/different", 12),
        ]
        config._validatePurge()

    def testValidate_047(self):
        """
        Test that we catch a duplicate extended action name.
        """
        config = Config()
        config.extensions = ExtensionsConfig()
        config.extensions.orderMode = "dependency"

        config.extensions.actions = [
            ExtendedAction("unique1", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("unique2", "f", "g", dependencies=ActionDependencies()),
        ]
        config._validateExtensions()

        config.extensions.actions = [
            ExtendedAction("duplicate", "b", "c", dependencies=ActionDependencies()),
            ExtendedAction("duplicate", "f", "g", dependencies=ActionDependencies()),
        ]
        self.assertRaises(ValueError, config._validateExtensions)

    def testValidate_048(self):
        """
        Test that we catch a duplicate local peer name in stage configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"

        config.stage.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
            LocalPeer(name="unique2", collectDir="/nowhere"),
        ]
        config._validateStage()

        config.stage.localPeers = [
            LocalPeer(name="duplicate", collectDir="/nowhere"),
            LocalPeer(name="duplicate", collectDir="/nowhere"),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_049(self):
        """
        Test that we catch a duplicate remote peer name in stage configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"

        config.stage.remotePeers = [
            RemotePeer(name="unique1", collectDir="/some/path/to/data"),
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]
        config._validateStage()

        config.stage.remotePeers = [
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_050(self):
        """
        Test that we catch a duplicate peer name duplicated between remote and
        local in stage configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.stage = StageConfig()
        config.stage.targetDir = "/whatever"

        config.stage.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.stage.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]
        config._validateStage()

        config.stage.localPeers = [
            LocalPeer(name="duplicate", collectDir="/nowhere"),
        ]
        config.stage.remotePeers = [
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_051(self):
        """
        Test validate on a None peers section.
        """
        config = Config()
        config.peers = None
        config._validatePeers()

    def testValidate_052(self):
        """
        Test validate on an empty peers section.
        """
        config = Config()
        config.peers = PeersConfig()
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_053(self):
        """
        Test validate on peers section containing None for the lists.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = None
        config.peers.remotePeers = None
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_054(self):
        """
        Test validate on peers section containing [] for the lists.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = []
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_055(self):
        """
        Test validate on peers section containing one local peer that is empty.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_056(self):
        """
        Test validate on peers section containing local peer with only a name.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(name="name"),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_057(self):
        """
        Test validate on peers section containing one local peer with a name and
        path, None for remote list.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(name="name", collectDir="/somewhere"),
        ]
        config.peers.remotePeers = None
        config._validatePeers()

    def testValidate_058(self):
        """
        Test validate on peers section containing one local peer with a name and
        path, [] for remote list.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(name="name", collectDir="/somewhere"),
        ]
        config.peers.remotePeers = []
        config._validatePeers()

    def testValidate_059(self):
        """
        Test validate on peers section containing one remote peer that is empty.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.remotePeers = [
            RemotePeer(),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_060(self):
        """
        Test validate on peers section containing one remote peer with only a name.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.remotePeers = [
            RemotePeer(name="blech"),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_061(self):
        """
        Test validate on peers section containing one remote peer with a name and
        path, None for local list.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = None
        config.peers.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validatePeers)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validatePeers()
        config.options = None
        self.assertRaises(ValueError, config._validatePeers)
        config.peers.remotePeers[-1].remoteUser = "remote"
        config.peers.remotePeers[-1].rcpCommand = "command"
        config._validatePeers()

    def testValidate_062(self):
        """
        Test validate on peers section containing one remote peer with a name and
        path, [] for local list.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validatePeers)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validatePeers()
        config.options = None
        self.assertRaises(ValueError, config._validatePeers)
        config.peers.remotePeers[-1].remoteUser = "remote"
        config.peers.remotePeers[-1].rcpCommand = "command"
        config._validatePeers()

    def testValidate_063(self):
        """
        Test validate on peers section containing one remote and one local peer.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(name="metoo", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validatePeers)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validatePeers()
        config.options = None
        self.assertRaises(ValueError, config._validatePeers)
        config.peers.remotePeers[-1].remoteUser = "remote"
        config.peers.remotePeers[-1].rcpCommand = "command"
        config._validatePeers()

    def testValidate_064(self):
        """
        Test validate on peers section containing multiple remote and local peers.
        """
        config = Config()
        config.peers = PeersConfig()
        config.peers.localPeers = [
            LocalPeer(name="metoo", collectDir="/nowhere"),
            LocalPeer("one", "/two"),
            LocalPeer("a", "/b"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="blech", collectDir="/some/path/to/data"),
            RemotePeer("c", "/d"),
        ]
        self.assertRaises(ValueError, config._validatePeers)
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config._validatePeers()
        config.options = None
        self.assertRaises(ValueError, config._validatePeers)
        config.peers.remotePeers[-1].remoteUser = "remote"
        config.peers.remotePeers[-1].rcpCommand = "command"
        self.assertRaises(ValueError, config._validatePeers)
        config.peers.remotePeers[0].remoteUser = "remote"
        config.peers.remotePeers[0].rcpCommand = "command"
        config._validatePeers()

    def testValidate_065(self):
        """
        Test that we catch a duplicate local peer name in peers configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
            LocalPeer(name="unique2", collectDir="/nowhere"),
        ]
        config._validatePeers()

        config.peers.localPeers = [
            LocalPeer(name="duplicate", collectDir="/nowhere"),
            LocalPeer(name="duplicate", collectDir="/nowhere"),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_066(self):
        """
        Test that we catch a duplicate remote peer name in peers configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()

        config.peers.remotePeers = [
            RemotePeer(name="unique1", collectDir="/some/path/to/data"),
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]
        config._validatePeers()

        config.peers.remotePeers = [
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_067(self):
        """
        Test that we catch a duplicate peer name duplicated between remote and
        local in peers configuration.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]
        config._validatePeers()

        config.peers.localPeers = [
            LocalPeer(name="duplicate", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="duplicate", collectDir="/some/path/to/data"),
        ]
        self.assertRaises(ValueError, config._validatePeers)

    def testValidate_068(self):
        """
        Test that stage peers can be None, if peers configuration is not None.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()
        config.stage = StageConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]

        config.stage.targetDir = "/whatever"
        config.stage.localPeers = None
        config.stage.remotePeers = None

        config._validatePeers()
        config._validateStage()

    def testValidate_069(self):
        """
        Test that stage peers can be empty lists, if peers configuration is not None.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()
        config.stage = StageConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]

        config.stage.targetDir = "/whatever"
        config.stage.localPeers = []
        config.stage.remotePeers = []

        config._validatePeers()
        config._validateStage()

    def testValidate_070(self):
        """
        Test that staging local peers must be valid if filled in, even if peers
        configuration is not None.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()
        config.stage = StageConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]

        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(),
        ]  # empty local peer is invalid, so validation should catch it
        config.stage.remotePeers = []

        config._validatePeers()
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_071(self):
        """
        Test that staging remote peers must be valid if filled in, even if peers
        configuration is not None.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()
        config.stage = StageConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]

        config.stage.targetDir = "/whatever"
        config.stage.localPeers = []
        config.stage.remotePeers = [
            RemotePeer(),
        ]  # empty remote peer is invalid, so validation should catch it

        config._validatePeers()
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_072(self):
        """
        Test that staging local and remote peers must be valid if filled in, even
        if peers configuration is not None.
        """
        config = Config()
        config.options = OptionsConfig(backupUser="ken", rcpCommand="command")
        config.peers = PeersConfig()
        config.stage = StageConfig()

        config.peers.localPeers = [
            LocalPeer(name="unique1", collectDir="/nowhere"),
        ]
        config.peers.remotePeers = [
            RemotePeer(name="unique2", collectDir="/some/path/to/data"),
        ]

        config.stage.targetDir = "/whatever"
        config.stage.localPeers = [
            LocalPeer(),
        ]  # empty local peer is invalid, so validation should catch it
        config.stage.remotePeers = [
            RemotePeer(),
        ]  # empty remote peer is invalid, so validation should catch it

        config._validatePeers()
        self.assertRaises(ValueError, config._validateStage)

    def testValidate_073(self):
        """
        Confirm that remote peer is required to have backup user if not set in options.
        """
        config = Config()
        config.options = OptionsConfig(
            backupUser="ken", rcpCommand="rcp", rshCommand="rsh", cbackCommand="cback", managedActions=["collect"]
        )
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="remote", collectDir="/path"),
        ]
        config._validatePeers()

        config.options.backupUser = None
        self.assertRaises(ValueError, config._validatePeers)

        config.peers.remotePeers[0].remoteUser = "ken"
        config._validatePeers()

    def testValidate_074(self):
        """
        Confirm that remote peer is required to have rcp command if not set in options.
        """
        config = Config()
        config.options = OptionsConfig(
            backupUser="ken", rcpCommand="rcp", rshCommand="rsh", cbackCommand="cback", managedActions=["collect"]
        )
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="remote", collectDir="/path"),
        ]
        config._validatePeers()

        config.options.rcpCommand = None
        self.assertRaises(ValueError, config._validatePeers)

        config.peers.remotePeers[0].rcpCommand = "rcp"
        config._validatePeers()

    def testValidate_075(self):
        """
        Confirm that remote managed peer is required to have rsh command if not set in options.
        """
        config = Config()
        config.options = OptionsConfig(
            backupUser="ken", rcpCommand="rcp", rshCommand="rsh", cbackCommand="cback", managedActions=["collect"]
        )
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="remote", collectDir="/path"),
        ]
        config._validatePeers()

        config.options.rshCommand = None
        config._validatePeers()

        config.peers.remotePeers[0].managed = True
        self.assertRaises(ValueError, config._validatePeers)

        config.peers.remotePeers[0].rshCommand = "rsh"
        config._validatePeers()

    def testValidate_076(self):
        """
        Confirm that remote managed peer is required to have cback command if not set in options.
        """
        config = Config()
        config.options = OptionsConfig(
            backupUser="ken", rcpCommand="rcp", rshCommand="rsh", cbackCommand="cback", managedActions=["collect"]
        )
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="remote", collectDir="/path"),
        ]
        config._validatePeers()

        config.options.cbackCommand = None
        config._validatePeers()

        config.peers.remotePeers[0].managed = True
        self.assertRaises(ValueError, config._validatePeers)

        config.peers.remotePeers[0].cbackCommand = "cback"
        config._validatePeers()

    def testValidate_077(self):
        """
        Confirm that remote managed peer is required to have managed actions list if not set in options.
        """
        config = Config()
        config.options = OptionsConfig(
            backupUser="ken", rcpCommand="rcp", rshCommand="rsh", cbackCommand="cback", managedActions=["collect"]
        )
        config.peers = PeersConfig()
        config.peers.localPeers = []
        config.peers.remotePeers = [
            RemotePeer(name="remote", collectDir="/path"),
        ]
        config._validatePeers()

        config.options.managedActions = None
        config._validatePeers()

        config.peers.remotePeers[0].managed = True
        self.assertRaises(ValueError, config._validatePeers)

        config.options.managedActions = []
        self.assertRaises(ValueError, config._validatePeers)

        config.peers.remotePeers[0].managedActions = [
            "collect",
        ]
        config._validatePeers()

    def testValidate_078(self):
        """
        Test case where dereference is True but link depth is None.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(
                absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=None, dereference=True
            ),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_079(self):
        """
        Test case where dereference is True but link depth is zero.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=0, dereference=True),
        ]
        self.assertRaises(ValueError, config._validateCollect)

    def testValidate_080(self):
        """
        Test case where dereference is False and linkDepth is None.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(
                absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=None, dereference=False
            ),
        ]
        config._validateCollect()

    def testValidate_081(self):
        """
        Test case where dereference is None and linkDepth is None.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(
                absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=None, dereference=None
            ),
        ]
        config._validateCollect()

    def testValidate_082(self):
        """
        Test case where dereference is False and linkDepth is zero.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(
                absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=0, dereference=False
            ),
        ]
        config._validateCollect()

    def testValidate_083(self):
        """
        Test case where dereference is None and linkDepth is zero.
        """
        config = Config()
        config.collect = CollectConfig()
        config.collect.targetDir = "/whatever"
        config.collect.collectDirs = [
            CollectDir(absolutePath="/stuff", collectMode="incr", archiveMode="tar", ignoreFile="i", linkDepth=0, dereference=None),
        ]
        config._validateCollect()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document, validate=False.
        """
        path = self.resources["cback.conf.2"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        self.assertEqual(expected, config)

    def testParse_002(self):
        """
        Parse empty config document, validate=True.
        """
        path = self.resources["cback.conf.2"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_003(self):
        """
        Parse config document containing only a reference section, containing
        only required fields, validate=False.
        """
        path = self.resources["cback.conf.3"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig()
        self.assertEqual(expected, config)

    def testParse_004(self):
        """
        Parse config document containing only a reference section, containing
        only required fields, validate=True.
        """
        path = self.resources["cback.conf.3"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_005(self):
        """
        Parse config document containing only a reference section, containing all
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.4"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        self.assertEqual(expected, config)

    def testParse_006(self):
        """
        Parse config document containing only a reference section, containing all
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.4"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_007(self):
        """
        Parse config document containing only a extensions section, containing
        only required fields, validate=False.
        """
        path = self.resources["cback.conf.16"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.extensions = ExtensionsConfig()
        expected.extensions.actions = []
        expected.extensions.actions.append(ExtendedAction("example", "something.whatever", "example", 1))
        self.assertEqual(expected, config)

    def testParse_008(self):
        """
        Parse config document containing only a extensions section, containing
        only required fields, validate=True.
        """
        path = self.resources["cback.conf.16"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_009(self):
        """
        Parse config document containing only a extensions section, containing
        all fields, order mode is "index", validate=False.
        """
        path = self.resources["cback.conf.18"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "index"
        expected.extensions.actions = []
        expected.extensions.actions.append(ExtendedAction("example", "something.whatever", "example", 1))
        self.assertEqual(expected, config)

    def testParse_009a(self):
        """
        Parse config document containing only a extensions section, containing
        all fields, order mode is "dependency", validate=False.
        """
        path = self.resources["cback.conf.19"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "dependency"
        expected.extensions.actions = []
        expected.extensions.actions.append(
            ExtendedAction("sysinfo", "CedarBackup3.extend.sysinfo", "executeAction", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction("mysql", "CedarBackup3.extend.mysql", "executeAction", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "postgresql",
                "CedarBackup3.extend.postgresql",
                "executeAction",
                index=None,
                dependencies=ActionDependencies(beforeList=["one"]),
            )
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "subversion",
                "CedarBackup3.extend.subversion",
                "executeAction",
                index=None,
                dependencies=ActionDependencies(afterList=["one"]),
            )
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "mbox",
                "CedarBackup3.extend.mbox",
                "executeAction",
                index=None,
                dependencies=ActionDependencies(beforeList=["one"], afterList=["one"]),
            )
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "encrypt",
                "CedarBackup3.extend.encrypt",
                "executeAction",
                index=None,
                dependencies=ActionDependencies(
                    beforeList=["a", "b", "c", "d"], afterList=["one", "two", "three", "four", "five", "six", "seven", "eight"]
                ),
            )
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "amazons3", "CedarBackup3.extend.amazons3", "executeAction", index=None, dependencies=ActionDependencies()
            )
        )
        self.assertEqual(expected, config)

    def testParse_010(self):
        """
        Parse config document containing only a extensions section, containing
        all fields, order mode is "index", validate=True.
        """
        path = self.resources["cback.conf.18"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_010a(self):
        """
        Parse config document containing only a extensions section, containing
        all fields, order mode is "dependency", validate=True.
        """
        path = self.resources["cback.conf.19"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_011(self):
        """
        Parse config document containing only an options section, containing only
        required fields, validate=False.
        """
        path = self.resources["cback.conf.5"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.options = OptionsConfig("tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B")
        self.assertEqual(expected, config)

    def testParse_012(self):
        """
        Parse config document containing only an options section, containing only
        required fields, validate=True.
        """
        path = self.resources["cback.conf.5"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_013(self):
        """
        Parse config document containing only an options section, containing
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.6"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        self.assertEqual(expected, config)

    def testParse_014(self):
        """
        Parse config document containing only an options section, containing
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.6"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_015(self):
        """
        Parse config document containing only a collect section, containing only
        required fields, validate=False.  (Case with single collect directory.)
        """
        path = self.resources["cback.conf.7"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "tar", ".ignore")
        expected.collect.collectDirs = [
            CollectDir(absolutePath="/etc"),
        ]
        self.assertEqual(expected, config)

    def testParse_015a(self):
        """
        Parse config document containing only a collect section, containing only
        required fields, validate=False.  (Case with single collect file.)
        """
        path = self.resources["cback.conf.17"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "tar", ".ignore")
        expected.collect.collectFiles = [
            CollectFile(absolutePath="/etc"),
        ]
        self.assertEqual(expected, config)

    def testParse_016(self):
        """
        Parse config document containing only a collect section, containing only
        required fields, validate=True.  (Case with single collect directory.)
        """
        path = self.resources["cback.conf.7"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_016a(self):
        """
        Parse config document containing only a collect section, containing only
        required fields, validate=True.  (Case with single collect file.)
        """
        path = self.resources["cback.conf.17"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_017(self):
        """
        Parse config document containing only a collect section, containing
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.8"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root", recursionLevel=1))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        self.assertEqual(expected, config)

    def testParse_018(self):
        """
        Parse config document containing only a collect section, containing
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.8"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_019(self):
        """
        Parse config document containing only a stage section, containing only
        required fields, validate=False.
        """
        path = self.resources["cback.conf.9"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = None
        expected.stage.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect"),
        ]
        self.assertEqual(expected, config)

    def testParse_020(self):
        """
        Parse config document containing only a stage section, containing only
        required fields, validate=True.
        """
        path = self.resources["cback.conf.9"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_021(self):
        """
        Parse config document containing only a stage section, containing all
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.10"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = []
        expected.stage.remotePeers = []
        expected.stage.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.stage.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.stage.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.stage.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        self.assertEqual(expected, config)

    def testParse_022(self):
        """
        Parse config document containing only a stage section, containing all
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.10"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_023(self):
        """
        Parse config document containing only a store section, containing only
        required fields, validate=False.
        """
        path = self.resources["cback.conf.11"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.store = StoreConfig("/opt/backup/staging", mediaType="cdrw-74", devicePath="/dev/cdrw", deviceScsiId=None)
        self.assertEqual(expected, config)

    def testParse_024(self):
        """
        Parse config document containing only a store section, containing only
        required fields, validate=True.
        """
        path = self.resources["cback.conf.11"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_025(self):
        """
        Parse config document containing only a store section, containing all
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.12"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "cdrw-74"
        expected.store.deviceType = "cdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = "0,0,0"
        expected.store.driveSpeed = 4
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.refreshMediaDelay = 12
        expected.store.ejectDelay = 13
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        self.assertEqual(expected, config)

    def testParse_026(self):
        """
        Parse config document containing only a store section, containing all
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.12"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_027(self):
        """
        Parse config document containing only a purge section, containing only
        required fields, validate=False.
        """
        path = self.resources["cback.conf.13"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = [
            PurgeDir("/opt/backup/stage", 5),
        ]
        self.assertEqual(expected, config)

    def testParse_028(self):
        """
        Parse config document containing only a purge section, containing only
        required fields, validate=True.
        """
        path = self.resources["cback.conf.13"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_029(self):
        """
        Parse config document containing only a purge section, containing all
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.14"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_030(self):
        """
        Parse config document containing only a purge section, containing all
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.14"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_031(self):
        """
        Parse complete document containing all required and optional fields, "index" extensions,
        validate=False.
        """
        path = self.resources["cback.conf.15"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "index"
        expected.extensions.actions = []
        expected.extensions.actions.append(ExtendedAction("example", "something.whatever", "example", 102))
        expected.extensions.actions.append(ExtendedAction("bogus", "module", "something", 350))
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = []
        expected.stage.remotePeers = []
        expected.stage.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.stage.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.stage.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.stage.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "cdrw-74"
        expected.store.deviceType = "cdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 4
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_031a(self):
        """
        Parse complete document containing all required and optional fields, "dependency" extensions,
        validate=False.
        """
        path = self.resources["cback.conf.20"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "dependency"
        expected.extensions.actions = []
        expected.extensions.actions.append(
            ExtendedAction("example", "something.whatever", "example", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "bogus",
                "module",
                "something",
                index=None,
                dependencies=ActionDependencies(beforeList=["a", "b", "c"], afterList=["one"]),
            )
        )
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = []
        expected.stage.remotePeers = []
        expected.stage.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.stage.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.stage.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.stage.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "dvd+rw"
        expected.store.deviceType = "dvdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 1
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_032(self):
        """
        Parse complete document containing all required and optional fields, "index" extensions,
        validate=True.
        """
        path = self.resources["cback.conf.15"]
        config = Config(xmlPath=path, validate=True)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "index"
        expected.extensions.actions = []
        expected.extensions.actions.append(ExtendedAction("example", "something.whatever", "example", 102))
        expected.extensions.actions.append(ExtendedAction("bogus", "module", "something", 350))
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = []
        expected.stage.remotePeers = []
        expected.stage.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.stage.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.stage.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.stage.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "cdrw-74"
        expected.store.deviceType = "cdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 4
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_032a(self):
        """
        Parse complete document containing all required and optional fields, "dependency" extensions,
        validate=True.
        """
        path = self.resources["cback.conf.20"]
        config = Config(xmlPath=path, validate=True)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "dependency"
        expected.extensions.actions = []
        expected.extensions.actions.append(
            ExtendedAction("example", "something.whatever", "example", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "bogus",
                "module",
                "something",
                index=None,
                dependencies=ActionDependencies(beforeList=["a", "b", "c"], afterList=["one"]),
            )
        )
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = []
        expected.stage.remotePeers = []
        expected.stage.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.stage.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.stage.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.stage.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "dvd+rw"
        expected.store.deviceType = "dvdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 1
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_033(self):
        """
        Parse a sample from Cedar Backup v1.x, which must still be valid,
        validate=False.
        """
        path = self.resources["cback.conf.1"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration")
        expected.options = OptionsConfig("tuesday", "/opt/backup/tmp", "backup", "backup", "/usr/bin/scp -1 -B")
        expected.collect = CollectConfig()
        expected.collect.targetDir = "/opt/backup/collect"
        expected.collect.archiveMode = "targz"
        expected.collect.ignoreFile = ".cbignore"
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir("/etc", collectMode="daily"))
        expected.collect.collectDirs.append(CollectDir("/var/log", collectMode="incr"))
        collectDir = CollectDir("/opt", collectMode="weekly")
        collectDir.absoluteExcludePaths = [
            "/opt/large",
            "/opt/backup",
            "/opt/tmp",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        expected.stage.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect", remoteUser="backup"),
        ]
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = "0,0,0"
        expected.store.driveSpeed = 4
        expected.store.mediaType = "cdrw-74"
        expected.store.checkData = True
        expected.store.checkMedia = False
        expected.store.warnMidnite = False
        expected.store.noEject = False
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        self.assertEqual(expected, config)

    def testParse_034(self):
        """
        Parse a sample from Cedar Backup v1.x, which must still be valid,
        validate=True.
        """
        path = self.resources["cback.conf.1"]
        config = Config(xmlPath=path, validate=True)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration")
        expected.options = OptionsConfig("tuesday", "/opt/backup/tmp", "backup", "backup", "/usr/bin/scp -1 -B")
        expected.collect = CollectConfig()
        expected.collect.targetDir = "/opt/backup/collect"
        expected.collect.archiveMode = "targz"
        expected.collect.ignoreFile = ".cbignore"
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir("/etc", collectMode="daily"))
        expected.collect.collectDirs.append(CollectDir("/var/log", collectMode="incr"))
        collectDir = CollectDir("/opt", collectMode="weekly")
        collectDir.absoluteExcludePaths = [
            "/opt/large",
            "/opt/backup",
            "/opt/tmp",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        expected.stage.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect", remoteUser="backup"),
        ]
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = "0,0,0"
        expected.store.driveSpeed = 4
        expected.store.mediaType = "cdrw-74"
        expected.store.checkData = True
        expected.store.checkMedia = False
        expected.store.warnMidnite = False
        expected.store.noEject = False
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        self.assertEqual(expected, config)

    def testParse_035(self):
        """
        Document containing all required fields, peers in peer configuration and not staging, validate=False.
        """
        path = self.resources["cback.conf.21"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "dependency"
        expected.extensions.actions = []
        expected.extensions.actions.append(
            ExtendedAction("example", "something.whatever", "example", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "bogus",
                "module",
                "something",
                index=None,
                dependencies=ActionDependencies(beforeList=["a", "b", "c"], afterList=["one"]),
            )
        )
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.peers = PeersConfig()
        expected.peers.localPeers = []
        expected.peers.remotePeers = []
        expected.peers.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.peers.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.peers.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.peers.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.peers.remotePeers.append(
            RemotePeer(
                "machine4",
                "/aa",
                remoteUser="someone",
                rcpCommand="scp -B",
                rshCommand="ssh",
                cbackCommand="cback",
                managed=True,
                managedActions=None,
            )
        )
        expected.peers.remotePeers.append(RemotePeer("machine5", "/bb", managed=False, managedActions=["collect", "purge"]))
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = None
        expected.stage.remotePeers = None
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "dvd+rw"
        expected.store.deviceType = "dvdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 1
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_036(self):
        """
        Document containing all required fields, peers in peer configuration and not staging, validate=True.
        """
        path = self.resources["cback.conf.21"]
        config = Config(xmlPath=path, validate=True)
        expected = Config()
        expected.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration", "Generated by hand.")
        expected.extensions = ExtensionsConfig()
        expected.extensions.orderMode = "dependency"
        expected.extensions.actions = []
        expected.extensions.actions.append(
            ExtendedAction("example", "something.whatever", "example", index=None, dependencies=ActionDependencies())
        )
        expected.extensions.actions.append(
            ExtendedAction(
                "bogus",
                "module",
                "something",
                index=None,
                dependencies=ActionDependencies(beforeList=["a", "b", "c"], afterList=["one"]),
            )
        )
        expected.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "group", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh", "/usr/bin/cback", []
        )
        expected.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        expected.options.hooks = [
            PreActionHook("collect", "ls -l"),
            PreActionHook("subversion", 'mailx -S "hello"'),
            PostActionHook("stage", "df -k"),
        ]
        expected.options.managedActions = [
            "collect",
            "purge",
        ]
        expected.peers = PeersConfig()
        expected.peers.localPeers = []
        expected.peers.remotePeers = []
        expected.peers.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.peers.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.peers.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.peers.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.peers.remotePeers.append(
            RemotePeer(
                "machine4",
                "/aa",
                remoteUser="someone",
                rcpCommand="scp -B",
                rshCommand="ssh",
                cbackCommand="cback",
                managed=True,
                managedActions=None,
            )
        )
        expected.peers.remotePeers.append(RemotePeer("machine5", "/bb", managed=False, managedActions=["collect", "purge"]))
        expected.collect = CollectConfig("/opt/backup/collect", "daily", "targz", ".cbignore")
        expected.collect.absoluteExcludePaths = [
            "/etc/cback.conf",
            "/etc/X11",
        ]
        expected.collect.excludePatterns = [
            ".*tmp.*",
            r".*\.netscape\/.*",
        ]
        expected.collect.collectFiles = []
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.profile"))
        expected.collect.collectFiles.append(CollectFile(absolutePath="/home/root/.kshrc", collectMode="weekly"))
        expected.collect.collectFiles.append(
            CollectFile(absolutePath="/home/root/.aliases", collectMode="daily", archiveMode="tarbz2")
        )
        expected.collect.collectDirs = []
        expected.collect.collectDirs.append(CollectDir(absolutePath="/root"))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/tmp", linkDepth=3))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/ken", linkDepth=1, dereference=True))
        expected.collect.collectDirs.append(CollectDir(absolutePath="/var/log", collectMode="incr"))
        expected.collect.collectDirs.append(
            CollectDir(absolutePath="/etc", collectMode="incr", archiveMode="tar", ignoreFile=".ignore")
        )
        collectDir = CollectDir(absolutePath="/opt")
        collectDir.absoluteExcludePaths = [
            "/opt/share",
            "/opt/tmp",
        ]
        collectDir.relativeExcludePaths = [
            "large",
            "backup",
        ]
        collectDir.excludePatterns = [
            r".*\.doc\.*",
            r".*\.xls\.*",
        ]
        expected.collect.collectDirs.append(collectDir)
        expected.stage = StageConfig()
        expected.stage.targetDir = "/opt/backup/staging"
        expected.stage.localPeers = None
        expected.stage.remotePeers = None
        expected.store = StoreConfig()
        expected.store.sourceDir = "/opt/backup/staging"
        expected.store.mediaType = "dvd+rw"
        expected.store.deviceType = "dvdwriter"
        expected.store.devicePath = "/dev/cdrw"
        expected.store.deviceScsiId = None
        expected.store.driveSpeed = 1
        expected.store.checkData = True
        expected.store.checkMedia = True
        expected.store.warnMidnite = True
        expected.store.noEject = True
        expected.store.blankBehavior = BlankBehavior()
        expected.store.blankBehavior.blankMode = "weekly"
        expected.store.blankBehavior.blankFactor = "1.3"
        expected.purge = PurgeConfig()
        expected.purge.purgeDirs = []
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/stage", 5))
        expected.purge.purgeDirs.append(PurgeDir("/opt/backup/collect", 0))
        expected.purge.purgeDirs.append(PurgeDir("/home/backup/tmp", 12))
        self.assertEqual(expected, config)

    def testParse_037(self):
        """
        Parse config document containing only a peers section, containing only
        required fields, validate=False.
        """
        path = self.resources["cback.conf.22"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.peers = PeersConfig()
        expected.peers.localPeers = None
        expected.peers.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect"),
        ]
        self.assertEqual(expected, config)

    def testParse_038(self):
        """
        Parse config document containing only a peers section, containing only
        required fields, validate=True.
        """
        path = self.resources["cback.conf.9"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    def testParse_039(self):
        """
        Parse config document containing only a peers section, containing all
        required and optional fields, validate=False.
        """
        path = self.resources["cback.conf.23"]
        config = Config(xmlPath=path, validate=False)
        expected = Config()
        expected.peers = PeersConfig()
        expected.peers.localPeers = []
        expected.peers.remotePeers = []
        expected.peers.localPeers.append(LocalPeer("machine1-1", "/opt/backup/collect"))
        expected.peers.localPeers.append(LocalPeer("machine1-2", "/var/backup"))
        expected.peers.remotePeers.append(RemotePeer("machine2", "/backup/collect", ignoreFailureMode="all"))
        expected.peers.remotePeers.append(RemotePeer("machine3", "/home/whatever/tmp", remoteUser="someone", rcpCommand="scp -B"))
        expected.peers.remotePeers.append(
            RemotePeer(
                "machine4",
                "/aa",
                remoteUser="someone",
                rcpCommand="scp -B",
                rshCommand="ssh",
                cbackCommand="cback",
                managed=True,
                managedActions=None,
            )
        )
        expected.peers.remotePeers.append(RemotePeer("machine5", "/bb", managed=False, managedActions=["collect", "purge"]))
        self.assertEqual(expected, config)

    def testParse_040(self):
        """
        Parse config document containing only a peers section, containing all
        required and optional fields, validate=True.
        """
        path = self.resources["cback.conf.23"]
        self.assertRaises(ValueError, Config, xmlPath=path, validate=True)

    #########################
    # Test the extract logic
    #########################

    def testExtractXml_001(self):
        """
        Extract empty config document, validate=True.
        """
        before = Config()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_002(self):
        """
        Extract empty config document, validate=False.
        """
        before = Config()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_003(self):
        """
        Extract document containing only a valid reference section,
        validate=True.
        """
        before = Config()
        before.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration")
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_004(self):
        """
        Extract document containing only a valid reference section,
        validate=False.
        """
        before = Config()
        before.reference = ReferenceConfig("$Author: pronovic $", "1.3", "Sample configuration")
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_005(self):
        """
        Extract document containing only a valid extensions section, empty list,
        orderMode=None, validate=True.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.orderMode = None
        before.extensions.actions = []
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_006(self):
        """
        Extract document containing only a valid extensions section,
        non-empty list and orderMode="index", validate=True.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.orderMode = "index"
        before.extensions.actions = []
        before.extensions.actions.append(ExtendedAction("name", "module", "function", 1))
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_006a(self):
        """
        Extract document containing only a valid extensions section,
        non-empty list and orderMode="dependency", validate=True.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.orderMode = "dependency"
        before.extensions.actions = []
        before.extensions.actions.append(
            ExtendedAction("name", "module", "function", dependencies=ActionDependencies(beforeList=["b"], afterList=["a"]))
        )
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_007(self):
        """
        Extract document containing only a valid extensions section, empty list,
        orderMode=None, validate=False.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_008(self):
        """
        Extract document containing only a valid extensions section,
        orderMode="index", validate=False.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.orderMode = "index"
        before.extensions.actions = []
        before.extensions.actions.append(ExtendedAction("name", "module", "function", 1))
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_009(self):
        """
        Extract document containing only an invalid extensions section,
        validate=True.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.actions = []
        before.extensions.actions.append(ExtendedAction("name", "module", None, None))
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_010(self):
        """
        Extract document containing only an invalid extensions section,
        validate=False.
        """
        before = Config()
        before.extensions = ExtensionsConfig()
        before.extensions.actions = []
        before.extensions.actions.append(ExtendedAction("name", "module", None, None))
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_011(self):
        """
        Extract document containing only a valid options section, validate=True.
        """
        before = Config()
        before.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "backup", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh"
        )
        before.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        before.options.hooks = [
            PostActionHook("collect", "ls -l"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_012(self):
        """
        Extract document containing only a valid options section, validate=False.
        """
        before = Config()
        before.options = OptionsConfig(
            "tuesday", "/opt/backup/tmp", "backup", "backup", "/usr/bin/scp -1 -B", [], [], "/usr/bin/ssh"
        )
        before.options.overrides = [
            CommandOverride("mkisofs", "/usr/bin/mkisofs"),
            CommandOverride("svnlook", "/svnlook"),
        ]
        before.options.hooks = [
            PostActionHook("collect", "ls -l"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_013(self):
        """
        Extract document containing only an invalid options section,
        validate=True.
        """
        before = Config()
        before.options = OptionsConfig()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_014(self):
        """
        Extract document containing only an invalid options section,
        validate=False.
        """
        before = Config()
        before.options = OptionsConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_015(self):
        """
        Extract document containing only a valid collect section, empty lists,
        validate=True.  (Test a directory.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.collectDirs = [
            CollectDir("/etc", collectMode="daily"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_015a(self):
        """
        Extract document containing only a valid collect section, empty lists,
        validate=True. (Test a file.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.collectFiles = [
            CollectFile("/etc", collectMode="daily"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_016(self):
        """
        Extract document containing only a valid collect section, empty lists,
        validate=False.   (Test a directory.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.collectDirs = [
            CollectDir("/etc", collectMode="daily"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_016a(self):
        """
        Extract document containing only a valid collect section, empty lists,
        validate=False.   (Test a file.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.collectFiles = [
            CollectFile("/etc", collectMode="daily"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_017(self):
        """
        Extract document containing only a valid collect section, non-empty
        lists, validate=True.   (Test a directory.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.absoluteExcludePaths = [
            "/one",
            "/two",
            "/three",
        ]
        before.collect.excludePatterns = [
            "pattern",
        ]
        before.collect.collectDirs = [
            CollectDir("/etc", collectMode="daily"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_017a(self):
        """
        Extract document containing only a valid collect section, non-empty
        lists, validate=True.   (Test a file.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.absoluteExcludePaths = [
            "/one",
            "/two",
            "/three",
        ]
        before.collect.excludePatterns = [
            "pattern",
        ]
        before.collect.collectFiles = [
            CollectFile("/etc", collectMode="daily"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_018(self):
        """
        Extract document containing only a valid collect section, non-empty
        lists, validate=False.  (Test a directory.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.absoluteExcludePaths = [
            "/one",
            "/two",
            "/three",
        ]
        before.collect.excludePatterns = [
            "pattern",
        ]
        before.collect.collectDirs = [
            CollectDir("/etc", collectMode="daily"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_018a(self):
        """
        Extract document containing only a valid collect section, non-empty
        lists, validate=False.  (Test a file.)
        """
        before = Config()
        before.collect = CollectConfig()
        before.collect.targetDir = "/opt/backup/collect"
        before.collect.archiveMode = "targz"
        before.collect.ignoreFile = ".cbignore"
        before.collect.absoluteExcludePaths = [
            "/one",
            "/two",
            "/three",
        ]
        before.collect.excludePatterns = [
            "pattern",
        ]
        before.collect.collectFiles = [
            CollectFile("/etc", collectMode="daily"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_019(self):
        """
        Extract document containing only an invalid collect section,
        validate=True.
        """
        before = Config()
        before.collect = CollectConfig()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_020(self):
        """
        Extract document containing only an invalid collect section,
        validate=False.
        """
        before = Config()
        before.collect = CollectConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_021(self):
        """
        Extract document containing only a valid stage section, one empty list,
        validate=True.
        """
        before = Config()
        before.stage = StageConfig()
        before.stage.targetDir = "/opt/backup/staging"
        before.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        before.stage.remotePeers = None
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_022(self):
        """
        Extract document containing only a valid stage section, empty lists,
        validate=False.
        """
        before = Config()
        before.stage = StageConfig()
        before.stage.targetDir = "/opt/backup/staging"
        before.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        before.stage.remotePeers = None
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_023(self):
        """
        Extract document containing only a valid stage section, non-empty lists,
        validate=True.
        """
        before = Config()
        before.stage = StageConfig()
        before.stage.targetDir = "/opt/backup/staging"
        before.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        before.stage.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect", remoteUser="backup"),
        ]
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_024(self):
        """
        Extract document containing only a valid stage section, non-empty lists,
        validate=False.
        """
        before = Config()
        before.stage = StageConfig()
        before.stage.targetDir = "/opt/backup/staging"
        before.stage.localPeers = [
            LocalPeer("machine1", "/opt/backup/collect"),
        ]
        before.stage.remotePeers = [
            RemotePeer("machine2", "/opt/backup/collect", remoteUser="backup"),
        ]
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_025(self):
        """
        Extract document containing only an invalid stage section, validate=True.
        """
        before = Config()
        before.stage = StageConfig()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_026(self):
        """
        Extract document containing only an invalid stage section,
        validate=False.
        """
        before = Config()
        before.stage = StageConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_027(self):
        """
        Extract document containing only a valid store section, validate=True.
        """
        before = Config()
        before.store = StoreConfig()
        before.store.sourceDir = "/opt/backup/staging"
        before.store.devicePath = "/dev/cdrw"
        before.store.deviceScsiId = "0,0,0"
        before.store.driveSpeed = 4
        before.store.mediaType = "cdrw-74"
        before.store.checkData = True
        before.store.checkMedia = True
        before.store.warnMidnite = True
        before.store.noEject = True
        before.store.refreshMediaDelay = 12
        before.store.ejectDelay = 13
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_028(self):
        """
        Extract document containing only a valid store section, validate=False.
        """
        before = Config()
        before.store = StoreConfig()
        before.store.sourceDir = "/opt/backup/staging"
        before.store.devicePath = "/dev/cdrw"
        before.store.deviceScsiId = "0,0,0"
        before.store.driveSpeed = 4
        before.store.mediaType = "cdrw-74"
        before.store.checkData = True
        before.store.checkMedia = True
        before.store.warnMidnite = True
        before.store.noEject = True
        before.store.refreshMediaDelay = 12
        before.store.ejectDelay = 13
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_029(self):
        """
        Extract document containing only an invalid store section, validate=True.
        """
        before = Config()
        before.store = StoreConfig()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_030(self):
        """
        Extract document containing only an invalid store section,
        validate=False.
        """
        before = Config()
        before.store = StoreConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_031(self):
        """
        Extract document containing only a valid purge section, empty list,
        validate=True.
        """
        before = Config()
        before.purge = PurgeConfig()
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_032(self):
        """
        Extract document containing only a valid purge section, empty list,
        validate=False.
        """
        before = Config()
        before.purge = PurgeConfig()
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_033(self):
        """
        Extract document containing only a valid purge section, non-empty list,
        validate=True.
        """
        before = Config()
        before.purge = PurgeConfig()
        before.purge.purgeDirs = []
        before.purge.purgeDirs.append(PurgeDir(absolutePath="/whatever", retainDays=3))
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_034(self):
        """
        Extract document containing only a valid purge section, non-empty list,
        validate=False.
        """
        before = Config()
        before.purge = PurgeConfig()
        before.purge.purgeDirs = []
        before.purge.purgeDirs.append(PurgeDir(absolutePath="/whatever", retainDays=3))
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_035(self):
        """
        Extract document containing only an invalid purge section, validate=True.
        """
        before = Config()
        before.purge = PurgeConfig()
        before.purge.purgeDirs = []
        before.purge.purgeDirs.append(PurgeDir(absolutePath="/whatever"))
        self.assertRaises(ValueError, before.extractXml, validate=True)

    def testExtractXml_036(self):
        """
        Extract document containing only an invalid purge section,
        validate=False.
        """
        before = Config()
        before.purge = PurgeConfig()
        before.purge.purgeDirs = []
        before.purge.purgeDirs.append(PurgeDir(absolutePath="/whatever"))
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_037(self):
        """
        Extract complete document containing all required and optional fields, "index" extensions,
        validate=False.
        """
        path = self.resources["cback.conf.15"]
        before = Config(xmlPath=path, validate=False)
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_037a(self):
        """
        Extract complete document containing all required and optional fields, "dependency" extensions,
        validate=False.
        """
        path = self.resources["cback.conf.20"]
        before = Config(xmlPath=path, validate=False)
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_038(self):
        """
        Extract complete document containing all required and optional fields, "index" extensions,
        validate=True.
        """
        path = self.resources["cback.conf.15"]
        before = Config(xmlPath=path, validate=True)
        beforeXml = before.extractXml(validate=True)
        after = Config(xmlData=beforeXml, validate=True)
        self.assertEqual(before, after)

    def testExtractXml_038a(self):
        """
        Extract complete document containing all required and optional fields, "dependency" extensions,
        validate=True.
        """
        path = self.resources["cback.conf.20"]
        before = Config(xmlPath=path, validate=True)
        beforeXml = before.extractXml(validate=True)
        after = Config(xmlData=beforeXml, validate=True)
        self.assertEqual(before, after)

    def testExtractXml_039(self):
        """
        Extract a sample from Cedar Backup v1.x, which must still be valid,
        validate=False.
        """
        path = self.resources["cback.conf.1"]
        before = Config(xmlPath=path, validate=False)
        beforeXml = before.extractXml(validate=False)
        after = Config(xmlData=beforeXml, validate=False)
        self.assertEqual(before, after)

    def testExtractXml_040(self):
        """
        Extract a sample from Cedar Backup v1.x, which must still be valid,
        validate=True.
        """
        path = self.resources["cback.conf.1"]
        before = Config(xmlPath=path, validate=True)
        beforeXml = before.extractXml(validate=True)
        after = Config(xmlData=beforeXml, validate=True)
        self.assertEqual(before, after)

    def testExtractXml_041(self):
        """
        Extract complete document containing all required and optional fields,
        using a peers configuration section, validate=True.
        """
        path = self.resources["cback.conf.21"]
        before = Config(xmlPath=path, validate=True)
        beforeXml = before.extractXml(validate=True)
        after = Config(xmlData=beforeXml, validate=True)
        self.assertEqual(before, after)
