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
# Copyright (c) 2005-2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests Subversion extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/subversion.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in extend/subversion.py.  There are also tests for
   several of the private methods.

   Unfortunately, it's rather difficult to test this code in an automated
   fashion, even if you have access to Subversion, since the actual backup
   would need to have access to real Subversion repositories.  Because of this,
   there aren't any tests below that actually back up repositories.

   As a compromise, I test some of the private methods in the implementation.
   Normally, I don't like to test private methods, but in this case, testing
   the private methods will help give us some reasonable confidence in the code
   even if we can't talk to Subversion successfully.  This isn't perfect, but
   it's better than nothing.

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
   build environment.  There is a no need to use a SUBVERSIONTESTS_FULL
   environment variable to provide a "reduced feature set" test suite as for
   some of the other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.extend.subversion import BDBRepository, FSFSRepository, LocalConfig, Repository, RepositoryDir, SubversionConfig
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
    "subversion.conf.1",
    "subversion.conf.2",
    "subversion.conf.3",
    "subversion.conf.4",
    "subversion.conf.5",
    "subversion.conf.6",
    "subversion.conf.7",
]


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestBDBRepository class
##########################


class TestBDBRepository(unittest.TestCase):

    """
    Tests for the BDBRepository class.

    *Note:* This class is deprecated.  These tests are kept around to make sure
    that we don't accidentally break the interface.
    """

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
        obj = BDBRepository()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        repository = BDBRepository()
        self.assertEqual("BDB", repository.repositoryType)
        self.assertEqual(None, repository.repositoryPath)
        self.assertEqual(None, repository.collectMode)
        self.assertEqual(None, repository.compressMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        repository = BDBRepository("/path/to/it", "daily", "gzip")
        self.assertEqual("BDB", repository.repositoryType)
        self.assertEqual("/path/to/it", repository.repositoryPath)
        self.assertEqual("daily", repository.collectMode)
        self.assertEqual("gzip", repository.compressMode)

    # Removed testConstructor_003 after BDBRepository was deprecated

    def testConstructor_004(self):
        """
        Test assignment of repositoryPath attribute, None value.
        """
        repository = BDBRepository(repositoryPath="/path/to/something")
        self.assertEqual("/path/to/something", repository.repositoryPath)
        repository.repositoryPath = None
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_005(self):
        """
        Test assignment of repositoryPath attribute, valid value.
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.repositoryPath)
        repository.repositoryPath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", repository.repositoryPath)

    def testConstructor_006(self):
        """
        Test assignment of repositoryPath attribute, invalid value (empty).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_007(self):
        """
        Test assignment of repositoryPath attribute, invalid value (not absolute).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "relative/path")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        repository = BDBRepository(collectMode="daily")
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = None
        self.assertEqual(None, repository.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.collectMode)
        repository.collectMode = "daily"
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = "weekly"
        self.assertEqual("weekly", repository.collectMode)
        repository.collectMode = "incr"
        self.assertEqual("incr", repository.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "monthly")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        repository = BDBRepository(compressMode="gzip")
        self.assertEqual("gzip", repository.compressMode)
        repository.compressMode = None
        self.assertEqual(None, repository.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.compressMode)
        repository.compressMode = "none"
        self.assertEqual("none", repository.compressMode)
        repository.compressMode = "bzip2"
        self.assertEqual("bzip2", repository.compressMode)
        repository.compressMode = "gzip"
        self.assertEqual("gzip", repository.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "")
        self.assertEqual(None, repository.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        repository = BDBRepository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "compress")
        self.assertEqual(None, repository.compressMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        repository1 = BDBRepository()
        repository2 = BDBRepository()
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        repository1 = BDBRepository("/path", "daily", "gzip")
        repository2 = BDBRepository("/path", "daily", "gzip")
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, repositoryPath differs (one None).
        """
        repository1 = BDBRepository()
        repository2 = BDBRepository(repositoryPath="/zippy")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, repositoryPath differs.
        """
        repository1 = BDBRepository("/path", "daily", "gzip")
        repository2 = BDBRepository("/zippy", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        repository1 = BDBRepository()
        repository2 = BDBRepository(collectMode="incr")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        repository1 = BDBRepository("/path", "daily", "gzip")
        repository2 = BDBRepository("/path", "incr", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        repository1 = BDBRepository()
        repository2 = BDBRepository(compressMode="gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        repository1 = BDBRepository("/path", "daily", "bzip2")
        repository2 = BDBRepository("/path", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)


###########################
# TestFSFSRepository class
###########################


class TestFSFSRepository(unittest.TestCase):

    """
    Tests for the FSFSRepository class.

    *Note:* This class is deprecated.  These tests are kept around to make sure
    that we don't accidentally break the interface.
    """

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
        obj = FSFSRepository()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        repository = FSFSRepository()
        self.assertEqual("FSFS", repository.repositoryType)
        self.assertEqual(None, repository.repositoryPath)
        self.assertEqual(None, repository.collectMode)
        self.assertEqual(None, repository.compressMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        repository = FSFSRepository("/path/to/it", "daily", "gzip")
        self.assertEqual("FSFS", repository.repositoryType)
        self.assertEqual("/path/to/it", repository.repositoryPath)
        self.assertEqual("daily", repository.collectMode)
        self.assertEqual("gzip", repository.compressMode)

    # Removed testConstructor_003 after FSFSRepository was deprecated

    def testConstructor_004(self):
        """
        Test assignment of repositoryPath attribute, None value.
        """
        repository = FSFSRepository(repositoryPath="/path/to/something")
        self.assertEqual("/path/to/something", repository.repositoryPath)
        repository.repositoryPath = None
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_005(self):
        """
        Test assignment of repositoryPath attribute, valid value.
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.repositoryPath)
        repository.repositoryPath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", repository.repositoryPath)

    def testConstructor_006(self):
        """
        Test assignment of repositoryPath attribute, invalid value (empty).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_007(self):
        """
        Test assignment of repositoryPath attribute, invalid value (not absolute).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "relative/path")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        repository = FSFSRepository(collectMode="daily")
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = None
        self.assertEqual(None, repository.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.collectMode)
        repository.collectMode = "daily"
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = "weekly"
        self.assertEqual("weekly", repository.collectMode)
        repository.collectMode = "incr"
        self.assertEqual("incr", repository.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "monthly")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        repository = FSFSRepository(compressMode="gzip")
        self.assertEqual("gzip", repository.compressMode)
        repository.compressMode = None
        self.assertEqual(None, repository.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.compressMode)
        repository.compressMode = "none"
        self.assertEqual("none", repository.compressMode)
        repository.compressMode = "bzip2"
        self.assertEqual("bzip2", repository.compressMode)
        repository.compressMode = "gzip"
        self.assertEqual("gzip", repository.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "")
        self.assertEqual(None, repository.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        repository = FSFSRepository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "compress")
        self.assertEqual(None, repository.compressMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        repository1 = FSFSRepository()
        repository2 = FSFSRepository()
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        repository1 = FSFSRepository("/path", "daily", "gzip")
        repository2 = FSFSRepository("/path", "daily", "gzip")
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, repositoryPath differs (one None).
        """
        repository1 = FSFSRepository()
        repository2 = FSFSRepository(repositoryPath="/zippy")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, repositoryPath differs.
        """
        repository1 = FSFSRepository("/path", "daily", "gzip")
        repository2 = FSFSRepository("/zippy", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        repository1 = FSFSRepository()
        repository2 = FSFSRepository(collectMode="incr")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        repository1 = FSFSRepository("/path", "daily", "gzip")
        repository2 = FSFSRepository("/path", "incr", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        repository1 = FSFSRepository()
        repository2 = FSFSRepository(compressMode="gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        repository1 = FSFSRepository("/path", "daily", "bzip2")
        repository2 = FSFSRepository("/path", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)


#######################
# TestRepository class
#######################


class TestRepository(unittest.TestCase):

    """Tests for the Repository class."""

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
        obj = Repository()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        repository = Repository()
        self.assertEqual(None, repository.repositoryType)
        self.assertEqual(None, repository.repositoryPath)
        self.assertEqual(None, repository.collectMode)
        self.assertEqual(None, repository.compressMode)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        repository = Repository("type", "/path/to/it", "daily", "gzip")
        self.assertEqual("type", repository.repositoryType)
        self.assertEqual("/path/to/it", repository.repositoryPath)
        self.assertEqual("daily", repository.collectMode)
        self.assertEqual("gzip", repository.compressMode)

    def testConstructor_003(self):
        """
        Test assignment of repositoryType attribute, None value.
        """
        repository = Repository(repositoryType="type")
        self.assertEqual("type", repository.repositoryType)
        repository.repositoryType = None
        self.assertEqual(None, repository.repositoryType)

    def testConstructor_004(self):
        """
        Test assignment of repositoryType attribute, non-None value.
        """
        repository = Repository()
        self.assertEqual(None, repository.repositoryType)
        repository.repositoryType = ""
        self.assertEqual("", repository.repositoryType)
        repository.repositoryType = "test"
        self.assertEqual("test", repository.repositoryType)

    def testConstructor_005(self):
        """
        Test assignment of repositoryPath attribute, None value.
        """
        repository = Repository(repositoryPath="/path/to/something")
        self.assertEqual("/path/to/something", repository.repositoryPath)
        repository.repositoryPath = None
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_006(self):
        """
        Test assignment of repositoryPath attribute, valid value.
        """
        repository = Repository()
        self.assertEqual(None, repository.repositoryPath)
        repository.repositoryPath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", repository.repositoryPath)

    def testConstructor_007(self):
        """
        Test assignment of repositoryPath attribute, invalid value (empty).
        """
        repository = Repository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_008(self):
        """
        Test assignment of repositoryPath attribute, invalid value (not absolute).
        """
        repository = Repository()
        self.assertEqual(None, repository.repositoryPath)
        self.failUnlessAssignRaises(ValueError, repository, "repositoryPath", "relative/path")
        self.assertEqual(None, repository.repositoryPath)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        repository = Repository(collectMode="daily")
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = None
        self.assertEqual(None, repository.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        repository = Repository()
        self.assertEqual(None, repository.collectMode)
        repository.collectMode = "daily"
        self.assertEqual("daily", repository.collectMode)
        repository.collectMode = "weekly"
        self.assertEqual("weekly", repository.collectMode)
        repository.collectMode = "incr"
        self.assertEqual("incr", repository.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        repository = Repository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_012(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        repository = Repository()
        self.assertEqual(None, repository.collectMode)
        self.failUnlessAssignRaises(ValueError, repository, "collectMode", "monthly")
        self.assertEqual(None, repository.collectMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        repository = Repository(compressMode="gzip")
        self.assertEqual("gzip", repository.compressMode)
        repository.compressMode = None
        self.assertEqual(None, repository.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        repository = Repository()
        self.assertEqual(None, repository.compressMode)
        repository.compressMode = "none"
        self.assertEqual("none", repository.compressMode)
        repository.compressMode = "bzip2"
        self.assertEqual("bzip2", repository.compressMode)
        repository.compressMode = "gzip"
        self.assertEqual("gzip", repository.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        repository = Repository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "")
        self.assertEqual(None, repository.compressMode)

    def testConstructor_016(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        repository = Repository()
        self.assertEqual(None, repository.compressMode)
        self.failUnlessAssignRaises(ValueError, repository, "compressMode", "compress")
        self.assertEqual(None, repository.compressMode)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        repository1 = Repository()
        repository2 = Repository()
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        repository1 = Repository("type", "/path", "daily", "gzip")
        repository2 = Repository("type", "/path", "daily", "gzip")
        self.assertEqual(repository1, repository2)
        self.assertTrue(repository1 == repository2)
        self.assertTrue(not repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(repository1 >= repository2)
        self.assertTrue(not repository1 != repository2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, repositoryType differs (one None).
        """
        repository1 = Repository()
        repository2 = Repository(repositoryType="type")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, repositoryType differs.
        """
        repository1 = Repository("other", "/path", "daily", "gzip")
        repository2 = Repository("type", "/path", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_004a(self):
        """
        Test comparison of two differing objects, repositoryPath differs (one None).
        """
        repository1 = Repository()
        repository2 = Repository(repositoryPath="/zippy")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, repositoryPath differs.
        """
        repository1 = Repository("type", "/path", "daily", "gzip")
        repository2 = Repository("type", "/zippy", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        repository1 = Repository()
        repository2 = Repository(collectMode="incr")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        repository1 = Repository("type", "/path", "daily", "gzip")
        repository2 = Repository("type", "/path", "incr", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        repository1 = Repository()
        repository2 = Repository(compressMode="gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        repository1 = Repository("type", "/path", "daily", "bzip2")
        repository2 = Repository("type", "/path", "daily", "gzip")
        self.assertNotEqual(repository1, repository2)
        self.assertTrue(not repository1 == repository2)
        self.assertTrue(repository1 < repository2)
        self.assertTrue(repository1 <= repository2)
        self.assertTrue(not repository1 > repository2)
        self.assertTrue(not repository1 >= repository2)
        self.assertTrue(repository1 != repository2)


##########################
# TestRepositoryDir class
##########################


class TestRepositoryDir(unittest.TestCase):

    """Tests for the RepositoryDir class."""

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
        obj = RepositoryDir()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.repositoryType)
        self.assertEqual(None, repositoryDir.directoryPath)
        self.assertEqual(None, repositoryDir.collectMode)
        self.assertEqual(None, repositoryDir.compressMode)
        self.assertEqual(None, repositoryDir.relativeExcludePaths)
        self.assertEqual(None, repositoryDir.excludePatterns)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in.
        """
        repositoryDir = RepositoryDir("type", "/path/to/it", "daily", "gzip", ["whatever"], [".*software.*"])
        self.assertEqual("type", repositoryDir.repositoryType)
        self.assertEqual("/path/to/it", repositoryDir.directoryPath)
        self.assertEqual("daily", repositoryDir.collectMode)
        self.assertEqual("gzip", repositoryDir.compressMode)
        self.assertEqual(["whatever"], repositoryDir.relativeExcludePaths)
        self.assertEqual([".*software.*"], repositoryDir.excludePatterns)

    def testConstructor_003(self):
        """
        Test assignment of repositoryType attribute, None value.
        """
        repositoryDir = RepositoryDir(repositoryType="type")
        self.assertEqual("type", repositoryDir.repositoryType)
        repositoryDir.repositoryType = None
        self.assertEqual(None, repositoryDir.repositoryType)

    def testConstructor_004(self):
        """
        Test assignment of repositoryType attribute, non-None value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.repositoryType)
        repositoryDir.repositoryType = ""
        self.assertEqual("", repositoryDir.repositoryType)
        repositoryDir.repositoryType = "test"
        self.assertEqual("test", repositoryDir.repositoryType)

    def testConstructor_005(self):
        """
        Test assignment of directoryPath attribute, None value.
        """
        repositoryDir = RepositoryDir(directoryPath="/path/to/something")
        self.assertEqual("/path/to/something", repositoryDir.directoryPath)
        repositoryDir.directoryPath = None
        self.assertEqual(None, repositoryDir.directoryPath)

    def testConstructor_006(self):
        """
        Test assignment of directoryPath attribute, valid value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.directoryPath)
        repositoryDir.directoryPath = "/path/to/whatever"
        self.assertEqual("/path/to/whatever", repositoryDir.directoryPath)

    def testConstructor_007(self):
        """
        Test assignment of directoryPath attribute, invalid value (empty).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.directoryPath)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "directoryPath", "")
        self.assertEqual(None, repositoryDir.directoryPath)

    def testConstructor_008(self):
        """
        Test assignment of directoryPath attribute, invalid value (not absolute).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.directoryPath)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "directoryPath", "relative/path")
        self.assertEqual(None, repositoryDir.directoryPath)

    def testConstructor_009(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        repositoryDir = RepositoryDir(collectMode="daily")
        self.assertEqual("daily", repositoryDir.collectMode)
        repositoryDir.collectMode = None
        self.assertEqual(None, repositoryDir.collectMode)

    def testConstructor_010(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.collectMode)
        repositoryDir.collectMode = "daily"
        self.assertEqual("daily", repositoryDir.collectMode)
        repositoryDir.collectMode = "weekly"
        self.assertEqual("weekly", repositoryDir.collectMode)
        repositoryDir.collectMode = "incr"
        self.assertEqual("incr", repositoryDir.collectMode)

    def testConstructor_011(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.collectMode)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "collectMode", "")
        self.assertEqual(None, repositoryDir.collectMode)

    def testConstructor_012(self):
        """
        Test assignment of collectMode attribute, invalid value (not in list).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.collectMode)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "collectMode", "monthly")
        self.assertEqual(None, repositoryDir.collectMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        repositoryDir = RepositoryDir(compressMode="gzip")
        self.assertEqual("gzip", repositoryDir.compressMode)
        repositoryDir.compressMode = None
        self.assertEqual(None, repositoryDir.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.compressMode)
        repositoryDir.compressMode = "none"
        self.assertEqual("none", repositoryDir.compressMode)
        repositoryDir.compressMode = "bzip2"
        self.assertEqual("bzip2", repositoryDir.compressMode)
        repositoryDir.compressMode = "gzip"
        self.assertEqual("gzip", repositoryDir.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.compressMode)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "compressMode", "")
        self.assertEqual(None, repositoryDir.compressMode)

    def testConstructor_016(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.compressMode)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "compressMode", "compress")
        self.assertEqual(None, repositoryDir.compressMode)

    def testConstructor_017(self):
        """
        Test assignment of relativeExcludePaths attribute, None value.
        """
        repositoryDir = RepositoryDir(relativeExcludePaths=[])
        self.assertEqual([], repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths = None
        self.assertEqual(None, repositoryDir.relativeExcludePaths)

    def testConstructor_018(self):
        """
        Test assignment of relativeExcludePaths attribute, [] value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths = []
        self.assertEqual([], repositoryDir.relativeExcludePaths)

    def testConstructor_019(self):
        """
        Test assignment of relativeExcludePaths attribute, single valid entry.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths = [
            "stuff",
        ]
        self.assertEqual(["stuff"], repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths.insert(0, "bogus")
        self.assertEqual(["bogus", "stuff"], repositoryDir.relativeExcludePaths)

    def testConstructor_020(self):
        """
        Test assignment of relativeExcludePaths attribute, multiple valid
        entries.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths = [
            "bogus",
            "stuff",
        ]
        self.assertEqual(["bogus", "stuff"], repositoryDir.relativeExcludePaths)
        repositoryDir.relativeExcludePaths.append("more")
        self.assertEqual(["bogus", "stuff", "more"], repositoryDir.relativeExcludePaths)

    def testConstructor_021(self):
        """
        Test assignment of excludePatterns attribute, None value.
        """
        repositoryDir = RepositoryDir(excludePatterns=[])
        self.assertEqual([], repositoryDir.excludePatterns)
        repositoryDir.excludePatterns = None
        self.assertEqual(None, repositoryDir.excludePatterns)

    def testConstructor_022(self):
        """
        Test assignment of excludePatterns attribute, [] value.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        repositoryDir.excludePatterns = []
        self.assertEqual([], repositoryDir.excludePatterns)

    def testConstructor_023(self):
        """
        Test assignment of excludePatterns attribute, single valid entry.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        repositoryDir.excludePatterns = [
            "valid",
        ]
        self.assertEqual(["valid"], repositoryDir.excludePatterns)
        repositoryDir.excludePatterns.append("more")
        self.assertEqual(["valid", "more"], repositoryDir.excludePatterns)

    def testConstructor_024(self):
        """
        Test assignment of excludePatterns attribute, multiple valid entries.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        repositoryDir.excludePatterns = [
            "valid",
            "more",
        ]
        self.assertEqual(["valid", "more"], repositoryDir.excludePatterns)
        repositoryDir.excludePatterns.insert(1, "bogus")
        self.assertEqual(["valid", "bogus", "more"], repositoryDir.excludePatterns)

    def testConstructor_025(self):
        """
        Test assignment of excludePatterns attribute, single invalid entry.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "excludePatterns", ["*.jpg"])
        self.assertEqual(None, repositoryDir.excludePatterns)

    def testConstructor_026(self):
        """
        Test assignment of excludePatterns attribute, multiple invalid entries.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "excludePatterns", ["*.jpg", "*"])
        self.assertEqual(None, repositoryDir.excludePatterns)

    def testConstructor_027(self):
        """
        Test assignment of excludePatterns attribute, mixed valid and invalid
        entries.
        """
        repositoryDir = RepositoryDir()
        self.assertEqual(None, repositoryDir.excludePatterns)
        self.failUnlessAssignRaises(ValueError, repositoryDir, "excludePatterns", ["*.jpg", "valid"])
        self.assertEqual(None, repositoryDir.excludePatterns)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        repositoryDir1 = RepositoryDir()
        repositoryDir2 = RepositoryDir()
        self.assertEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(repositoryDir1 == repositoryDir2)
        self.assertTrue(not repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(repositoryDir1 >= repositoryDir2)
        self.assertTrue(not repositoryDir1 != repositoryDir2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        repositoryDir1 = RepositoryDir("type", "/path", "daily", "gzip")
        repositoryDir2 = RepositoryDir("type", "/path", "daily", "gzip")
        self.assertEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(repositoryDir1 == repositoryDir2)
        self.assertTrue(not repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(repositoryDir1 >= repositoryDir2)
        self.assertTrue(not repositoryDir1 != repositoryDir2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, repositoryType differs (one None).
        """
        repositoryDir1 = RepositoryDir()
        repositoryDir2 = RepositoryDir(repositoryType="type")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, repositoryType differs.
        """
        repositoryDir1 = RepositoryDir("other", "/path", "daily", "gzip")
        repositoryDir2 = RepositoryDir("type", "/path", "daily", "gzip")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_004a(self):
        """
        Test comparison of two differing objects, directoryPath differs (one None).
        """
        repositoryDir1 = RepositoryDir()
        repositoryDir2 = RepositoryDir(directoryPath="/zippy")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, directoryPath differs.
        """
        repositoryDir1 = RepositoryDir("type", "/path", "daily", "gzip")
        repositoryDir2 = RepositoryDir("type", "/zippy", "daily", "gzip")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        repositoryDir1 = RepositoryDir()
        repositoryDir2 = RepositoryDir(collectMode="incr")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        repositoryDir1 = RepositoryDir("type", "/path", "daily", "gzip")
        repositoryDir2 = RepositoryDir("type", "/path", "incr", "gzip")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        repositoryDir1 = RepositoryDir()
        repositoryDir2 = RepositoryDir(compressMode="gzip")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        repositoryDir1 = RepositoryDir("type", "/path", "daily", "bzip2")
        repositoryDir2 = RepositoryDir("type", "/path", "daily", "gzip")
        self.assertNotEqual(repositoryDir1, repositoryDir2)
        self.assertTrue(not repositoryDir1 == repositoryDir2)
        self.assertTrue(repositoryDir1 < repositoryDir2)
        self.assertTrue(repositoryDir1 <= repositoryDir2)
        self.assertTrue(not repositoryDir1 > repositoryDir2)
        self.assertTrue(not repositoryDir1 >= repositoryDir2)
        self.assertTrue(repositoryDir1 != repositoryDir2)


#############################
# TestSubversionConfig class
#############################


class TestSubversionConfig(unittest.TestCase):

    """Tests for the SubversionConfig class."""

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
        obj = SubversionConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.collectMode)
        self.assertEqual(None, subversion.compressMode)
        self.assertEqual(None, subversion.repositories)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values, repositories=None.
        """
        subversion = SubversionConfig("daily", "gzip", None)
        self.assertEqual("daily", subversion.collectMode)
        self.assertEqual("gzip", subversion.compressMode)
        self.assertEqual(None, subversion.repositories)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values, no repositories.
        """
        subversion = SubversionConfig("daily", "gzip", [])
        self.assertEqual("daily", subversion.collectMode)
        self.assertEqual("gzip", subversion.compressMode)
        self.assertEqual([], subversion.repositories)

    def testConstructor_004(self):
        """
        Test constructor with all values filled in, with valid values, with one repository.
        """
        repositories = [
            Repository(),
        ]
        subversion = SubversionConfig("daily", "gzip", repositories)
        self.assertEqual("daily", subversion.collectMode)
        self.assertEqual("gzip", subversion.compressMode)
        self.assertEqual(repositories, subversion.repositories)

    def testConstructor_005(self):
        """
        Test constructor with all values filled in, with valid values, with multiple repositories.
        """
        repositories = [
            Repository(collectMode="daily"),
            Repository(collectMode="weekly"),
        ]
        subversion = SubversionConfig("daily", "gzip", repositories=repositories)
        self.assertEqual("daily", subversion.collectMode)
        self.assertEqual("gzip", subversion.compressMode)
        self.assertEqual(repositories, subversion.repositories)

    def testConstructor_006(self):
        """
        Test assignment of collectMode attribute, None value.
        """
        subversion = SubversionConfig(collectMode="daily")
        self.assertEqual("daily", subversion.collectMode)
        subversion.collectMode = None
        self.assertEqual(None, subversion.collectMode)

    def testConstructor_007(self):
        """
        Test assignment of collectMode attribute, valid value.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.collectMode)
        subversion.collectMode = "weekly"
        self.assertEqual("weekly", subversion.collectMode)

    def testConstructor_008(self):
        """
        Test assignment of collectMode attribute, invalid value (empty).
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.collectMode)
        self.failUnlessAssignRaises(ValueError, subversion, "collectMode", "")
        self.assertEqual(None, subversion.collectMode)

    def testConstructor_009(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        subversion = SubversionConfig(compressMode="gzip")
        self.assertEqual("gzip", subversion.compressMode)
        subversion.compressMode = None
        self.assertEqual(None, subversion.compressMode)

    def testConstructor_010(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.compressMode)
        subversion.compressMode = "bzip2"
        self.assertEqual("bzip2", subversion.compressMode)

    def testConstructor_011(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.compressMode)
        self.failUnlessAssignRaises(ValueError, subversion, "compressMode", "")
        self.assertEqual(None, subversion.compressMode)

    def testConstructor_012(self):
        """
        Test assignment of repositories attribute, None value.
        """
        subversion = SubversionConfig(repositories=[])
        self.assertEqual([], subversion.repositories)
        subversion.repositories = None
        self.assertEqual(None, subversion.repositories)

    def testConstructor_013(self):
        """
        Test assignment of repositories attribute, [] value.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        subversion.repositories = []
        self.assertEqual([], subversion.repositories)

    def testConstructor_014(self):
        """
        Test assignment of repositories attribute, single valid entry.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        subversion.repositories = [
            Repository(),
        ]
        self.assertEqual([Repository()], subversion.repositories)
        subversion.repositories.append(Repository(collectMode="daily"))
        self.assertEqual([Repository(), Repository(collectMode="daily")], subversion.repositories)

    def testConstructor_015(self):
        """
        Test assignment of repositories attribute, multiple valid entries.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        subversion.repositories = [
            Repository(collectMode="daily"),
            Repository(collectMode="weekly"),
        ]
        self.assertEqual([Repository(collectMode="daily"), Repository(collectMode="weekly")], subversion.repositories)
        subversion.repositories.append(Repository(collectMode="incr"))
        self.assertEqual(
            [Repository(collectMode="daily"), Repository(collectMode="weekly"), Repository(collectMode="incr")],
            subversion.repositories,
        )

    def testConstructor_016(self):
        """
        Test assignment of repositories attribute, single invalid entry (None).
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        self.failUnlessAssignRaises(ValueError, subversion, "repositories", [None])
        self.assertEqual(None, subversion.repositories)

    def testConstructor_017(self):
        """
        Test assignment of repositories attribute, single invalid entry (wrong type).
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        self.failUnlessAssignRaises(ValueError, subversion, "repositories", [SubversionConfig()])
        self.assertEqual(None, subversion.repositories)

    def testConstructor_018(self):
        """
        Test assignment of repositories attribute, mixed valid and invalid entries.
        """
        subversion = SubversionConfig()
        self.assertEqual(None, subversion.repositories)
        self.failUnlessAssignRaises(ValueError, subversion, "repositories", [Repository(), SubversionConfig()])
        self.assertEqual(None, subversion.repositories)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        subversion1 = SubversionConfig()
        subversion2 = SubversionConfig()
        self.assertEqual(subversion1, subversion2)
        self.assertTrue(subversion1 == subversion2)
        self.assertTrue(not subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(subversion1 >= subversion2)
        self.assertTrue(not subversion1 != subversion2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None, list None.
        """
        subversion1 = SubversionConfig("daily", "gzip", None)
        subversion2 = SubversionConfig("daily", "gzip", None)
        self.assertEqual(subversion1, subversion2)
        self.assertTrue(subversion1 == subversion2)
        self.assertTrue(not subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(subversion1 >= subversion2)
        self.assertTrue(not subversion1 != subversion2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None, list empty.
        """
        subversion1 = SubversionConfig("daily", "gzip", [])
        subversion2 = SubversionConfig("daily", "gzip", [])
        self.assertEqual(subversion1, subversion2)
        self.assertTrue(subversion1 == subversion2)
        self.assertTrue(not subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(subversion1 >= subversion2)
        self.assertTrue(not subversion1 != subversion2)

    def testComparison_004(self):
        """
        Test comparison of two identical objects, all attributes non-None, list non-empty.
        """
        subversion1 = SubversionConfig("daily", "gzip", [Repository()])
        subversion2 = SubversionConfig("daily", "gzip", [Repository()])
        self.assertEqual(subversion1, subversion2)
        self.assertTrue(subversion1 == subversion2)
        self.assertTrue(not subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(subversion1 >= subversion2)
        self.assertTrue(not subversion1 != subversion2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, collectMode differs (one None).
        """
        subversion1 = SubversionConfig()
        subversion2 = SubversionConfig(collectMode="daily")
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, collectMode differs.
        """
        subversion1 = SubversionConfig("daily", "gzip", [Repository()])
        subversion2 = SubversionConfig("weekly", "gzip", [Repository()])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        subversion1 = SubversionConfig()
        subversion2 = SubversionConfig(compressMode="bzip2")
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        subversion1 = SubversionConfig("daily", "bzip2", [Repository()])
        subversion2 = SubversionConfig("daily", "gzip", [Repository()])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, repositories differs (one None, one empty).
        """
        subversion1 = SubversionConfig()
        subversion2 = SubversionConfig(repositories=[])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, repositories differs (one None, one not empty).
        """
        subversion1 = SubversionConfig()
        subversion2 = SubversionConfig(repositories=[Repository()])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, repositories differs (one empty, one not empty).
        """
        subversion1 = SubversionConfig("daily", "gzip", [])
        subversion2 = SubversionConfig("daily", "gzip", [Repository()])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, repositories differs (both not empty).
        """
        subversion1 = SubversionConfig("daily", "gzip", [Repository()])
        subversion2 = SubversionConfig("daily", "gzip", [Repository(), Repository()])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, repositories differs (both not empty).
        """
        subversion1 = SubversionConfig("daily", "gzip", [Repository(repositoryType="other")])
        subversion2 = SubversionConfig("daily", "gzip", [Repository(repositoryType="type")])
        self.assertNotEqual(subversion1, subversion2)
        self.assertTrue(not subversion1 == subversion2)
        self.assertTrue(subversion1 < subversion2)
        self.assertTrue(subversion1 <= subversion2)
        self.assertTrue(not subversion1 > subversion2)
        self.assertTrue(not subversion1 >= subversion2)
        self.assertTrue(subversion1 != subversion2)


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

        We dump a document containing just the subversion configuration, and then
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
        self.assertEqual(None, config.subversion)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.subversion)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["subversion.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of subversion attribute, None value.
        """
        config = LocalConfig()
        config.subversion = None
        self.assertEqual(None, config.subversion)

    def testConstructor_005(self):
        """
        Test assignment of subversion attribute, valid value.
        """
        config = LocalConfig()
        config.subversion = SubversionConfig()
        self.assertEqual(SubversionConfig(), config.subversion)

    def testConstructor_006(self):
        """
        Test assignment of subversion attribute, invalid value (not SubversionConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "subversion", "STRING!")

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
        config1.subversion = SubversionConfig()

        config2 = LocalConfig()
        config2.subversion = SubversionConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, subversion differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.subversion = SubversionConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, subversion differs.
        """
        config1 = LocalConfig()
        config1.subversion = SubversionConfig(collectMode="daily")

        config2 = LocalConfig()
        config2.subversion = SubversionConfig(collectMode="weekly")

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
        Test validate on a None subversion section.
        """
        config = LocalConfig()
        config.subversion = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty subversion section.
        """
        config = LocalConfig()
        config.subversion = SubversionConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty subversion section, repositories=None.
        """
        config = LocalConfig()
        config.subversion = SubversionConfig("weekly", "gzip", None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_004(self):
        """
        Test validate on a non-empty subversion section, repositories=[].
        """
        config = LocalConfig()
        config.subversion = SubversionConfig("weekly", "gzip", [])
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        defaults set, no values on repositories.
        """
        repositories = [Repository(repositoryPath="/one"), Repository(repositoryPath="/two")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_006(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        no defaults set, no values on repositiories.
        """
        repositories = [Repository(repositoryPath="/one"), Repository(repositoryPath="/two")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.repositories = repositories
        self.assertRaises(ValueError, config.validate)

    def testValidate_007(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        no defaults set, both values on repositories.
        """
        repositories = [Repository(repositoryPath="/two", collectMode="weekly", compressMode="gzip")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_008(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        collectMode only on repositories.
        """
        repositories = [Repository(repositoryPath="/two", collectMode="weekly")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.compressMode = "gzip"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_009(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        compressMode only on repositories.
        """
        repositories = [Repository(repositoryPath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "weekly"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_010(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        compressMode default and on repository.
        """
        repositories = [Repository(repositoryPath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_011(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        collectMode default and on repository.
        """
        repositories = [Repository(repositoryPath="/two", collectMode="daily")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_012(self):
        """
        Test validate on a non-empty subversion section, non-empty repositories,
        collectMode and compressMode default and on repository.
        """
        repositories = [Repository(repositoryPath="/two", collectMode="daily", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositories = repositories
        config.validate()

    def testValidate_013(self):
        """
        Test validate on a non-empty subversion section, repositoryDirs=None.
        """
        config = LocalConfig()
        config.subversion = SubversionConfig("weekly", "gzip", repositoryDirs=None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_014(self):
        """
        Test validate on a non-empty subversion section, repositoryDirs=[].
        """
        config = LocalConfig()
        config.subversion = SubversionConfig("weekly", "gzip", repositoryDirs=[])
        self.assertRaises(ValueError, config.validate)

    def testValidate_015(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        defaults set, no values on repositoryDirs.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/one"), RepositoryDir(directoryPath="/two")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_016(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        no defaults set, no values on repositiories.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/one"), RepositoryDir(directoryPath="/two")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.repositoryDirs = repositoryDirs
        self.assertRaises(ValueError, config.validate)

    def testValidate_017(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        no defaults set, both values on repositoryDirs.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", collectMode="weekly", compressMode="gzip")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_018(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        collectMode only on repositoryDirs.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", collectMode="weekly")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.compressMode = "gzip"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_019(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        compressMode only on repositoryDirs.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "weekly"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_020(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        compressMode default and on repository.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_021(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        collectMode default and on repository.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", collectMode="daily")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    def testValidate_022(self):
        """
        Test validate on a non-empty subversion section, non-empty repositoryDirs,
        collectMode and compressMode default and on repository.
        """
        repositoryDirs = [RepositoryDir(directoryPath="/two", collectMode="daily", compressMode="bzip2")]
        config = LocalConfig()
        config.subversion = SubversionConfig()
        config.subversion.collectMode = "daily"
        config.subversion.compressMode = "gzip"
        config.subversion.repositoryDirs = repositoryDirs
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["subversion.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.subversion)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.subversion)

    def testParse_002(self):
        """
        Parse config document with default modes, one repository.
        """
        repositories = [
            Repository(repositoryPath="/opt/public/svn/software"),
        ]
        path = self.resources["subversion.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)

    def testParse_003(self):
        """
        Parse config document with no default modes, one repository
        """
        repositories = [
            Repository(repositoryPath="/opt/public/svn/software", collectMode="daily", compressMode="gzip"),
        ]
        path = self.resources["subversion.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual(None, config.subversion.collectMode)
        self.assertEqual(None, config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual(None, config.subversion.collectMode)
        self.assertEqual(None, config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)

    def testParse_004(self):
        """
        Parse config document with default modes, several repositories with
        various overrides.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/opt/public/svn/one"))
        repositories.append(Repository(repositoryType="BDB", repositoryPath="/opt/public/svn/two", collectMode="weekly"))
        repositories.append(Repository(repositoryPath="/opt/public/svn/three", compressMode="bzip2"))
        repositories.append(
            Repository(repositoryType="FSFS", repositoryPath="/opt/public/svn/four", collectMode="incr", compressMode="bzip2")
        )
        path = self.resources["subversion.conf.4"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(repositories, config.subversion.repositories)
        self.assertEqual(None, config.subversion.repositoryDirs)

    def testParse_005(self):
        """
        Parse config document with default modes, one repository.
        """
        repositoryDirs = [
            RepositoryDir(directoryPath="/opt/public/svn/software"),
        ]
        path = self.resources["subversion.conf.5"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)

    def testParse_006(self):
        """
        Parse config document with no default modes, one repository
        """
        repositoryDirs = [
            RepositoryDir(directoryPath="/opt/public/svn/software", collectMode="daily", compressMode="gzip"),
        ]
        path = self.resources["subversion.conf.6"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual(None, config.subversion.collectMode)
        self.assertEqual(None, config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual(None, config.subversion.collectMode)
        self.assertEqual(None, config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)

    def testParse_007(self):
        """
        Parse config document with default modes, several repositoryDirs with
        various overrides.
        """
        repositoryDirs = []
        repositoryDirs.append(RepositoryDir(directoryPath="/opt/public/svn/one"))
        repositoryDirs.append(
            RepositoryDir(
                repositoryType="BDB", directoryPath="/opt/public/svn/two", collectMode="weekly", relativeExcludePaths=["software"]
            )
        )
        repositoryDirs.append(
            RepositoryDir(directoryPath="/opt/public/svn/three", compressMode="bzip2", excludePatterns=[".*software.*"])
        )
        repositoryDirs.append(
            RepositoryDir(
                repositoryType="FSFS",
                directoryPath="/opt/public/svn/four",
                collectMode="incr",
                compressMode="bzip2",
                relativeExcludePaths=["cedar", "banner"],
                excludePatterns=[".*software.*", ".*database.*"],
            )
        )
        path = self.resources["subversion.conf.7"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.subversion)
        self.assertEqual("daily", config.subversion.collectMode)
        self.assertEqual("gzip", config.subversion.compressMode)
        self.assertEqual(None, config.subversion.repositories)
        self.assertEqual(repositoryDirs, config.subversion.repositoryDirs)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        subversion = SubversionConfig()
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with defaults set, single repository with no optional values.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path"))
        subversion = SubversionConfig(collectMode="daily", compressMode="gzip", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_003(self):
        """
        Test with defaults set, single repository with collectMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="incr"))
        subversion = SubversionConfig(collectMode="daily", compressMode="gzip", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_004(self):
        """
        Test with defaults set, single repository with compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", compressMode="bzip2"))
        subversion = SubversionConfig(collectMode="daily", compressMode="gzip", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_005(self):
        """
        Test with defaults set, single repository with collectMode and compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="weekly", compressMode="bzip2"))
        subversion = SubversionConfig(collectMode="daily", compressMode="gzip", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_006(self):
        """
        Test with no defaults set, single repository with collectMode and compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="weekly", compressMode="bzip2"))
        subversion = SubversionConfig(repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_007(self):
        """
        Test with compressMode set, single repository with collectMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="weekly"))
        subversion = SubversionConfig(compressMode="gzip", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_008(self):
        """
        Test with collectMode set, single repository with compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", compressMode="gzip"))
        subversion = SubversionConfig(collectMode="weekly", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_009(self):
        """
        Test with compressMode set, single repository with collectMode and compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="incr", compressMode="gzip"))
        subversion = SubversionConfig(compressMode="bzip2", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_010(self):
        """
        Test with collectMode set, single repository with collectMode and compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path", collectMode="weekly", compressMode="gzip"))
        subversion = SubversionConfig(collectMode="incr", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)

    def testAddConfig_011(self):
        """
        Test with defaults set, multiple repositories with collectMode and compressMode set.
        """
        repositories = []
        repositories.append(Repository(repositoryPath="/path1", collectMode="daily", compressMode="gzip"))
        repositories.append(Repository(repositoryPath="/path2", collectMode="weekly", compressMode="gzip"))
        repositories.append(Repository(repositoryPath="/path3", collectMode="incr", compressMode="gzip"))
        repositories.append(Repository(repositoryPath="/path1", collectMode="daily", compressMode="bzip2"))
        repositories.append(Repository(repositoryPath="/path2", collectMode="weekly", compressMode="bzip2"))
        repositories.append(Repository(repositoryPath="/path3", collectMode="incr", compressMode="bzip2"))
        subversion = SubversionConfig(collectMode="incr", compressMode="bzip2", repositories=repositories)
        config = LocalConfig()
        config.subversion = subversion
        self.validateAddConfig(config)
