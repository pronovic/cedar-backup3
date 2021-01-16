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
# Copyright (c) 2004-2005,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests knapsack functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/knapsack.py.

Code Coverage
=============

   This module contains individual tests for each of the public functions
   implemented in knapsack.py: ``firstFit()``, ``bestFit()``, ``worstFit()`` and
   ``alternateFit()``.

   Note that the tests for each function are pretty much identical and so
   there's pretty much code duplication.  In production code, I would argue
   that this implies some refactoring is needed.  In here, however, I prefer
   having lots of individual test cases even if there is duplication, because I
   think this makes it easier to judge the extent of a problem when one exists.

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

Full vs. Reduced Tests
======================

   All of the tests in this module are considered safe to be run in an average
   build environment.  There is a no need to use a KNAPSACKTESTS_FULL
   environment variable to provide a "reduced feature set" test suite as for
   some of the other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

# Import standard modules
import unittest

from CedarBackup3.knapsack import alternateFit, bestFit, firstFit, worstFit
from CedarBackup3.testutil import configureLogging

#######################################################################
# Module-wide configuration and constants
#######################################################################

# These all have random letters for keys because the original data had a,b,c,d,
# etc. in ascending order, which actually masked a sorting bug in the implementation.

ITEMS_01 = {}
ITEMS_02 = {
    "z": 0,
    "^": 0,
    "3": 0,
    "(": 0,
    "[": 0,
    "/": 0,
    "a": 0,
    "r": 0,
}
ITEMS_03 = {
    "k": 0,
    "*": 1,
    "u": 10,
    "$": 100,
    "h": 1000,
    "?": 10000,
    "b": 100000,
    "s": 1000000,
}
ITEMS_04 = {
    "l": 1000000,
    "G": 100000,
    "h": 10000,
    "#": 1000,
    "a": 100,
    "'": 10,
    "c": 1,
    "t": 0,
}
ITEMS_05 = {
    "n": 1,
    "N": 1,
    "z": 1,
    "@": 1,
    "c": 1,
    "h": 1,
    "d": 1,
    "u": 1,
}
ITEMS_06 = {
    "o": 10,
    "b": 10,
    "G": 10,
    "+": 10,
    "B": 10,
    "O": 10,
    "e": 10,
    "v": 10,
}
ITEMS_07 = {
    "$": 100,
    "K": 100,
    "f": 100,
    "=": 100,
    "n": 100,
    "I": 100,
    "F": 100,
    "w": 100,
}
ITEMS_08 = {
    "y": 1000,
    "C": 1000,
    "s": 1000,
    "f": 1000,
    "a": 1000,
    "U": 1000,
    "g": 1000,
    "x": 1000,
}
ITEMS_09 = {
    "7": 10000,
    "d": 10000,
    "f": 10000,
    "g": 10000,
    "t": 10000,
    "l": 10000,
    "h": 10000,
    "y": 10000,
}
ITEMS_10 = {
    "5": 100000,
    "#": 100000,
    "l": 100000,
    "t": 100000,
    "6": 100000,
    "T": 100000,
    "i": 100000,
    "z": 100000,
}
ITEMS_11 = {
    "t": 1,
    "d": 1,
    "k": 100000,
    "l": 100000,
    "7": 100000,
    "G": 100000,
    "j": 1,
    "1": 1,
}
ITEMS_12 = {
    "a": 10,
    "e": 10,
    "M": 100000,
    "u": 100000,
    "y": 100000,
    "f": 100000,
    "k": 10,
    "2": 10,
}
ITEMS_13 = {
    "n": 100,
    "p": 100,
    "b": 100000,
    "i": 100000,
    "$": 100000,
    "/": 100000,
    "l": 100,
    "3": 100,
}
ITEMS_14 = {
    "b": 1000,
    ":": 1000,
    "e": 100000,
    "O": 100000,
    "o": 100000,
    "#": 100000,
    "m": 1000,
    "4": 1000,
}
ITEMS_15 = {
    "c": 1,
    "j": 1,
    "e": 1,
    "H": 100000,
    "n": 100000,
    "h": 1,
    "N": 1,
    "5": 1,
}
ITEMS_16 = {
    "a": 10,
    "M": 10,
    "%": 10,
    "'": 100000,
    "l": 100000,
    "?": 10,
    "o": 10,
    "6": 10,
}
ITEMS_17 = {
    "h": 100,
    "z": 100,
    "(": 100,
    "?": 100000,
    "k": 100000,
    "|": 100,
    "p": 100,
    "7": 100,
}
ITEMS_18 = {
    "[": 1000,
    "l": 1000,
    "*": 1000,
    "/": 100000,
    "z": 100000,
    "|": 1000,
    "q": 1000,
    "h": 1000,
}

# This is a more realistic example, taken from tree9.tar.gz
ITEMS_19 = {
    "dir001/file001": 243,
    "dir001/file002": 268,
    "dir002/file001": 134,
    "dir002/file002": 74,
    "file001": 155,
    "file002": 242,
    "link001": 0,
    "link002": 0,
}


#######################################################################
# Utility functions
#######################################################################


def buildItemDict(origDict):
    """
    Creates an item dictionary suitable for passing to a knapsack function.

    The knapsack functions take a dictionary, keyed on item, of (item, size)
    tuples.  This function converts a simple item/size dictionary to a knapsack
    dictionary.  It exists for convenience.

    Args:
       origDict (Simple dictionary mapping item to size, like ``ITEMS_02``): Dictionary to convert
    Returns:
        Dictionary suitable for passing to a knapsack function
    """
    itemDict = {}
    for key in list(origDict.keys()):
        itemDict[key] = (key, origDict[key])
    return itemDict


#######################################################################
# Test Case Classes
#######################################################################

#####################
# TestKnapsack class
#####################


class TestKnapsack(unittest.TestCase):

    """Tests for the various knapsack functions."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ################################
    # Tests for firstFit() function
    ################################

    def testFirstFit_001(self):
        """
        Test firstFit() behavior for an empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 0
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testFirstFit_002(self):
        """
        Test firstFit() behavior for an empty items dictionary, non-zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 10000
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testFirstFit_003(self):
        """
        Test firstFit() behavior for an non-empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_04)
        capacity = 0
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_13)
        capacity = 0
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testFirstFit_004(self):
        """
        Test firstFit() behavior for non-empty items dictionary with zero-sized items, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testFirstFit_005(self):
        """
        Test firstFit() behavior for items dictionary where only one item fits.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 1
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 10
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 100
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 10000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 100000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100000, result[1])

    def testFirstFit_006(self):
        """
        Test firstFit() behavior for items dictionary where only 25% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 2
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 25
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 250
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 2500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 25000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 250000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 2
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 25
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 250
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 2500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

    def testFirstFit_007(self):
        """
        Test firstFit() behavior for items dictionary where only 50% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 4
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 45
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 450
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 4500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 45000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 450000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 4
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 45
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 450
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 4500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testFirstFit_008(self):
        """
        Test firstFit() behavior for items dictionary where only 75% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 6
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 65
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 650
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 6500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 65000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 650000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 7
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 65
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 650
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 6500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

    def testFirstFit_009(self):
        """
        Test firstFit() behavior for items dictionary where all items individually
        exceed the capacity.
        """
        items = buildItemDict(ITEMS_06)
        capacity = 9
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_07)
        capacity = 99
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_08)
        capacity = 999
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_09)
        capacity = 9999
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_10)
        capacity = 99999
        result = firstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testFirstFit_010(self):
        """
        Test firstFit() behavior for items dictionary where first half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 200
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testFirstFit_011(self):
        """
        Test firstFit() behavior for items dictionary where middle half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 5
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 50
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 5000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testFirstFit_012(self):
        """
        Test firstFit() behavior for items dictionary where second half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 200
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testFirstFit_013(self):
        """
        Test firstFit() behavior for items dictionary where first half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 50
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testFirstFit_014(self):
        """
        Test firstFit() behavior for items dictionary where middle half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 3
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_12)
        capacity = 35
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_13)
        capacity = 350
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_14)
        capacity = 3500
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testFirstFit_015(self):
        """
        Test firstFit() behavior for items dictionary where second half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 50
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testFirstFit_016(self):
        """
        Test firstFit() behavior for items dictionary where all items fit.
        """
        items = buildItemDict(ITEMS_02)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(0, result[1])

        items = buildItemDict(ITEMS_03)
        capacity = 2000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_04)
        capacity = 2000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_05)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400004, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400040, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(404000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200006, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200060, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 1000000
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(206000, result[1])

    def testFirstFit_017(self):
        """
        Test firstFit() behavior for a more realistic set of items
        """
        items = buildItemDict(ITEMS_19)
        capacity = 760
        result = firstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        # Unfortunately, can't test any more than this, since dict keys come out in random order

    ###############################
    # Tests for bestFit() function
    ###############################

    def testBestFit_001(self):
        """
        Test bestFit() behavior for an empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 0
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testBestFit_002(self):
        """
        Test bestFit() behavior for an empty items dictionary, non-zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 10000
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testBestFit_003(self):
        """
        Test bestFit() behavior for an non-empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_04)
        capacity = 0
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_13)
        capacity = 0
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testBestFit_004(self):
        """
        Test bestFit() behavior for non-empty items dictionary with zero-sized items, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testBestFit_005(self):
        """
        Test bestFit() behavior for items dictionary where only one item fits.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 1
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 10
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 100
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 10000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 100000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100000, result[1])

    def testBestFit_006(self):
        """
        Test bestFit() behavior for items dictionary where only 25% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 2
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 25
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 250
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 2500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 25000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 250000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 2
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 25
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 250
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 2500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

    def testBestFit_007(self):
        """
        Test bestFit() behavior for items dictionary where only 50% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 4
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 45
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 450
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 4500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 45000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 450000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 4
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 45
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 450
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 4500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testBestFit_008(self):
        """
        Test bestFit() behavior for items dictionary where only 75% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 6
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 65
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 650
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 6500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 65000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 650000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 7
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 65
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 650
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 6500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

    def testBestFit_009(self):
        """
        Test bestFit() behavior for items dictionary where all items individually
        exceed the capacity.
        """
        items = buildItemDict(ITEMS_06)
        capacity = 9
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_07)
        capacity = 99
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_08)
        capacity = 999
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_09)
        capacity = 9999
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_10)
        capacity = 99999
        result = bestFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testBestFit_010(self):
        """
        Test bestFit() behavior for items dictionary where first half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 200
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testBestFit_011(self):
        """
        Test bestFit() behavior for items dictionary where middle half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 5
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 50
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 5000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testBestFit_012(self):
        """
        Test bestFit() behavior for items dictionary where second half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 200
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testBestFit_013(self):
        """
        Test bestFit() behavior for items dictionary where first half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 50
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testBestFit_014(self):
        """
        Test bestFit() behavior for items dictionary where middle half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 3
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_12)
        capacity = 35
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_13)
        capacity = 350
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_14)
        capacity = 3500
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testBestFit_015(self):
        """
        Test bestFit() behavior for items dictionary where second half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 50
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testBestFit_016(self):
        """
        Test bestFit() behavior for items dictionary where all items fit.
        """
        items = buildItemDict(ITEMS_02)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(0, result[1])

        items = buildItemDict(ITEMS_03)
        capacity = 2000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_04)
        capacity = 2000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_05)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400004, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400040, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(404000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200006, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200060, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 1000000
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(206000, result[1])

    def testBestFit_017(self):
        """
        Test bestFit() behavior for a more realistic set of items
        """
        items = buildItemDict(ITEMS_19)
        capacity = 760
        result = bestFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(5, len(result[0]))
        self.assertEqual(753, result[1])
        self.assertTrue("dir001/file001" in result[0])
        self.assertTrue("dir001/file002" in result[0])
        self.assertTrue("file002" in result[0])
        self.assertTrue("link001" in result[0])
        self.assertTrue("link002" in result[0])

    ################################
    # Tests for worstFit() function
    ################################

    def testWorstFit_001(self):
        """
        Test worstFit() behavior for an empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 0
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testWorstFit_002(self):
        """
        Test worstFit() behavior for an empty items dictionary, non-zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 10000
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testWorstFit_003(self):
        """
        Test worstFit() behavior for an non-empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_04)
        capacity = 0
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_13)
        capacity = 0
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testWorstFit_004(self):
        """
        Test worstFit() behavior for non-empty items dictionary with zero-sized items, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testWorstFit_005(self):
        """
        Test worstFit() behavior for items dictionary where only one item fits.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 1
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 10
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 100
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 10000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 100000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100000, result[1])

    def testWorstFit_006(self):
        """
        Test worstFit() behavior for items dictionary where only 25% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 2
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 25
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 250
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 2500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 25000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 250000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 2
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 25
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 250
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 2500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

    def testWorstFit_007(self):
        """
        Test worstFit() behavior for items dictionary where only 50% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 4
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 45
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 450
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 4500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 45000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 450000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 4
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 45
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 450
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 4500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testWorstFit_008(self):
        """
        Test worstFit() behavior for items dictionary where only 75% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 6
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 65
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 650
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 6500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 65000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 650000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 7
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 65
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 650
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 6500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

    def testWorstFit_009(self):
        """
        Test worstFit() behavior for items dictionary where all items individually
        exceed the capacity.
        """
        items = buildItemDict(ITEMS_06)
        capacity = 9
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_07)
        capacity = 99
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_08)
        capacity = 999
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_09)
        capacity = 9999
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_10)
        capacity = 99999
        result = worstFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testWorstFit_010(self):
        """
        Test worstFit() behavior for items dictionary where first half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 200
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testWorstFit_011(self):
        """
        Test worstFit() behavior for items dictionary where middle half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 5
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 50
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 5000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testWorstFit_012(self):
        """
        Test worstFit() behavior for items dictionary where second half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 200
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testWorstFit_013(self):
        """
        Test worstFit() behavior for items dictionary where first half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 50
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testWorstFit_014(self):
        """
        Test worstFit() behavior for items dictionary where middle half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 3
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_12)
        capacity = 35
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_13)
        capacity = 350
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_14)
        capacity = 3500
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testWorstFit_015(self):
        """
        Test worstFit() behavior for items dictionary where second half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 50
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testWorstFit_016(self):
        """
        Test worstFit() behavior for items dictionary where all items fit.
        """
        items = buildItemDict(ITEMS_02)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(0, result[1])

        items = buildItemDict(ITEMS_03)
        capacity = 2000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_04)
        capacity = 2000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_05)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400004, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400040, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(404000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200006, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200060, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 1000000
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(206000, result[1])

    def testWorstFit_017(self):
        """
        Test worstFit() behavior for a more realistic set of items
        """
        items = buildItemDict(ITEMS_19)
        capacity = 760
        result = worstFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(605, result[1])
        self.assertTrue("dir002/file001" in result[0])
        self.assertTrue("dir002/file002" in result[0])
        self.assertTrue("file001" in result[0])
        self.assertTrue("file002" in result[0])
        self.assertTrue("link001" in result[0])
        self.assertTrue("link002" in result[0])

    ####################################
    # Tests for alternateFit() function
    ####################################

    def testAlternateFit_001(self):
        """
        Test alternateFit() behavior for an empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 0
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testAlternateFit_002(self):
        """
        Test alternateFit() behavior for an empty items dictionary, non-zero capacity.
        """
        items = buildItemDict(ITEMS_01)
        capacity = 10000
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testAlternateFit_003(self):
        """
        Test alternateFit() behavior for an non-empty items dictionary, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_04)
        capacity = 0
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_13)
        capacity = 0
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testAlternateFit_004(self):
        """
        Test alternateFit() behavior for non-empty items dictionary with zero-sized items, zero capacity.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 0
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testAlternateFit_005(self):
        """
        Test alternateFit() behavior for items dictionary where only one item fits.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 1
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 10
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 100
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(1000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 10000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(10000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 100000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(1, len(result[0]))
        self.assertEqual(100000, result[1])

    def testAlternateFit_006(self):
        """
        Test alternateFit() behavior for items dictionary where only 25% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 2
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 25
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 250
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 2500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 25000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 250000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 2
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 25
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(20, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 250
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(200, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 2500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2000, result[1])

    def testAlternateFit_007(self):
        """
        Test alternateFit() behavior for items dictionary where only 50% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 4
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 45
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 450
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 4500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 45000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 450000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 4
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 45
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 450
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 4500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testAlternateFit_008(self):
        """
        Test alternateFit() behavior for items dictionary where only 75% of items fit.
        """
        items = buildItemDict(ITEMS_05)
        capacity = 6
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 65
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 650
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 6500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 65000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 650000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 7
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 65
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(60, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 650
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 6500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(6000, result[1])

    def testAlternateFit_009(self):
        """
        Test alternateFit() behavior for items dictionary where all items individually
        exceed the capacity.
        """
        items = buildItemDict(ITEMS_06)
        capacity = 9
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_07)
        capacity = 99
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_08)
        capacity = 999
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_09)
        capacity = 9999
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

        items = buildItemDict(ITEMS_10)
        capacity = 99999
        result = alternateFit(items, capacity)
        self.assertEqual(([], 0), result)

    def testAlternateFit_010(self):
        """
        Test alternateFit() behavior for items dictionary where first half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 200
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testAlternateFit_011(self):
        """
        Test alternateFit() behavior for items dictionary where middle half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 5
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 50
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(40, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 5000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(4000, result[1])

    def testAlternateFit_012(self):
        """
        Test alternateFit() behavior for items dictionary where second half of items
        individually exceed capacity and remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 200
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(4, len(result[0]))
        self.assertEqual(111, result[1])

    def testAlternateFit_013(self):
        """
        Test alternateFit() behavior for items dictionary where first half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_04)
        capacity = 50
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testAlternateFit_014(self):
        """
        Test alternateFit() behavior for items dictionary where middle half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_11)
        capacity = 3
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_12)
        capacity = 35
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_13)
        capacity = 350
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

        items = buildItemDict(ITEMS_14)
        capacity = 3500
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testAlternateFit_015(self):
        """
        Test alternateFit() behavior for items dictionary where second half of items
        individually exceed capacity and only some of remainder fit.
        """
        items = buildItemDict(ITEMS_03)
        capacity = 50
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertTrue(len(result[0]) < 4, "%s < 4" % len(result[0]))

    def testAlternateFit_016(self):
        """
        Test alternateFit() behavior for items dictionary where all items fit.
        """
        items = buildItemDict(ITEMS_02)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(0, result[1])

        items = buildItemDict(ITEMS_03)
        capacity = 2000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_04)
        capacity = 2000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(1111111, result[1])

        items = buildItemDict(ITEMS_05)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8, result[1])

        items = buildItemDict(ITEMS_06)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80, result[1])

        items = buildItemDict(ITEMS_07)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800, result[1])

        items = buildItemDict(ITEMS_08)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(8000, result[1])

        items = buildItemDict(ITEMS_09)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(80000, result[1])

        items = buildItemDict(ITEMS_10)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(800000, result[1])

        items = buildItemDict(ITEMS_11)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400004, result[1])

        items = buildItemDict(ITEMS_12)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400040, result[1])

        items = buildItemDict(ITEMS_13)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(400400, result[1])

        items = buildItemDict(ITEMS_14)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(404000, result[1])

        items = buildItemDict(ITEMS_15)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200006, result[1])

        items = buildItemDict(ITEMS_16)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200060, result[1])

        items = buildItemDict(ITEMS_17)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(200600, result[1])

        items = buildItemDict(ITEMS_18)
        capacity = 1000000
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(8, len(result[0]))
        self.assertEqual(206000, result[1])

    def testAlternateFit_017(self):
        """
        Test alternateFit() behavior for a more realistic set of items
        """
        items = buildItemDict(ITEMS_19)
        capacity = 760
        result = alternateFit(items, capacity)
        self.assertTrue(result[1] <= capacity, "%s <= %s" % (result[1], capacity))
        self.assertEqual(6, len(result[0]))
        self.assertEqual(719, result[1])
        self.assertTrue("link001" in result[0])
        self.assertTrue("dir001/file002" in result[0])
        self.assertTrue("link002" in result[0])
        self.assertTrue("dir001/file001" in result[0])
        self.assertTrue("dir002/file002" in result[0])
        self.assertTrue("dir002/file001" in result[0])
