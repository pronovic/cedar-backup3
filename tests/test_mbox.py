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
# Purpose  : Tests mbox extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/mbox.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in extend/mbox.py.  There are also tests for
   several of the private methods.

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
   build environment.  There is a no need to use a MBOXTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.extend.mbox import LocalConfig, MboxConfig, MboxDir, MboxFile
from CedarBackup3.testutil import configureLogging, failUnlessAssignRaises, findResources
from CedarBackup3.xmlutil import createOutputDom, serializeDom

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "mbox.conf.1",
    "mbox.conf.2",
    "mbox.conf.3",
    "mbox.conf.4",
]


#######################################################################
# Test Case Classes
#######################################################################

#####################
# TestMboxFile class
#####################


class TestMboxFile(unittest.TestCase):

    """Tests for the MboxFile class."""

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
        obj = MboxFile()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.absolutePath)
        self.assertEqual(None, mboxFile.collectMode)
        self.assertEqual(None, mboxFile.compressMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        mboxFile = MboxFile("/path/to/it", "daily", "gzip")
        self.assertEqual("/path/to/it", mboxFile.absolutePath)
        self.assertEqual("daily", mboxFile.collectMode)
        self.assertEqual("gzip", mboxFile.compressMode)

    def testConstructor_003(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        mboxFile = MboxFile(absolutePath="/path/to/something")
        self.assertEqual("/path/to/something", mboxFile.absolutePath)
        mboxFile.absolutePath = None
        self.assertEqual(None, mboxFile.absolutePath)

    def testConstructor_004(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.absolutePath)
        mboxFile.absolutePath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", mboxFile.absolutePath)

    def testConstructor_005(self):
        """
        Test assignment of absolutePath attribute, invalid value (empty).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.absolutePath)
        self.failUnlessAssignRaises(ValueError, mboxFile, "absolutePath", "")
        self.assertEqual(None, mboxFile.absolutePath)

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, invalid value (not absolute).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.absolutePath)
        self.failUnlessAssignRaises(ValueError, mboxFile, "absolutePath", "relative/path")
        self.assertEqual(None, mboxFile.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        mboxFile = MboxFile(collectMode="daily")
        self.assertEqual("daily", mboxFile.collectMode)
        mboxFile.collectMode = None
        self.assertEqual(None, mboxFile.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.collectMode)
        mboxFile.collectMode = "daily"
        self.assertEqual("daily", mboxFile.collectMode)
        mboxFile.collectMode = "weekly"
        self.assertEqual("weekly", mboxFile.collectMode)
        mboxFile.collectMode = "incr"
        self.assertEqual("incr", mboxFile.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.collectMode)
        self.failUnlessAssignRaises(ValueError, mboxFile, "collectMode", "")
        self.assertEqual(None, mboxFile.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.collectMode)
        self.failUnlessAssignRaises(ValueError, mboxFile, "collectMode", "monthly")
        self.assertEqual(None, mboxFile.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        mboxFile = MboxFile(compressMode="gzip")
        self.assertEqual("gzip", mboxFile.compressMode)
        mboxFile.compressMode = None
        self.assertEqual(None, mboxFile.compressMode)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.compressMode)
        mboxFile.compressMode = "none"
        self.assertEqual("none", mboxFile.compressMode)
        mboxFile.compressMode = "bzip2"
        self.assertEqual("bzip2", mboxFile.compressMode)
        mboxFile.compressMode = "gzip"
        self.assertEqual("gzip", mboxFile.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.compressMode)
        self.failUnlessAssignRaises(ValueError, mboxFile, "compressMode", "")
        self.assertEqual(None, mboxFile.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        mboxFile = MboxFile()
        self.assertEqual(None, mboxFile.compressMode)
        self.failUnlessAssignRaises(ValueError, mboxFile, "compressMode", "compress")
        self.assertEqual(None, mboxFile.compressMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        mboxFile1 = MboxFile()
        mboxFile2 = MboxFile()
        self.assertEqual(mboxFile1, mboxFile2)
        self.assertTrue(mboxFile1 == mboxFile2)
        self.assertTrue(not mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(mboxFile1 >= mboxFile2)
        self.assertTrue(not mboxFile1 != mboxFile2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        mboxFile1 = MboxFile("/path", "daily", "gzip")
        mboxFile2 = MboxFile("/path", "daily", "gzip")
        self.assertEqual(mboxFile1, mboxFile2)
        self.assertTrue(mboxFile1 == mboxFile2)
        self.assertTrue(not mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(mboxFile1 >= mboxFile2)
        self.assertTrue(not mboxFile1 != mboxFile2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, absolutePath differs (one None).
        """
        mboxFile1 = MboxFile()
        mboxFile2 = MboxFile(absolutePath="/zippy")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, absolutePath differs.
        """
        mboxFile1 = MboxFile("/path", "daily", "gzip")
        mboxFile2 = MboxFile("/zippy", "daily", "gzip")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        mboxFile1 = MboxFile()
        mboxFile2 = MboxFile(collectMode="incr")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        mboxFile1 = MboxFile("/path", "daily", "gzip")
        mboxFile2 = MboxFile("/path", "incr", "gzip")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        mboxFile1 = MboxFile()
        mboxFile2 = MboxFile(compressMode="gzip")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        mboxFile1 = MboxFile("/path", "daily", "bzip2")
        mboxFile2 = MboxFile("/path", "daily", "gzip")
        self.assertNotEqual(mboxFile1, mboxFile2)
        self.assertTrue(not mboxFile1 == mboxFile2)
        self.assertTrue(mboxFile1 < mboxFile2)
        self.assertTrue(mboxFile1 <= mboxFile2)
        self.assertTrue(not mboxFile1 > mboxFile2)
        self.assertTrue(not mboxFile1 >= mboxFile2)
        self.assertTrue(mboxFile1 != mboxFile2)


#####################
# TestMboxDir class
#####################


class TestMboxDir(unittest.TestCase):

    """Tests for the MboxDir class."""

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
        obj = MboxDir()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.absolutePath)
        self.assertEqual(None, mboxDir.collectMode)
        self.assertEqual(None, mboxDir.compressMode)
        self.assertEqual(None, mboxDir.relativeExcludePaths)
        self.assertEqual(None, mboxDir.excludePatterns)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        mboxDir = MboxDir("/path/to/it", "daily", "gzip", ["whatever"], [".*SPAM.*"])
        self.assertEqual("/path/to/it", mboxDir.absolutePath)
        self.assertEqual("daily", mboxDir.collectMode)
        self.assertEqual("gzip", mboxDir.compressMode)
        self.assertEqual(["whatever"], mboxDir.relativeExcludePaths)
        self.assertEqual([".*SPAM.*"], mboxDir.excludePatterns)

    def testConstructor_003(self):
        """
        Test assignment of absolutePath attribute, None value.
        """
        mboxDir = MboxDir(absolutePath="/path/to/something")
        self.assertEqual("/path/to/something", mboxDir.absolutePath)
        mboxDir.absolutePath = None
        self.assertEqual(None, mboxDir.absolutePath)

    def testConstructor_004(self):
        """
        Test assignment of absolutePath attribute, valid value.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.absolutePath)
        mboxDir.absolutePath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", mboxDir.absolutePath)

    def testConstructor_005(self):
        """
        Test assignment of absolutePath attribute, invalid value (empty).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, mboxDir, "absolutePath", "")
        self.assertEqual(None, mboxDir.absolutePath)

    def testConstructor_006(self):
        """
        Test assignment of absolutePath attribute, invalid value (not absolute).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.absolutePath)
        self.failUnlessAssignRaises(ValueError, mboxDir, "absolutePath", "relative/path")
        self.assertEqual(None, mboxDir.absolutePath)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        mboxDir = MboxDir(collectMode="daily")
        self.assertEqual("daily", mboxDir.collectMode)
        mboxDir.collectMode = None
        self.assertEqual(None, mboxDir.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.collectMode)
        mboxDir.collectMode = "daily"
        self.assertEqual("daily", mboxDir.collectMode)
        mboxDir.collectMode = "weekly"
        self.assertEqual("weekly", mboxDir.collectMode)
        mboxDir.collectMode = "incr"
        self.assertEqual("incr", mboxDir.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.collectMode)
        self.failUnlessAssignRaises(ValueError, mboxDir, "collectMode", "")
        self.assertEqual(None, mboxDir.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.collectMode)
        self.failUnlessAssignRaises(ValueError, mboxDir, "collectMode", "monthly")
        self.assertEqual(None, mboxDir.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        mboxDir = MboxDir(compressMode="gzip")
        self.assertEqual("gzip", mboxDir.compressMode)
        mboxDir.compressMode = None
        self.assertEqual(None, mboxDir.compressMode)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.compressMode)
        mboxDir.compressMode = "none"
        self.assertEqual("none", mboxDir.compressMode)
        mboxDir.compressMode = "bzip2"
        self.assertEqual("bzip2", mboxDir.compressMode)
        mboxDir.compressMode = "gzip"
        self.assertEqual("gzip", mboxDir.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.compressMode)
        self.failUnlessAssignRaises(ValueError, mboxDir, "compressMode", "")
        self.assertEqual(None, mboxDir.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.compressMode)
        self.failUnlessAssignRaises(ValueError, mboxDir, "compressMode", "compress")
        self.assertEqual(None, mboxDir.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of relativeExcludePaths attribute, None value.
        """
        mboxDir = MboxDir(relativeExcludePaths=[])
        self.assertEqual([], mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths = None
        self.assertEqual(None, mboxDir.relativeExcludePaths)

    def testConstructor_016(self):
        """
        Test assignment of relativeExcludePaths attribute, [] value.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths = []
        self.assertEqual([], mboxDir.relativeExcludePaths)

    def testConstructor_017(self):
        """
        Test assignment of relativeExcludePaths attribute, single valid entry.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths = [
            "stuff",
        ]
        self.assertEqual(["stuff"], mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths.insert(0, "bogus")
        self.assertEqual(["bogus", "stuff"], mboxDir.relativeExcludePaths)

    def testConstructor_018(self):
        """
        Test assignment of relativeExcludePaths attribute, multiple valid
        entries.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths = [
            "bogus",
            "stuff",
        ]
        self.assertEqual(["bogus", "stuff"], mboxDir.relativeExcludePaths)
        mboxDir.relativeExcludePaths.append("more")
        self.assertEqual(["bogus", "stuff", "more"], mboxDir.relativeExcludePaths)

    def testConstructor_019(self):
        """
        Test assignment of excludePatterns attribute, None value.
        """
        mboxDir = MboxDir(excludePatterns=[])
        self.assertEqual([], mboxDir.excludePatterns)
        mboxDir.excludePatterns = None
        self.assertEqual(None, mboxDir.excludePatterns)

    def testConstructor_020(self):
        """
        Test assignment of excludePatterns attribute, [] value.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        mboxDir.excludePatterns = []
        self.assertEqual([], mboxDir.excludePatterns)

    def testConstructor_021(self):
        """
        Test assignment of excludePatterns attribute, single valid entry.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        mboxDir.excludePatterns = [
            "valid",
        ]
        self.assertEqual(["valid"], mboxDir.excludePatterns)
        mboxDir.excludePatterns.append("more")
        self.assertEqual(["valid", "more"], mboxDir.excludePatterns)

    def testConstructor_022(self):
        """
        Test assignment of excludePatterns attribute, multiple valid entries.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        mboxDir.excludePatterns = [
            "valid",
            "more",
        ]
        self.assertEqual(["valid", "more"], mboxDir.excludePatterns)
        mboxDir.excludePatterns.insert(1, "bogus")
        self.assertEqual(["valid", "bogus", "more"], mboxDir.excludePatterns)

    def testConstructor_023(self):
        """
        Test assignment of excludePatterns attribute, single invalid entry.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, mboxDir, "excludePatterns", ["*.jpg"])
        self.assertEqual(None, mboxDir.excludePatterns)

    def testConstructor_024(self):
        """
        Test assignment of excludePatterns attribute, multiple invalid entries.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, mboxDir, "excludePatterns", ["*.jpg", "*"])
        self.assertEqual(None, mboxDir.excludePatterns)

    def testConstructor_025(self):
        """
        Test assignment of excludePatterns attribute, mixed valid and invalid
        entries.
        """
        mboxDir = MboxDir()
        self.assertEqual(None, mboxDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, mboxDir, "excludePatterns", ["*.jpg", "valid"])
        self.assertEqual(None, mboxDir.excludePatterns)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir()
        self.assertEqual(mboxDir1, mboxDir2)
        self.assertTrue(mboxDir1 == mboxDir2)
        self.assertTrue(not mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(mboxDir1 >= mboxDir2)
        self.assertTrue(not mboxDir1 != mboxDir2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        mboxDir1 = MboxDir("/path", "daily", "gzip")
        mboxDir2 = MboxDir("/path", "daily", "gzip")
        self.assertEqual(mboxDir1, mboxDir2)
        self.assertTrue(mboxDir1 == mboxDir2)
        self.assertTrue(not mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(mboxDir1 >= mboxDir2)
        self.assertTrue(not mboxDir1 != mboxDir2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, absolutePath differs (one None).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(absolutePath="/zippy")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, absolutePath differs.
        """
        mboxDir1 = MboxDir("/path", "daily", "gzip")
        mboxDir2 = MboxDir("/zippy", "daily", "gzip")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(collectMode="incr")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        mboxDir1 = MboxDir("/path", "daily", "gzip")
        mboxDir2 = MboxDir("/path", "incr", "gzip")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(compressMode="gzip")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        mboxDir1 = MboxDir("/path", "daily", "bzip2")
        mboxDir2 = MboxDir("/path", "daily", "gzip")
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one None, one empty).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(relativeExcludePaths=[])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one None, one not empty).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(relativeExcludePaths=["stuff", "other"])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (one empty, one not empty).
        """
        mboxDir1 = MboxDir("/etc/whatever", "incr", "none", ["one"], [])
        mboxDir2 = MboxDir("/etc/whatever", "incr", "none", [], [])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(not mboxDir1 < mboxDir2)
        self.assertTrue(not mboxDir1 <= mboxDir2)
        self.assertTrue(mboxDir1 > mboxDir2)
        self.assertTrue(mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, relativeExcludePaths differs
        (both not empty).
        """
        mboxDir1 = MboxDir("/etc/whatever", "incr", "none", ["one"], [])
        mboxDir2 = MboxDir("/etc/whatever", "incr", "none", ["two"], [])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one empty).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(excludePatterns=[])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        None, one not empty).
        """
        mboxDir1 = MboxDir()
        mboxDir2 = MboxDir(excludePatterns=["one", "two", "three"])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, excludePatterns differs (one
        empty, one not empty).
        """
        mboxDir1 = MboxDir("/etc/whatever", "incr", "none", [], [])
        mboxDir2 = MboxDir("/etc/whatever", "incr", "none", [], ["pattern"])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, excludePatterns differs (both
        not empty).
        """
        mboxDir1 = MboxDir("/etc/whatever", "incr", "none", [], ["p1"])
        mboxDir2 = MboxDir("/etc/whatever", "incr", "none", [], ["p2"])
        self.assertNotEqual(mboxDir1, mboxDir2)
        self.assertTrue(not mboxDir1 == mboxDir2)
        self.assertTrue(mboxDir1 < mboxDir2)
        self.assertTrue(mboxDir1 <= mboxDir2)
        self.assertTrue(not mboxDir1 > mboxDir2)
        self.assertTrue(not mboxDir1 >= mboxDir2)
        self.assertTrue(mboxDir1 != mboxDir2)


#######################
# TestMboxConfig class
#######################


class TestMboxConfig(unittest.TestCase):

    """Tests for the MboxConfig class."""

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
        obj = MboxConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.collectMode)
        self.assertEqual(None, mbox.compressMode)
        self.assertEqual(None, mbox.mboxFiles)
        self.assertEqual(None, mbox.mboxDirs)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values, mboxFiles=None and mboxDirs=None.
        """
        mbox = MboxConfig("daily", "gzip", None, None)
        self.assertEqual("daily", mbox.collectMode)
        self.assertEqual("gzip", mbox.compressMode)
        self.assertEqual(None, mbox.mboxFiles)
        self.assertEqual(None, mbox.mboxDirs)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values, no mboxFiles, no mboxDirs.
        """
        mbox = MboxConfig("daily", "gzip", [], [])
        self.assertEqual("daily", mbox.collectMode)
        self.assertEqual("gzip", mbox.compressMode)
        self.assertEqual([], mbox.mboxFiles)
        self.assertEqual([], mbox.mboxDirs)

    def testConstructor_004(self):
        """
        Test constructor with all values filled in, with valid values, with one mboxFile, no mboxDirs.
        """
        mboxFiles = [
            MboxFile(),
        ]
        mbox = MboxConfig("daily", "gzip", mboxFiles, [])
        self.assertEqual("daily", mbox.collectMode)
        self.assertEqual("gzip", mbox.compressMode)
        self.assertEqual(mboxFiles, mbox.mboxFiles)
        self.assertEqual([], mbox.mboxDirs)

    def testConstructor_005(self):
        """
        Test constructor with all values filled in, with valid values, with no mboxFiles, one mboxDir.
        """
        mboxDirs = [
            MboxDir(),
        ]
        mbox = MboxConfig("daily", "gzip", [], mboxDirs)
        self.assertEqual("daily", mbox.collectMode)
        self.assertEqual("gzip", mbox.compressMode)
        self.assertEqual([], mbox.mboxFiles)
        self.assertEqual(mboxDirs, mbox.mboxDirs)

    def testConstructor_006(self):
        """
        Test constructor with all values filled in, with valid values, with multiple mboxFiles and mboxDirs.
        """
        mboxFiles = [
            MboxFile(collectMode="daily"),
            MboxFile(collectMode="weekly"),
        ]
        mboxDirs = [
            MboxDir(collectMode="weekly"),
            MboxDir(collectMode="incr"),
        ]
        mbox = MboxConfig("daily", "gzip", mboxFiles=mboxFiles, mboxDirs=mboxDirs)
        self.assertEqual("daily", mbox.collectMode)
        self.assertEqual("gzip", mbox.compressMode)
        self.assertEqual(mboxFiles, mbox.mboxFiles)
        self.assertEqual(mboxDirs, mbox.mboxDirs)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        mbox = MboxConfig(collectMode="daily")
        self.assertEqual("daily", mbox.collectMode)
        mbox.collectMode = None
        self.assertEqual(None, mbox.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.collectMode)
        mbox.collectMode = "weekly"
        self.assertEqual("weekly", mbox.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.collectMode)
        self.failUnlessAssignRaises(ValueError, mbox, "collectMode", "")
        self.assertEqual(None, mbox.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        mbox = MboxConfig(compressMode="gzip")
        self.assertEqual("gzip", mbox.compressMode)
        mbox.compressMode = None
        self.assertEqual(None, mbox.compressMode)

    def testConstructor_011(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.compressMode)
        mbox.compressMode = "bzip2"
        self.assertEqual("bzip2", mbox.compressMode)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.compressMode)
        self.failUnlessAssignRaises(ValueError, mbox, "compressMode", "")
        self.assertEqual(None, mbox.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of mboxFiles attribute, None value.
        """
        mbox = MboxConfig(mboxFiles=[])
        self.assertEqual([], mbox.mboxFiles)
        mbox.mboxFiles = None
        self.assertEqual(None, mbox.mboxFiles)

    def testConstructor_014(self):
        """
        Test assignment of mboxFiles attribute, [] value.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        mbox.mboxFiles = []
        self.assertEqual([], mbox.mboxFiles)

    def testConstructor_015(self):
        """
        Test assignment of mboxFiles attribute, single valid entry.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        mbox.mboxFiles = [
            MboxFile(),
        ]
        self.assertEqual([MboxFile()], mbox.mboxFiles)
        mbox.mboxFiles.append(MboxFile(collectMode="daily"))
        self.assertEqual([MboxFile(), MboxFile(collectMode="daily")], mbox.mboxFiles)

    def testConstructor_016(self):
        """
        Test assignment of mboxFiles attribute, multiple valid entries.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        mbox.mboxFiles = [
            MboxFile(collectMode="daily"),
            MboxFile(collectMode="weekly"),
        ]
        self.assertEqual([MboxFile(collectMode="daily"), MboxFile(collectMode="weekly")], mbox.mboxFiles)
        mbox.mboxFiles.append(MboxFile(collectMode="incr"))
        self.assertEqual(
            [MboxFile(collectMode="daily"), MboxFile(collectMode="weekly"), MboxFile(collectMode="incr")], mbox.mboxFiles
        )

    def testConstructor_017(self):
        """
        Test assignment of mboxFiles attribute, single invalid entry (None).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxFiles", [None])
        self.assertEqual(None, mbox.mboxFiles)

    def testConstructor_018(self):
        """
        Test assignment of mboxFiles attribute, single invalid entry (wrong type).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxFiles", [MboxDir()])
        self.assertEqual(None, mbox.mboxFiles)

    def testConstructor_019(self):
        """
        Test assignment of mboxFiles attribute, mixed valid and invalid entries.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxFiles)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxFiles", [MboxFile(), MboxDir()])
        self.assertEqual(None, mbox.mboxFiles)

    def testConstructor_020(self):
        """
        Test assignment of mboxDirs attribute, None value.
        """
        mbox = MboxConfig(mboxDirs=[])
        self.assertEqual([], mbox.mboxDirs)
        mbox.mboxDirs = None
        self.assertEqual(None, mbox.mboxDirs)

    def testConstructor_021(self):
        """
        Test assignment of mboxDirs attribute, [] value.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        mbox.mboxDirs = []
        self.assertEqual([], mbox.mboxDirs)

    def testConstructor_022(self):
        """
        Test assignment of mboxDirs attribute, single valid entry.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        mbox.mboxDirs = [
            MboxDir(),
        ]
        self.assertEqual([MboxDir()], mbox.mboxDirs)
        mbox.mboxDirs.append(MboxDir(collectMode="daily"))
        self.assertEqual([MboxDir(), MboxDir(collectMode="daily")], mbox.mboxDirs)

    def testConstructor_023(self):
        """
        Test assignment of mboxDirs attribute, multiple valid entries.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        mbox.mboxDirs = [
            MboxDir(collectMode="daily"),
            MboxDir(collectMode="weekly"),
        ]
        self.assertEqual([MboxDir(collectMode="daily"), MboxDir(collectMode="weekly")], mbox.mboxDirs)
        mbox.mboxDirs.append(MboxDir(collectMode="incr"))
        self.assertEqual([MboxDir(collectMode="daily"), MboxDir(collectMode="weekly"), MboxDir(collectMode="incr")], mbox.mboxDirs)

    def testConstructor_024(self):
        """
        Test assignment of mboxDirs attribute, single invalid entry (None).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxDirs", [None])
        self.assertEqual(None, mbox.mboxDirs)

    def testConstructor_025(self):
        """
        Test assignment of mboxDirs attribute, single invalid entry (wrong type).
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxDirs", [MboxFile()])
        self.assertEqual(None, mbox.mboxDirs)

    def testConstructor_026(self):
        """
        Test assignment of mboxDirs attribute, mixed valid and invalid entries.
        """
        mbox = MboxConfig()
        self.assertEqual(None, mbox.mboxDirs)
        self.failUnlessAssignRaises(ValueError, mbox, "mboxDirs", [MboxDir(), MboxFile()])
        self.assertEqual(None, mbox.mboxDirs)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig()
        self.assertEqual(mbox1, mbox2)
        self.assertTrue(mbox1 == mbox2)
        self.assertTrue(not mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(mbox1 >= mbox2)
        self.assertTrue(not mbox1 != mbox2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None, lists None.
        """
        mbox1 = MboxConfig("daily", "gzip", None, None)
        mbox2 = MboxConfig("daily", "gzip", None, None)
        self.assertEqual(mbox1, mbox2)
        self.assertTrue(mbox1 == mbox2)
        self.assertTrue(not mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(mbox1 >= mbox2)
        self.assertTrue(not mbox1 != mbox2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None, lists empty.
        """
        mbox1 = MboxConfig("daily", "gzip", [], [])
        mbox2 = MboxConfig("daily", "gzip", [], [])
        self.assertEqual(mbox1, mbox2)
        self.assertTrue(mbox1 == mbox2)
        self.assertTrue(not mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(mbox1 >= mbox2)
        self.assertTrue(not mbox1 != mbox2)

    def testComparison_004(self):
        """
        Test comparison of two identical objects, all attributes non-None, lists non-empty.
        """
        mbox1 = MboxConfig("daily", "gzip", [MboxFile()], [MboxDir()])
        mbox2 = MboxConfig("daily", "gzip", [MboxFile()], [MboxDir()])
        self.assertEqual(mbox1, mbox2)
        self.assertTrue(mbox1 == mbox2)
        self.assertTrue(not mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(mbox1 >= mbox2)
        self.assertTrue(not mbox1 != mbox2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(collectMode="daily")
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        mbox1 = MboxConfig("daily", "gzip", [MboxFile()])
        mbox2 = MboxConfig("weekly", "gzip", [MboxFile()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(compressMode="bzip2")
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        mbox1 = MboxConfig("daily", "bzip2", [MboxFile()])
        mbox2 = MboxConfig("daily", "gzip", [MboxFile()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, mboxFiles differs (one None, one empty).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(mboxFiles=[])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, mboxFiles differs (one None, one not empty).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(mboxFiles=[MboxFile()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, mboxFiles differs (one empty, one not empty).
        """
        mbox1 = MboxConfig("daily", "gzip", [], None)
        mbox2 = MboxConfig("daily", "gzip", [MboxFile()], None)
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, mboxFiles differs (both not empty).
        """
        mbox1 = MboxConfig("daily", "gzip", [MboxFile()], None)
        mbox2 = MboxConfig("daily", "gzip", [MboxFile(), MboxFile()], None)
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, mboxDirs differs (one None, one empty).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(mboxDirs=[])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, mboxDirs differs (one None, one not empty).
        """
        mbox1 = MboxConfig()
        mbox2 = MboxConfig(mboxDirs=[MboxDir()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, mboxDirs differs (one empty, one not empty).
        """
        mbox1 = MboxConfig("daily", "gzip", None, [])
        mbox2 = MboxConfig("daily", "gzip", None, [MboxDir()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, mboxDirs differs (both not empty).
        """
        mbox1 = MboxConfig("daily", "gzip", None, [MboxDir()])
        mbox2 = MboxConfig("daily", "gzip", None, [MboxDir(), MboxDir()])
        self.assertNotEqual(mbox1, mbox2)
        self.assertTrue(not mbox1 == mbox2)
        self.assertTrue(mbox1 < mbox2)
        self.assertTrue(mbox1 <= mbox2)
        self.assertTrue(not mbox1 > mbox2)
        self.assertTrue(not mbox1 >= mbox2)
        self.assertTrue(mbox1 != mbox2)


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

        We dump a document containing just the mbox configuration, and then
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
        self.assertEqual(None, config.mbox)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.mbox)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["mbox.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of mbox attribute, None value.
        """
        config = LocalConfig()
        config.mbox = None
        self.assertEqual(None, config.mbox)

    def testConstructor_005(self):
        """
        Test assignment of mbox attribute, valid value.
        """
        config = LocalConfig()
        config.mbox = MboxConfig()
        self.assertEqual(MboxConfig(), config.mbox)

    def testConstructor_006(self):
        """
        Test assignment of mbox attribute, invalid value (not MboxConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "mbox", "STRING!")

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
        config1.mbox = MboxConfig()

        config2 = LocalConfig()
        config2.mbox = MboxConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, mbox differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.mbox = MboxConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, mbox differs.
        """
        config1 = LocalConfig()
        config1.mbox = MboxConfig(collectMode="daily")

        config2 = LocalConfig()
        config2.mbox = MboxConfig(collectMode="weekly")

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
        Test validate on a None mbox section.
        """
        config = LocalConfig()
        config.mbox = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty mbox section.
        """
        config = LocalConfig()
        config.mbox = MboxConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty mbox section, mboxFiles=None and mboxDirs=None.
        """
        config = LocalConfig()
        config.mbox = MboxConfig("weekly", "gzip", None, None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_004(self):
        """
        Test validate on a non-empty mbox section, mboxFiles=[] and mboxDirs=[].
        """
        config = LocalConfig()
        config.mbox = MboxConfig("weekly", "gzip", [], [])
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        defaults set, no values on files.
        """
        mboxFiles = [MboxFile(absolutePath="/one"), MboxFile(absolutePath="/two")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_006(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        defaults set, no values on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/one"), MboxDir(absolutePath="/two")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_007(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        no defaults set, no values on files.
        """
        mboxFiles = [MboxFile(absolutePath="/one"), MboxFile(absolutePath="/two")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_008(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        no defaults set, no values on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/one"), MboxDir(absolutePath="/two")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        self.assertRaises(ValueError, config.validate)

    def testValidate_009(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        no defaults set, both values on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", collectMode="weekly", compressMode="gzip")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_010(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        no defaults set, both values on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", collectMode="weekly", compressMode="gzip")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_011(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        collectMode only on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", collectMode="weekly")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_012(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        collectMode only on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", collectMode="weekly")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_013(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        compressMode only on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "weekly"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_014(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        compressMode only on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "weekly"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_015(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        compressMode default and on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_016(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        compressMode default and on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_017(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        collectMode default and on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", collectMode="daily")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_018(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        collectMode default and on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", collectMode="daily")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    def testValidate_019(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxFiles,
        collectMode and compressMode default and on files.
        """
        mboxFiles = [MboxFile(absolutePath="/two", collectMode="daily", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = mboxFiles
        config.mbox.mboxDirs = None
        config.validate()

    def testValidate_020(self):
        """
        Test validate on a non-empty mbox section, non-empty mboxDirs,
        collectMode and compressMode default and on directories.
        """
        mboxDirs = [MboxDir(absolutePath="/two", collectMode="daily", compressMode="bzip2")]
        config = LocalConfig()
        config.mbox = MboxConfig()
        config.mbox.collectMode = "daily"
        config.mbox.compressMode = "gzip"
        config.mbox.mboxFiles = None
        config.mbox.mboxDirs = mboxDirs
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["mbox.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.mbox)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.mbox)

    def testParse_002(self):
        """
        Parse config document with default modes, one collect file and one collect dir.
        """
        mboxFiles = [
            MboxFile(absolutePath="/home/joebob/mail/cedar-backup-users"),
        ]
        mboxDirs = [
            MboxDir(absolutePath="/home/billiejoe/mail"),
        ]
        path = self.resources["mbox.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual("daily", config.mbox.collectMode)
        self.assertEqual("gzip", config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual("daily", config.mbox.collectMode)
        self.assertEqual("gzip", config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)

    def testParse_003(self):
        """
        Parse config document with no default modes, one collect file and one collect dir.
        """
        mboxFiles = [
            MboxFile(absolutePath="/home/joebob/mail/cedar-backup-users", collectMode="daily", compressMode="gzip"),
        ]
        mboxDirs = [
            MboxDir(absolutePath="/home/billiejoe/mail", collectMode="weekly", compressMode="bzip2"),
        ]
        path = self.resources["mbox.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual(None, config.mbox.collectMode)
        self.assertEqual(None, config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual(None, config.mbox.collectMode)
        self.assertEqual(None, config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)

    def testParse_004(self):
        """
        Parse config document with default modes, several files with
        various overrides and exclusions.
        """
        mboxFiles = []
        mboxFile = MboxFile(absolutePath="/home/jimbo/mail/cedar-backup-users")
        mboxFiles.append(mboxFile)
        mboxFile = MboxFile(absolutePath="/home/joebob/mail/cedar-backup-users", collectMode="daily", compressMode="gzip")
        mboxFiles.append(mboxFile)
        mboxDirs = []
        mboxDir = MboxDir(absolutePath="/home/frank/mail/cedar-backup-users")
        mboxDirs.append(mboxDir)
        mboxDir = MboxDir(absolutePath="/home/jimbob/mail", compressMode="bzip2", relativeExcludePaths=["logomachy-devel"])
        mboxDirs.append(mboxDir)
        mboxDir = MboxDir(
            absolutePath="/home/billiejoe/mail", collectMode="weekly", compressMode="bzip2", excludePatterns=[".*SPAM.*"]
        )
        mboxDirs.append(mboxDir)
        mboxDir = MboxDir(
            absolutePath="/home/billybob/mail",
            relativeExcludePaths=["debian-devel", "debian-python"],
            excludePatterns=[".*SPAM.*", ".*JUNK.*"],
        )
        mboxDirs.append(mboxDir)
        path = self.resources["mbox.conf.4"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual("incr", config.mbox.collectMode)
        self.assertEqual("none", config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mbox)
        self.assertEqual("incr", config.mbox.collectMode)
        self.assertEqual("none", config.mbox.compressMode)
        self.assertEqual(mboxFiles, config.mbox.mboxFiles)
        self.assertEqual(mboxDirs, config.mbox.mboxDirs)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        mbox = MboxConfig()
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with defaults set, single mbox file with no optional values.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_003(self):
        """
        Test with defaults set, single mbox directory with no optional values.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_004(self):
        """
        Test with defaults set, single mbox file with collectMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="incr"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_005(self):
        """
        Test with defaults set, single mbox directory with collectMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="incr"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_006(self):
        """
        Test with defaults set, single mbox file with compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", compressMode="bzip2"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_007(self):
        """
        Test with defaults set, single mbox directory with compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", compressMode="bzip2"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_008(self):
        """
        Test with defaults set, single mbox file with collectMode and compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="weekly", compressMode="bzip2"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_009(self):
        """
        Test with defaults set, single mbox directory with collectMode and compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="weekly", compressMode="bzip2"))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_010(self):
        """
        Test with no defaults set, single mbox file with collectMode and compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="weekly", compressMode="bzip2"))
        mbox = MboxConfig(mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_011(self):
        """
        Test with no defaults set, single mbox directory with collectMode and compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="weekly", compressMode="bzip2"))
        mbox = MboxConfig(mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_012(self):
        """
        Test with compressMode set, single mbox file with collectMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="weekly"))
        mbox = MboxConfig(compressMode="gzip", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_013(self):
        """
        Test with compressMode set, single mbox directory with collectMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="weekly"))
        mbox = MboxConfig(compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_014(self):
        """
        Test with collectMode set, single mbox file with compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", compressMode="gzip"))
        mbox = MboxConfig(collectMode="weekly", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_015(self):
        """
        Test with collectMode set, single mbox directory with compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", compressMode="gzip"))
        mbox = MboxConfig(collectMode="weekly", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_016(self):
        """
        Test with compressMode set, single mbox file with collectMode and compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="incr", compressMode="gzip"))
        mbox = MboxConfig(compressMode="bzip2", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_017(self):
        """
        Test with compressMode set, single mbox directory with collectMode and compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="incr", compressMode="gzip"))
        mbox = MboxConfig(compressMode="bzip2", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_018(self):
        """
        Test with collectMode set, single mbox file with collectMode and compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path", collectMode="weekly", compressMode="gzip"))
        mbox = MboxConfig(collectMode="incr", mboxFiles=mboxFiles)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_019(self):
        """
        Test with collectMode set, single mbox directory with collectMode and compressMode set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", collectMode="weekly", compressMode="gzip"))
        mbox = MboxConfig(collectMode="incr", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_020(self):
        """
        Test with defaults set, single mbox directory with relativeExcludePaths set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", relativeExcludePaths=["one", "two"]))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_021(self):
        """
        Test with defaults set, single mbox directory with excludePatterns set.
        """
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path", excludePatterns=["one", "two"]))
        mbox = MboxConfig(collectMode="daily", compressMode="gzip", mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)

    def testAddConfig_022(self):
        """
        Test with defaults set, multiple mbox files and directories with collectMode and compressMode set.
        """
        mboxFiles = []
        mboxFiles.append(MboxFile(absolutePath="/path1", collectMode="daily", compressMode="gzip"))
        mboxFiles.append(MboxFile(absolutePath="/path2", collectMode="weekly", compressMode="gzip"))
        mboxFiles.append(MboxFile(absolutePath="/path3", collectMode="incr", compressMode="gzip"))
        mboxDirs = []
        mboxDirs.append(MboxDir(absolutePath="/path1", collectMode="daily", compressMode="bzip2"))
        mboxDirs.append(MboxDir(absolutePath="/path2", collectMode="weekly", compressMode="bzip2"))
        mboxDirs.append(MboxDir(absolutePath="/path3", collectMode="incr", compressMode="bzip2"))
        mbox = MboxConfig(collectMode="incr", compressMode="bzip2", mboxFiles=mboxFiles, mboxDirs=mboxDirs)
        config = LocalConfig()
        config.mbox = mbox
        self.validateAddConfig(config)
