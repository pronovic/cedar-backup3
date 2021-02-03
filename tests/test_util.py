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
# Purpose  : Tests utility functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# pylint: disable=C0322,C0324

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/util.py.

Code Coverage
=============

   This module contains individual tests for the public functions and classes
   implemented in util.py.

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
   build environment.  There is a no need to use a UTILTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import logging
import os
import sys
import tempfile
import time
import unittest
from os.path import isdir

from CedarBackup3.testutil import (
    buildPath,
    captureOutput,
    configureLogging,
    extractTar,
    findResources,
    platformSupportsLinks,
    platformWindows,
    removedir,
)
from CedarBackup3.util import (
    UNIT_BYTES,
    UNIT_GBYTES,
    UNIT_KBYTES,
    UNIT_MBYTES,
    UNIT_SECTORS,
    AbsolutePathList,
    Diagnostics,
    DirectedGraph,
    ObjectTypeList,
    PathResolverSingleton,
    RegexList,
    RegexMatchList,
    RestrictedContentList,
    UnorderedList,
    buildNormalizedPath,
    convertSize,
    dereferenceLink,
    deriveDayOfWeek,
    displayBytes,
    encodePath,
    executeCommand,
    getFunctionReference,
    isStartOfWeek,
    nullDevice,
    parseCommaSeparatedString,
    pathJoin,
    resolveCommand,
    sortDict,
    splitCommandLine,
)

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = ["./data", "./tests/data"]
RESOURCES = [
    "lotsoflines.py",
    "tree10.tar.gz",
]

# This is a command that is always valid on the platform, something other than the Python interpreter
# The command must return a success status (zero) for the tests to pass
if platformWindows():
    VALID_COMMAND = [pathJoin(os.environ["SystemRoot"], "system32", "WindowsPowerShell", "v1.0", "powershell.exe")]
    VALID_ARGS = ["Write-Output hello"]
    VALID_OUTPUT = "hello\r\n"
else:
    VALID_COMMAND = ["echo"]
    VALID_ARGS = ["hello"]
    VALID_OUTPUT = "hello\n"


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestUnorderedList class
##########################


class TestUnorderedList(unittest.TestCase):

    """Tests for the UnorderedList class."""

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

    ##################################
    # Test unordered list comparisons
    ##################################

    def testComparison_001(self):
        """
        Test two empty lists.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        self.assertEqual(list1, list2)
        self.assertEqual(list2, list1)

    def testComparison_002(self):
        """
        Test empty vs. non-empty list.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        self.assertEqual([1, 2, 3, 4], list1)
        self.assertEqual([2, 3, 4, 1], list1)
        self.assertEqual([3, 4, 1, 2], list1)
        self.assertEqual([4, 1, 2, 3], list1)
        self.assertEqual(list1, [4, 3, 2, 1])
        self.assertEqual(list1, [3, 2, 1, 4])
        self.assertEqual(list1, [2, 1, 4, 3])
        self.assertEqual(list1, [1, 4, 3, 2])
        self.assertNotEqual(list1, list2)
        self.assertNotEqual(list2, list1)

    def testComparison_003(self):
        """
        Test two non-empty lists, completely different contents.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list2.append("a")
        list2.append("b")
        list2.append("c")
        list2.append("d")
        self.assertEqual([1, 2, 3, 4], list1)
        self.assertEqual([2, 3, 4, 1], list1)
        self.assertEqual([3, 4, 1, 2], list1)
        self.assertEqual([4, 1, 2, 3], list1)
        self.assertEqual(list1, [4, 3, 2, 1])
        self.assertEqual(list1, [3, 2, 1, 4])
        self.assertEqual(list1, [2, 1, 4, 3])
        self.assertEqual(list1, [1, 4, 3, 2])
        self.assertEqual(["a", "b", "c", "d"], list2)
        self.assertEqual(["b", "c", "d", "a"], list2)
        self.assertEqual(["c", "d", "a", "b"], list2)
        self.assertEqual(["d", "a", "b", "c"], list2)
        self.assertEqual(list2, ["d", "c", "b", "a"])
        self.assertEqual(list2, ["c", "b", "a", "d"])
        self.assertEqual(list2, ["b", "a", "d", "c"])
        self.assertEqual(list2, ["a", "d", "c", "b"])
        self.assertNotEqual(list1, list2)
        self.assertNotEqual(list2, list1)

    def testComparison_004(self):
        """
        Test two non-empty lists, different but overlapping contents.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list2.append(3)
        list2.append(4)
        list2.append("a")
        list2.append("b")
        self.assertEqual([1, 2, 3, 4], list1)
        self.assertEqual([2, 3, 4, 1], list1)
        self.assertEqual([3, 4, 1, 2], list1)
        self.assertEqual([4, 1, 2, 3], list1)
        self.assertEqual(list1, [4, 3, 2, 1])
        self.assertEqual(list1, [3, 2, 1, 4])
        self.assertEqual(list1, [2, 1, 4, 3])
        self.assertEqual(list1, [1, 4, 3, 2])
        self.assertEqual([3, 4, "a", "b"], list2)
        self.assertEqual([4, "a", "b", 3], list2)
        self.assertEqual(["a", "b", 3, 4], list2)
        self.assertEqual(["b", 3, 4, "a"], list2)
        self.assertEqual(list2, ["b", "a", 4, 3])
        self.assertEqual(list2, ["a", 4, 3, "b"])
        self.assertEqual(list2, [4, 3, "b", "a"])
        self.assertEqual(list2, [3, "b", "a", 4])
        self.assertNotEqual(list1, list2)
        self.assertNotEqual(list2, list1)

    def testComparison_005(self):
        """
        Test two non-empty lists, exactly the same contents, same order.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list2.append(1)
        list2.append(2)
        list2.append(3)
        list2.append(4)
        self.assertEqual([1, 2, 3, 4], list1)
        self.assertEqual([2, 3, 4, 1], list1)
        self.assertEqual([3, 4, 1, 2], list1)
        self.assertEqual([4, 1, 2, 3], list1)
        self.assertEqual(list1, [4, 3, 2, 1])
        self.assertEqual(list1, [3, 2, 1, 4])
        self.assertEqual(list1, [2, 1, 4, 3])
        self.assertEqual(list1, [1, 4, 3, 2])
        self.assertEqual([1, 2, 3, 4], list2)
        self.assertEqual([2, 3, 4, 1], list2)
        self.assertEqual([3, 4, 1, 2], list2)
        self.assertEqual([4, 1, 2, 3], list2)
        self.assertEqual(list2, [4, 3, 2, 1])
        self.assertEqual(list2, [3, 2, 1, 4])
        self.assertEqual(list2, [2, 1, 4, 3])
        self.assertEqual(list2, [1, 4, 3, 2])
        self.assertEqual(list1, list2)
        self.assertEqual(list2, list1)

    def testComparison_006(self):
        """
        Test two non-empty lists, exactly the same contents, different order.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list2.append(3)
        list2.append(1)
        list2.append(2)
        list2.append(4)
        self.assertEqual([1, 2, 3, 4], list1)
        self.assertEqual([2, 3, 4, 1], list1)
        self.assertEqual([3, 4, 1, 2], list1)
        self.assertEqual([4, 1, 2, 3], list1)
        self.assertEqual(list1, [4, 3, 2, 1])
        self.assertEqual(list1, [3, 2, 1, 4])
        self.assertEqual(list1, [2, 1, 4, 3])
        self.assertEqual(list1, [1, 4, 3, 2])
        self.assertEqual([1, 2, 3, 4], list2)
        self.assertEqual([2, 3, 4, 1], list2)
        self.assertEqual([3, 4, 1, 2], list2)
        self.assertEqual([4, 1, 2, 3], list2)
        self.assertEqual(list2, [4, 3, 2, 1])
        self.assertEqual(list2, [3, 2, 1, 4])
        self.assertEqual(list2, [2, 1, 4, 3])
        self.assertEqual(list2, [1, 4, 3, 2])
        self.assertEqual(list1, list2)
        self.assertEqual(list2, list1)

    def testComparison_007(self):
        """
        Test two non-empty lists, exactly the same contents, some duplicates,
        same order.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list1.append(4)
        list2.append(1)
        list2.append(2)
        list2.append(2)
        list2.append(3)
        list2.append(4)
        list2.append(4)
        self.assertEqual([1, 2, 2, 3, 4, 4], list1)
        self.assertEqual([2, 2, 3, 4, 1, 4], list1)
        self.assertEqual([2, 3, 4, 1, 4, 2], list1)
        self.assertEqual([2, 4, 1, 4, 2, 3], list1)
        self.assertEqual(list1, [1, 2, 2, 3, 4, 4])
        self.assertEqual(list1, [2, 2, 3, 4, 1, 4])
        self.assertEqual(list1, [2, 3, 4, 1, 4, 2])
        self.assertEqual(list1, [2, 4, 1, 4, 2, 3])
        self.assertEqual([1, 2, 2, 3, 4, 4], list2)
        self.assertEqual([2, 2, 3, 4, 1, 4], list2)
        self.assertEqual([2, 3, 4, 1, 4, 2], list2)
        self.assertEqual([2, 4, 1, 4, 2, 3], list2)
        self.assertEqual(list2, [1, 2, 2, 3, 4, 4])
        self.assertEqual(list2, [2, 2, 3, 4, 1, 4])
        self.assertEqual(list2, [2, 3, 4, 1, 4, 2])
        self.assertEqual(list2, [2, 4, 1, 4, 2, 3])
        self.assertEqual(list1, list2)
        self.assertEqual(list2, list1)

    def testComparison_008(self):
        """
        Test two non-empty lists, exactly the same contents, some duplicates,
        different order.
        """
        list1 = UnorderedList()
        list2 = UnorderedList()
        list1.append(1)
        list1.append(2)
        list1.append(2)
        list1.append(3)
        list1.append(4)
        list1.append(4)
        list2.append(3)
        list2.append(1)
        list2.append(2)
        list2.append(2)
        list2.append(4)
        list2.append(4)
        self.assertEqual([1, 2, 2, 3, 4, 4], list1)
        self.assertEqual([2, 2, 3, 4, 1, 4], list1)
        self.assertEqual([2, 3, 4, 1, 4, 2], list1)
        self.assertEqual([2, 4, 1, 4, 2, 3], list1)
        self.assertEqual(list1, [1, 2, 2, 3, 4, 4])
        self.assertEqual(list1, [2, 2, 3, 4, 1, 4])
        self.assertEqual(list1, [2, 3, 4, 1, 4, 2])
        self.assertEqual(list1, [2, 4, 1, 4, 2, 3])
        self.assertEqual([1, 2, 2, 3, 4, 4], list2)
        self.assertEqual([2, 2, 3, 4, 1, 4], list2)
        self.assertEqual([2, 3, 4, 1, 4, 2], list2)
        self.assertEqual([2, 4, 1, 4, 2, 3], list2)
        self.assertEqual(list2, [1, 2, 2, 3, 4, 4])
        self.assertEqual(list2, [2, 2, 3, 4, 1, 4])
        self.assertEqual(list2, [2, 3, 4, 1, 4, 2])
        self.assertEqual(list2, [2, 4, 1, 4, 2, 3])
        self.assertEqual(list1, list2)
        self.assertEqual(list2, list1)


#############################
# TestAbsolutePathList class
#############################


class TestAbsolutePathList(unittest.TestCase):

    """Tests for the AbsolutePathList class."""

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

    #######################
    # Test list operations
    #######################

    def testListOperations_001(self):
        """
        Test append() for a valid absolute path.
        """
        list1 = AbsolutePathList()
        list1.append("/path/to/something/absolute")
        self.assertEqual(list1, ["/path/to/something/absolute"])
        self.assertEqual(list1[0], "/path/to/something/absolute")
        list1.append("/path/to/something/else")
        self.assertEqual(list1, ["/path/to/something/absolute", "/path/to/something/else"])
        self.assertEqual(list1[0], "/path/to/something/absolute")
        self.assertEqual(list1[1], "/path/to/something/else")

    def testListOperations_002(self):
        """
        Test append() for an invalid, non-absolute path.
        """
        list1 = AbsolutePathList()
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "path/to/something/relative")
        self.assertEqual(list1, [])

    def testListOperations_003(self):
        """
        Test insert() for a valid absolute path.
        """
        list1 = AbsolutePathList()
        list1.insert(0, "/path/to/something/absolute")
        self.assertEqual(list1, ["/path/to/something/absolute"])
        self.assertEqual(list1[0], "/path/to/something/absolute")
        list1.insert(0, "/path/to/something/else")
        self.assertEqual(list1, ["/path/to/something/else", "/path/to/something/absolute"])
        self.assertEqual(list1[0], "/path/to/something/else")
        self.assertEqual(list1[1], "/path/to/something/absolute")

    def testListOperations_004(self):
        """
        Test insert() for an invalid, non-absolute path.
        """
        list1 = AbsolutePathList()
        self.assertRaises(ValueError, list1.insert, 0, "path/to/something/relative")

    def testListOperations_005(self):
        """
        Test extend() for a valid absolute path.
        """
        list1 = AbsolutePathList()
        list1.extend(["/path/to/something/absolute"])
        self.assertEqual(list1, ["/path/to/something/absolute"])
        self.assertEqual(list1[0], "/path/to/something/absolute")
        list1.extend(["/path/to/something/else"])
        self.assertEqual(list1, ["/path/to/something/absolute", "/path/to/something/else"])
        self.assertEqual(list1[0], "/path/to/something/absolute")
        self.assertEqual(list1[1], "/path/to/something/else")

    def testListOperations_006(self):
        """
        Test extend() for an invalid, non-absolute path.
        """
        list1 = AbsolutePathList()
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["path/to/something/relative"])
        self.assertEqual(list1, [])


###########################
# TestObjectTypeList class
###########################


class TestObjectTypeList(unittest.TestCase):

    """Tests for the ObjectTypeList class."""

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

    #######################
    # Test list operations
    #######################

    def testListOperations_001(self):
        """
        Test append() for a valid object type.
        """
        list1 = ObjectTypeList(str, "str")
        list1.append("string")
        self.assertEqual(list1, ["string"])
        self.assertEqual(list1[0], "string")
        list1.append("string2")
        self.assertEqual(list1, ["string", "string2"])
        self.assertEqual(list1[0], "string")
        self.assertEqual(list1[1], "string2")

    def testListOperations_002(self):
        """
        Test append() for an invalid object type.
        """
        list1 = ObjectTypeList(str, "str")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, 1)
        self.assertEqual(list1, [])

    def testListOperations_003(self):
        """
        Test insert() for a valid object type.
        """
        list1 = ObjectTypeList(str, "str")
        list1.insert(0, "string")
        self.assertEqual(list1, ["string"])
        self.assertEqual(list1[0], "string")
        list1.insert(0, "string2")
        self.assertEqual(list1, ["string2", "string"])
        self.assertEqual(list1[0], "string2")
        self.assertEqual(list1[1], "string")

    def testListOperations_004(self):
        """
        Test insert() for an invalid object type.
        """
        list1 = ObjectTypeList(str, "str")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, AbsolutePathList())
        self.assertEqual(list1, [])

    def testListOperations_005(self):
        """
        Test extend() for a valid object type.
        """
        list1 = ObjectTypeList(str, "str")
        list1.extend(["string"])
        self.assertEqual(list1, ["string"])
        self.assertEqual(list1[0], "string")
        list1.extend(["string2"])
        self.assertEqual(list1, ["string", "string2"])
        self.assertEqual(list1[0], "string")
        self.assertEqual(list1[1], "string2")

    def testListOperations_006(self):
        """
        Test extend() for an invalid object type.
        """
        list1 = ObjectTypeList(str, "str")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [12.0])
        self.assertEqual(list1, [])


##################################
# TestRestrictedContentList class
##################################


class TestRestrictedContentList(unittest.TestCase):

    """Tests for the RestrictedContentList class."""

    ################
    # Setup methods
    ################

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #######################
    # Test list operations
    #######################

    def testListOperations_001(self):
        """
        Test append() for a valid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        list1.append("a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.append("b")
        self.assertEqual(list1, ["a", "b"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "b")
        list1.append("c")
        self.assertEqual(list1, ["a", "b", "c"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "b")
        self.assertEqual(list1[2], "c")

    def testListOperations_002(self):
        """
        Test append() for an invalid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "d")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, 1)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, UnorderedList())
        self.assertEqual(list1, [])

    def testListOperations_003(self):
        """
        Test insert() for a valid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        list1.insert(0, "a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.insert(0, "b")
        self.assertEqual(list1, ["b", "a"])
        self.assertEqual(list1[0], "b")
        self.assertEqual(list1[1], "a")
        list1.insert(0, "c")
        self.assertEqual(list1, ["c", "b", "a"])
        self.assertEqual(list1[0], "c")
        self.assertEqual(list1[1], "b")
        self.assertEqual(list1[2], "a")

    def testListOperations_004(self):
        """
        Test insert() for an invalid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "d")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, 1)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, UnorderedList())
        self.assertEqual(list1, [])

    def testListOperations_005(self):
        """
        Test extend() for a valid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        list1.extend(["a"])
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.extend(["b"])
        self.assertEqual(list1, ["a", "b"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "b")
        list1.extend(["c"])
        self.assertEqual(list1, ["a", "b", "c"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "b")
        self.assertEqual(list1[2], "c")

    def testListOperations_006(self):
        """
        Test extend() for an invalid value.
        """
        list1 = RestrictedContentList(["a", "b", "c"], "values")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["d"])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [1])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [UnorderedList()])
        self.assertEqual(list1, [])


###########################
# TestRegexMatchList class
###########################


class TestRegexMatchList(unittest.TestCase):

    """Tests for the RegexMatchList class."""

    ################
    # Setup methods
    ################

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #######################
    # Test list operations
    #######################

    def testListOperations_001(self):
        """
        Test append() for a valid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        list1.append("a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.append("1")
        self.assertEqual(list1, ["a", "1"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        list1.append("abcd12345")
        self.assertEqual(list1, ["a", "1", "abcd12345"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")
        list1.append("")
        self.assertEqual(list1, ["a", "1", "abcd12345", ""])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")
        self.assertEqual(list1[3], "")

    def testListOperations_002(self):
        """
        Test append() for an invalid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "A")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "ABC")
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.append, 12)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "KEN_12")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, None)
        self.assertEqual(list1, [])

    def testListOperations_003(self):
        """
        Test insert() for a valid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        list1.insert(0, "a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.insert(0, "1")
        self.assertEqual(list1, ["1", "a"])
        self.assertEqual(list1[0], "1")
        self.assertEqual(list1[1], "a")
        list1.insert(0, "abcd12345")
        self.assertEqual(list1, ["abcd12345", "1", "a"])
        self.assertEqual(list1[0], "abcd12345")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "a")
        list1.insert(0, "")
        self.assertEqual(list1, ["abcd12345", "1", "a", ""])
        self.assertEqual(list1[0], "")
        self.assertEqual(list1[1], "abcd12345")
        self.assertEqual(list1[2], "1")
        self.assertEqual(list1[3], "a")

    def testListOperations_004(self):
        """
        Test insert() for an invalid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "A")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "ABC")
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.insert, 0, 12)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "KEN_12")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, None)
        self.assertEqual(list1, [])

    def testListOperations_005(self):
        """
        Test extend() for a valid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        list1.extend(["a"])
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.extend(["1"])
        self.assertEqual(list1, ["a", "1"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        list1.extend(["abcd12345"])
        self.assertEqual(list1, ["a", "1", "abcd12345"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")
        list1.extend([""])
        self.assertEqual(list1, ["a", "1", "abcd12345", ""])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")
        self.assertEqual(list1[3], "")

    def testListOperations_006(self):
        """
        Test extend() for an invalid value, emptyAllowed=True.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=True)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["A"])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["ABC"])
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.extend, [12])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["KEN_12"])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [None])
        self.assertEqual(list1, [])

    def testListOperations_007(self):
        """
        Test append() for a valid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        list1.append("a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.append("1")
        self.assertEqual(list1, ["a", "1"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        list1.append("abcd12345")
        self.assertEqual(list1, ["a", "1", "abcd12345"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")

    def testListOperations_008(self):
        """
        Test append() for an invalid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "A")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "ABC")
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.append, 12)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "KEN_12")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, None)
        self.assertEqual(list1, [])

    def testListOperations_009(self):
        """
        Test insert() for a valid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        list1.insert(0, "a")
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.insert(0, "1")
        self.assertEqual(list1, ["1", "a"])
        self.assertEqual(list1[0], "1")
        self.assertEqual(list1[1], "a")
        list1.insert(0, "abcd12345")
        self.assertEqual(list1, ["abcd12345", "1", "a"])
        self.assertEqual(list1[0], "abcd12345")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "a")

    def testListOperations_010(self):
        """
        Test insert() for an invalid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "A")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "ABC")
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.insert, 0, 12)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "KEN_12")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, "")
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.insert, 0, None)
        self.assertEqual(list1, [])

    def testListOperations_011(self):
        """
        Test extend() for a valid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        list1.extend(["a"])
        self.assertEqual(list1, ["a"])
        self.assertEqual(list1[0], "a")
        list1.extend(["1"])
        self.assertEqual(list1, ["a", "1"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        list1.extend(["abcd12345"])
        self.assertEqual(list1, ["a", "1", "abcd12345"])
        self.assertEqual(list1[0], "a")
        self.assertEqual(list1[1], "1")
        self.assertEqual(list1[2], "abcd12345")

    def testListOperations_012(self):
        """
        Test extend() for an invalid value, emptyAllowed=False.
        """
        list1 = RegexMatchList(r"^[a-z0-9]*$", emptyAllowed=False)
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["A"])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["ABC"])
        self.assertEqual(list1, [])
        self.assertRaises(TypeError, list1.extend, [12])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["KEN_12"])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [""])
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, [None])
        self.assertEqual(list1, [])


######################
# TestRegexList class
######################


class TestRegexList(unittest.TestCase):

    """Tests for the RegexList class."""

    ################
    # Setup methods
    ################

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #######################
    # Test list operations
    #######################

    def testListOperations_001(self):
        """
        Test append() for a valid regular expresson.
        """
        list1 = RegexList()
        list1.append(r".*\.jpg")
        self.assertEqual(list1, [r".*\.jpg"])
        self.assertEqual(list1[0], r".*\.jpg")
        list1.append("[a-zA-Z0-9]*")
        self.assertEqual(list1, [r".*\.jpg", "[a-zA-Z0-9]*"])
        self.assertEqual(list1[0], r".*\.jpg")
        self.assertEqual(list1[1], "[a-zA-Z0-9]*")

    def testListOperations_002(self):
        """
        Test append() for an invalid regular expression.
        """
        list1 = RegexList()
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.append, "*.jpg")
        self.assertEqual(list1, [])

    def testListOperations_003(self):
        """
        Test insert() for a valid regular expression.
        """
        list1 = RegexList()
        list1.insert(0, r".*\.jpg")
        self.assertEqual(list1, [r".*\.jpg"])
        self.assertEqual(list1[0], r".*\.jpg")
        list1.insert(0, "[a-zA-Z0-9]*")
        self.assertEqual(list1, ["[a-zA-Z0-9]*", r".*\.jpg"])
        self.assertEqual(list1[0], "[a-zA-Z0-9]*")
        self.assertEqual(list1[1], r".*\.jpg")

    def testListOperations_004(self):
        """
        Test insert() for an invalid regular expression.
        """
        list1 = RegexList()
        self.assertRaises(ValueError, list1.insert, 0, "*.jpg")

    def testListOperations_005(self):
        """
        Test extend() for a valid regular expression.
        """
        list1 = RegexList()
        list1.extend([r".*\.jpg"])
        self.assertEqual(list1, [r".*\.jpg"])
        self.assertEqual(list1[0], r".*\.jpg")
        list1.extend(["[a-zA-Z0-9]*"])
        self.assertEqual(list1, [r".*\.jpg", "[a-zA-Z0-9]*"])
        self.assertEqual(list1[0], r".*\.jpg")
        self.assertEqual(list1[1], "[a-zA-Z0-9]*")

    def testListOperations_006(self):
        """
        Test extend() for an invalid regular expression.
        """
        list1 = RegexList()
        self.assertEqual(list1, [])
        self.assertRaises(ValueError, list1.extend, ["*.jpg"])
        self.assertEqual(list1, [])


##########################
# TestDirectedGraph class
##########################


class TestDirectedGraph(unittest.TestCase):

    """Tests for the DirectedGraph class."""

    ############################
    # Test __repr__ and __str__
    ############################

    def testStringFuncs_001(self):
        """
        Just make sure that the string functions don't have errors (i.e. bad variable names).
        """
        obj = DirectedGraph("test")
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with a valid name filled in.
        """
        graph = DirectedGraph("Ken")
        self.assertEqual("Ken", graph.name)

    def testConstructor_002(self):
        """
        Test constructor with a ``None`` name filled in.
        """
        self.assertRaises(ValueError, DirectedGraph, None)

    ##########################
    # Test depth first search
    ##########################

    def testTopologicalSort_001(self):
        """
        Empty graph.
        """
        graph = DirectedGraph("test")
        path = graph.topologicalSort()
        self.assertEqual([], path)

    def testTopologicalSort_002(self):
        """
        Graph with 1 vertex, no edges.
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        path = graph.topologicalSort()
        self.assertEqual(["1"], path)

    def testTopologicalSort_003(self):
        """
        Graph with 2 vertices, no edges.
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1"], path)

    def testTopologicalSort_004(self):
        """
        Graph with 3 vertices, no edges.
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_005(self):
        """
        Graph with 4 vertices, no edges.
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("4")
        path = graph.topologicalSort()
        self.assertEqual(["4", "2", "1", "3"], path)

    def testTopologicalSort_006(self):
        """
        Graph with 4 vertices, no edges.
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("4")
        graph.createVertex("5")
        path = graph.topologicalSort()
        self.assertEqual(["5", "4", "2", "1", "3"], path)

    def testTopologicalSort_007(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_008(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_009(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_010(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_011(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_012(self):
        """
        Graph with 3 vertices, in a chain (1->2->3), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_013(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_014(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_015(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_016(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_017(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_018(self):
        """
        Graph with 3 vertices, in a chain (3->2->1), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("3", "2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_019(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_020(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_021(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_022(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_023(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_024(self):
        """
        Graph with 3 vertices, chain and orphan (1->2,3), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_025(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_026(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_027(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_028(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_029(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_030(self):
        """
        Graph with 3 vertices, chain and orphan (1->3,2), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("1", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_031(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_032(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_033(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_034(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_035(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_036(self):
        """
        Graph with 3 vertices, chain and orphan (2->3,1), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("2", "3")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3"], path)

    def testTopologicalSort_037(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_038(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_039(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_040(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_041(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_042(self):
        """
        Graph with 3 vertices, chain and orphan (2->1,3), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("2", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "3"], path)

    def testTopologicalSort_043(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_044(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_045(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_046(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_047(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_048(self):
        """
        Graph with 3 vertices, chain and orphan (3->1,2), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("3", "1")
        path = graph.topologicalSort()
        self.assertEqual(["2", "3", "1"], path)

    def testTopologicalSort_049(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (1,2,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_050(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (1,3,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "2", "1"], path)

    def testTopologicalSort_051(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (2,3,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_052(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (2,1,3)
        """
        graph = DirectedGraph("test")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createVertex("3")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["3", "1", "2"], path)

    def testTopologicalSort_053(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (3,1,2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_054(self):
        """
        Graph with 3 vertices, chain and orphan (3->2,1), create order (3,2,1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("3")
        graph.createVertex("2")
        graph.createVertex("1")
        graph.createEdge("3", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "3", "2"], path)

    def testTopologicalSort_055(self):
        """
        Graph with 1 vertex, with an edge to itself (1->1).
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createEdge("1", "1")
        self.assertRaises(ValueError, graph.topologicalSort)

    def testTopologicalSort_056(self):
        """
        Graph with 2 vertices, each with an edge to itself (1->1, 2->2).
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createEdge("1", "1")
        graph.createEdge("2", "2")
        self.assertRaises(ValueError, graph.topologicalSort)

    def testTopologicalSort_057(self):
        """
        Graph with 3 vertices, each with an edge to itself (1->1, 2->2, 3->3).
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("1", "1")
        graph.createEdge("2", "2")
        graph.createEdge("3", "3")
        self.assertRaises(ValueError, graph.topologicalSort)

    def testTopologicalSort_058(self):
        """
        Graph with 3 vertices, in a loop (1->2->3->1).
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createEdge("1", "2")
        graph.createEdge("2", "3")
        graph.createEdge("3", "1")
        self.assertRaises(ValueError, graph.topologicalSort)

    def testTopologicalSort_059(self):
        """
        Graph with 5 vertices, (2, 1->3, 1->4, 1->5)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "5", "4", "3"], path)

    def testTopologicalSort_060(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "5", "4", "3"], path)

    def testTopologicalSort_061(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5, 3->4)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        graph.createEdge("3", "4")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "5", "3", "4"], path)

    def testTopologicalSort_062(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5, 3->4, 5->4)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        graph.createEdge("3", "4")
        graph.createEdge("5", "4")
        path = graph.topologicalSort()
        self.assertEqual(["2", "1", "5", "3", "4"], path)

    def testTopologicalSort_063(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5, 3->4, 5->4, 1->2)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        graph.createEdge("3", "4")
        graph.createEdge("5", "4")
        graph.createEdge("1", "2")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "5", "3", "4"], path)

    def testTopologicalSort_064(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5, 3->4, 5->4, 1->2, 3->5)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        graph.createEdge("3", "4")
        graph.createEdge("5", "4")
        graph.createEdge("1", "2")
        graph.createEdge("3", "5")
        path = graph.topologicalSort()
        self.assertEqual(["1", "2", "3", "5", "4"], path)

    def testTopologicalSort_065(self):
        """
        Graph with 5 vertices, (1->3, 1->4, 1->5, 2->5, 3->4, 5->4, 5->1)
        """
        graph = DirectedGraph("test")
        graph.createVertex("1")
        graph.createVertex("2")
        graph.createVertex("3")
        graph.createVertex("4")
        graph.createVertex("5")
        graph.createEdge("1", "3")
        graph.createEdge("1", "4")
        graph.createEdge("1", "5")
        graph.createEdge("2", "5")
        graph.createEdge("3", "4")
        graph.createEdge("5", "4")
        graph.createEdge("5", "1")
        self.assertRaises(ValueError, graph.topologicalSort)


##################################
# TestPathResolverSingleton class
##################################


class TestPathResolverSingleton(unittest.TestCase):

    """Tests for the PathResolverSingleton class."""

    ################
    # Setup methods
    ################

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ##########################
    # Test singleton behavior
    ##########################

    def testBehavior_001(self):
        """
        Check behavior of constructor around filling and clearing instance variable.
        """
        PathResolverSingleton._instance = None
        instance = PathResolverSingleton()
        self.assertNotEqual(None, PathResolverSingleton._instance)
        self.assertTrue(instance is PathResolverSingleton._instance)

    def testBehavior_002(self):
        """
        Check behavior of getInstance() around filling and clearing instance variable.
        """
        PathResolverSingleton._instance = None
        instance1 = PathResolverSingleton.getInstance()
        instance2 = PathResolverSingleton.getInstance()
        instance3 = PathResolverSingleton.getInstance()
        self.assertNotEqual(None, PathResolverSingleton._instance)
        self.assertTrue(instance1 is PathResolverSingleton._instance)
        self.assertTrue(instance1 is instance2)
        self.assertTrue(instance1 is instance3)

        PathResolverSingleton._instance = None
        PathResolverSingleton()
        instance4 = PathResolverSingleton.getInstance()
        instance5 = PathResolverSingleton.getInstance()
        instance6 = PathResolverSingleton.getInstance()
        self.assertTrue(instance1 is not instance4)
        self.assertTrue(instance4 is PathResolverSingleton._instance)
        self.assertTrue(instance4 is instance5)
        self.assertTrue(instance4 is instance6)

        PathResolverSingleton._instance = None
        instance7 = PathResolverSingleton.getInstance()
        instance8 = PathResolverSingleton.getInstance()
        instance9 = PathResolverSingleton.getInstance()
        self.assertTrue(instance1 is not instance7)
        self.assertTrue(instance4 is not instance7)
        self.assertTrue(instance7 is PathResolverSingleton._instance)
        self.assertTrue(instance7 is instance8)
        self.assertTrue(instance7 is instance9)

    ############################
    # Test lookup functionality
    ############################

    def testLookup_001(self):
        """
        Test that lookup() always returns default when singleton is empty.
        """
        PathResolverSingleton._instance = None
        instance = PathResolverSingleton.getInstance()

        result = instance.lookup("whatever")
        self.assertEqual(result, None)

        result = instance.lookup("whatever", None)
        self.assertEqual(result, None)

        result = instance.lookup("other")
        self.assertEqual(result, None)

        result = instance.lookup("other", "default")
        self.assertEqual(result, "default")

    def testLookup_002(self):
        """
        Test that lookup() returns proper values when singleton is not empty.
        """
        mappings = {"one": "/path/to/one", "two": "/path/to/two"}
        PathResolverSingleton._instance = None
        singleton = PathResolverSingleton()
        singleton.fill(mappings)

        instance = PathResolverSingleton.getInstance()

        result = instance.lookup("whatever")
        self.assertEqual(result, None)

        result = instance.lookup("whatever", None)
        self.assertEqual(result, None)

        result = instance.lookup("other")
        self.assertEqual(result, None)

        result = instance.lookup("other", "default")
        self.assertEqual(result, "default")

        result = instance.lookup("one")
        self.assertEqual(result, "/path/to/one")

        result = instance.lookup("one", None)
        self.assertEqual(result, "/path/to/one")

        result = instance.lookup("two", None)
        self.assertEqual(result, "/path/to/two")

        result = instance.lookup("two", "default")
        self.assertEqual(result, "/path/to/two")


########################
# TestDiagnostics class
########################


class TestDiagnostics(unittest.TestCase):

    """Tests for the Diagnostics class."""

    def testMethods_001(self):
        """
        Test the version attribute.
        """
        diagnostics = Diagnostics()
        self.assertFalse(diagnostics.version is None)
        self.assertNotEqual("", diagnostics.version)

    def testMethods_002(self):
        """
        Test the interpreter attribute.
        """
        diagnostics = Diagnostics()
        self.assertFalse(diagnostics.interpreter is None)
        self.assertNotEqual("", diagnostics.interpreter)

    def testMethods_003(self):
        """
        Test the platform attribute.
        """
        diagnostics = Diagnostics()
        self.assertFalse(diagnostics.platform is None)
        self.assertNotEqual("", diagnostics.platform)

    def testMethods_004(self):
        """
        Test the encoding attribute.
        """
        diagnostics = Diagnostics()
        self.assertFalse(diagnostics.encoding is None)
        self.assertNotEqual("", diagnostics.encoding)

    # noinspection PyStatementEffect
    def testMethods_005(self):
        """
        Test the locale attribute.
        """
        # pylint: disable=W0104
        diagnostics = Diagnostics()
        diagnostics.locale  # might not be set, so just make sure method doesn't fail

    def testMethods_006(self):
        """
        Test the getValues() method.
        """
        diagnostics = Diagnostics()
        values = diagnostics.getValues()
        self.assertEqual(diagnostics.version, values["version"])
        self.assertEqual(diagnostics.interpreter, values["interpreter"])
        self.assertEqual(diagnostics.platform, values["platform"])
        self.assertEqual(diagnostics.encoding, values["encoding"])
        self.assertEqual(diagnostics.locale, values["locale"])
        self.assertEqual(diagnostics.timestamp, values["timestamp"])

    def testMethods_007(self):
        """
        Test the _buildDiagnosticLines() method.
        """
        values = Diagnostics().getValues()
        lines = Diagnostics()._buildDiagnosticLines()
        self.assertEqual(len(values), len(lines))

    def testMethods_008(self):
        """
        Test the printDiagnostics() method.
        """
        captureOutput(Diagnostics().printDiagnostics)

    def testMethods_009(self):
        """
        Test the logDiagnostics() method.
        """
        logger = logging.getLogger("CedarBackup3.test")
        Diagnostics().logDiagnostics(logger.info)

    def testMethods_010(self):
        """
        Test the timestamp attribute.
        """
        diagnostics = Diagnostics()
        self.assertFalse(diagnostics.timestamp is None)
        self.assertNotEqual("", diagnostics.timestamp)


######################
# TestFunctions class
######################


# noinspection PyUnusedLocal,PyShadowingBuiltins
class TestFunctions(unittest.TestCase):

    """Tests for the various public functions."""

    ################
    # Setup methods
    ################

    def setUp(self):
        try:
            self.tmpdir = tempfile.mkdtemp()
            self.resources = findResources(RESOURCES, DATA_DIRS)
        except Exception as e:
            self.fail(e)

    def tearDown(self):
        removedir(self.tmpdir)

    ##################
    # Utility methods
    ##################

    def getTempfile(self):
        """Gets a path to a temporary file on disk."""
        (fd, name) = tempfile.mkstemp(dir=self.tmpdir)
        try:
            os.close(fd)
        except:
            pass
        return name

    def extractTar(self, tarname):
        """Extracts a tarfile with a particular name."""
        extractTar(self.tmpdir, self.resources["%s.tar.gz" % tarname])

    def buildPath(self, components):
        """Builds a complete search path from a list of components."""
        components.insert(0, self.tmpdir)
        return buildPath(components)

    ##################
    # Test sortDict()
    ##################

    def testSortDict_001(self):
        """
        Test for empty dictionary.
        """
        d = {}
        result = sortDict(d)
        self.assertEqual([], result)

    def testSortDict_002(self):
        """
        Test for dictionary with one item.
        """
        d = {"a": 1}
        result = sortDict(d)
        self.assertEqual(["a"], result)

    def testSortDict_003(self):
        """
        Test for dictionary with two items, same value.
        """
        d = {
            "a": 1,
            "b": 1,
        }
        result = sortDict(d)
        self.assertEqual(["a", "b"], result)

    def testSortDict_004(self):
        """
        Test for dictionary with two items, different values.
        """
        d = {
            "a": 1,
            "b": 2,
        }
        result = sortDict(d)
        self.assertEqual(["a", "b"], result)

    def testSortDict_005(self):
        """
        Test for dictionary with many items, same and different values.
        """
        d = {"rebuild": 0, "purge": 400, "collect": 100, "validate": 0, "store": 300, "stage": 200}
        result = sortDict(d)
        self.assertEqual(["rebuild", "validate", "collect", "stage", "store", "purge"], result)

    ##############################
    # Test getFunctionReference()
    ##############################

    def testGetFunctionReference_001(self):
        """
        Check that the search works within "standard" Python namespace.
        """
        module = "os.path"
        function = "isdir"
        reference = getFunctionReference(module, function)
        self.assertTrue(isdir is reference)

    def testGetFunctionReference_002(self):
        """
        Check that the search works for things within CedarBackup3.
        """
        module = "CedarBackup3.util"
        function = "executeCommand"
        reference = getFunctionReference(module, function)
        self.assertTrue(executeCommand is reference)

    ########################
    # Test resolveCommand()
    ########################

    def testResolveCommand_001(self):
        """
        Test that the command is echoed back unchanged when singleton is empty.
        """
        PathResolverSingleton._instance = None

        command = [
            "BAD",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "GOOD",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "WHATEVER",
            "--verbose",
            "--debug",
            "tvh:asa892831",
            "blech",
            "<",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

    def testResolveCommand_002(self):
        """
        Test that the command is echoed back unchanged when mapping is not found.
        """
        PathResolverSingleton._instance = None
        mappings = {"one": "/path/to/one", "two": "/path/to/two"}
        singleton = PathResolverSingleton()
        singleton.fill(mappings)

        command = [
            "BAD",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "GOOD",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "WHATEVER",
            "--verbose",
            "--debug",
            "tvh:asa892831",
            "blech",
            "<",
        ]
        expected = command[:]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

    def testResolveCommand_003(self):
        """
        Test that the command is echoed back changed appropriately when mapping is found.
        """
        PathResolverSingleton._instance = None
        mappings = {"one": "/path/to/one", "two": "/path/to/two"}
        singleton = PathResolverSingleton()
        singleton.fill(mappings)

        command = [
            "one",
        ]
        expected = [
            "/path/to/one",
        ]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "two",
        ]
        expected = [
            "/path/to/two",
        ]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

        command = [
            "two",
            "--verbose",
            "--debug",
            "tvh:asa892831",
            "blech",
            "<",
        ]
        expected = [
            "/path/to/two",
            "--verbose",
            "--debug",
            "tvh:asa892831",
            "blech",
            "<",
        ]
        result = resolveCommand(command)
        self.assertEqual(expected, result)

    ########################
    # Test executeCommand()
    ########################

    def testExecuteCommand_001(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=False
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_002(self):
        """
        Execute a command that should succeed, one argument, returnOutput=False
        Command-line: python -V
        """
        command = [
            sys.executable,
        ]
        args = [
            "-V",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_003(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=False
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_004(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=False
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_005(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=False
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_006(self):
        """
        Execute a command that should fail, returnOutput=False
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_007(self):
        """
        Execute a command that should fail, more arguments, returnOutput=False
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_008(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=True
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(VALID_OUTPUT, output[0])

    def testExecuteCommand_009(self):
        """
        Execute a command that should succeed, one argument, returnOutput=True
        Command-line: python -V
        """
        command = [
            sys.executable,
        ]
        args = [
            "-V",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertTrue(output[0].startswith("Python"))

    def testExecuteCommand_010(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=True
        Command-line: python -c "import sys; print(''); sys.exit(0)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(''); sys.exit(0)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_011(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=True
        Command-line: python -c "import sys; print('%s' % (sys.argv[1])); sys.exit(0)" first
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % (sys.argv[1])); sys.exit(0)",
            "first",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])

    def testExecuteCommand_012(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=True
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_013(self):
        """
        Execute a command that should fail, returnOutput=True
        Command-line: python -c "import sys; print(''); sys.exit(1)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(''); sys.exit(1)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertNotEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_014(self):
        """
        Execute a command that should fail, more arguments, returnOutput=True
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertNotEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_015(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_016(self):
        """
        Execute a command that should succeed, one argument, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -V
        """
        command = [
            sys.executable,
            "-V",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_017(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_018(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_019(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_020(self):
        """
        Execute a command that should fail, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_021(self):
        """
        Execute a command that should fail, more arguments, returnOutput=False
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_022(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(VALID_OUTPUT, output[0])

    def testExecuteCommand_023(self):
        """
        Execute a command that should succeed, one argument, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -V
        """
        command = [sys.executable, "-V"]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertTrue(output[0].startswith("Python"))

    def testExecuteCommand_024(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(0)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(0)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_025(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % (sys.argv[1])); sys.exit(0)" first
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % (sys.argv[1])); sys.exit(0)",
            "first",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])

    def testExecuteCommand_026(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_027(self):
        """
        Execute a command that should fail, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(1)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(1)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertNotEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_028(self):
        """
        Execute a command that should fail, more arguments, returnOutput=True
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True)
        self.assertNotEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_030(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=False, ignoring stderr.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_031(self):
        """
        Execute a command that should succeed, one argument, returnOutput=False, ignoring stderr.
        Command-line: python -V
        """
        command = [
            sys.executable,
        ]
        args = [
            "-V",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_032(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=False, ignoring stderr.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_033(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=False, ignoring stderr.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_034(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=False, ignoring stderr.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_035(self):
        """
        Execute a command that should fail, returnOutput=False, ignoring stderr.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_036(self):
        """
        Execute a command that should fail, more arguments, returnOutput=False, ignoring stderr.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_037(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=True, ignoring stderr.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(VALID_OUTPUT, output[0])

    def testExecuteCommand_038(self):
        """
        Execute a command that should succeed, one argument, returnOutput=True, ignoring stderr.
        Command-line: python -V
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('X', file=sys.stderr)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=False)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("X%s" % os.linesep, output[0])  # prove stderr is captured
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(0, len(output))  # prove stderr is now ignored

    def testExecuteCommand_039(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=True, ignoring stderr.
        Command-line: python -c "import sys; print(''); sys.exit(0)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(''); sys.exit(0)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_040(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=True, ignoring stderr.
        Command-line: python -c "import sys; print('%s' % (sys.argv[1])); sys.exit(0)" first
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % (sys.argv[1])); sys.exit(0)",
            "first",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])

    def testExecuteCommand_041(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=True, ignoring stderr.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_042(self):
        """
        Execute a command that should fail, returnOutput=True, ignoring stderr.
        Command-line: python -c "import sys; print(''); sys.exit(1)"
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print(''); sys.exit(1)",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_043(self):
        """
        Execute a command that should fail, more arguments, returnOutput=True, ignoring stderr.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
        ]
        args = [
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)",
            "first",
            "second",
        ]
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_044(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_045(self):
        """
        Execute a command that should succeed, one argument, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -V
        """
        command = [
            sys.executable,
            "-V",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_046(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_047(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_048(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(0)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_049(self):
        """
        Execute a command that should fail, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_050(self):
        """
        Execute a command that should fail, more arguments, returnOutput=False, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(sys.argv[1:]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1:]); sys.exit(1)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=False, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(None, output)

    def testExecuteCommand_051(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(VALID_OUTPUT, output[0])

    def testExecuteCommand_052(self):
        """
        Execute a command that should succeed, one argument, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -V
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('X', file=sys.stderr)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=False)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("X%s" % os.linesep, output[0])  # prove stderr is captured
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(0, len(output))  # prove stderr is now ignored

    def testExecuteCommand_053(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(0)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(0)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_054(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % (sys.argv[1])); sys.exit(0)" first
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % (sys.argv[1])); sys.exit(0)",
            "first",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])

    def testExecuteCommand_055(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_056(self):
        """
        Execute a command that should fail, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(1)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(1)",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(1, len(output))
        self.assertEqual(os.linesep, output[0])

    def testExecuteCommand_057(self):
        """
        Execute a command that should fail, more arguments, returnOutput=True, ignoring stderr.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)",
            "first",
            "second",
        ]
        args = []
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        self.assertNotEqual(0, result)
        self.assertEqual(2, len(output))
        self.assertEqual("first%s" % os.linesep, output[0])
        self.assertEqual("second%s" % os.linesep, output[1])

    def testExecuteCommand_058(self):
        """
        Execute a command that should succeed, no arguments, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: non-Python platform-specific valid command
        """
        command = VALID_COMMAND
        args = VALID_ARGS

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(1, len(output))
        self.assertEqual(
            VALID_OUTPUT, output[0].replace("\n", os.linesep)
        )  # when reading from a file, Python translates the line ending

    def testExecuteCommand_059(self):
        """
        Execute a command that should succeed, one argument, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -V
        """
        command = [sys.executable, "-V"]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(1, len(output))
        self.assertTrue(output[0].startswith("Python"))

    def testExecuteCommand_060(self):
        """
        Execute a command that should succeed, two arguments, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(0)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(0)",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(1, len(output))
        self.assertEqual("\n", output[0])

    def testExecuteCommand_061(self):
        """
        Execute a command that should succeed, three arguments, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % (sys.argv[1])); sys.exit(0)" first
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % (sys.argv[1])); sys.exit(0)",
            "first",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(1, len(output))
        self.assertEqual("first\n", output[0])

    def testExecuteCommand_062(self):
        """
        Execute a command that should succeed, four arguments, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(0)",
            "first",
            "second",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(2, len(output))
        self.assertEqual("first\n", output[0])
        self.assertEqual("second\n", output[1])

    def testExecuteCommand_063(self):
        """
        Execute a command that should fail, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print(''); sys.exit(1)"
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print(''); sys.exit(1)",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertNotEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(1, len(output))
        self.assertEqual("\n", output[0])

    def testExecuteCommand_064(self):
        """
        Execute a command that should fail, more arguments, returnOutput=False, using outputFile.
        Do this all bundled into the command list, just to check that this works as expected.
        Command-line: python -c "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)" first second
        """
        command = [
            sys.executable,
            "-c",
            "import sys; print('%s' % sys.argv[1]); print('%s' % sys.argv[2]); sys.exit(1)",
            "first",
            "second",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, returnOutput=False, outputFile=outputFile)[0]
        self.assertNotEqual(0, result)
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            output = f.readlines()

        self.assertEqual(2, len(output))
        self.assertEqual("first\n", output[0])
        self.assertEqual("second\n", output[1])

    def testExecuteCommand_065(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain only data on stdout, and ignoreStderr should be True.
        This test helps confirm that the function doesn't hang when there is
        either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "stdout",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=True, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(100000, length)

    def testExecuteCommand_066(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain only data on stdout, and ignoreStderr should be False.
        This test helps confirm that the function doesn't hang when there is
        either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "stdout",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=False, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(100000, length)

    def testExecuteCommand_067(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain only data on stderr, and ignoreStderr should be True.
        This test helps confirm that the function doesn't hang when there is
        either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "stderr",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=True, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(0, length)

    def testExecuteCommand_068(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain only data on stdout, and ignoreStderr should be False.
        This test helps confirm that the function doesn't hang when there is
        either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "stderr",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=False, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(100000, length)

    def testExecuteCommand_069(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain data on stdout and stderr, and ignoreStderr should be
        True.  This test helps confirm that the function doesn't hang when there
        is either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "both",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=True, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(100000, length)

    def testExecuteCommand_070(self):
        """
        Execute a command with a huge amount of output all on stdout.  The output
        should contain data on stdout and stderr, and ignoreStderr should be
        False.  This test helps confirm that the function doesn't hang when there
        is either a lot of data or a lot of data to ignore.
        """
        lotsoflines = self.resources["lotsoflines.py"]
        command = [
            sys.executable,
            lotsoflines,
            "both",
        ]
        args = []

        filename = self.getTempfile()
        with open(filename, "wb") as outputFile:
            result = executeCommand(command, args, ignoreStderr=False, returnOutput=False, outputFile=outputFile)[0]
        self.assertEqual(0, result)

        length = 0
        with open(filename) as contents:
            for i in contents:
                length += 1

        self.assertEqual(100000 * 2, length)

    ####################
    # Test encodePath()
    ####################

    def testEncodePath_002(self):
        """
        Test with a simple string, empty.
        """
        path = ""
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_003(self):
        """
        Test with an simple string, an ascii word.
        """
        path = "whatever"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_004(self):
        """
        Test with simple string, a complete path.
        """
        path = "/usr/share/doc/xmltv/README.Debian"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_005(self):
        """
        Test with simple string, a non-ascii path.
        """
        path = "\xe2\x99\xaa\xe2\x99\xac"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_006(self):
        """
        Test with a simple string, empty.
        """
        path = ""
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_007(self):
        """
        Test with an simple string, an ascii word.
        """
        path = "whatever"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_008(self):
        """
        Test with simple string, a complete path.
        """
        path = "/usr/share/doc/xmltv/README.Debian"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual(path, safePath)

    def testEncodePath_009(self):
        """
        Test with simple string, a non-ascii path.
        """
        path = "\xe2\x99\xaa\xe2\x99\xac"
        safePath = encodePath(path)
        self.assertTrue(isinstance(safePath, str))
        self.assertEqual("\xe2\x99\xaa\xe2\x99\xac", safePath)

    #####################
    # Test convertSize()
    ######################

    def testConvertSize_001(self):
        """
        Test valid conversion from bytes to bytes.
        """
        fromUnit = UNIT_BYTES
        toUnit = UNIT_BYTES
        size = 10.0
        result = convertSize(size, fromUnit, toUnit)
        self.assertEqual(result, size)

    def testConvertSize_002(self):
        """
        Test valid conversion from sectors to bytes and back.
        """
        fromUnit = UNIT_SECTORS
        toUnit = UNIT_BYTES
        size = 10
        result1 = convertSize(size, fromUnit, toUnit)
        self.assertEqual(10 * 2048, result1)
        result2 = convertSize(result1, toUnit, fromUnit)
        self.assertEqual(result2, size)

    def testConvertSize_003(self):
        """
        Test valid conversion from kbytes to bytes and back.
        """
        fromUnit = UNIT_KBYTES
        toUnit = UNIT_BYTES
        size = 10
        result1 = convertSize(size, fromUnit, toUnit)
        self.assertEqual(10 * 1024, result1)
        result2 = convertSize(result1, toUnit, fromUnit)
        self.assertEqual(result2, size)

    def testConvertSize_004(self):
        """
        Test valid conversion from mbytes to bytes and back.
        """
        fromUnit = UNIT_MBYTES
        toUnit = UNIT_BYTES
        size = 10
        result1 = convertSize(size, fromUnit, toUnit)
        self.assertEqual(10 * 1024 * 1024, result1)
        result2 = convertSize(result1, toUnit, fromUnit)
        self.assertEqual(result2, size)

    def testConvertSize_005(self):
        """
        Test valid conversion from gbytes to bytes and back.
        """
        fromUnit = UNIT_GBYTES
        toUnit = UNIT_BYTES
        size = 10
        result1 = convertSize(size, fromUnit, toUnit)
        self.assertEqual(10 * 1024 * 1024 * 1024, result1)
        result2 = convertSize(result1, toUnit, fromUnit)
        self.assertEqual(result2, size)

    def testConvertSize_006(self):
        """
        Test valid conversion from mbytes to kbytes and back.
        """
        fromUnit = UNIT_MBYTES
        toUnit = UNIT_KBYTES
        size = 10
        result1 = convertSize(size, fromUnit, toUnit)
        self.assertEqual(size * 1024, result1)
        result2 = convertSize(result1, toUnit, fromUnit)
        self.assertEqual(result2, size)

    def testConvertSize_007(self):
        """
        Test with an invalid from unit (None).
        """
        fromUnit = None
        toUnit = UNIT_BYTES
        size = 10
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    def testConvertSize_008(self):
        """
        Test with an invalid from unit.
        """
        fromUnit = 333
        toUnit = UNIT_BYTES
        size = 10
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    def testConvertSize_009(self):
        """
        Test with an invalid to unit (None)
        """
        fromUnit = UNIT_BYTES
        toUnit = None
        size = 10
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    def testConvertSize_010(self):
        """
        Test with an invalid to unit.
        """
        fromUnit = UNIT_BYTES
        toUnit = "ken"
        size = 10
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    def testConvertSize_011(self):
        """
        Test with an invalid quantity (None)
        """
        fromUnit = UNIT_BYTES
        toUnit = UNIT_BYTES
        size = None
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    def testConvertSize_012(self):
        """
        Test with an invalid quantity (not a floating point).
        """
        fromUnit = UNIT_BYTES
        toUnit = UNIT_BYTES
        size = "blech"
        self.assertRaises(ValueError, convertSize, size, fromUnit, toUnit)

    ####################
    # Test nullDevice()
    #####################

    def testNullDevice_001(self):
        """
        Test that the function behaves sensibly.
        """
        device = nullDevice()
        if sys.platform == "win32":
            self.assertEqual("nul", device)
        else:
            self.assertEqual("/dev/null", device)

    ######################
    # Test displayBytes()
    ######################

    def testDisplayBytes_001(self):
        """
        Test display for a positive value < 1 KB
        """
        bytes = 12  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("12 bytes", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("12 bytes", result)

    def testDisplayBytes_002(self):
        """
        Test display for a negative value < 1 KB
        """
        bytes = -12  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("-12 bytes", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("-12 bytes", result)

    def testDisplayBytes_003(self):
        """
        Test display for a positive value = 1kB
        """
        bytes = 1024  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("1.00 kB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("1.000 kB", result)

    def testDisplayBytes_004(self):
        """
        Test display for a positive value >= 1kB
        """
        bytes = 5678  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("5.54 kB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("5.545 kB", result)

    def testDisplayBytes_005(self):
        """
        Test display for a negative value >= 1kB
        """
        bytes = -5678  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("-5.54 kB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("-5.545 kB", result)

    def testDisplayBytes_006(self):
        """
        Test display for a positive value = 1MB
        """
        bytes = 1024.0 * 1024.0  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("1.00 MB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("1.000 MB", result)

    def testDisplayBytes_007(self):
        """
        Test display for a positive value >= 1MB
        """
        bytes = 72372224  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("69.02 MB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("69.020 MB", result)

    def testDisplayBytes_008(self):
        """
        Test display for a negative value >= 1MB
        """
        bytes = -72372224.0  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("-69.02 MB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("-69.020 MB", result)

    def testDisplayBytes_009(self):
        """
        Test display for a positive value = 1GB
        """
        bytes = 1024.0 * 1024.0 * 1024.0  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("1.00 GB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("1.000 GB", result)

    def testDisplayBytes_010(self):
        """
        Test display for a positive value >= 1GB
        """
        bytes = 4.4 * 1024.0 * 1024.0 * 1024.0  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("4.40 GB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("4.400 GB", result)

    def testDisplayBytes_011(self):
        """
        Test display for a negative value >= 1GB
        """
        bytes = -1234567891011  # pylint: disable=W0622
        result = displayBytes(bytes)
        self.assertEqual("-1149.78 GB", result)
        result = displayBytes(bytes, 3)
        self.assertEqual("-1149.781 GB", result)

    def testDisplayBytes_012(self):
        """
        Test display with an invalid quantity (None).
        """
        bytes = None  # pylint: disable=W0622
        self.assertRaises(ValueError, displayBytes, bytes)

    def testDisplayBytes_013(self):
        """
        Test display with an invalid quantity (not a floating point).
        """
        bytes = "ken"  # pylint: disable=W0622
        self.assertRaises(ValueError, displayBytes, bytes)

    #########################
    # Test deriveDayOfWeek()
    #########################

    def testDeriveDayOfWeek_001(self):
        """
        Test for valid day names.
        """
        self.assertEqual(0, deriveDayOfWeek("monday"))
        self.assertEqual(1, deriveDayOfWeek("tuesday"))
        self.assertEqual(2, deriveDayOfWeek("wednesday"))
        self.assertEqual(3, deriveDayOfWeek("thursday"))
        self.assertEqual(4, deriveDayOfWeek("friday"))
        self.assertEqual(5, deriveDayOfWeek("saturday"))
        self.assertEqual(6, deriveDayOfWeek("sunday"))

    def testDeriveDayOfWeek_002(self):
        """
        Test for invalid day names.
        """
        self.assertEqual(-1, deriveDayOfWeek("bogus"))

    #######################
    # Test isStartOfWeek()
    #######################

    # noinspection PyUnboundLocalVariable
    def testIsStartOfWeek001(self):
        """
        Test positive case.
        """
        day = time.localtime().tm_wday
        if day == 0:
            result = isStartOfWeek("monday")
        elif day == 1:
            result = isStartOfWeek("tuesday")
        elif day == 2:
            result = isStartOfWeek("wednesday")
        elif day == 3:
            result = isStartOfWeek("thursday")
        elif day == 4:
            result = isStartOfWeek("friday")
        elif day == 5:
            result = isStartOfWeek("saturday")
        elif day == 6:
            result = isStartOfWeek("sunday")
        self.assertEqual(True, result)

    # noinspection PyUnboundLocalVariable
    def testIsStartOfWeek002(self):
        """
        Test negative case.
        """
        day = time.localtime().tm_wday
        if day == 0:
            result = isStartOfWeek("friday")
        elif day == 1:
            result = isStartOfWeek("saturday")
        elif day == 2:
            result = isStartOfWeek("sunday")
        elif day == 3:
            result = isStartOfWeek("monday")
        elif day == 4:
            result = isStartOfWeek("tuesday")
        elif day == 5:
            result = isStartOfWeek("wednesday")
        elif day == 6:
            result = isStartOfWeek("thursday")
        self.assertEqual(False, result)

    #############################
    # Test buildNormalizedPath()
    #############################

    def testBuildNormalizedPath001(self):
        """
        Test for a None path.
        """
        self.assertRaises(ValueError, buildNormalizedPath, None)

    def testBuildNormalizedPath002(self):
        """
        Test for an empty path.
        """
        path = ""
        expected = ""
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath003(self):
        """
        Test for "."
        """
        path = "."
        expected = "_"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath004(self):
        """
        Test for ".."
        """
        path = ".."
        expected = "_."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath005(self):
        """
        Test for "..........."
        """
        path = ".........."
        expected = "_........."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath006(self):
        """
        Test for "/"
        """
        path = "/"
        expected = "_"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath007(self):
        """
        Test for "\\"
        """
        path = "\\"
        expected = "_"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath008(self):
        """
        Test for "/."
        """
        path = "/."
        expected = "_"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath009(self):
        """
        Test for "/.."
        """
        path = "/.."
        expected = "_."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath010(self):
        """
        Test for "/..."
        """
        path = "/..."
        expected = "_.."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath011(self):
        r"""
        Test for "\."
        """
        path = r"\."
        expected = "_"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath012(self):
        r"""
        Test for "\.."
        """
        path = r"\.."
        expected = "_."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath013(self):
        r"""
        Test for "\..."
        """
        path = r"\..."
        expected = "_.."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath014(self):
        """
        Test for "/var/log/apache/httpd.log.1"
        """
        path = "/var/log/apache/httpd.log.1"
        expected = "var-log-apache-httpd.log.1"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath015(self):
        """
        Test for "var/log/apache/httpd.log.1"
        """
        path = "var/log/apache/httpd.log.1"
        expected = "var-log-apache-httpd.log.1"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath016(self):
        """
        Test for "\\var/log/apache\\httpd.log.1"
        """
        path = "\\var/log/apache\\httpd.log.1"
        expected = "var-log-apache-httpd.log.1"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath017(self):
        """
        Test for "/Big Nasty Base Path With Spaces/something/else/space s/file.  log   .2 ."
        """
        path = "/Big Nasty Base Path With Spaces/something/else/space s/file.  log   .2 ."
        expected = "Big_Nasty_Base_Path_With_Spaces-something-else-space_s-file.__log___.2_."
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath018(self):
        """
        Test for Windows path with drive letter and slashes.
        """
        path = "c:/Users/pronovic/projects/repos"
        expected = "c-Users-pronovic-projects-repos"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath019(self):
        """
        Test for Windows path with drive letter and backslashes.
        """
        path = r"c:\Users\pronovic\projects\repos"
        expected = "c-Users-pronovic-projects-repos"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    def testBuildNormalizedPath020(self):
        """
        Test for path with embedded colon.
        """
        path = "/path/to/whatever/key:value"
        expected = "path-to-whatever-key_value"
        actual = buildNormalizedPath(path)
        self.assertEqual(expected, actual)

    ##########################
    # Test splitCommandLine()
    ##########################

    def testSplitCommandLine_001(self):
        """
        Test for a None command line.
        """
        commandLine = None
        self.assertRaises(ValueError, splitCommandLine, commandLine)

    def testSplitCommandLine_002(self):
        """
        Test for an empty command line.
        """
        commandLine = ""
        result = splitCommandLine(commandLine)
        self.assertEqual([], result)

    def testSplitCommandLine_003(self):
        """
        Test for a command line with no quoted arguments.
        """
        commandLine = "cback --verbose stage store purge"
        result = splitCommandLine(commandLine)
        self.assertEqual(["cback", "--verbose", "stage", "store", "purge"], result)

    def testSplitCommandLine_004(self):
        """
        Test for a command line with double-quoted arguments.
        """
        commandLine = 'cback "this is a really long double-quoted argument"'
        result = splitCommandLine(commandLine)
        self.assertEqual(["cback", "this is a really long double-quoted argument"], result)

    def testSplitCommandLine_005(self):
        """
        Test for a command line with single-quoted arguments.
        """
        commandLine = "cback 'this is a really long single-quoted argument'"
        result = splitCommandLine(commandLine)
        self.assertEqual(["cback", "'this", "is", "a", "really", "long", "single-quoted", "argument'"], result)

    #########################
    # Test dereferenceLink()
    #########################

    @unittest.skipUnless(platformSupportsLinks(), "Requires soft links")
    def testDereferenceLink_001(self):
        """
        Test for a path that is a link, absolute=false.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "link002"])
        expected = "file002"
        actual = dereferenceLink(path, absolute=False)
        self.assertEqual(expected, actual)

    @unittest.skipUnless(platformSupportsLinks(), "Requires soft links")
    def testDereferenceLink_002(self):
        """
        Test for a path that is a link, absolute=true.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "link002"])
        expected = self.buildPath(["tree10", "file002"])
        actual = dereferenceLink(path)
        self.assertEqual(expected, actual)
        actual = dereferenceLink(path, absolute=True)
        self.assertEqual(expected, actual)

    def testDereferenceLink_003(self):
        """
        Test for a path that is a file (not a link), absolute=false.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "file001"])
        expected = path
        actual = dereferenceLink(path, absolute=False)
        self.assertEqual(expected, actual)

    def testDereferenceLink_004(self):
        """
        Test for a path that is a file (not a link), absolute=true.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "file001"])
        expected = path
        actual = dereferenceLink(path)
        self.assertEqual(expected, actual)
        actual = dereferenceLink(path, absolute=True)
        self.assertEqual(expected, actual)

    def testDereferenceLink_005(self):
        """
        Test for a path that is a directory (not a link), absolute=false.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "dir001"])
        expected = path
        actual = dereferenceLink(path, absolute=False)
        self.assertEqual(expected, actual)

    def testDereferenceLink_006(self):
        """
        Test for a path that is a directory (not a link), absolute=true.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "dir001"])
        expected = path
        actual = dereferenceLink(path)
        self.assertEqual(expected, actual)
        actual = dereferenceLink(path, absolute=True)
        self.assertEqual(expected, actual)

    def testDereferenceLink_007(self):
        """
        Test for a path that does not exist, absolute=false.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "blech"])
        expected = path
        actual = dereferenceLink(path, absolute=False)
        self.assertEqual(expected, actual)

    def testDereferenceLink_008(self):
        """
        Test for a path that does not exist, absolute=true.
        """
        self.extractTar("tree10")
        path = self.buildPath(["tree10", "blech"])
        expected = path
        actual = dereferenceLink(path)
        self.assertEqual(expected, actual)
        actual = dereferenceLink(path, absolute=True)
        self.assertEqual(expected, actual)

    ###################################
    # Test parseCommaSeparatedString()
    ###################################

    def testParseCommaSeparatedString_001(self):
        """
        Test parseCommaSeparatedString() for a None string.
        """
        actual = parseCommaSeparatedString(None)
        self.assertEqual(None, actual)

    def testParseCommaSeparatedString_002(self):
        """
        Test parseCommaSeparatedString() for an empty string.
        """
        actual = parseCommaSeparatedString("")
        self.assertEqual([], actual)

    def testParseCommaSeparatedString_003(self):
        """
        Test parseCommaSeparatedString() for a string with one value.
        """
        actual = parseCommaSeparatedString("ken")
        self.assertEqual(["ken"], actual)

    def testParseCommaSeparatedString_004(self):
        """
        Test parseCommaSeparatedString() for a string with multiple values, no
        spaces.
        """
        actual = parseCommaSeparatedString("a,b,c")
        self.assertEqual(["a", "b", "c"], actual)

    def testParseCommaSeparatedString_005(self):
        """
        Test parseCommaSeparatedString() for a string with multiple values, with
        spaces.
        """
        actual = parseCommaSeparatedString("a, b, c")
        self.assertEqual(["a", "b", "c"], actual)

    def testParseCommaSeparatedString_006(self):
        """
        Test parseCommaSeparatedString() for a string with multiple values,
        worst-case kind of value.
        """
        actual = parseCommaSeparatedString("   one,  two,three,   four , five   , six,   seven,,eight    ,")
        self.assertEqual(["one", "two", "three", "four", "five", "six", "seven", "eight"], actual)
