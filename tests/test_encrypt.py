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
# Copyright (c) 2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests encrypt extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/encrypt.py.

Code Coverage
=============

   This module contains individual tests for the the public classes implemented
   in extend/encrypt.py.  There are also tests for some of the private
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
   want to run all of the tests, set ENCRYPTTESTS_FULL to "Y" in the environment.

   In this module, the primary dependency is that for some tests, GPG must have
   access to the public key EFD75934.  There is also an assumption that GPG
   does *not* have access to a public key for anyone named "Bogus J. User" (so
   we can test failure scenarios).

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import os
import tempfile
import unittest

from CedarBackup3.extend.encrypt import EncryptConfig, LocalConfig, _encryptDailyDir, _encryptFile, _encryptFileWithGpg
from CedarBackup3.filesystem import FilesystemList
from CedarBackup3.testutil import buildPath, configureLogging, extractTar, failUnlessAssignRaises, findResources, removedir
from CedarBackup3.xmlutil import createOutputDom, serializeDom

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "encrypt.conf.1",
    "encrypt.conf.2",
    "tree1.tar.gz",
    "tree2.tar.gz",
    "tree8.tar.gz",
    "tree15.tar.gz",
    "tree16.tar.gz",
    "tree17.tar.gz",
    "tree18.tar.gz",
    "tree19.tar.gz",
    "tree20.tar.gz",
]

VALID_GPG_RECIPIENT = "EFD75934"
INVALID_GPG_RECIPIENT = "Bogus J. User"

INVALID_PATH = "bogus"  # This path name should never exist


#######################################################################
# Utility functions
#######################################################################


def runAllTests():
    """Returns true/false depending on whether the full test suite should be run."""
    if "ENCRYPTTESTS_FULL" in os.environ:
        return os.environ["ENCRYPTTESTS_FULL"] == "Y"
    else:
        return False


#######################################################################
# Test Case Classes
#######################################################################

##########################
# TestEncryptConfig class
##########################


class TestEncryptConfig(unittest.TestCase):

    """Tests for the EncryptConfig class."""

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
        obj = EncryptConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        encrypt = EncryptConfig()
        self.assertEqual(None, encrypt.encryptMode)
        self.assertEqual(None, encrypt.encryptTarget)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values.
        """
        encrypt = EncryptConfig("gpg", "Backup User")
        self.assertEqual("gpg", encrypt.encryptMode)
        self.assertEqual("Backup User", encrypt.encryptTarget)

    def testConstructor_003(self):
        """
        Test assignment of encryptMode attribute, None value.
        """
        encrypt = EncryptConfig(encryptMode="gpg")
        self.assertEqual("gpg", encrypt.encryptMode)
        encrypt.encryptMode = None
        self.assertEqual(None, encrypt.encryptMode)

    def testConstructor_004(self):
        """
        Test assignment of encryptMode attribute, valid value.
        """
        encrypt = EncryptConfig()
        self.assertEqual(None, encrypt.encryptMode)
        encrypt.encryptMode = "gpg"
        self.assertEqual("gpg", encrypt.encryptMode)

    def testConstructor_005(self):
        """
        Test assignment of encryptMode attribute, invalid value (empty).
        """
        encrypt = EncryptConfig()
        self.assertEqual(None, encrypt.encryptMode)
        self.failUnlessAssignRaises(ValueError, encrypt, "encryptMode", "")
        self.assertEqual(None, encrypt.encryptMode)

    def testConstructor_006(self):
        """
        Test assignment of encryptTarget attribute, None value.
        """
        encrypt = EncryptConfig(encryptTarget="Backup User")
        self.assertEqual("Backup User", encrypt.encryptTarget)
        encrypt.encryptTarget = None
        self.assertEqual(None, encrypt.encryptTarget)

    def testConstructor_007(self):
        """
        Test assignment of encryptTarget attribute, valid value.
        """
        encrypt = EncryptConfig()
        self.assertEqual(None, encrypt.encryptTarget)
        encrypt.encryptTarget = "Backup User"
        self.assertEqual("Backup User", encrypt.encryptTarget)

    def testConstructor_008(self):
        """
        Test assignment of encryptTarget attribute, invalid value (empty).
        """
        encrypt = EncryptConfig()
        self.assertEqual(None, encrypt.encryptTarget)
        self.failUnlessAssignRaises(ValueError, encrypt, "encryptTarget", "")
        self.assertEqual(None, encrypt.encryptTarget)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        encrypt1 = EncryptConfig()
        encrypt2 = EncryptConfig()
        self.assertEqual(encrypt1, encrypt2)
        self.assertTrue(encrypt1 == encrypt2)
        self.assertTrue(not encrypt1 < encrypt2)
        self.assertTrue(encrypt1 <= encrypt2)
        self.assertTrue(not encrypt1 > encrypt2)
        self.assertTrue(encrypt1 >= encrypt2)
        self.assertTrue(not encrypt1 != encrypt2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None.
        """
        encrypt1 = EncryptConfig("gpg", "Backup User")
        encrypt2 = EncryptConfig("gpg", "Backup User")
        self.assertEqual(encrypt1, encrypt2)
        self.assertTrue(encrypt1 == encrypt2)
        self.assertTrue(not encrypt1 < encrypt2)
        self.assertTrue(encrypt1 <= encrypt2)
        self.assertTrue(not encrypt1 > encrypt2)
        self.assertTrue(encrypt1 >= encrypt2)
        self.assertTrue(not encrypt1 != encrypt2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, encryptMode differs (one None).
        """
        encrypt1 = EncryptConfig()
        encrypt2 = EncryptConfig(encryptMode="gpg")
        self.assertNotEqual(encrypt1, encrypt2)
        self.assertTrue(not encrypt1 == encrypt2)
        self.assertTrue(encrypt1 < encrypt2)
        self.assertTrue(encrypt1 <= encrypt2)
        self.assertTrue(not encrypt1 > encrypt2)
        self.assertTrue(not encrypt1 >= encrypt2)
        self.assertTrue(encrypt1 != encrypt2)

    # Note: no test to check when encrypt mode differs, since only one value is allowed

    def testComparison_004(self):
        """
        Test comparison of two differing objects, encryptTarget differs (one None).
        """
        encrypt1 = EncryptConfig()
        encrypt2 = EncryptConfig(encryptTarget="Backup User")
        self.assertNotEqual(encrypt1, encrypt2)
        self.assertTrue(not encrypt1 == encrypt2)
        self.assertTrue(encrypt1 < encrypt2)
        self.assertTrue(encrypt1 <= encrypt2)
        self.assertTrue(not encrypt1 > encrypt2)
        self.assertTrue(not encrypt1 >= encrypt2)
        self.assertTrue(encrypt1 != encrypt2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, encryptTarget differs.
        """
        encrypt1 = EncryptConfig("gpg", "Another User")
        encrypt2 = EncryptConfig("gpg", "Backup User")
        self.assertNotEqual(encrypt1, encrypt2)
        self.assertTrue(not encrypt1 == encrypt2)
        self.assertTrue(encrypt1 < encrypt2)
        self.assertTrue(encrypt1 <= encrypt2)
        self.assertTrue(not encrypt1 > encrypt2)
        self.assertTrue(not encrypt1 >= encrypt2)
        self.assertTrue(encrypt1 != encrypt2)


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

        We dump a document containing just the encrypt configuration, and then
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
        self.assertEqual(None, config.encrypt)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.encrypt)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["encrypt.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of encrypt attribute, None value.
        """
        config = LocalConfig()
        config.encrypt = None
        self.assertEqual(None, config.encrypt)

    def testConstructor_005(self):
        """
        Test assignment of encrypt attribute, valid value.
        """
        config = LocalConfig()
        config.encrypt = EncryptConfig()
        self.assertEqual(EncryptConfig(), config.encrypt)

    def testConstructor_006(self):
        """
        Test assignment of encrypt attribute, invalid value (not EncryptConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "encrypt", "STRING!")

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
        config1.encrypt = EncryptConfig()

        config2 = LocalConfig()
        config2.encrypt = EncryptConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, encrypt differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.encrypt = EncryptConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, encrypt differs.
        """
        config1 = LocalConfig()
        config1.encrypt = EncryptConfig(encryptTarget="Another User")

        config2 = LocalConfig()
        config2.encrypt = EncryptConfig(encryptTarget="Backup User")

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
        Test validate on a None encrypt section.
        """
        config = LocalConfig()
        config.encrypt = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty encrypt section.
        """
        config = LocalConfig()
        config.encrypt = EncryptConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty encrypt section with no values filled in.
        """
        config = LocalConfig()
        config.encrypt = EncryptConfig(None, None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_004(self):
        """
        Test validate on a non-empty encrypt section with only one value filled in.
        """
        config = LocalConfig()
        config.encrypt = EncryptConfig("gpg", None)
        self.assertRaises(ValueError, config.validate)
        config.encrypt = EncryptConfig(None, "Backup User")
        self.assertRaises(ValueError, config.validate)

    def testValidate_005(self):
        """
        Test validate on a non-empty encrypt section with valid values filled in.
        """
        config = LocalConfig()
        config.encrypt = EncryptConfig("gpg", "Backup User")
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["encrypt.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.encrypt)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.encrypt)

    def testParse_002(self):
        """
        Parse config document with filled-in values.
        """
        path = self.resources["encrypt.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.encrypt)
        self.assertEqual("gpg", config.encrypt.encryptMode)
        self.assertEqual("Backup User", config.encrypt.encryptTarget)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.encrypt)
        self.assertEqual("gpg", config.encrypt.encryptMode)
        self.assertEqual("Backup User", config.encrypt.encryptTarget)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document.
        """
        encrypt = EncryptConfig()
        config = LocalConfig()
        config.encrypt = encrypt
        self.validateAddConfig(config)

    def testAddConfig_002(self):
        """
        Test with values set.
        """
        encrypt = EncryptConfig(encryptMode="gpg", encryptTarget="Backup User")
        config = LocalConfig()
        config.encrypt = encrypt
        self.validateAddConfig(config)


######################
# TestFunctions class
######################


@unittest.skipUnless(runAllTests(), "Limited test suite")
class TestFunctions(unittest.TestCase):

    """Tests for the functions in encrypt.py."""

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

    #############################
    # Test _encryptFileWithGpg()
    #############################

    def testEncryptFileWithGpg_001(self):
        """
        Test for a non-existent file in a non-existent directory.
        """
        sourceFile = self.buildPath([INVALID_PATH, INVALID_PATH])
        self.assertRaises(IOError, _encryptFileWithGpg, sourceFile, INVALID_GPG_RECIPIENT)

    def testEncryptFileWithGpg_002(self):
        """
        Test for a non-existent file in an existing directory.
        """
        self.extractTar("tree8")
        sourceFile = self.buildPath(["tree8", "dir001", INVALID_PATH])
        self.assertRaises(IOError, _encryptFileWithGpg, sourceFile, INVALID_GPG_RECIPIENT)

    def testEncryptFileWithGpg_003(self):
        """
        Test for an unknown recipient.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        self.assertRaises(IOError, _encryptFileWithGpg, sourceFile, INVALID_GPG_RECIPIENT)
        self.assertFalse(os.path.exists(expectedFile))
        self.assertTrue(os.path.exists(sourceFile))

    def testEncryptFileWithGpg_004(self):
        """
        Test for a valid recipient.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        actualFile = _encryptFileWithGpg(sourceFile, VALID_GPG_RECIPIENT)
        self.assertEqual(actualFile, expectedFile)
        self.assertTrue(os.path.exists(sourceFile))
        self.assertTrue(os.path.exists(actualFile))

    ######################
    # Test _encryptFile()
    ######################

    def testEncryptFile_001(self):
        """
        Test for a mode other than "gpg".
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        self.assertRaises(ValueError, _encryptFile, sourceFile, "pgp", INVALID_GPG_RECIPIENT, None, None, removeSource=False)
        self.assertTrue(os.path.exists(sourceFile))
        self.assertFalse(os.path.exists(expectedFile))

    def testEncryptFile_002(self):
        """
        Test for a source path that does not exist.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", INVALID_PATH])
        expectedFile = self.buildPath(["tree1", "%s.gpg" % INVALID_PATH])
        self.assertRaises(ValueError, _encryptFile, sourceFile, "gpg", INVALID_GPG_RECIPIENT, None, None, removeSource=False)
        self.assertFalse(os.path.exists(sourceFile))
        self.assertFalse(os.path.exists(expectedFile))

    def testEncryptFile_003(self):
        """
        Test "gpg" mode with a valid source path and invalid recipient, removeSource=False.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        self.assertRaises(IOError, _encryptFile, sourceFile, "gpg", INVALID_GPG_RECIPIENT, None, None, removeSource=False)
        self.assertTrue(os.path.exists(sourceFile))
        self.assertFalse(os.path.exists(expectedFile))

    def testEncryptFile_004(self):
        """
        Test "gpg" mode with a valid source path and invalid recipient, removeSource=True.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        self.assertRaises(IOError, _encryptFile, sourceFile, "gpg", INVALID_GPG_RECIPIENT, None, None, removeSource=True)
        self.assertTrue(os.path.exists(sourceFile))
        self.assertFalse(os.path.exists(expectedFile))

    def testEncryptFile_005(self):
        """
        Test "gpg" mode with a valid source path and recipient, removeSource=False.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        actualFile = _encryptFile(sourceFile, "gpg", VALID_GPG_RECIPIENT, None, None, removeSource=False)
        self.assertEqual(actualFile, expectedFile)
        self.assertTrue(os.path.exists(sourceFile))
        self.assertTrue(os.path.exists(actualFile))

    def testEncryptFile_006(self):
        """
        Test "gpg" mode with a valid source path and recipient, removeSource=True.
        """
        self.extractTar("tree1")
        sourceFile = self.buildPath(["tree1", "file001"])
        expectedFile = self.buildPath(["tree1", "file001.gpg"])
        actualFile = _encryptFile(sourceFile, "gpg", VALID_GPG_RECIPIENT, None, None, removeSource=True)
        self.assertEqual(actualFile, expectedFile)
        self.assertFalse(os.path.exists(sourceFile))
        self.assertTrue(os.path.exists(actualFile))

    ##########################
    # Test _encryptDailyDir()
    ##########################

    def testEncryptDailyDir_001(self):
        """
        Test with a nonexistent daily staging directory.
        """
        self.extractTar("tree1")
        dailyDir = self.buildPath(["tree1", "dir001"])
        self.assertRaises(ValueError, _encryptDailyDir, dailyDir, "gpg", VALID_GPG_RECIPIENT, None, None)

    def testEncryptDailyDir_002(self):
        """
        Test with a valid staging directory containing only links.
        """
        self.extractTar("tree15")
        dailyDir = self.buildPath(["tree15", "dir001"])
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(3, len(fsList))
        self.assertTrue(self.buildPath(["tree15", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree15", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree15", "dir001", "link002"]) in fsList)
        _encryptDailyDir(dailyDir, "gpg", VALID_GPG_RECIPIENT, None, None)
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(3, len(fsList))
        self.assertTrue(self.buildPath(["tree15", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree15", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree15", "dir001", "link002"]) in fsList)

    def testEncryptDailyDir_003(self):
        """
        Test with a valid staging directory containing only directories.
        """
        self.extractTar("tree2")
        dailyDir = self.buildPath(["tree2"])
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(11, len(fsList))
        self.assertTrue(self.buildPath(["tree2"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir005"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir006"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir007"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir008"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir009"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir010"]) in fsList)
        _encryptDailyDir(dailyDir, "gpg", VALID_GPG_RECIPIENT, None, None)
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(11, len(fsList))
        self.assertTrue(self.buildPath(["tree2"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir005"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir006"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir007"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir008"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir009"]) in fsList)
        self.assertTrue(self.buildPath(["tree2", "dir010"]) in fsList)

    def testEncryptDailyDir_004(self):
        """
        Test with a valid staging directory containing only files.
        """
        self.extractTar("tree1")
        dailyDir = self.buildPath(["tree1"])
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(8, len(fsList))
        self.assertTrue(self.buildPath(["tree1"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file007"]) in fsList)
        _encryptDailyDir(dailyDir, "gpg", VALID_GPG_RECIPIENT, None, None)
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(8, len(fsList))
        self.assertTrue(self.buildPath(["tree1"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree1", "file007.gpg"]) in fsList)

    def testEncryptDailyDir_005(self):
        """
        Test with a valid staging directory containing files, directories and
        links, including various files that match the general Cedar Backup
        indicator file pattern ("cback.<something>").
        """
        self.extractTar("tree16")
        dailyDir = self.buildPath(["tree16"])
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        self.assertEqual(122, len(fsList))
        self.assertTrue(self.buildPath(["tree16"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file007"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file008"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "link002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "link002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "link003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "link004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "link005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file007"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file008"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "cback."]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "link002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "cback.store"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file007"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file008"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "cback."]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "cback.collect"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "link002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file007"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file008"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "cback.store"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file006"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file007"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file008"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "link001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.collect"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.stage"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.store"]) in fsList)
        _encryptDailyDir(dailyDir, "gpg", VALID_GPG_RECIPIENT, None, None)
        fsList = FilesystemList()
        fsList.addDirContents(dailyDir)
        # since all links are to files, and the files all changed names, the links are invalid and disappear
        self.assertEqual(102, len(fsList))
        self.assertTrue(self.buildPath(["tree16"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file007.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir001", "file008.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir002", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir001", "dir003", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir001", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir002", "dir002", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file007.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "file008.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir001", "cback."]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir003", "dir003", "cback.store"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file007.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "file008.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "cback."]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir001", "cback.collect"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir002", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir003", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "cback.encrypt"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file007.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "file008.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir004", "cback.store"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file001.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file002.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file003.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file004.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file005.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file006.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file007.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "dir004", "dir005", "file008.gpg"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.collect"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.stage"]) in fsList)
        self.assertTrue(self.buildPath(["tree16", "cback.store"]) in fsList)
