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
# Copyright (c) 2005-2006,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests MySQL extension functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/extend/mysql.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in extend/mysql.py.  There are also tests for
   several of the private methods.

   Unfortunately, it's rather difficult to test this code in an automated
   fashion, even if you have access to MySQL, since the actual dump would need
   to have access to a real database.  Because of this, there aren't any tests
   below that actually talk to a database.

   As a compromise, I test some of the private methods in the implementation.
   Normally, I don't like to test private methods, but in this case, testing
   the private methods will help give us some reasonable confidence in the code
   even if we can't talk to a database..  This isn't perfect, but it's better
   than nothing.

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
   build environment.  There is a no need to use a MYSQLTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.extend.mysql import LocalConfig, MysqlConfig
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
    "mysql.conf.1",
    "mysql.conf.2",
    "mysql.conf.3",
    "mysql.conf.4",
    "mysql.conf.5",
]


#######################################################################
# Test Case Classes
#######################################################################

########################
# TestMysqlConfig class
########################


class TestMysqlConfig(unittest.TestCase):

    """Tests for the MysqlConfig class."""

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
        obj = MysqlConfig()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no values filled in.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.user)
        self.assertEqual(None, mysql.password)
        self.assertEqual(None, mysql.compressMode)
        self.assertEqual(False, mysql.all)
        self.assertEqual(None, mysql.databases)

    def testConstructor_002(self):
        """
        Test constructor with all values filled in, with valid values, databases=None.
        """
        mysql = MysqlConfig("user", "password", "none", False, None)
        self.assertEqual("user", mysql.user)
        self.assertEqual("password", mysql.password)
        self.assertEqual("none", mysql.compressMode)
        self.assertEqual(False, mysql.all)
        self.assertEqual(None, mysql.databases)

    def testConstructor_003(self):
        """
        Test constructor with all values filled in, with valid values, no databases.
        """
        mysql = MysqlConfig("user", "password", "none", True, [])
        self.assertEqual("user", mysql.user)
        self.assertEqual("password", mysql.password)
        self.assertEqual("none", mysql.compressMode)
        self.assertEqual(True, mysql.all)
        self.assertEqual([], mysql.databases)

    def testConstructor_004(self):
        """
        Test constructor with all values filled in, with valid values, with one database.
        """
        mysql = MysqlConfig("user", "password", "gzip", True, ["one"])
        self.assertEqual("user", mysql.user)
        self.assertEqual("password", mysql.password)
        self.assertEqual("gzip", mysql.compressMode)
        self.assertEqual(True, mysql.all)
        self.assertEqual(["one"], mysql.databases)

    def testConstructor_005(self):
        """
        Test constructor with all values filled in, with valid values, with multiple databases.
        """
        mysql = MysqlConfig("user", "password", "bzip2", True, ["one", "two"])
        self.assertEqual("user", mysql.user)
        self.assertEqual("password", mysql.password)
        self.assertEqual("bzip2", mysql.compressMode)
        self.assertEqual(True, mysql.all)
        self.assertEqual(["one", "two"], mysql.databases)

    def testConstructor_006(self):
        """
        Test assignment of user attribute, None value.
        """
        mysql = MysqlConfig(user="user")
        self.assertEqual("user", mysql.user)
        mysql.user = None
        self.assertEqual(None, mysql.user)

    def testConstructor_007(self):
        """
        Test assignment of user attribute, valid value.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.user)
        mysql.user = "user"
        self.assertEqual("user", mysql.user)

    def testConstructor_008(self):
        """
        Test assignment of user attribute, invalid value (empty).
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.user)
        self.failUnlessAssignRaises(ValueError, mysql, "user", "")
        self.assertEqual(None, mysql.user)

    def testConstructor_009(self):
        """
        Test assignment of password attribute, None value.
        """
        mysql = MysqlConfig(password="password")
        self.assertEqual("password", mysql.password)
        mysql.password = None
        self.assertEqual(None, mysql.password)

    def testConstructor_010(self):
        """
        Test assignment of password attribute, valid value.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.password)
        mysql.password = "password"
        self.assertEqual("password", mysql.password)

    def testConstructor_011(self):
        """
        Test assignment of password attribute, invalid value (empty).
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.password)
        self.failUnlessAssignRaises(ValueError, mysql, "password", "")
        self.assertEqual(None, mysql.password)

    def testConstructor_012(self):
        """
        Test assignment of compressMode attribute, None value.
        """
        mysql = MysqlConfig(compressMode="none")
        self.assertEqual("none", mysql.compressMode)
        mysql.compressMode = None
        self.assertEqual(None, mysql.compressMode)

    def testConstructor_013(self):
        """
        Test assignment of compressMode attribute, valid value.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.compressMode)
        mysql.compressMode = "none"
        self.assertEqual("none", mysql.compressMode)
        mysql.compressMode = "gzip"
        self.assertEqual("gzip", mysql.compressMode)
        mysql.compressMode = "bzip2"
        self.assertEqual("bzip2", mysql.compressMode)

    def testConstructor_014(self):
        """
        Test assignment of compressMode attribute, invalid value (empty).
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.compressMode)
        self.failUnlessAssignRaises(ValueError, mysql, "compressMode", "")
        self.assertEqual(None, mysql.compressMode)

    def testConstructor_015(self):
        """
        Test assignment of compressMode attribute, invalid value (not in list).
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.compressMode)
        self.failUnlessAssignRaises(ValueError, mysql, "compressMode", "bogus")
        self.assertEqual(None, mysql.compressMode)

    def testConstructor_016(self):
        """
        Test assignment of all attribute, None value.
        """
        mysql = MysqlConfig(all=True)
        self.assertEqual(True, mysql.all)
        mysql.all = None
        self.assertEqual(False, mysql.all)

    def testConstructor_017(self):
        """
        Test assignment of all attribute, valid value (real boolean).
        """
        mysql = MysqlConfig()
        self.assertEqual(False, mysql.all)
        mysql.all = True
        self.assertEqual(True, mysql.all)
        mysql.all = False
        self.assertEqual(False, mysql.all)

    def testConstructor_018(self):
        """
        Test assignment of all attribute, valid value (expression).
        """
        mysql = MysqlConfig()
        self.assertEqual(False, mysql.all)
        mysql.all = 0
        self.assertEqual(False, mysql.all)
        mysql.all = []
        self.assertEqual(False, mysql.all)
        mysql.all = None
        self.assertEqual(False, mysql.all)
        mysql.all = ["a"]
        self.assertEqual(True, mysql.all)
        mysql.all = 3
        self.assertEqual(True, mysql.all)

    def testConstructor_019(self):
        """
        Test assignment of databases attribute, None value.
        """
        mysql = MysqlConfig(databases=[])
        self.assertEqual([], mysql.databases)
        mysql.databases = None
        self.assertEqual(None, mysql.databases)

    def testConstructor_020(self):
        """
        Test assignment of databases attribute, [] value.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.databases)
        mysql.databases = []
        self.assertEqual([], mysql.databases)

    def testConstructor_021(self):
        """
        Test assignment of databases attribute, single valid entry.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.databases)
        mysql.databases = [
            "/whatever",
        ]
        self.assertEqual(["/whatever"], mysql.databases)
        mysql.databases.append("/stuff")
        self.assertEqual(["/whatever", "/stuff"], mysql.databases)

    def testConstructor_022(self):
        """
        Test assignment of databases attribute, multiple valid entries.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.databases)
        mysql.databases = [
            "/whatever",
            "/stuff",
        ]
        self.assertEqual(["/whatever", "/stuff"], mysql.databases)
        mysql.databases.append("/etc/X11")
        self.assertEqual(["/whatever", "/stuff", "/etc/X11"], mysql.databases)

    def testConstructor_023(self):
        """
        Test assignment of databases attribute, single invalid entry (empty).
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.databases)
        self.failUnlessAssignRaises(ValueError, mysql, "databases", [""])
        self.assertEqual(None, mysql.databases)

    def testConstructor_024(self):
        """
        Test assignment of databases attribute, mixed valid and invalid entries.
        """
        mysql = MysqlConfig()
        self.assertEqual(None, mysql.databases)
        self.failUnlessAssignRaises(ValueError, mysql, "databases", ["good", "", "alsogood"])
        self.assertEqual(None, mysql.databases)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes None.
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig()
        self.assertEqual(mysql1, mysql2)
        self.assertTrue(mysql1 == mysql2)
        self.assertTrue(not mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(mysql1 >= mysql2)
        self.assertTrue(not mysql1 != mysql2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes non-None, list None.
        """
        mysql1 = MysqlConfig("user", "password", "gzip", True, None)
        mysql2 = MysqlConfig("user", "password", "gzip", True, None)
        self.assertEqual(mysql1, mysql2)
        self.assertTrue(mysql1 == mysql2)
        self.assertTrue(not mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(mysql1 >= mysql2)
        self.assertTrue(not mysql1 != mysql2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes non-None, list empty.
        """
        mysql1 = MysqlConfig("user", "password", "bzip2", True, [])
        mysql2 = MysqlConfig("user", "password", "bzip2", True, [])
        self.assertEqual(mysql1, mysql2)
        self.assertTrue(mysql1 == mysql2)
        self.assertTrue(not mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(mysql1 >= mysql2)
        self.assertTrue(not mysql1 != mysql2)

    def testComparison_004(self):
        """
        Test comparison of two identical objects, all attributes non-None, list non-empty.
        """
        mysql1 = MysqlConfig("user", "password", "none", True, ["whatever"])
        mysql2 = MysqlConfig("user", "password", "none", True, ["whatever"])
        self.assertEqual(mysql1, mysql2)
        self.assertTrue(mysql1 == mysql2)
        self.assertTrue(not mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(mysql1 >= mysql2)
        self.assertTrue(not mysql1 != mysql2)

    def testComparison_005(self):
        """
        Test comparison of two differing objects, user differs (one None).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(user="user")
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_006(self):
        """
        Test comparison of two differing objects, user differs.
        """
        mysql1 = MysqlConfig("user1", "password", "gzip", True, ["whatever"])
        mysql2 = MysqlConfig("user2", "password", "gzip", True, ["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_007(self):
        """
        Test comparison of two differing objects, password differs (one None).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(password="password")
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_008(self):
        """
        Test comparison of two differing objects, password differs.
        """
        mysql1 = MysqlConfig("user", "password1", "gzip", True, ["whatever"])
        mysql2 = MysqlConfig("user", "password2", "gzip", True, ["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_009(self):
        """
        Test comparison of two differing objects, compressMode differs (one None).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(compressMode="gzip")
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_010(self):
        """
        Test comparison of two differing objects, compressMode differs.
        """
        mysql1 = MysqlConfig("user", "password", "bzip2", True, ["whatever"])
        mysql2 = MysqlConfig("user", "password", "gzip", True, ["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_011(self):
        """
        Test comparison of two differing objects, all differs (one None).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(all=True)
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_012(self):
        """
        Test comparison of two differing objects, all differs.
        """
        mysql1 = MysqlConfig("user", "password", "gzip", False, ["whatever"])
        mysql2 = MysqlConfig("user", "password", "gzip", True, ["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_013(self):
        """
        Test comparison of two differing objects, databases differs (one None, one empty).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(databases=[])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_014(self):
        """
        Test comparison of two differing objects, databases differs (one None, one not empty).
        """
        mysql1 = MysqlConfig()
        mysql2 = MysqlConfig(databases=["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_015(self):
        """
        Test comparison of two differing objects, databases differs (one empty, one not empty).
        """
        mysql1 = MysqlConfig("user", "password", "gzip", True, [])
        mysql2 = MysqlConfig("user", "password", "gzip", True, ["whatever"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(mysql1 < mysql2)
        self.assertTrue(mysql1 <= mysql2)
        self.assertTrue(not mysql1 > mysql2)
        self.assertTrue(not mysql1 >= mysql2)
        self.assertTrue(mysql1 != mysql2)

    def testComparison_016(self):
        """
        Test comparison of two differing objects, databases differs (both not empty).
        """
        mysql1 = MysqlConfig("user", "password", "gzip", True, ["whatever"])
        mysql2 = MysqlConfig("user", "password", "gzip", True, ["whatever", "bogus"])
        self.assertNotEqual(mysql1, mysql2)
        self.assertTrue(not mysql1 == mysql2)
        self.assertTrue(not mysql1 < mysql2)  # note: different than standard due to unsorted list
        self.assertTrue(not mysql1 <= mysql2)  # note: different than standard due to unsorted list
        self.assertTrue(mysql1 > mysql2)  # note: different than standard due to unsorted list
        self.assertTrue(mysql1 >= mysql2)  # note: different than standard due to unsorted list
        self.assertTrue(mysql1 != mysql2)


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

        We dump a document containing just the mysql configuration, and then make
        sure that if we push that document back into the ``LocalConfig`` object,
        that the resulting object matches the original.

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
        self.assertEqual(None, config.mysql)

    def testConstructor_002(self):
        """
        Test empty constructor, validate=True.
        """
        config = LocalConfig(validate=True)
        self.assertEqual(None, config.mysql)

    def testConstructor_003(self):
        """
        Test with empty config document as both data and file, validate=False.
        """
        path = self.resources["mysql.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, xmlPath=path, validate=False)

    def testConstructor_004(self):
        """
        Test assignment of mysql attribute, None value.
        """
        config = LocalConfig()
        config.mysql = None
        self.assertEqual(None, config.mysql)

    def testConstructor_005(self):
        """
        Test assignment of mysql attribute, valid value.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig()
        self.assertEqual(MysqlConfig(), config.mysql)

    def testConstructor_006(self):
        """
        Test assignment of mysql attribute, invalid value (not MysqlConfig).
        """
        config = LocalConfig()
        self.failUnlessAssignRaises(ValueError, config, "mysql", "STRING!")

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
        config1.mysql = MysqlConfig()

        config2 = LocalConfig()
        config2.mysql = MysqlConfig()

        self.assertEqual(config1, config2)
        self.assertTrue(config1 == config2)
        self.assertTrue(not config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(config1 >= config2)
        self.assertTrue(not config1 != config2)

    def testComparison_003(self):
        """
        Test comparison of two differing objects, mysql differs (one None).
        """
        config1 = LocalConfig()
        config2 = LocalConfig()
        config2.mysql = MysqlConfig()
        self.assertNotEqual(config1, config2)
        self.assertTrue(not config1 == config2)
        self.assertTrue(config1 < config2)
        self.assertTrue(config1 <= config2)
        self.assertTrue(not config1 > config2)
        self.assertTrue(not config1 >= config2)
        self.assertTrue(config1 != config2)

    def testComparison_004(self):
        """
        Test comparison of two differing objects, mysql differs.
        """
        config1 = LocalConfig()
        config1.mysql = MysqlConfig(user="one")

        config2 = LocalConfig()
        config2.mysql = MysqlConfig(user="two")

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
        Test validate on a None mysql section.
        """
        config = LocalConfig()
        config.mysql = None
        self.assertRaises(ValueError, config.validate)

    def testValidate_002(self):
        """
        Test validate on an empty mysql section.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig()
        self.assertRaises(ValueError, config.validate)

    def testValidate_003(self):
        """
        Test validate on a non-empty mysql section, all=True, databases=None.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "gzip", True, None)
        config.validate()

    def testValidate_004(self):
        """
        Test validate on a non-empty mysql section, all=True, empty databases.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "none", True, [])
        config.validate()

    def testValidate_005(self):
        """
        Test validate on a non-empty mysql section, all=True, non-empty databases.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "bzip2", True, ["whatever"])
        self.assertRaises(ValueError, config.validate)

    def testValidate_006(self):
        """
        Test validate on a non-empty mysql section, all=False, databases=None.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "gzip", False, None)
        self.assertRaises(ValueError, config.validate)

    def testValidate_007(self):
        """
        Test validate on a non-empty mysql section, all=False, empty databases.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "bzip2", False, [])
        self.assertRaises(ValueError, config.validate)

    def testValidate_008(self):
        """
        Test validate on a non-empty mysql section, all=False, non-empty databases.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "gzip", False, ["whatever"])
        config.validate()

    def testValidate_009(self):
        """
        Test validate on a non-empty mysql section, with user=None.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig(None, "password", "gzip", True, None)
        config.validate()

    def testValidate_010(self):
        """
        Test validate on a non-empty mysql section, with password=None.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", None, "gzip", True, None)
        config.validate()

    def testValidate_011(self):
        """
        Test validate on a non-empty mysql section, with user=None and password=None.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig(None, None, "gzip", True, None)
        config.validate()

    ############################
    # Test parsing of documents
    ############################

    def testParse_001(self):
        """
        Parse empty config document.
        """
        path = self.resources["mysql.conf.1"]
        with open(path) as f:
            contents = f.read()
        self.assertRaises(ValueError, LocalConfig, xmlPath=path, validate=True)
        self.assertRaises(ValueError, LocalConfig, xmlData=contents, validate=True)
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertEqual(None, config.mysql)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual(None, config.mysql)

    def testParse_003(self):
        """
        Parse config document containing only a mysql section, no databases, all=True.
        """
        path = self.resources["mysql.conf.2"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("none", config.mysql.compressMode)
        self.assertEqual(True, config.mysql.all)
        self.assertEqual(None, config.mysql.databases)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("none", config.mysql.compressMode)
        self.assertNotEqual(None, config.mysql.password)
        self.assertEqual(True, config.mysql.all)
        self.assertEqual(None, config.mysql.databases)

    def testParse_004(self):
        """
        Parse config document containing only a mysql section, single database, all=False.
        """
        path = self.resources["mysql.conf.3"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("gzip", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database"], config.mysql.databases)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("gzip", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database"], config.mysql.databases)

    def testParse_005(self):
        """
        Parse config document containing only a mysql section, multiple databases, all=False.
        """
        path = self.resources["mysql.conf.4"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("bzip2", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database1", "database2"], config.mysql.databases)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual("user", config.mysql.user)
        self.assertEqual("password", config.mysql.password)
        self.assertEqual("bzip2", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database1", "database2"], config.mysql.databases)

    def testParse_006(self):
        """
        Parse config document containing only a mysql section, no user or password, multiple databases, all=False.
        """
        path = self.resources["mysql.conf.5"]
        with open(path) as f:
            contents = f.read()
        config = LocalConfig(xmlPath=path, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual(None, config.mysql.user)
        self.assertEqual(None, config.mysql.password)
        self.assertEqual("bzip2", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database1", "database2"], config.mysql.databases)
        config = LocalConfig(xmlData=contents, validate=False)
        self.assertNotEqual(None, config.mysql)
        self.assertEqual(None, config.mysql.user)
        self.assertEqual(None, config.mysql.password)
        self.assertEqual("bzip2", config.mysql.compressMode)
        self.assertEqual(False, config.mysql.all)
        self.assertEqual(["database1", "database2"], config.mysql.databases)

    ###################
    # Test addConfig()
    ###################

    def testAddConfig_001(self):
        """
        Test with empty config document
        """
        config = LocalConfig()
        self.validateAddConfig(config)

    def testAddConfig_003(self):
        """
        Test with no databases, all other values filled in, all=True.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "none", True, None)
        self.validateAddConfig(config)

    def testAddConfig_004(self):
        """
        Test with no databases, all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "gzip", False, None)
        self.validateAddConfig(config)

    def testAddConfig_005(self):
        """
        Test with single database, all other values filled in, all=True.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "bzip2", True, ["database"])
        self.validateAddConfig(config)

    def testAddConfig_006(self):
        """
        Test with single database, all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "none", False, ["database"])
        self.validateAddConfig(config)

    def testAddConfig_007(self):
        """
        Test with multiple databases, all other values filled in, all=True.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "bzip2", True, ["database1", "database2"])
        self.validateAddConfig(config)

    def testAddConfig_008(self):
        """
        Test with multiple databases, all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", "password", "gzip", True, ["database1", "database2"])
        self.validateAddConfig(config)

    def testAddConfig_009(self):
        """
        Test with multiple databases, user=None but all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig(None, "password", "gzip", True, ["database1", "database2"])
        self.validateAddConfig(config)

    def testAddConfig_010(self):
        """
        Test with multiple databases, password=None but all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig("user", None, "gzip", True, ["database1", "database2"])
        self.validateAddConfig(config)

    def testAddConfig_011(self):
        """
        Test with multiple databases, user=None and password=None but all other values filled in, all=False.
        """
        config = LocalConfig()
        config.mysql = MysqlConfig(None, None, "gzip", True, ["database1", "database2"])
        self.validateAddConfig(config)
