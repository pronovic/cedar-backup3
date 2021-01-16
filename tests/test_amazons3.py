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
# Copyright (c) 2014-2015 Kenneth J. Pronovici.
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
# Purpose  : Tests amazons3 extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/amazons3.py.

Code Coverage
=============

   This module contains individual tests for the the public classes implemented
   in extend/amazons3.py.  There are also tests for some of the private
   functions.

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

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import tempfile
import unittest

from CedarBackup3.config import ByteQuantity
from CedarBackup3.extend.amazons3 import AmazonS3Config, LocalConfig
from CedarBackup3.testutil import (
    buildPath,
    configureLogging,
    extractTar,
    failUnlessAssignRaises,
    findResources,
    platformMacOsX,
    removedir,
)
from CedarBackup3.tools.amazons3 import _buildSourceFiles, _checkSourceFiles
from CedarBackup3.util import UNIT_BYTES, UNIT_GBYTES, UNIT_MBYTES
from CedarBackup3.xmlutil import createOutputDom, serializeDom

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "amazons3.conf.1",
    "amazons3.conf.2",
    "amazons3.conf.3",
    "tree1.tar.gz",
    "tree2.tar.gz",
    "tree4.tar.gz",
    "tree8.tar.gz",
    "tree13.tar.gz",
    "tree15.tar.gz",
    "tree16.tar.gz",
    "tree17.tar.gz",
    "tree18.tar.gz",
    "tree19.tar.gz",
    "tree20.tar.gz",
]


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestAmazonS3Config class
##########################


class TestAmazonS3Config(unittest.TestCase):

    """Tests for the AmazonS3Config class."""

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
        obj = AmazonS3Config()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(False, amazons3.warnMidnite)
        self.assertEqual(None, amazons3.s3Bucket)
        self.assertEqual(None, amazons3.encryptCommand)
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)

    def testConstructor_002a(self):
        """
        Test constructor with all values filled in, with valid values (integers).
        """
        amazons3 = AmazonS3Config(True, "bucket", "encrypt", 1, 2)
        self.assertEqual(True, amazons3.warnMidnite)
        self.assertEqual("bucket", amazons3.s3Bucket)
        self.assertEqual("encrypt", amazons3.encryptCommand)
        self.assertEqual(1, amazons3.fullBackupSizeLimit)
        self.assertEqual(2, amazons3.incrementalBackupSizeLimit)
        self.assertEqual(ByteQuantity(1, UNIT_BYTES), amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(2, UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_002b(self):
        """
        Test constructor with all values filled in, with valid values (byte quantities).
        """
        amazons3 = AmazonS3Config(True, "bucket", "encrypt", ByteQuantity(1, UNIT_BYTES), ByteQuantity(2, UNIT_BYTES))
        self.assertEqual(True, amazons3.warnMidnite)
        self.assertEqual("bucket", amazons3.s3Bucket)
        self.assertEqual("encrypt", amazons3.encryptCommand)
        self.assertEqual(ByteQuantity(1, UNIT_BYTES), amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(2, UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_003(self):
        """
        Test assignment of warnMidnite attribute, valid value (real boolean).
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(False, amazons3.warnMidnite)
        amazons3.warnMidnite = True
        self.assertEqual(True, amazons3.warnMidnite)
        amazons3.warnMidnite = False
        self.assertEqual(False, amazons3.warnMidnite)

    def testConstructor_004(self):
        """
        Test assignment of warnMidnite attribute, valid value (expression).
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(False, amazons3.warnMidnite)
        amazons3.warnMidnite = 0
        self.assertEqual(False, amazons3.warnMidnite)
        amazons3.warnMidnite = []
        self.assertEqual(False, amazons3.warnMidnite)
        amazons3.warnMidnite = None
        self.assertEqual(False, amazons3.warnMidnite)
        amazons3.warnMidnite = ["a"]
        self.assertEqual(True, amazons3.warnMidnite)
        amazons3.warnMidnite = 3
        self.assertEqual(True, amazons3.warnMidnite)

    def testConstructor_005(self):
        """
        Test assignment of s3Bucket attribute, None value.
        """
        amazons3 = AmazonS3Config(s3Bucket="bucket")
        self.assertEqual("bucket", amazons3.s3Bucket)
        amazons3.s3Bucket = None
        self.assertEqual(None, amazons3.s3Bucket)

    def testConstructor_006(self):
        """
        Test assignment of s3Bucket attribute, valid value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.s3Bucket)
        amazons3.s3Bucket = "bucket"
        self.assertEqual("bucket", amazons3.s3Bucket)

    def testConstructor_007(self):
        """
        Test assignment of s3Bucket attribute, invalid value (empty).
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.s3Bucket)
        self.failUnlessAssignRaises(ValueError, amazons3, "s3Bucket", "")
        self.assertEqual(None, amazons3.s3Bucket)

    def testConstructor_008(self):
        """
        Test assignment of encryptCommand attribute, None value.
        """
        amazons3 = AmazonS3Config(encryptCommand="encrypt")
        self.assertEqual("encrypt", amazons3.encryptCommand)
        amazons3.encryptCommand = None
        self.assertEqual(None, amazons3.encryptCommand)

    def testConstructor_009(self):
        """
        Test assignment of encryptCommand attribute, valid value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.encryptCommand)
        amazons3.encryptCommand = "encrypt"
        self.assertEqual("encrypt", amazons3.encryptCommand)

    def testConstructor_010(self):
        """
        Test assignment of encryptCommand attribute, invalid value (empty).
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.encryptCommand)
        self.failUnlessAssignRaises(ValueError, amazons3, "encryptCommand", "")
        self.assertEqual(None, amazons3.encryptCommand)

    def testConstructor_011(self):
        """
        Test assignment of fullBackupSizeLimit attribute, None value.
        """
        amazons3 = AmazonS3Config(fullBackupSizeLimit=100)
        self.assertEqual(100, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = None
        self.assertEqual(None, amazons3.fullBackupSizeLimit)

    def testConstructor_012a(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid int value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = 15
        self.assertEqual(15, amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(15, UNIT_BYTES), amazons3.fullBackupSizeLimit)

    def testConstructor_012b(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid long value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = 7516192768
        self.assertEqual(7516192768, amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(7516192768, UNIT_BYTES), amazons3.fullBackupSizeLimit)

    def testConstructor_012c(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid float value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = 7516192768.0
        self.assertEqual(7516192768.0, amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(7516192768.0, UNIT_BYTES), amazons3.fullBackupSizeLimit)

    def testConstructor_012d(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid string value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = "7516192768"
        self.assertEqual(7516192768, amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity("7516192768", UNIT_BYTES), amazons3.fullBackupSizeLimit)

    def testConstructor_012e(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid byte quantity value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = ByteQuantity(2.5, UNIT_GBYTES)
        self.assertEqual(ByteQuantity(2.5, UNIT_GBYTES), amazons3.fullBackupSizeLimit)
        self.assertEqual(2684354560.0, amazons3.fullBackupSizeLimit.bytes)

    def testConstructor_012f(self):
        """
        Test assignment of fullBackupSizeLimit attribute, valid byte quantity value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        amazons3.fullBackupSizeLimit = ByteQuantity(600, UNIT_MBYTES)
        self.assertEqual(ByteQuantity(600, UNIT_MBYTES), amazons3.fullBackupSizeLimit)
        self.assertEqual(629145600.0, amazons3.fullBackupSizeLimit.bytes)

    def testConstructor_013(self):
        """
        Test assignment of fullBackupSizeLimit attribute, invalid value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.fullBackupSizeLimit)
        self.failUnlessAssignRaises(ValueError, amazons3, "fullBackupSizeLimit", "xxx")
        self.assertEqual(None, amazons3.fullBackupSizeLimit)

    def testConstructor_014(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, None value.
        """
        amazons3 = AmazonS3Config(incrementalBackupSizeLimit=100)
        self.assertEqual(100, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = None
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)

    def testConstructor_015a(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid int value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = 15
        self.assertEqual(15, amazons3.incrementalBackupSizeLimit)
        self.assertEqual(ByteQuantity(15, UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_015b(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid long value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = 7516192768
        self.assertEqual(7516192768, amazons3.incrementalBackupSizeLimit)
        self.assertEqual(ByteQuantity(7516192768, UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_015c(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid float value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = 7516192768.0
        self.assertEqual(7516192768.0, amazons3.incrementalBackupSizeLimit)
        self.assertEqual(ByteQuantity(7516192768.0, UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_015d(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid string value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = "7516192768"
        self.assertEqual(7516192768, amazons3.incrementalBackupSizeLimit)
        self.assertEqual(ByteQuantity("7516192768", UNIT_BYTES), amazons3.incrementalBackupSizeLimit)

    def testConstructor_015e(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid byte quantity value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = ByteQuantity(2.5, UNIT_GBYTES)
        self.assertEqual(ByteQuantity(2.5, UNIT_GBYTES), amazons3.incrementalBackupSizeLimit)
        self.assertEqual(2684354560.0, amazons3.incrementalBackupSizeLimit.bytes)

    def testConstructor_015f(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, valid byte quantity value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        amazons3.incrementalBackupSizeLimit = ByteQuantity(600, UNIT_MBYTES)
        self.assertEqual(ByteQuantity(600, UNIT_MBYTES), amazons3.incrementalBackupSizeLimit)
        self.assertEqual(629145600.0, amazons3.incrementalBackupSizeLimit.bytes)

    def testConstructor_016(self):
        """
        Test assignment of incrementalBackupSizeLimit attribute, invalid value.
        """
        amazons3 = AmazonS3Config()
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)
        self.failUnlessAssignRaises(ValueError, amazons3, "incrementalBackupSizeLimit", "xxx")
        self.assertEqual(None, amazons3.incrementalBackupSizeLimit)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        amazons31 = AmazonS3Config()
        amazons32 = AmazonS3Config()
        self.assertEqual(amazons31, amazons32)
        self.assertTrue(amazons31 == amazons32)
        self.assertTrue(not amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(amazons31 >= amazons32)
        self.assertTrue(not amazons31 != amazons32)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        amazons31 = AmazonS3Config(True, "bucket", "encrypt", 1, 2)
        amazons32 = AmazonS3Config(True, "bucket", "encrypt", 1, 2)
        self.assertEqual(amazons31, amazons32)
        self.assertTrue(amazons31 == amazons32)
        self.assertTrue(not amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(amazons31 >= amazons32)
        self.assertTrue(not amazons31 != amazons32)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, warnMidnite differs.
        """
        amazons31 = AmazonS3Config(warnMidnite=False)
        amazons32 = AmazonS3Config(warnMidnite=True)
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, s3Bucket differs (one None).
        """
        amazons31 = AmazonS3Config()
        amazons32 = AmazonS3Config(s3Bucket="bucket")
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, s3Bucket differs.
        """
        amazons31 = AmazonS3Config(s3Bucket="bucket1")
        amazons32 = AmazonS3Config(s3Bucket="bucket2")
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, encryptCommand differs (one None).
        """
        amazons31 = AmazonS3Config()
        amazons32 = AmazonS3Config(encryptCommand="encrypt")
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, encryptCommand differs.
        """
        amazons31 = AmazonS3Config(encryptCommand="encrypt1")
        amazons32 = AmazonS3Config(encryptCommand="encrypt2")
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, fullBackupSizeLimit differs (one None).
        """
        amazons31 = AmazonS3Config()
        amazons32 = AmazonS3Config(fullBackupSizeLimit=1)
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, fullBackupSizeLimit differs.
        """
        amazons31 = AmazonS3Config(fullBackupSizeLimit=1)
        amazons32 = AmazonS3Config(fullBackupSizeLimit=2)
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, incrementalBackupSizeLimit differs (one None).
        """
        amazons31 = AmazonS3Config()
        amazons32 = AmazonS3Config(incrementalBackupSizeLimit=1)
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, incrementalBackupSizeLimit differs.
        """
        amazons31 = AmazonS3Config(incrementalBackupSizeLimit=1)
        amazons32 = AmazonS3Config(incrementalBackupSizeLimit=2)
        self.assertNotEqual(amazons31, amazons32)
        self.assertTrue(not amazons31 == amazons32)
        self.assertTrue(amazons31 < amazons32)
        self.assertTrue(amazons31 <= amazons32)
        self.assertTrue(not amazons31 > amazons32)
        self.assertTrue(not amazons31 >= amazons32)
        self.assertTrue(amazons31 != amazons32)


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

        We dump a document containing just the amazons3 configuration, and then
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
        self.assertEqual(None, config.amazons3)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.amazons3)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["amazons3.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of amazons3 attribute, None value.
        """
        config = LocalConfig()
        config.amazons3 = None
        self.assertEqual(None, config.amazons3)

    def testConstructor_005(self):
        """
        Test assignment of amazons3 attribute, valid value.
        """
        config = LocalConfig()
        config.amazons3 = AmazonS3Config()
        self.assertEqual(AmazonS3Config(), config.amazons3)

    def testConstructor_006(self):
        """
        Test assignment of amazons3 attribute, invalid value (not AmazonS3Config).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "amazons3", "STRING!")

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
        config1.amazons3 = AmazonS3Config()

        config2 = LocalConfig()
        config2.amazons3 = AmazonS3Config()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, amazons3 differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.amazons3 = AmazonS3Config()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, s3Bucket differs.
        """
        config1 = LocalConfig()
        config1.amazons3 = AmazonS3Config(True, "bucket1", "encrypt", 1, 2)

        config2 = LocalConfig()
        config2.amazons3 = AmazonS3Config(True, "bucket2", "encrypt", 1, 2)

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
        Test validate on a None amazons3 section.
        """
        config = LocalConfig()
        config.amazons3 = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty amazons3 section.
        """
        config = LocalConfig()
        config.amazons3 = AmazonS3Config()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty amazons3 section with no values filled in.
        """
        config = LocalConfig()
        config.amazons3 = AmazonS3Config(None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty amazons3 section with valid values filled in.
        """
        config = LocalConfig()
        config.amazons3 = AmazonS3Config(True, "bucket")
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["amazons3.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.amazons3)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.amazons3)

    def testParse_002(self):
        """
        Parse config document with filled-in values.
        """
        path = self.resources["amazons3.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.amazons3)
        self.assertEqual(True, config.amazons3.warnMidnite)
        self.assertEqual("mybucket", config.amazons3.s3Bucket)
        self.assertEqual("encrypt", config.amazons3.encryptCommand)
        self.assertEqual(5368709120, config.amazons3.fullBackupSizeLimit)
        self.assertEqual(2147483648, config.amazons3.incrementalBackupSizeLimit)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.amazons3)
        self.assertEqual(True, config.amazons3.warnMidnite)
        self.assertEqual("mybucket", config.amazons3.s3Bucket)
        self.assertEqual("encrypt", config.amazons3.encryptCommand)
        self.assertEqual(5368709120, config.amazons3.fullBackupSizeLimit)
        self.assertEqual(2147483648, config.amazons3.incrementalBackupSizeLimit)

    def testParse_003(self):
        """
        Parse config document with filled-in values.
        """
        path = self.resources["amazons3.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.amazons3)
        self.assertEqual(True, config.amazons3.warnMidnite)
        self.assertEqual("mybucket", config.amazons3.s3Bucket)
        self.assertEqual("encrypt", config.amazons3.encryptCommand)
        self.assertEqual(ByteQuantity(2.5, UNIT_GBYTES), config.amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(600, UNIT_MBYTES), config.amazons3.incrementalBackupSizeLimit)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.amazons3)
        self.assertEqual(True, config.amazons3.warnMidnite)
        self.assertEqual("mybucket", config.amazons3.s3Bucket)
        self.assertEqual("encrypt", config.amazons3.encryptCommand)
        self.assertEqual(ByteQuantity(2.5, UNIT_GBYTES), config.amazons3.fullBackupSizeLimit)
        self.assertEqual(ByteQuantity(600, UNIT_MBYTES), config.amazons3.incrementalBackupSizeLimit)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        amazons3 = AmazonS3Config()
        config = LocalConfig()
        config.amazons3 = amazons3
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with values set.
        """
        amazons3 = AmazonS3Config(True, "bucket", "encrypt", 1, 2)
        config = LocalConfig()
        config.amazons3 = amazons3
        self.validateAddConfig(config)


#################
# TestTool class
#################


class TestTool(unittest.TestCase):

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    def setUp(self):
        try:
            self.tmpdir = tempfile.mkdtemp()
            self.resources = findResources(RESOURCES, DATA_DIRS)
        except Exception as e:
            self.fail(e)

    def tearDown(self):
        try:
            removedir(self.tmpdir)
        except:
            pass

    ##################
    # Utility methods
    ##################

    def extractTar(self, tarname):
        """Extracts a tarfile with a particular name."""
        extractTar(self.tmpdir, self.resources["%s.tar.gz" % tarname])

    def buildPath(self, components):
        """Builds a complete search path from a list of components."""
        components.insert(0, self.tmpdir)
        return buildPath(components)

    ###########################
    # Test _checkSourceFiles()
    ###########################

    def testCheckSourceFiles_001(self):
        """
        Test _checkSourceFiles() where some files have an invalid encoding.
        """
        if not platformMacOsX():
            self.extractTar("tree13")
            sourceDir = self.buildPath(["tree13"])
            sourceFiles = _buildSourceFiles(sourceDir)
            self.assertRaises(ValueError, _checkSourceFiles, sourceDir=sourceDir, sourceFiles=sourceFiles)

    def testCheckSourceFiles_002(self):
        """
        Test _checkSourceFiles() where all files have a valid encoding.
        """
        self.extractTar("tree4")
        sourceDir = self.buildPath(["tree4", "dir006"])
        sourceFiles = _buildSourceFiles(sourceDir)
        _checkSourceFiles(sourceDir=sourceDir, sourceFiles=sourceFiles)
