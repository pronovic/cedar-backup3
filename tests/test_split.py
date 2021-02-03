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
# Copyright (c) 2007-2008,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests split extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/split.py.

Code Coverage
=============

   This module contains individual tests for the the public classes implemented
   in extend/split.py.  There are also tests for some of the private
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

Full vs. Reduced Tests
======================

   Some Cedar Backup regression tests require a specialized environment in
   order to run successfully.  This environment won't necessarily be available
   on every build system out there (for instance, on a Debian autobuilder).
   Because of this, the default behavior is to run a "reduced feature set" test
   suite that has no surprising system, kernel or network requirements.  If you
   want to run all of the tests, set SPLITTESTS_FULL to "Y" in the environment.

   In this module, the primary dependency is that the split utility must be
   available.  There is also one test that wants at least one non-English
   locale (fr_FR, ru_RU or pt_PT) available to check localization issues (but
   that test will just automatically be skipped if such a locale is not
   available).

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import os
import tempfile
import unittest

from CedarBackup3.extend.split import ByteQuantity, LocalConfig, SplitConfig, _splitDailyDir, _splitFile
from CedarBackup3.testutil import (
    availableLocales,
    buildPath,
    configureLogging,
    extractTar,
    failUnlessAssignRaises,
    findResources,
    removedir,
)
from CedarBackup3.util import UNIT_BYTES, UNIT_GBYTES, UNIT_KBYTES, UNIT_MBYTES, pathJoin
from CedarBackup3.xmlutil import createOutputDom, serializeDom

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "split.conf.1",
    "split.conf.2",
    "split.conf.3",
    "split.conf.4",
    "split.conf.5",
    "tree21.tar.gz",
]

INVALID_PATH = "bogus"  # This path name should never exist


#######################################################################
# Utility functions
#######################################################################


def runAllTests():
    """Returns true/false depending on whether the full test suite should be run."""
    if "SPLITTESTS_FULL" in os.environ:
        return os.environ["SPLITTESTS_FULL"] == "Y"
    else:
        return False


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestSplitConfig class
##########################


class TestSplitConfig(unittest.TestCase):

    """Tests for the SplitConfig class."""

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
        obj = SplitConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        split = SplitConfig()
        self.assertEqual(None, split.sizeLimit)
        self.assertEqual(None, split.splitSize)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        split = SplitConfig(ByteQuantity("1.0", UNIT_BYTES), ByteQuantity("2.0", UNIT_KBYTES))
        self.assertEqual(ByteQuantity("1.0", UNIT_BYTES), split.sizeLimit)
        self.assertEqual(ByteQuantity("2.0", UNIT_KBYTES), split.splitSize)

    def testConstructor_003(self):
        """
        Test assignment of sizeLimit attribute, None value.
        """
        split = SplitConfig(sizeLimit=ByteQuantity("1.0", UNIT_BYTES))
        self.assertEqual(ByteQuantity("1.0", UNIT_BYTES), split.sizeLimit)
        split.sizeLimit = None
        self.assertEqual(None, split.sizeLimit)

    def testConstructor_004(self):
        """
        Test assignment of sizeLimit attribute, valid value.
        """
        split = SplitConfig()
        self.assertEqual(None, split.sizeLimit)
        split.sizeLimit = ByteQuantity("1.0", UNIT_BYTES)
        self.assertEqual(ByteQuantity("1.0", UNIT_BYTES), split.sizeLimit)

    def testConstructor_005(self):
        """
        Test assignment of sizeLimit attribute, invalid value (empty).
        """
        split = SplitConfig()
        self.assertEqual(None, split.sizeLimit)
        self.failUnlessAssignRaises(ValueError, split, "sizeLimit", "")
        self.assertEqual(None, split.sizeLimit)

    def testConstructor_006(self):
        """
        Test assignment of sizeLimit attribute, invalid value (not a ByteQuantity).
        """
        split = SplitConfig()
        self.assertEqual(None, split.sizeLimit)
        self.failUnlessAssignRaises(ValueError, split, "sizeLimit", "1.0 GB")
        self.assertEqual(None, split.sizeLimit)

    def testConstructor_007(self):
        """
        Test assignment of splitSize attribute, None value.
        """
        split = SplitConfig(splitSize=ByteQuantity("1.00", UNIT_KBYTES))
        self.assertEqual(ByteQuantity("1.00", UNIT_KBYTES), split.splitSize)
        split.splitSize = None
        self.assertEqual(None, split.splitSize)

    def testConstructor_008(self):
        """
        Test assignment of splitSize attribute, valid value.
        """
        split = SplitConfig()
        self.assertEqual(None, split.splitSize)
        split.splitSize = ByteQuantity("1.00", UNIT_KBYTES)
        self.assertEqual(ByteQuantity("1.00", UNIT_KBYTES), split.splitSize)

    def testConstructor_009(self):
        """
        Test assignment of splitSize attribute, invalid value (empty).
        """
        split = SplitConfig()
        self.assertEqual(None, split.splitSize)
        self.failUnlessAssignRaises(ValueError, split, "splitSize", "")
        self.assertEqual(None, split.splitSize)

    def testConstructor_010(self):
        """
        Test assignment of splitSize attribute, invalid value (not a ByteQuantity).
        """
        split = SplitConfig()
        self.assertEqual(None, split.splitSize)
        self.failUnlessAssignRaises(ValueError, split, "splitSize", 12)
        self.assertEqual(None, split.splitSize)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        split1 = SplitConfig()
        split2 = SplitConfig()
        self.assertEqual(split1, split2)
        self.assertTrue(split1 == split2)
        self.assertTrue(not split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(split1 >= split2)
        self.assertTrue(not split1 != split2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        split1 = SplitConfig(ByteQuantity("99", UNIT_KBYTES), ByteQuantity("1.00", UNIT_MBYTES))
        split2 = SplitConfig(ByteQuantity("99", UNIT_KBYTES), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertEqual(split1, split2)
        self.assertTrue(split1 == split2)
        self.assertTrue(not split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(split1 >= split2)
        self.assertTrue(not split1 != split2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, sizeLimit differs (one None).
        """
        split1 = SplitConfig()
        split2 = SplitConfig(sizeLimit=ByteQuantity("99", UNIT_KBYTES))
        self.assertNotEqual(split1, split2)
        self.assertTrue(not split1 == split2)
        self.assertTrue(split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(not split1 >= split2)
        self.assertTrue(split1 != split2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, sizeLimit differs.
        """
        split1 = SplitConfig(ByteQuantity("99", UNIT_BYTES), ByteQuantity("1.00", UNIT_MBYTES))
        split2 = SplitConfig(ByteQuantity("99", UNIT_KBYTES), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(split1, split2)
        self.assertTrue(not split1 == split2)
        self.assertTrue(split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(not split1 >= split2)
        self.assertTrue(split1 != split2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, splitSize differs (one None).
        """
        split1 = SplitConfig()
        split2 = SplitConfig(splitSize=ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(split1, split2)
        self.assertTrue(not split1 == split2)
        self.assertTrue(split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(not split1 >= split2)
        self.assertTrue(split1 != split2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, splitSize differs.
        """
        split1 = SplitConfig(ByteQuantity("99", UNIT_KBYTES), ByteQuantity("0.5", UNIT_MBYTES))
        split2 = SplitConfig(ByteQuantity("99", UNIT_KBYTES), ByteQuantity("1.00", UNIT_MBYTES))
        self.assertNotEqual(split1, split2)
        self.assertTrue(not split1 == split2)
        self.assertTrue(split1 < split2)
        self.assertTrue(split1 <= split2)
        self.assertTrue(not split1 > split2)
        self.assertTrue(not split1 >= split2)
        self.assertTrue(split1 != split2)


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

        We dump a document containing just the split configuration, and then
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
        self.assertEqual(None, config.split)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.split)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["split.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of split attribute, None value.
        """
        config = LocalConfig()
        config.split = None
        self.assertEqual(None, config.split)

    def testConstructor_005(self):
        """
        Test assignment of split attribute, valid value.
        """
        config = LocalConfig()
        config.split = SplitConfig()
        self.assertEqual(SplitConfig(), config.split)

    def testConstructor_006(self):
        """
        Test assignment of split attribute, invalid value (not SplitConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "split", "STRING!")

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
        config1.split = SplitConfig()

        config2 = LocalConfig()
        config2.split = SplitConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, split differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.split = SplitConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, split differs.
        """
        config1 = LocalConfig()
        config1.split = SplitConfig(sizeLimit=ByteQuantity("0.1", UNIT_MBYTES))

        config2 = LocalConfig()
        config2.split = SplitConfig(sizeLimit=ByteQuantity("1.00", UNIT_MBYTES))

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
        Test validate on a None split section.
        """
        config = LocalConfig()
        config.split = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty split section.
        """
        config = LocalConfig()
        config.split = SplitConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty split section with no values filled in.
        """
        config = LocalConfig()
        config.split = SplitConfig(None, None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_004(self):
        """
        Test validate on a non-empty split section with only one value filled in.
        """
        config = LocalConfig()
        config.split = SplitConfig(ByteQuantity("1.00", UNIT_MBYTES), None)
        self.assertRaises(ValueError, config.validate)
        config.split = SplitConfig(None, ByteQuantity("1.00", UNIT_MBYTES))
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty split section with valid values filled in.
        """
        config = LocalConfig()
        config.split = SplitConfig(ByteQuantity("1.00", UNIT_MBYTES), ByteQuantity("1.00", UNIT_MBYTES))
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["split.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.split)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.split)

    def testParse_002(self):
        """
        Parse config document with filled-in values, size in bytes.
        """
        path = self.resources["split.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("12345", UNIT_BYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("67890.0", UNIT_BYTES), config.split.splitSize)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("12345", UNIT_BYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("67890.0", UNIT_BYTES), config.split.splitSize)

    def testParse_003(self):
        """
        Parse config document with filled-in values, size in KB.
        """
        path = self.resources["split.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_KBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_KBYTES), config.split.splitSize)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_KBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_KBYTES), config.split.splitSize)

    def testParse_004(self):
        """
        Parse config document with filled-in values, size in MB.
        """
        path = self.resources["split.conf.4"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_MBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_MBYTES), config.split.splitSize)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_MBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_MBYTES), config.split.splitSize)

    def testParse_005(self):
        """
        Parse config document with filled-in values, size in GB.
        """
        path = self.resources["split.conf.5"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_GBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_GBYTES), config.split.splitSize)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.split)
        self.assertEqual(ByteQuantity("1.25", UNIT_GBYTES), config.split.sizeLimit)
        self.assertEqual(ByteQuantity("0.6", UNIT_GBYTES), config.split.splitSize)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        split = SplitConfig()
        config = LocalConfig()
        config.split = split
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with values set, byte values.
        """
        split = SplitConfig(ByteQuantity("57521.0", UNIT_BYTES), ByteQuantity("121231", UNIT_BYTES))
        config = LocalConfig()
        config.split = split
        self.validateAddConfig(config)

    def testAddConfig_003(self):
        """
        Test with values set, KB values.
        """
        split = SplitConfig(ByteQuantity("12", UNIT_KBYTES), ByteQuantity("63352", UNIT_KBYTES))
        config = LocalConfig()
        config.split = split
        self.validateAddConfig(config)

    def testAddConfig_004(self):
        """
        Test with values set, MB values.
        """
        split = SplitConfig(ByteQuantity("12", UNIT_MBYTES), ByteQuantity("63352", UNIT_MBYTES))
        config = LocalConfig()
        config.split = split
        self.validateAddConfig(config)

    def testAddConfig_005(self):
        """
        Test with values set, GB values.
        """
        split = SplitConfig(ByteQuantity("12", UNIT_GBYTES), ByteQuantity("63352", UNIT_GBYTES))
        config = LocalConfig()
        config.split = split
        self.validateAddConfig(config)


######################
# TestFunctions class
######################


@unittest.skipUnless(runAllTests(), "Limited test suite")
class TestFunctions(unittest.TestCase):

    """Tests for the functions in split.py."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    @classmethod
    def checkDisabled(cls):
        if not runAllTests():
            raise unittest.SkipTest("Disabled")

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

    def checkSplit(self, sourcePath, origSize, splitSize):
        """Checks that a file was split properly."""
        wholeFiles = int(float(origSize) / float(splitSize))
        leftoverBytes = int(float(origSize) % float(splitSize))
        for i in range(0, wholeFiles):
            splitPath = "%s_%05d" % (sourcePath, i)
            self.assertTrue(os.path.exists(splitPath))
            self.assertEqual(splitSize, os.stat(splitPath).st_size)
        if leftoverBytes > 0:
            splitPath = "%s_%05d" % (sourcePath, wholeFiles)
            self.assertTrue(os.path.exists(splitPath))
            self.assertEqual(leftoverBytes, os.stat(splitPath).st_size)

    def findBadLocale(self):
        """
        The split command localizes its output for certain locales.  This breaks
        the parsing code in split.py.  This method returns a list of the locales
        (if any) that are currently configured which could be expected to cause a
        failure if the localization-fixing code doesn't work.
        """
        locales = availableLocales()
        if "fr_FR" in locales:
            return "fr_FR"
        if "pl_PL" in locales:
            return "pl_PL"
        if "ru_RU" in locales:
            return "ru_RU"
        return None

    ####################
    # Test _splitFile()
    ####################

    def testSplitFile_001(self):
        """
        Test with a nonexistent file.
        """
        self.extractTar("tree21")
        sourcePath = self.buildPath(["tree21", "2007", "01", "01", INVALID_PATH])
        self.assertFalse(os.path.exists(sourcePath))
        splitSize = ByteQuantity("320", UNIT_BYTES)
        self.assertRaises(ValueError, _splitFile, sourcePath, splitSize, None, None, removeSource=False)

    def testSplitFile_002(self):
        """
        Test with integer split size, removeSource=False.
        """
        self.extractTar("tree21")
        sourcePath = self.buildPath(["tree21", "2007", "01", "01", "system1", "file001.a.b"])
        self.assertTrue(os.path.exists(sourcePath))
        splitSize = ByteQuantity("320", UNIT_BYTES)
        _splitFile(sourcePath, splitSize, None, None, removeSource=False)
        self.assertTrue(os.path.exists(sourcePath))
        self.checkSplit(sourcePath, 3200, 320)

    def testSplitFile_003(self):
        """
        Test with floating point split size, removeSource=False.
        """
        self.extractTar("tree21")
        sourcePath = self.buildPath(["tree21", "2007", "01", "01", "system1", "file001.a.b"])
        self.assertTrue(os.path.exists(sourcePath))
        splitSize = ByteQuantity("320.1", UNIT_BYTES)
        _splitFile(sourcePath, splitSize, None, None, removeSource=False)
        self.assertTrue(os.path.exists(sourcePath))
        self.checkSplit(sourcePath, 3200, 320)

    def testSplitFile_004(self):
        """
        Test with integer split size, removeSource=True.
        """
        self.extractTar("tree21")
        sourcePath = self.buildPath(["tree21", "2007", "01", "01", "system1", "file001.a.b"])
        self.assertTrue(os.path.exists(sourcePath))
        splitSize = ByteQuantity("320", UNIT_BYTES)
        _splitFile(sourcePath, splitSize, None, None, removeSource=True)
        self.assertFalse(os.path.exists(sourcePath))
        self.checkSplit(sourcePath, 3200, 320)

    def testSplitFile_005(self):
        """
        Test with a local other than "C" or "en_US" set.
        """
        locale = self.findBadLocale()
        if locale is not None:
            os.environ["LANG"] = locale
            os.environ["LC_ADDRESS"] = locale
            os.environ["LC_ALL"] = locale
            os.environ["LC_COLLATE"] = locale
            os.environ["LC_CTYPE"] = locale
            os.environ["LC_IDENTIFICATION"] = locale
            os.environ["LC_MEASUREMENT"] = locale
            os.environ["LC_MESSAGES"] = locale
            os.environ["LC_MONETARY"] = locale
            os.environ["LC_NAME"] = locale
            os.environ["LC_NUMERIC"] = locale
            os.environ["LC_PAPER"] = locale
            os.environ["LC_TELEPHONE"] = locale
            os.environ["LC_TIME"] = locale
            self.extractTar("tree21")
            sourcePath = self.buildPath(["tree21", "2007", "01", "01", "system1", "file001.a.b"])
            self.assertTrue(os.path.exists(sourcePath))
            splitSize = ByteQuantity("320", UNIT_BYTES)
            _splitFile(sourcePath, splitSize, None, None, removeSource=True)
            self.assertFalse(os.path.exists(sourcePath))
            self.checkSplit(sourcePath, 3200, 320)

    ##########################
    # Test _splitDailyDir()
    ##########################

    def testSplitDailyDir_001(self):
        """
        Test with a nonexistent daily staging directory.
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", INVALID_PATH])
        self.assertFalse(os.path.exists(dailyDir))
        sizeLimit = ByteQuantity("1.0", UNIT_MBYTES)
        splitSize = ByteQuantity("100000", UNIT_BYTES)
        self.assertRaises(ValueError, _splitDailyDir, dailyDir, sizeLimit, splitSize, None, None)

    def testSplitDailyDir_002(self):
        """
        Test with 1.0 MB limit.
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("1.0", UNIT_MBYTES)
        splitSize = ByteQuantity("100000", UNIT_BYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))

    def testSplitDailyDir_003(self):
        """
        Test with 100,000 byte limit, chopped down to 10 KB
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("100000", UNIT_BYTES)
        splitSize = ByteQuantity("10", UNIT_KBYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        self.checkSplit(pathJoin(dailyDir, "system1", "file003"), 320000, 10 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system3", "file003"), 100001, 10 * 1024)

    def testSplitDailyDir_004(self):
        """
        Test with 99,999 byte limit, chopped down to 5,000 bytes
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("99999", UNIT_BYTES)
        splitSize = ByteQuantity("5000", UNIT_BYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        self.checkSplit(pathJoin(dailyDir, "system1", "file003"), 320000, 5000)
        self.checkSplit(pathJoin(dailyDir, "system2", "file003"), 100000, 5000)
        self.checkSplit(pathJoin(dailyDir, "system3", "file002"), 100000, 5000)
        self.checkSplit(pathJoin(dailyDir, "system3", "file003"), 100001, 5000)

    def testSplitDailyDir_005(self):
        """
        Test with 99,998 byte limit, chopped down to 2500 bytes
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("10000.0", UNIT_BYTES)
        splitSize = ByteQuantity("2500", UNIT_BYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        self.checkSplit(pathJoin(dailyDir, "system1", "file002"), 32000, 2500)
        self.checkSplit(pathJoin(dailyDir, "system1", "file003"), 320000, 2500)
        self.checkSplit(pathJoin(dailyDir, "system2", "file003"), 100000, 2500)
        self.checkSplit(pathJoin(dailyDir, "system3", "file001"), 99999, 2500)
        self.checkSplit(pathJoin(dailyDir, "system3", "file002"), 100000, 2500)
        self.checkSplit(pathJoin(dailyDir, "system3", "file003"), 100001, 2500)

    def testSplitDailyDir_006(self):
        """
        Test with 10,000 byte limit, chopped down to 1024 bytes
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("10000", UNIT_BYTES)
        splitSize = ByteQuantity("1.0", UNIT_KBYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        self.checkSplit(pathJoin(dailyDir, "system1", "file002"), 32000, 1 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system1", "file003"), 320000, 1 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system2", "file003"), 100000, 1 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system3", "file001"), 99999, 1 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system3", "file002"), 100000, 1 * 1024)
        self.checkSplit(pathJoin(dailyDir, "system3", "file003"), 100001, 1 * 1024)

    def testSplitDailyDir_007(self):
        """
        Test with 9,999 byte limit, chopped down to 1000 bytes
        """
        self.extractTar("tree21")
        dailyDir = self.buildPath(["tree21", "2007", "01", "01"])
        self.assertTrue(os.path.exists(dailyDir) and os.path.isdir(dailyDir))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        sizeLimit = ByteQuantity("9999", UNIT_BYTES)
        splitSize = ByteQuantity("1000", UNIT_BYTES)
        _splitDailyDir(dailyDir, sizeLimit, splitSize, None, None)
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system1", "file001.a.b")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system1", "file003")))
        self.assertTrue(os.path.exists(pathJoin(dailyDir, "system2", "file001")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system2", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system2", "file003")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file001")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file002")))
        self.assertFalse(os.path.exists(pathJoin(dailyDir, "system3", "file003")))
        self.checkSplit(pathJoin(dailyDir, "system1", "file002"), 32000, 1000)
        self.checkSplit(pathJoin(dailyDir, "system1", "file003"), 320000, 1000)
        self.checkSplit(pathJoin(dailyDir, "system2", "file002"), 10000, 1000)
        self.checkSplit(pathJoin(dailyDir, "system2", "file003"), 100000, 1000)
        self.checkSplit(pathJoin(dailyDir, "system3", "file001"), 99999, 1000)
        self.checkSplit(pathJoin(dailyDir, "system3", "file002"), 100000, 1000)
        self.checkSplit(pathJoin(dailyDir, "system3", "file003"), 100001, 1000)
