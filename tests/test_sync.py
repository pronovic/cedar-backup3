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
# Copyright (c) 2007,2010,2015,2020 Kenneth J. Pronovici.
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
# Purpose  : Tests Amazon S3 sync tool functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/tools/amazons3.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in tools/amazons3.py.  Where possible, we test
   functions that print output by passing a custom file descriptor.  Sometimes,
   we only ensure that a function or method runs without failure, and we don't
   validate what its result is or what it prints out.

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
   build environment.  There is a no need to use a SYNCTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest
from getopt import GetoptError

from CedarBackup3.testutil import captureOutput, configureLogging, failUnlessAssignRaises
from CedarBackup3.tools.amazons3 import Options, _usage, _version

#######################################################################
# Test Case Classes
#######################################################################

######################
# TestFunctions class
######################


class TestFunctions(unittest.TestCase):

    """Tests for the public functions."""

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

    ########################
    # Test simple functions
    ########################

    def testSimpleFuncs_001(self):
        """
        Test that the _usage() function runs without errors.
        We don't care what the output is, and we don't check.
        """
        captureOutput(_usage)

    def testSimpleFuncs_002(self):
        """
        Test that the _version() function runs without errors.
        We don't care what the output is, and we don't check.
        """
        captureOutput(_version)


####################
# TestOptions class
####################


class TestOptions(unittest.TestCase):

    """Tests for the Options class."""

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
        obj = Options()
        obj.__repr__()
        obj.__str__()

    ##################################
    # Test constructor and attributes
    ##################################

    def testConstructor_001(self):
        """
        Test constructor with no arguments.
        """
        options = Options()
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_002(self):
        """
        Test constructor with validate=False, no other arguments.
        """
        options = Options(validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_003(self):
        """
        Test constructor with argumentList=[], validate=False.
        """
        options = Options(argumentList=[], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_004(self):
        """
        Test constructor with argumentString="", validate=False.
        """
        options = Options(argumentString="", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_005(self):
        """
        Test constructor with argumentList=["--help", ], validate=False.
        """
        options = Options(argumentList=["--help"], validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_006(self):
        """
        Test constructor with argumentString="--help", validate=False.
        """
        options = Options(argumentString="--help", validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_007(self):
        """
        Test constructor with argumentList=["-h", ], validate=False.
        """
        options = Options(argumentList=["-h"], validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_008(self):
        """
        Test constructor with argumentString="-h", validate=False.
        """
        options = Options(argumentString="-h", validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_009(self):
        """
        Test constructor with argumentList=["--version", ], validate=False.
        """
        options = Options(argumentList=["--version"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_010(self):
        """
        Test constructor with argumentString="--version", validate=False.
        """
        options = Options(argumentString="--version", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_011(self):
        """
        Test constructor with argumentList=["-V", ], validate=False.
        """
        options = Options(argumentList=["-V"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_012(self):
        """
        Test constructor with argumentString="-V", validate=False.
        """
        options = Options(argumentString="-V", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_013(self):
        """
        Test constructor with argumentList=["--verbose", ], validate=False.
        """
        options = Options(argumentList=["--verbose"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_014(self):
        """
        Test constructor with argumentString="--verbose", validate=False.
        """
        options = Options(argumentString="--verbose", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_015(self):
        """
        Test constructor with argumentList=["-b", ], validate=False.
        """
        options = Options(argumentList=["-b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_016(self):
        """
        Test constructor with argumentString="-b", validate=False.
        """
        options = Options(argumentString="-b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_017(self):
        """
        Test constructor with argumentList=["--quiet", ], validate=False.
        """
        options = Options(argumentList=["--quiet"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_018(self):
        """
        Test constructor with argumentString="--quiet", validate=False.
        """
        options = Options(argumentString="--quiet", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_019(self):
        """
        Test constructor with argumentList=["-q", ], validate=False.
        """
        options = Options(argumentList=["-q"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_020(self):
        """
        Test constructor with argumentString="-q", validate=False.
        """
        options = Options(argumentString="-q", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_021(self):
        """
        Test constructor with argumentList=["--logfile", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--logfile"], validate=False)

    def testConstructor_022(self):
        """
        Test constructor with argumentString="--logfile", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--logfile", validate=False)

    def testConstructor_023(self):
        """
        Test constructor with argumentList=["-l", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-l"], validate=False)

    def testConstructor_024(self):
        """
        Test constructor with argumentString="-l", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-l", validate=False)

    def testConstructor_025(self):
        """
        Test constructor with argumentList=["--logfile", "something", ], validate=False.
        """
        options = Options(argumentList=["--logfile", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_026(self):
        """
        Test constructor with argumentString="--logfile something", validate=False.
        """
        options = Options(argumentString="--logfile something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_027(self):
        """
        Test constructor with argumentList=["-l", "something", ], validate=False.
        """
        options = Options(argumentList=["-l", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_028(self):
        """
        Test constructor with argumentString="-l something", validate=False.
        """
        options = Options(argumentString="-l something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_029(self):
        """
        Test constructor with argumentList=["--owner", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--owner"], validate=False)

    def testConstructor_030(self):
        """
        Test constructor with argumentString="--owner", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--owner", validate=False)

    def testConstructor_040(self):
        """
        Test constructor with argumentList=["-o", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-o"], validate=False)

    def testConstructor_041(self):
        """
        Test constructor with argumentString="-o", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-o", validate=False)

    def testConstructor_042(self):
        """
        Test constructor with argumentList=["--owner", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "something"], validate=False)

    def testConstructor_043(self):
        """
        Test constructor with argumentString="--owner something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner something", validate=False)

    def testConstructor_044(self):
        """
        Test constructor with argumentList=["-o", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "something"], validate=False)

    def testConstructor_045(self):
        """
        Test constructor with argumentString="-o something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="-o something", validate=False)

    def testConstructor_046(self):
        """
        Test constructor with argumentList=["--owner", "a:b", ], validate=False.
        """
        options = Options(argumentList=["--owner", "a:b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_047(self):
        """
        Test constructor with argumentString="--owner a:b", validate=False.
        """
        options = Options(argumentString="--owner a:b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_048(self):
        """
        Test constructor with argumentList=["-o", "a:b", ], validate=False.
        """
        options = Options(argumentList=["-o", "a:b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_049(self):
        """
        Test constructor with argumentString="-o a:b", validate=False.
        """
        options = Options(argumentString="-o a:b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_050(self):
        """
        Test constructor with argumentList=["--mode", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--mode"], validate=False)

    def testConstructor_051(self):
        """
        Test constructor with argumentString="--mode", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--mode", validate=False)

    def testConstructor_052(self):
        """
        Test constructor with argumentList=["-m", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-m"], validate=False)

    def testConstructor_053(self):
        """
        Test constructor with argumentString="-m", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-m", validate=False)

    def testConstructor_054(self):
        """
        Test constructor with argumentList=["--mode", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "something"], validate=False)

    def testConstructor_055(self):
        """
        Test constructor with argumentString="--mode something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode something", validate=False)

    def testConstructor_056(self):
        """
        Test constructor with argumentList=["-m", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "something"], validate=False)

    def testConstructor_057(self):
        """
        Test constructor with argumentString="-m something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="-m something", validate=False)

    def testConstructor_058(self):
        """
        Test constructor with argumentList=["--mode", "631", ], validate=False.
        """
        options = Options(argumentList=["--mode", "631"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_059(self):
        """
        Test constructor with argumentString="--mode 631", validate=False.
        """
        options = Options(argumentString="--mode 631", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_060(self):
        """
        Test constructor with argumentList=["-m", "631", ], validate=False.
        """
        options = Options(argumentList=["-m", "631"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_061(self):
        """
        Test constructor with argumentString="-m 631", validate=False.
        """
        options = Options(argumentString="-m 631", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_062(self):
        """
        Test constructor with argumentList=["--output", ], validate=False.
        """
        options = Options(argumentList=["--output"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_063(self):
        """
        Test constructor with argumentString="--output", validate=False.
        """
        options = Options(argumentString="--output", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_064(self):
        """
        Test constructor with argumentList=["-O", ], validate=False.
        """
        options = Options(argumentList=["-O"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_065(self):
        """
        Test constructor with argumentString="-O", validate=False.
        """
        options = Options(argumentString="-O", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_066(self):
        """
        Test constructor with argumentList=["--debug", ], validate=False.
        """
        options = Options(argumentList=["--debug"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_067(self):
        """
        Test constructor with argumentString="--debug", validate=False.
        """
        options = Options(argumentString="--debug", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_068(self):
        """
        Test constructor with argumentList=["-d", ], validate=False.
        """
        options = Options(argumentList=["-d"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_069(self):
        """
        Test constructor with argumentString="-d", validate=False.
        """
        options = Options(argumentString="-d", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_070(self):
        """
        Test constructor with argumentList=["--stack", ], validate=False.
        """
        options = Options(argumentList=["--stack"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_071(self):
        """
        Test constructor with argumentString="--stack", validate=False.
        """
        options = Options(argumentString="--stack", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_072(self):
        """
        Test constructor with argumentList=["-s", ], validate=False.
        """
        options = Options(argumentList=["-s"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_073(self):
        """
        Test constructor with argumentString="-s", validate=False.
        """
        options = Options(argumentString="-s", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_074(self):
        """
        Test constructor with argumentList=["--diagnostics", ], validate=False.
        """
        options = Options(argumentList=["--diagnostics"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_075(self):
        """
        Test constructor with argumentString="--diagnostics", validate=False.
        """
        options = Options(argumentString="--diagnostics", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_076(self):
        """
        Test constructor with argumentList=["-D", ], validate=False.
        """
        options = Options(argumentList=["-D"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_077(self):
        """
        Test constructor with argumentString="-D", validate=False.
        """
        options = Options(argumentString="-D", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_078(self):
        """
        Test constructor with argumentList=["--verifyOnly", ], validate=False.
        """
        options = Options(argumentList=["--verifyOnly"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(True, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_079(self):
        """
        Test constructor with argumentString="--verifyOnly", validate=False.
        """
        options = Options(argumentString="--verifyOnly", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(True, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_080(self):
        """
        Test constructor with argumentList=["-v", ], validate=False.
        """
        options = Options(argumentList=["-v"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(True, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_081(self):
        """
        Test constructor with argumentString="-v", validate=False.
        """
        options = Options(argumentString="-v", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(True, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_082(self):
        """
        Test constructor with argumentList=["--ignoreWarnings", ], validate=False.
        """
        options = Options(argumentList=["--ignoreWarnings"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(True, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_083(self):
        """
        Test constructor with argumentString="--ignoreWarnings", validate=False.
        """
        options = Options(argumentString="--ignoreWarnings", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(True, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_084(self):
        """
        Test constructor with argumentList=["-w", ], validate=False.
        """
        options = Options(argumentList=["-w"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(True, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_085(self):
        """
        Test constructor with argumentString="-w", validate=False.
        """
        options = Options(argumentString="-w", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(True, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_086(self):
        """
        Test constructor with argumentList=["source", "bucket", ], validate=False.
        """
        options = Options(argumentList=["source", "bucket"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_087(self):
        """
        Test constructor with argumentString="source bucket", validate=False.
        """
        options = Options(argumentString="source bucket", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_088(self):
        """
        Test constructor with argumentList=["-d", "--verbose", "-O", "--mode", "600", "source", "bucket", ], validate=False.
        """
        options = Options(argumentList=["-d", "--verbose", "-O", "--mode", "600", "source", "bucket"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_089(self):
        """
        Test constructor with argumentString="-d --verbose -O --mode 600 source bucket", validate=False.
        """
        options = Options(argumentString="-d --verbose -O --mode 600 source bucket", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_090(self):
        """
        Test constructor with argumentList=[], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=[], validate=True)

    def testConstructor_091(self):
        """
        Test constructor with argumentString="", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="", validate=True)

    def testConstructor_092(self):
        """
        Test constructor with argumentList=["--help", ], validate=True.
        """
        options = Options(argumentList=["--help"], validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_093(self):
        """
        Test constructor with argumentString="--help", validate=True.
        """
        options = Options(argumentString="--help", validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_094(self):
        """
        Test constructor with argumentList=["-h", ], validate=True.
        """
        options = Options(argumentList=["-h"], validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_095(self):
        """
        Test constructor with argumentString="-h", validate=True.
        """
        options = Options(argumentString="-h", validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_096(self):
        """
        Test constructor with argumentList=["--version", ], validate=True.
        """
        options = Options(argumentList=["--version"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_097(self):
        """
        Test constructor with argumentString="--version", validate=True.
        """
        options = Options(argumentString="--version", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_098(self):
        """
        Test constructor with argumentList=["-V", ], validate=True.
        """
        options = Options(argumentList=["-V"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_099(self):
        """
        Test constructor with argumentString="-V", validate=True.
        """
        options = Options(argumentString="-V", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_100(self):
        """
        Test constructor with argumentList=["--verbose", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--verbose"], validate=True)

    def testConstructor_101(self):
        """
        Test constructor with argumentString="--verbose", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--verbose", validate=True)

    def testConstructor_102(self):
        """
        Test constructor with argumentList=["-b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-b"], validate=True)

    def testConstructor_103(self):
        """
        Test constructor with argumentString="-b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-b", validate=True)

    def testConstructor_104(self):
        """
        Test constructor with argumentList=["--quiet", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--quiet"], validate=True)

    def testConstructor_105(self):
        """
        Test constructor with argumentString="--quiet", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--quiet", validate=True)

    def testConstructor_106(self):
        """
        Test constructor with argumentList=["-q", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-q"], validate=True)

    def testConstructor_107(self):
        """
        Test constructor with argumentString="-q", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-q", validate=True)

    def testConstructor_108(self):
        """
        Test constructor with argumentList=["--logfile", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--logfile"], validate=True)

    def testConstructor_109(self):
        """
        Test constructor with argumentString="--logfile", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--logfile", validate=True)

    def testConstructor_110(self):
        """
        Test constructor with argumentList=["-l", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-l"], validate=True)

    def testConstructor_111(self):
        """
        Test constructor with argumentString="-l", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-l", validate=True)

    def testConstructor_112(self):
        """
        Test constructor with argumentList=["--logfile", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--logfile", "something"], validate=True)

    def testConstructor_113(self):
        """
        Test constructor with argumentString="--logfile something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--logfile something", validate=True)

    def testConstructor_114(self):
        """
        Test constructor with argumentList=["-l", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-l", "something"], validate=True)

    def testConstructor_115(self):
        """
        Test constructor with argumentString="-l something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-l something", validate=True)

    def testConstructor_116(self):
        """
        Test constructor with argumentList=["--owner", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--owner"], validate=True)

    def testConstructor_117(self):
        """
        Test constructor with argumentString="--owner", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--owner", validate=True)

    def testConstructor_118(self):
        """
        Test constructor with argumentList=["-o", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-o"], validate=True)

    def testConstructor_119(self):
        """
        Test constructor with argumentString="-o", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-o", validate=True)

    def testConstructor_120(self):
        """
        Test constructor with argumentList=["--owner", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "something"], validate=True)

    def testConstructor_121(self):
        """
        Test constructor with argumentString="--owner something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner something", validate=True)

    def testConstructor_122(self):
        """
        Test constructor with argumentList=["-o", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "something"], validate=True)

    def testConstructor_123(self):
        """
        Test constructor with argumentString="-o something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-o something", validate=True)

    def testConstructor_124(self):
        """
        Test constructor with argumentList=["--owner", "a:b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "a:b"], validate=True)

    def testConstructor_125(self):
        """
        Test constructor with argumentString="--owner a:b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner a:b", validate=True)

    def testConstructor_126(self):
        """
        Test constructor with argumentList=["-o", "a:b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "a:b"], validate=True)

    def testConstructor_127(self):
        """
        Test constructor with argumentString="-o a:b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-o a:b", validate=True)

    def testConstructor_128(self):
        """
        Test constructor with argumentList=["--mode", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--mode"], validate=True)

    def testConstructor_129(self):
        """
        Test constructor with argumentString="--mode", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--mode", validate=True)

    def testConstructor_130(self):
        """
        Test constructor with argumentList=["-m", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-m"], validate=True)

    def testConstructor_131(self):
        """
        Test constructor with argumentString="-m", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-m", validate=True)

    def testConstructor_132(self):
        """
        Test constructor with argumentList=["--mode", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "something"], validate=True)

    def testConstructor_133(self):
        """
        Test constructor with argumentString="--mode something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode something", validate=True)

    def testConstructor_134(self):
        """
        Test constructor with argumentList=["-m", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "something"], validate=True)

    def testConstructor_135(self):
        """
        Test constructor with argumentString="-m something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-m something", validate=True)

    def testConstructor_136(self):
        """
        Test constructor with argumentList=["--mode", "631", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "631"], validate=True)

    def testConstructor_137(self):
        """
        Test constructor with argumentString="--mode 631", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode 631", validate=True)

    def testConstructor_138(self):
        """
        Test constructor with argumentList=["-m", "631", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "631"], validate=True)

    def testConstructor_139(self):
        """
        Test constructor with argumentString="-m 631", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-m 631", validate=True)

    def testConstructor_140(self):
        """
        Test constructor with argumentList=["--output", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--output"], validate=True)

    def testConstructor_141(self):
        """
        Test constructor with argumentString="--output", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--output", validate=True)

    def testConstructor_142(self):
        """
        Test constructor with argumentList=["-O", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-O"], validate=True)

    def testConstructor_143(self):
        """
        Test constructor with argumentString="-O", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-O", validate=True)

    def testConstructor_144(self):
        """
        Test constructor with argumentList=["--debug", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--debug"], validate=True)

    def testConstructor_145(self):
        """
        Test constructor with argumentString="--debug", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--debug", validate=True)

    def testConstructor_146(self):
        """
        Test constructor with argumentList=["-d", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-d"], validate=True)

    def testConstructor_147(self):
        """
        Test constructor with argumentString="-d", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-d", validate=True)

    def testConstructor_148(self):
        """
        Test constructor with argumentList=["--stack", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--stack"], validate=True)

    def testConstructor_149(self):
        """
        Test constructor with argumentString="--stack", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--stack", validate=True)

    def testConstructor_150(self):
        """
        Test constructor with argumentList=["-s", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-s"], validate=True)

    def testConstructor_151(self):
        """
        Test constructor with argumentString="-s", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-s", validate=True)

    def testConstructor_152(self):
        """
        Test constructor with argumentList=["--diagnostics", ], validate=True.
        """
        options = Options(argumentList=["--diagnostics"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_153(self):
        """
        Test constructor with argumentString="--diagnostics", validate=True.
        """
        options = Options(argumentString="--diagnostics", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_154(self):
        """
        Test constructor with argumentList=["-D", ], validate=True.
        """
        options = Options(argumentList=["-D"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_155(self):
        """
        Test constructor with argumentString="-D", validate=True.
        """
        options = Options(argumentString="-D", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_156(self):
        """
        Test constructor with argumentList=["--verifyOnly", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--verifyOnly"], validate=True)

    def testConstructor_157(self):
        """
        Test constructor with argumentString="--verifyOnly", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--verifyOnly", validate=True)

    def testConstructor_158(self):
        """
        Test constructor with argumentList=["-v", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-v"], validate=True)

    def testConstructor_159(self):
        """
        Test constructor with argumentString="-v", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-v", validate=True)

    def testConstructor_160(self):
        """
        Test constructor with argumentList=["--ignoreWarnings", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--ignoreWarnings"], validate=True)

    def testConstructor_161(self):
        """
        Test constructor with argumentString="--ignoreWarnings", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--ignoreWarnings", validate=True)

    def testConstructor_162(self):
        """
        Test constructor with argumentList=["-w", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-w"], validate=True)

    def testConstructor_163(self):
        """
        Test constructor with argumentString="-w", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-w", validate=True)

    def testConstructor_164(self):
        """
        Test constructor with argumentList=["source", "bucket", ], validate=True.
        """
        options = Options(argumentList=["source", "bucket"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_165(self):
        """
        Test constructor with argumentString="source bucket", validate=True.
        """
        options = Options(argumentString="source bucket", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_166(self):
        """
        Test constructor with argumentList=["source", "bucket", ], validate=True.
        """
        options = Options(argumentList=["source", "bucket"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_167(self):
        """
        Test constructor with argumentString="source bucket", validate=True.
        """
        options = Options(argumentString="source bucket", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_168(self):
        """
        Test constructor with argumentList=["-d", "--verbose", "-O", "--mode", "600", "source", "bucket", ], validate=True.
        """
        options = Options(argumentList=["-d", "--verbose", "-O", "--mode", "600", "source", "bucket"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_169(self):
        """
        Test constructor with argumentString="-d --verbose -O --mode 600 source bucket", validate=True.
        """
        options = Options(argumentString="-d --verbose -O --mode 600 source bucket", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(False, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual("source", options.sourceDir)
        self.assertEqual("bucket", options.s3BucketUrl)

    def testConstructor_170(self):
        """
        Test constructor with argumentList=["--uploadOnly", ], validate=False.
        """
        options = Options(argumentList=["--uploadOnly"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(True, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_171(self):
        """
        Test constructor with argumentString="--verifyOnly", validate=False.
        """
        options = Options(argumentString="--uploadOnly", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(True, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_172(self):
        """
        Test constructor with argumentList=["-u", ], validate=False.
        """
        options = Options(argumentList=["-u"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(True, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    def testConstructor_173(self):
        """
        Test constructor with argumentString="-u", validate=False.
        """
        options = Options(argumentString="-u", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.verifyOnly)
        self.assertEqual(True, options.uploadOnly)
        self.assertEqual(False, options.ignoreWarnings)
        self.assertEqual(None, options.sourceDir)
        self.assertEqual(None, options.s3BucketUrl)

    ############################
    # Test comparison operators
    ############################

    def testComparison_001(self):
        """
        Test comparison of two identical objects, all attributes at defaults.
        """
        options1 = Options()
        options2 = Options()
        self.assertEqual(options1, options2)
        self.assertTrue(options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(not options1 != options2)

    def testComparison_002(self):
        """
        Test comparison of two identical objects, all attributes filled in and same.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertEqual(options1, options2)
        self.assertTrue(options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(not options1 != options2)

    def testComparison_003(self):
        """
        Test comparison of two identical objects, all attributes filled in, help different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = False
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_004(self):
        """
        Test comparison of two identical objects, all attributes filled in, version different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = False
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_005(self):
        """
        Test comparison of two identical objects, all attributes filled in, verbose different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = False
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_006(self):
        """
        Test comparison of two identical objects, all attributes filled in, quiet different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = False
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_007(self):
        """
        Test comparison of two identical objects, all attributes filled in, logfile different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = None
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_008(self):
        """
        Test comparison of two identical objects, all attributes filled in, owner different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = None
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_009(self):
        """
        Test comparison of two identical objects, all attributes filled in, mode different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = None
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_010(self):
        """
        Test comparison of two identical objects, all attributes filled in, output different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = False
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_011(self):
        """
        Test comparison of two identical objects, all attributes filled in, debug different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = False
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_012(self):
        """
        Test comparison of two identical objects, all attributes filled in, stacktrace different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_013(self):
        """
        Test comparison of two identical objects, all attributes filled in, diagnostics different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = False
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_014(self):
        """
        Test comparison of two identical objects, all attributes filled in, verifyOnly different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = False
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_015(self):
        """
        Test comparison of two identical objects, all attributes filled in, sourceDir different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = None
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_016(self):
        """
        Test comparison of two identical objects, all attributes filled in, s3BucketUrl different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = True
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = None

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_017(self):
        """
        Test comparison of two identical objects, all attributes filled in, uploadOnly different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = True
        options1.diagnostics = True
        options1.verifyOnly = True
        options1.uploadOnly = False
        options1.ignoreWarnings = True
        options1.sourceDir = "source"
        options1.s3BucketUrl = "bucket"

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = "631"
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = True
        options2.verifyOnly = True
        options2.uploadOnly = True
        options2.ignoreWarnings = True
        options2.sourceDir = "source"
        options2.s3BucketUrl = "bucket"

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    ###########################
    # Test buildArgumentList()
    ###########################

    def testBuildArgumentList_001(self):
        """Test with no values set, validate=False."""
        options = Options()
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual([], argumentList)

    def testBuildArgumentList_002(self):
        """Test with help set, validate=False."""
        options = Options()
        options.help = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--help"], argumentList)

    def testBuildArgumentList_003(self):
        """Test with version set, validate=False."""
        options = Options()
        options.version = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--version"], argumentList)

    def testBuildArgumentList_004(self):
        """Test with verbose set, validate=False."""
        options = Options()
        options.verbose = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--verbose"], argumentList)

    def testBuildArgumentList_005(self):
        """Test with quiet set, validate=False."""
        options = Options()
        options.quiet = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--quiet"], argumentList)

    def testBuildArgumentList_006(self):
        """Test with logfile set, validate=False."""
        options = Options()
        options.logfile = "bogus"
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--logfile", "bogus"], argumentList)

    def testBuildArgumentList_007(self):
        """Test with owner set, validate=False."""
        options = Options()
        options.owner = ("ken", "group")
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--owner", "ken:group"], argumentList)

    def testBuildArgumentList_008(self):
        """Test with mode set, validate=False."""
        options = Options()
        options.mode = 0o644
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--mode", "644"], argumentList)

    def testBuildArgumentList_009(self):
        """Test with output set, validate=False."""
        options = Options()
        options.output = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--output"], argumentList)

    def testBuildArgumentList_010(self):
        """Test with debug set, validate=False."""
        options = Options()
        options.debug = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--debug"], argumentList)

    def testBuildArgumentList_011(self):
        """Test with stacktrace set, validate=False."""
        options = Options()
        options.stacktrace = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--stack"], argumentList)

    def testBuildArgumentList_012(self):
        """Test with diagnostics set, validate=False."""
        options = Options()
        options.diagnostics = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--diagnostics"], argumentList)

    def testBuildArgumentList_013(self):
        """Test with verifyOnly set, validate=False."""
        options = Options()
        options.verifyOnly = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--verifyOnly"], argumentList)

    def testBuildArgumentList_014(self):
        """Test with ignoreWarnings set, validate=False."""
        options = Options()
        options.ignoreWarnings = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--ignoreWarnings"], argumentList)

    def testBuildArgumentList_015(self):
        """Test with valid source and target, validate=False."""
        options = Options()
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["source", "bucket"], argumentList)

    def testBuildArgumentList_016(self):
        """Test with all values set, actions containing one item, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.verifyOnly = True
        options.ignoreWarnings = True
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--logfile",
                "logfile",
                "--owner",
                "a:b",
                "--mode",
                "631",
                "--output",
                "--debug",
                "--stack",
                "--diagnostics",
                "--verifyOnly",
                "--ignoreWarnings",
                "source",
                "bucket",
            ],
            argumentList,
        )

    def testBuildArgumentList_017(self):
        """Test with no values set, validate=True."""
        options = Options()
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_018(self):
        """Test with help set, validate=True."""
        options = Options()
        options.help = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--help"], argumentList)

    def testBuildArgumentList_019(self):
        """Test with version set, validate=True."""
        options = Options()
        options.version = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--version"], argumentList)

    def testBuildArgumentList_020(self):
        """Test with verbose set, validate=True."""
        options = Options()
        options.verbose = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_021(self):
        """Test with quiet set, validate=True."""
        options = Options()
        options.quiet = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_022(self):
        """Test with logfile set, validate=True."""
        options = Options()
        options.logfile = "bogus"
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_023(self):
        """Test with owner set, validate=True."""
        options = Options()
        options.owner = ("ken", "group")
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_024(self):
        """Test with mode set, validate=True."""
        options = Options()
        options.mode = 0o644
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_025(self):
        """Test with output set, validate=True."""
        options = Options()
        options.output = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_026(self):
        """Test with debug set, validate=True."""
        options = Options()
        options.debug = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_027(self):
        """Test with stacktrace set, validate=True."""
        options = Options()
        options.stacktrace = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_028(self):
        """Test with diagnostics set, validate=True."""
        options = Options()
        options.diagnostics = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--diagnostics"], argumentList)

    def testBuildArgumentList_029(self):
        """Test with verifyOnly set, validate=True."""
        options = Options()
        options.verifyOnly = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_030(self):
        """Test with ignoreWarnings set, validate=True."""
        options = Options()
        options.ignoreWarnings = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_031(self):
        """Test with valid source and target, validate=True."""
        options = Options()
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["source", "bucket"], argumentList)

    def testBuildArgumentList_032(self):
        """Test with all values set (except managed ones), actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.verifyOnly = True
        options.ignoreWarnings = True
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--logfile",
                "logfile",
                "--owner",
                "a:b",
                "--mode",
                "631",
                "--output",
                "--debug",
                "--stack",
                "--diagnostics",
                "--verifyOnly",
                "--ignoreWarnings",
                "source",
                "bucket",
            ],
            argumentList,
        )

    def testBuildArgumentList_033(self):
        """Test with uploadOnly set, validate=False."""
        options = Options()
        options.uploadOnly = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--uploadOnly"], argumentList)

    #############################
    # Test buildArgumentString()
    #############################

    def testBuildArgumentString_001(self):
        """Test with no values set, validate=False."""
        options = Options()
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("", argumentString)

    def testBuildArgumentString_002(self):
        """Test with help set, validate=False."""
        options = Options()
        options.help = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--help ", argumentString)

    def testBuildArgumentString_003(self):
        """Test with version set, validate=False."""
        options = Options()
        options.version = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--version ", argumentString)

    def testBuildArgumentString_004(self):
        """Test with verbose set, validate=False."""
        options = Options()
        options.verbose = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--verbose ", argumentString)

    def testBuildArgumentString_005(self):
        """Test with quiet set, validate=False."""
        options = Options()
        options.quiet = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--quiet ", argumentString)

    def testBuildArgumentString_006(self):
        """Test with logfile set, validate=False."""
        options = Options()
        options.logfile = "bogus"
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('--logfile "bogus" ', argumentString)

    def testBuildArgumentString_007(self):
        """Test with owner set, validate=False."""
        options = Options()
        options.owner = ("ken", "group")
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('--owner "ken:group" ', argumentString)

    def testBuildArgumentString_008(self):
        """Test with mode set, validate=False."""
        options = Options()
        options.mode = 0o644
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--mode 644 ", argumentString)

    def testBuildArgumentString_009(self):
        """Test with output set, validate=False."""
        options = Options()
        options.output = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--output ", argumentString)

    def testBuildArgumentString_010(self):
        """Test with debug set, validate=False."""
        options = Options()
        options.debug = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--debug ", argumentString)

    def testBuildArgumentString_011(self):
        """Test with stacktrace set, validate=False."""
        options = Options()
        options.stacktrace = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--stack ", argumentString)

    def testBuildArgumentString_012(self):
        """Test with diagnostics set, validate=False."""
        options = Options()
        options.diagnostics = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--diagnostics ", argumentString)

    def testBuildArgumentString_013(self):
        """Test with verifyOnly set, validate=False."""
        options = Options()
        options.verifyOnly = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--verifyOnly ", argumentString)

    def testBuildArgumentString_014(self):
        """Test with ignoreWarnings set, validate=False."""
        options = Options()
        options.ignoreWarnings = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--ignoreWarnings ", argumentString)

    def testBuildArgumentString_015(self):
        """Test with valid source and target, validate=False."""
        options = Options()
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('"source" "bucket" ', argumentString)

    def testBuildArgumentString_016(self):
        """Test with all values set, actions containing one item, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.verifyOnly = True
        options.ignoreWarnings = True
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual(
            '--help --version --verbose --quiet --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics --verifyOnly --ignoreWarnings "source" "bucket" ',
            argumentString,
        )

    def testBuildArgumentString_017(self):
        """Test with no values set, validate=True."""
        options = Options()
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_018(self):
        """Test with help set, validate=True."""
        options = Options()
        options.help = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--help ", argumentString)

    def testBuildArgumentString_019(self):
        """Test with version set, validate=True."""
        options = Options()
        options.version = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--version ", argumentString)

    def testBuildArgumentString_020(self):
        """Test with verbose set, validate=True."""
        options = Options()
        options.verbose = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_021(self):
        """Test with quiet set, validate=True."""
        options = Options()
        options.quiet = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_022(self):
        """Test with logfile set, validate=True."""
        options = Options()
        options.logfile = "bogus"
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_023(self):
        """Test with owner set, validate=True."""
        options = Options()
        options.owner = ("ken", "group")
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_024(self):
        """Test with mode set, validate=True."""
        options = Options()
        options.mode = 0o644
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_025(self):
        """Test with output set, validate=True."""
        options = Options()
        options.output = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_026(self):
        """Test with debug set, validate=True."""
        options = Options()
        options.debug = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_027(self):
        """Test with stacktrace set, validate=True."""
        options = Options()
        options.stacktrace = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_028(self):
        """Test with diagnostics set, validate=True."""
        options = Options()
        options.diagnostics = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--diagnostics ", argumentString)

    def testBuildArgumentString_029(self):
        """Test with verifyOnly set, validate=True."""
        options = Options()
        options.verifyOnly = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_030(self):
        """Test with ignoreWarnings set, validate=True."""
        options = Options()
        options.ignoreWarnings = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_031(self):
        """Test with valid source and target, validate=True."""
        options = Options()
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual('"source" "bucket" ', argumentString)

    def testBuildArgumentString_032(self):
        """Test with all values set (except managed ones), actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.verifyOnly = True
        options.ignoreWarnings = True
        options.sourceDir = "source"
        options.s3BucketUrl = "bucket"
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual(
            '--help --version --verbose --quiet --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics --verifyOnly --ignoreWarnings "source" "bucket" ',
            argumentString,
        )

    def testBuildArgumentString_033(self):
        """Test with uploadOnly set, validate=False."""
        options = Options()
        options.uploadOnly = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--uploadOnly ", argumentString)
