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
# Copyright (c) 2004-2005,2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests command-line interface functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/cli.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in cli.py.  Where possible, we test functions that
   print output by passing a custom file descriptor.  Sometimes, we only ensure
   that a function or method runs without failure, and we don't validate what
   its result is or what it prints out.

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
   build environment.  There is a no need to use a CLITESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest
from getopt import GetoptError
from os.path import exists, isabs, isdir, isfile, islink

from CedarBackup3.action import executeCollect, executePurge, executeRebuild, executeStage, executeStore, executeValidate
from CedarBackup3.cli import Options, _ActionSet, _diagnostics, _usage, _version
from CedarBackup3.config import (
    ActionDependencies,
    ExtendedAction,
    ExtensionsConfig,
    LocalPeer,
    OptionsConfig,
    PeersConfig,
    PostActionHook,
    PreActionHook,
    RemotePeer,
)
from CedarBackup3.testutil import captureOutput, configureLogging, failUnlessAssignRaises

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

    def testSimpleFuncs_003(self):
        """
        Test that the _diagnostics() function runs without errors.
        We don't care what the output is, and we don't check.
        """
        captureOutput(_diagnostics)


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
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_002(self):
        """
        Test constructor with validate=False, no other arguments.
        """
        options = Options(validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_003(self):
        """
        Test constructor with argumentList=[], validate=False.
        """
        options = Options(argumentList=[], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_004(self):
        """
        Test constructor with argumentString="", validate=False.
        """
        options = Options(argumentString="", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_005(self):
        """
        Test constructor with argumentList=["--help", ], validate=False.
        """
        options = Options(argumentList=["--help"], validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_006(self):
        """
        Test constructor with argumentString="--help", validate=False.
        """
        options = Options(argumentString="--help", validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_007(self):
        """
        Test constructor with argumentList=["-h", ], validate=False.
        """
        options = Options(argumentList=["-h"], validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_008(self):
        """
        Test constructor with argumentString="-h", validate=False.
        """
        options = Options(argumentString="-h", validate=False)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_009(self):
        """
        Test constructor with argumentList=["--version", ], validate=False.
        """
        options = Options(argumentList=["--version"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_010(self):
        """
        Test constructor with argumentString="--version", validate=False.
        """
        options = Options(argumentString="--version", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_011(self):
        """
        Test constructor with argumentList=["-V", ], validate=False.
        """
        options = Options(argumentList=["-V"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_012(self):
        """
        Test constructor with argumentString="-V", validate=False.
        """
        options = Options(argumentString="-V", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_013(self):
        """
        Test constructor with argumentList=["--verbose", ], validate=False.
        """
        options = Options(argumentList=["--verbose"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_014(self):
        """
        Test constructor with argumentString="--verbose", validate=False.
        """
        options = Options(argumentString="--verbose", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_015(self):
        """
        Test constructor with argumentList=["-b", ], validate=False.
        """
        options = Options(argumentList=["-b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_016(self):
        """
        Test constructor with argumentString="-b", validate=False.
        """
        options = Options(argumentString="-b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_017(self):
        """
        Test constructor with argumentList=["--quiet", ], validate=False.
        """
        options = Options(argumentList=["--quiet"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_018(self):
        """
        Test constructor with argumentString="--quiet", validate=False.
        """
        options = Options(argumentString="--quiet", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_019(self):
        """
        Test constructor with argumentList=["-q", ], validate=False.
        """
        options = Options(argumentList=["-q"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_020(self):
        """
        Test constructor with argumentString="-q", validate=False.
        """
        options = Options(argumentString="-q", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(True, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_021(self):
        """
        Test constructor with argumentList=["--config", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--config"], validate=False)

    def testConstructor_022(self):
        """
        Test constructor with argumentString="--config", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--config", validate=False)

    def testConstructor_023(self):
        """
        Test constructor with argumentList=["-c", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-c"], validate=False)

    def testConstructor_024(self):
        """
        Test constructor with argumentString="-c", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-c", validate=False)

    def testConstructor_025(self):
        """
        Test constructor with argumentList=["--config", "something", ], validate=False.
        """
        options = Options(argumentList=["--config", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_026(self):
        """
        Test constructor with argumentString="--config something", validate=False.
        """
        options = Options(argumentString="--config something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_027(self):
        """
        Test constructor with argumentList=["-c", "something", ], validate=False.
        """
        options = Options(argumentList=["-c", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_028(self):
        """
        Test constructor with argumentString="-c something", validate=False.
        """
        options = Options(argumentString="-c something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual("something", options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_029(self):
        """
        Test constructor with argumentList=["--full", ], validate=False.
        """
        options = Options(argumentList=["--full"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(True, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_030(self):
        """
        Test constructor with argumentString="--full", validate=False.
        """
        options = Options(argumentString="--full", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(True, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_031(self):
        """
        Test constructor with argumentList=["-f", ], validate=False.
        """
        options = Options(argumentList=["-f"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(True, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_032(self):
        """
        Test constructor with argumentString="-f", validate=False.
        """
        options = Options(argumentString="-f", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(True, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_033(self):
        """
        Test constructor with argumentList=["--logfile", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--logfile"], validate=False)

    def testConstructor_034(self):
        """
        Test constructor with argumentString="--logfile", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--logfile", validate=False)

    def testConstructor_035(self):
        """
        Test constructor with argumentList=["-l", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-l"], validate=False)

    def testConstructor_036(self):
        """
        Test constructor with argumentString="-l", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-l", validate=False)

    def testConstructor_037(self):
        """
        Test constructor with argumentList=["--logfile", "something", ], validate=False.
        """
        options = Options(argumentList=["--logfile", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_038(self):
        """
        Test constructor with argumentString="--logfile something", validate=False.
        """
        options = Options(argumentString="--logfile something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_039(self):
        """
        Test constructor with argumentList=["-l", "something", ], validate=False.
        """
        options = Options(argumentList=["-l", "something"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_040(self):
        """
        Test constructor with argumentString="-l something", validate=False.
        """
        options = Options(argumentString="-l something", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual("something", options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_041(self):
        """
        Test constructor with argumentList=["--owner", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--owner"], validate=False)

    def testConstructor_042(self):
        """
        Test constructor with argumentString="--owner", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--owner", validate=False)

    def testConstructor_043(self):
        """
        Test constructor with argumentList=["-o", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-o"], validate=False)

    def testConstructor_044(self):
        """
        Test constructor with argumentString="-o", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-o", validate=False)

    def testConstructor_045(self):
        """
        Test constructor with argumentList=["--owner", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "something"], validate=False)

    def testConstructor_046(self):
        """
        Test constructor with argumentString="--owner something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner something", validate=False)

    def testConstructor_047(self):
        """
        Test constructor with argumentList=["-o", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "something"], validate=False)

    def testConstructor_048(self):
        """
        Test constructor with argumentString="-o something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="-o something", validate=False)

    def testConstructor_049(self):
        """
        Test constructor with argumentList=["--owner", "a:b", ], validate=False.
        """
        options = Options(argumentList=["--owner", "a:b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_050(self):
        """
        Test constructor with argumentString="--owner a:b", validate=False.
        """
        options = Options(argumentString="--owner a:b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_051(self):
        """
        Test constructor with argumentList=["-o", "a:b", ], validate=False.
        """
        options = Options(argumentList=["-o", "a:b"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_052(self):
        """
        Test constructor with argumentString="-o a:b", validate=False.
        """
        options = Options(argumentString="-o a:b", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(("a", "b"), options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_053(self):
        """
        Test constructor with argumentList=["--mode", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--mode"], validate=False)

    def testConstructor_054(self):
        """
        Test constructor with argumentString="--mode", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="--mode", validate=False)

    def testConstructor_055(self):
        """
        Test constructor with argumentList=["-m", ], validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-m"], validate=False)

    def testConstructor_056(self):
        """
        Test constructor with argumentString="-m", validate=False.
        """
        self.assertRaises(GetoptError, Options, argumentString="-m", validate=False)

    def testConstructor_057(self):
        """
        Test constructor with argumentList=["--mode", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "something"], validate=False)

    def testConstructor_058(self):
        """
        Test constructor with argumentString="--mode something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode something", validate=False)

    def testConstructor_059(self):
        """
        Test constructor with argumentList=["-m", "something", ], validate=False.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "something"], validate=False)

    def testConstructor_060(self):
        """
        Test constructor with argumentString="-m something", validate=False.
        """
        self.assertRaises(ValueError, Options, argumentString="-m something", validate=False)

    def testConstructor_061(self):
        """
        Test constructor with argumentList=["--mode", "631", ], validate=False.
        """
        options = Options(argumentList=["--mode", "631"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_062(self):
        """
        Test constructor with argumentString="--mode 631", validate=False.
        """
        options = Options(argumentString="--mode 631", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_063(self):
        """
        Test constructor with argumentList=["-m", "631", ], validate=False.
        """
        options = Options(argumentList=["-m", "631"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_064(self):
        """
        Test constructor with argumentString="-m 631", validate=False.
        """
        options = Options(argumentString="-m 631", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o631, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_065(self):
        """
        Test constructor with argumentList=["--output", ], validate=False.
        """
        options = Options(argumentList=["--output"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_066(self):
        """
        Test constructor with argumentString="--output", validate=False.
        """
        options = Options(argumentString="--output", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_067(self):
        """
        Test constructor with argumentList=["-O", ], validate=False.
        """
        options = Options(argumentList=["-O"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_068(self):
        """
        Test constructor with argumentString="-O", validate=False.
        """
        options = Options(argumentString="-O", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_069(self):
        """
        Test constructor with argumentList=["--debug", ], validate=False.
        """
        options = Options(argumentList=["--debug"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_070(self):
        """
        Test constructor with argumentString="--debug", validate=False.
        """
        options = Options(argumentString="--debug", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_071(self):
        """
        Test constructor with argumentList=["-d", ], validate=False.
        """
        options = Options(argumentList=["-d"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_072(self):
        """
        Test constructor with argumentString="-d", validate=False.
        """
        options = Options(argumentString="-d", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_073(self):
        """
        Test constructor with argumentList=["--stack", ], validate=False.
        """
        options = Options(argumentList=["--stack"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_074(self):
        """
        Test constructor with argumentString="--stack", validate=False.
        """
        options = Options(argumentString="--stack", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_075(self):
        """
        Test constructor with argumentList=["-s", ], validate=False.
        """
        options = Options(argumentList=["-s"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual([], options.actions)

    def testConstructor_076(self):
        """
        Test constructor with argumentString="-s", validate=False.
        """
        options = Options(argumentString="-s", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(True, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_077(self):
        """
        Test constructor with argumentList=["all", ], validate=False.
        """
        options = Options(argumentList=["all"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["all"], options.actions)

    def testConstructor_078(self):
        """
        Test constructor with argumentString="all", validate=False.
        """
        options = Options(argumentString="all", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["all"], options.actions)

    def testConstructor_079(self):
        """
        Test constructor with argumentList=["collect", ], validate=False.
        """
        options = Options(argumentList=["collect"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect"], options.actions)

    def testConstructor_080(self):
        """
        Test constructor with argumentString="collect", validate=False.
        """
        options = Options(argumentString="collect", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect"], options.actions)

    def testConstructor_081(self):
        """
        Test constructor with argumentList=["stage", ], validate=False.
        """
        options = Options(argumentList=["stage"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["stage"], options.actions)

    def testConstructor_082(self):
        """
        Test constructor with argumentString="stage", validate=False.
        """
        options = Options(argumentString="stage", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["stage"], options.actions)

    def testConstructor_083(self):
        """
        Test constructor with argumentList=["store", ], validate=False.
        """
        options = Options(argumentList=["store"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["store"], options.actions)

    def testConstructor_084(self):
        """
        Test constructor with argumentString="store", validate=False.
        """
        options = Options(argumentString="store", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["store"], options.actions)

    def testConstructor_085(self):
        """
        Test constructor with argumentList=["purge", ], validate=False.
        """
        options = Options(argumentList=["purge"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["purge"], options.actions)

    def testConstructor_086(self):
        """
        Test constructor with argumentString="purge", validate=False.
        """
        options = Options(argumentString="purge", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["purge"], options.actions)

    def testConstructor_087(self):
        """
        Test constructor with argumentList=["rebuild", ], validate=False.
        """
        options = Options(argumentList=["rebuild"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["rebuild"], options.actions)

    def testConstructor_088(self):
        """
        Test constructor with argumentString="rebuild", validate=False.
        """
        options = Options(argumentString="rebuild", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["rebuild"], options.actions)

    def testConstructor_089(self):
        """
        Test constructor with argumentList=["validate", ], validate=False.
        """
        options = Options(argumentList=["validate"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["validate"], options.actions)

    def testConstructor_090(self):
        """
        Test constructor with argumentString="validate", validate=False.
        """
        options = Options(argumentString="validate", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["validate"], options.actions)

    def testConstructor_091(self):
        """
        Test constructor with argumentList=["collect", "all", ], validate=False.
        """
        options = Options(argumentList=["collect", "all"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "all"], options.actions)

    def testConstructor_092(self):
        """
        Test constructor with argumentString="collect all", validate=False.
        """
        options = Options(argumentString="collect all", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "all"], options.actions)

    def testConstructor_093(self):
        """
        Test constructor with argumentList=["collect", "rebuild", ], validate=False.
        """
        options = Options(argumentList=["collect", "rebuild"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "rebuild"], options.actions)

    def testConstructor_094(self):
        """
        Test constructor with argumentString="collect rebuild", validate=False.
        """
        options = Options(argumentString="collect rebuild", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "rebuild"], options.actions)

    def testConstructor_095(self):
        """
        Test constructor with argumentList=["collect", "validate", ], validate=False.
        """
        options = Options(argumentList=["collect", "validate"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "validate"], options.actions)

    def testConstructor_096(self):
        """
        Test constructor with argumentString="collect validate", validate=False.
        """
        options = Options(argumentString="collect validate", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "validate"], options.actions)

    def testConstructor_097(self):
        """
        Test constructor with argumentList=["-d", "--verbose", "-O", "--mode", "600", "collect", "stage", ], validate=False.
        """
        options = Options(argumentList=["-d", "--verbose", "-O", "--mode", "600", "collect", "stage"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "stage"], options.actions)

    def testConstructor_098(self):
        """
        Test constructor with argumentString="-d --verbose -O --mode 600 collect stage", validate=False.
        """
        options = Options(argumentString="-d --verbose -O --mode 600 collect stage", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "stage"], options.actions)

    def testConstructor_099(self):
        """
        Test constructor with argumentList=[], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=[], validate=True)

    def testConstructor_100(self):
        """
        Test constructor with argumentString="", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="", validate=True)

    def testConstructor_101(self):
        """
        Test constructor with argumentList=["--help", ], validate=True.
        """
        options = Options(argumentList=["--help"], validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_102(self):
        """
        Test constructor with argumentString="--help", validate=True.
        """
        options = Options(argumentString="--help", validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_103(self):
        """
        Test constructor with argumentList=["-h", ], validate=True.
        """
        options = Options(argumentList=["-h"], validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_104(self):
        """
        Test constructor with argumentString="-h", validate=True.
        """
        options = Options(argumentString="-h", validate=True)
        self.assertEqual(True, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_105(self):
        """
        Test constructor with argumentList=["--version", ], validate=True.
        """
        options = Options(argumentList=["--version"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_106(self):
        """
        Test constructor with argumentString="--version", validate=True.
        """
        options = Options(argumentString="--version", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_107(self):
        """
        Test constructor with argumentList=["-V", ], validate=True.
        """
        options = Options(argumentList=["-V"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_108(self):
        """
        Test constructor with argumentString="-V", validate=True.
        """
        options = Options(argumentString="-V", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(True, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_109(self):
        """
        Test constructor with argumentList=["--verbose", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--verbose"], validate=True)

    def testConstructor_110(self):
        """
        Test constructor with argumentString="--verbose", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--verbose", validate=True)

    def testConstructor_111(self):
        """
        Test constructor with argumentList=["-b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-b"], validate=True)

    def testConstructor_112(self):
        """
        Test constructor with argumentString="-b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-b", validate=True)

    def testConstructor_113(self):
        """
        Test constructor with argumentList=["--quiet", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--quiet"], validate=True)

    def testConstructor_114(self):
        """
        Test constructor with argumentString="--quiet", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--quiet", validate=True)

    def testConstructor_115(self):
        """
        Test constructor with argumentList=["-q", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-q"], validate=True)

    def testConstructor_116(self):
        """
        Test constructor with argumentString="-q", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-q", validate=True)

    def testConstructor_117(self):
        """
        Test constructor with argumentList=["--config", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--config"], validate=True)

    def testConstructor_118(self):
        """
        Test constructor with argumentString="--config", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--config", validate=True)

    def testConstructor_119(self):
        """
        Test constructor with argumentList=["-c", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-c"], validate=True)

    def testConstructor_120(self):
        """
        Test constructor with argumentString="-c", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-c", validate=True)

    def testConstructor_121(self):
        """
        Test constructor with argumentList=["--config", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--config", "something"], validate=True)

    def testConstructor_122(self):
        """
        Test constructor with argumentString="--config something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--config something", validate=True)

    def testConstructor_123(self):
        """
        Test constructor with argumentList=["-c", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-c", "something"], validate=True)

    def testConstructor_124(self):
        """
        Test constructor with argumentString="-c something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-c something", validate=True)

    def testConstructor_125(self):
        """
        Test constructor with argumentList=["--full", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--full"], validate=True)

    def testConstructor_126(self):
        """
        Test constructor with argumentString="--full", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--full", validate=True)

    def testConstructor_127(self):
        """
        Test constructor with argumentList=["-f", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-f"], validate=True)

    def testConstructor_128(self):
        """
        Test constructor with argumentString="-f", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-f", validate=True)

    def testConstructor_129(self):
        """
        Test constructor with argumentList=["--logfile", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--logfile"], validate=True)

    def testConstructor_130(self):
        """
        Test constructor with argumentString="--logfile", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--logfile", validate=True)

    def testConstructor_131(self):
        """
        Test constructor with argumentList=["-l", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-l"], validate=True)

    def testConstructor_132(self):
        """
        Test constructor with argumentString="-l", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-l", validate=True)

    def testConstructor_133(self):
        """
        Test constructor with argumentList=["--logfile", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--logfile", "something"], validate=True)

    def testConstructor_134(self):
        """
        Test constructor with argumentString="--logfile something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--logfile something", validate=True)

    def testConstructor_135(self):
        """
        Test constructor with argumentList=["-l", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-l", "something"], validate=True)

    def testConstructor_136(self):
        """
        Test constructor with argumentString="-l something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-l something", validate=True)

    def testConstructor_137(self):
        """
        Test constructor with argumentList=["--owner", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--owner"], validate=True)

    def testConstructor_138(self):
        """
        Test constructor with argumentString="--owner", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--owner", validate=True)

    def testConstructor_139(self):
        """
        Test constructor with argumentList=["-o", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-o"], validate=True)

    def testConstructor_140(self):
        """
        Test constructor with argumentString="-o", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-o", validate=True)

    def testConstructor_141(self):
        """
        Test constructor with argumentList=["--owner", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "something"], validate=True)

    def testConstructor_142(self):
        """
        Test constructor with argumentString="--owner something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner something", validate=True)

    def testConstructor_143(self):
        """
        Test constructor with argumentList=["-o", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "something"], validate=True)

    def testConstructor_144(self):
        """
        Test constructor with argumentString="-o something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-o something", validate=True)

    def testConstructor_145(self):
        """
        Test constructor with argumentList=["--owner", "a:b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--owner", "a:b"], validate=True)

    def testConstructor_146(self):
        """
        Test constructor with argumentString="--owner a:b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--owner a:b", validate=True)

    def testConstructor_147(self):
        """
        Test constructor with argumentList=["-o", "a:b", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-o", "a:b"], validate=True)

    def testConstructor_148(self):
        """
        Test constructor with argumentString="-o a:b", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-o a:b", validate=True)

    def testConstructor_149(self):
        """
        Test constructor with argumentList=["--mode", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["--mode"], validate=True)

    def testConstructor_150(self):
        """
        Test constructor with argumentString="--mode", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="--mode", validate=True)

    def testConstructor_151(self):
        """
        Test constructor with argumentList=["-m", ], validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentList=["-m"], validate=True)

    def testConstructor_152(self):
        """
        Test constructor with argumentString="-m", validate=True.
        """
        self.assertRaises(GetoptError, Options, argumentString="-m", validate=True)

    def testConstructor_153(self):
        """
        Test constructor with argumentList=["--mode", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "something"], validate=True)

    def testConstructor_154(self):
        """
        Test constructor with argumentString="--mode something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode something", validate=True)

    def testConstructor_155(self):
        """
        Test constructor with argumentList=["-m", "something", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "something"], validate=True)

    def testConstructor_156(self):
        """
        Test constructor with argumentString="-m something", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-m something", validate=True)

    def testConstructor_157(self):
        """
        Test constructor with argumentList=["--mode", "631", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--mode", "631"], validate=True)

    def testConstructor_158(self):
        """
        Test constructor with argumentString="--mode 631", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--mode 631", validate=True)

    def testConstructor_159(self):
        """
        Test constructor with argumentList=["-m", "631", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-m", "631"], validate=True)

    def testConstructor_160(self):
        """
        Test constructor with argumentString="-m 631", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-m 631", validate=True)

    def testConstructor_161(self):
        """
        Test constructor with argumentList=["--output", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--output"], validate=True)

    def testConstructor_162(self):
        """
        Test constructor with argumentString="--output", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--output", validate=True)

    def testConstructor_163(self):
        """
        Test constructor with argumentList=["-O", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-O"], validate=True)

    def testConstructor_164(self):
        """
        Test constructor with argumentString="-O", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-O", validate=True)

    def testConstructor_165(self):
        """
        Test constructor with argumentList=["--debug", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--debug"], validate=True)

    def testConstructor_166(self):
        """
        Test constructor with argumentString="--debug", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--debug", validate=True)

    def testConstructor_167(self):
        """
        Test constructor with argumentList=["-d", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-d"], validate=True)

    def testConstructor_168(self):
        """
        Test constructor with argumentString="-d", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-d", validate=True)

    def testConstructor_169(self):
        """
        Test constructor with argumentList=["--stack", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--stack"], validate=True)

    def testConstructor_170(self):
        """
        Test constructor with argumentString="--stack", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--stack", validate=True)

    def testConstructor_171(self):
        """
        Test constructor with argumentList=["-s", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-s"], validate=True)

    def testConstructor_172(self):
        """
        Test constructor with argumentString="-s", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-s", validate=True)

    def testConstructor_173(self):
        """
        Test constructor with argumentList=["all", ], validate=True.
        """
        options = Options(argumentList=["all"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["all"], options.actions)

    def testConstructor_174(self):
        """
        Test constructor with argumentString="all", validate=True.
        """
        options = Options(argumentString="all", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["all"], options.actions)

    def testConstructor_175(self):
        """
        Test constructor with argumentList=["collect", ], validate=True.
        """
        options = Options(argumentList=["collect"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect"], options.actions)

    def testConstructor_176(self):
        """
        Test constructor with argumentString="collect", validate=True.
        """
        options = Options(argumentString="collect", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect"], options.actions)

    def testConstructor_177(self):
        """
        Test constructor with argumentList=["stage", ], validate=True.
        """
        options = Options(argumentList=["stage"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["stage"], options.actions)

    def testConstructor_178(self):
        """
        Test constructor with argumentString="stage", validate=True.
        """
        options = Options(argumentString="stage", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["stage"], options.actions)

    def testConstructor_179(self):
        """
        Test constructor with argumentList=["store", ], validate=True.
        """
        options = Options(argumentList=["store"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["store"], options.actions)

    def testConstructor_180(self):
        """
        Test constructor with argumentString="store", validate=True.
        """
        options = Options(argumentString="store", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["store"], options.actions)

    def testConstructor_181(self):
        """
        Test constructor with argumentList=["purge", ], validate=True.
        """
        options = Options(argumentList=["purge"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["purge"], options.actions)

    def testConstructor_182(self):
        """
        Test constructor with argumentString="purge", validate=True.
        """
        options = Options(argumentString="purge", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["purge"], options.actions)

    def testConstructor_183(self):
        """
        Test constructor with argumentList=["rebuild", ], validate=True.
        """
        options = Options(argumentList=["rebuild"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["rebuild"], options.actions)

    def testConstructor_184(self):
        """
        Test constructor with argumentString="rebuild", validate=True.
        """
        options = Options(argumentString="rebuild", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["rebuild"], options.actions)

    def testConstructor_185(self):
        """
        Test constructor with argumentList=["validate", ], validate=True.
        """
        options = Options(argumentList=["validate"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["validate"], options.actions)

    def testConstructor_186(self):
        """
        Test constructor with argumentString="validate", validate=True.
        """
        options = Options(argumentString="validate", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["validate"], options.actions)

    def testConstructor_187(self):
        """
        Test constructor with argumentList=["-d", "--verbose", "-O", "--mode", "600", "collect", "stage", ], validate=True.
        """
        options = Options(argumentList=["-d", "--verbose", "-O", "--mode", "600", "collect", "stage"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "stage"], options.actions)

    def testConstructor_188(self):
        """
        Test constructor with argumentString="-d --verbose -O --mode 600 collect stage", validate=True.
        """
        options = Options(argumentString="-d --verbose -O --mode 600 collect stage", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(True, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(0o600, options.mode)
        self.assertEqual(True, options.output)
        self.assertEqual(True, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual(["collect", "stage"], options.actions)

    def testConstructor_189(self):
        """
        Test constructor with argumentList=["--managed", ], validate=False.
        """
        options = Options(argumentList=["--managed"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(True, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_190(self):
        """
        Test constructor with argumentString="--managed", validate=False.
        """
        options = Options(argumentString="--managed", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(True, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_191(self):
        """
        Test constructor with argumentList=["-M", ], validate=False.
        """
        options = Options(argumentList=["-M"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(True, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_192(self):
        """
        Test constructor with argumentString="-M", validate=False.
        """
        options = Options(argumentString="-M", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(True, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_193(self):
        """
        Test constructor with argumentList=["--managed-only", ], validate=False.
        """
        options = Options(argumentList=["--managed-only"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(True, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_194(self):
        """
        Test constructor with argumentString="--managed-only", validate=False.
        """
        options = Options(argumentString="--managed-only", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(True, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_195(self):
        """
        Test constructor with argumentList=["-N", ], validate=False.
        """
        options = Options(argumentList=["-N"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(True, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_196(self):
        """
        Test constructor with argumentString="-N", validate=False.
        """
        options = Options(argumentString="-N", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(True, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(False, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_197(self):
        """
        Test constructor with argumentList=["--managed", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--managed"], validate=True)

    def testConstructor_198(self):
        """
        Test constructor with argumentString="--managed", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--managed", validate=True)

    def testConstructor_199(self):
        """
        Test constructor with argumentList=["-M", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-M"], validate=True)

    def testConstructor_200(self):
        """
        Test constructor with argumentString="-M", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-M", validate=True)

    def testConstructor_201(self):
        """
        Test constructor with argumentList=["--managed-only", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["--managed-only"], validate=True)

    def testConstructor_202(self):
        """
        Test constructor with argumentString="--managed-only", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="--managed-only", validate=True)

    def testConstructor_203(self):
        """
        Test constructor with argumentList=["-N", ], validate=True.
        """
        self.assertRaises(ValueError, Options, argumentList=["-N"], validate=True)

    def testConstructor_204(self):
        """
        Test constructor with argumentString="-N", validate=True.
        """
        self.assertRaises(ValueError, Options, argumentString="-N", validate=True)

    def testConstructor_205(self):
        """
        Test constructor with argumentList=["--diagnostics", ], validate=False.
        """
        options = Options(argumentList=["--diagnostics"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_206(self):
        """
        Test constructor with argumentString="--diagnostics", validate=False.
        """
        options = Options(argumentString="--diagnostics", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_207(self):
        """
        Test constructor with argumentList=["-D", ], validate=False.
        """
        options = Options(argumentList=["-D"], validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_208(self):
        """
        Test constructor with argumentString="-D", validate=False.
        """
        options = Options(argumentString="-D", validate=False)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_209(self):
        """
        Test constructor with argumentList=["--diagnostics", ], validate=True.
        """
        options = Options(argumentList=["--diagnostics"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_210(self):
        """
        Test constructor with argumentString="--diagnostics", validate=True.
        """
        options = Options(argumentString="--diagnostics", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_211(self):
        """
        Test constructor with argumentList=["-D", ], validate=True.
        """
        options = Options(argumentList=["-D"], validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

    def testConstructor_212(self):
        """
        Test constructor with argumentString="-D", validate=True.
        """
        options = Options(argumentString="-D", validate=True)
        self.assertEqual(False, options.help)
        self.assertEqual(False, options.version)
        self.assertEqual(False, options.verbose)
        self.assertEqual(False, options.quiet)
        self.assertEqual(None, options.config)
        self.assertEqual(False, options.full)
        self.assertEqual(False, options.managed)
        self.assertEqual(False, options.managedOnly)
        self.assertEqual(None, options.logfile)
        self.assertEqual(None, options.owner)
        self.assertEqual(None, options.mode)
        self.assertEqual(False, options.output)
        self.assertEqual(False, options.debug)
        self.assertEqual(False, options.stacktrace)
        self.assertEqual(True, options.diagnostics)
        self.assertEqual([], options.actions)

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
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

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

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = False
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
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
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

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
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

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
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = False
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_007(self):
        """
        Test comparison of two identical objects, all attributes filled in, config different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "whatever"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_008(self):
        """
        Test comparison of two identical objects, all attributes filled in, full different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = False
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_009(self):
        """
        Test comparison of two identical objects, all attributes filled in, logfile different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "stuff"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_010(self):
        """
        Test comparison of two identical objects, all attributes filled in, owner different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("c", "d")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_011(self):
        """
        Test comparison of two identical objects, all attributes filled in, mode different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = 0o600
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_012(self):
        """
        Test comparison of two identical objects, all attributes filled in, output different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = False
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_013(self):
        """
        Test comparison of two identical objects, all attributes filled in, debug different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = False
        options1.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(not options1 < options2)
        self.assertTrue(not options1 <= options2)
        self.assertTrue(options1 > options2)
        self.assertTrue(options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_014(self):
        """
        Test comparison of two identical objects, all attributes filled in, stacktrace different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = True
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_015(self):
        """
        Test comparison of two identical objects, all attributes filled in, managed different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = False
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_016(self):
        """
        Test comparison of two identical objects, all attributes filled in, managedOnly different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = False
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = "631"
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = False
        options2.actions = [
            "collect",
        ]

        self.assertNotEqual(options1, options2)
        self.assertTrue(not options1 == options2)
        self.assertTrue(options1 < options2)
        self.assertTrue(options1 <= options2)
        self.assertTrue(not options1 > options2)
        self.assertTrue(not options1 >= options2)
        self.assertTrue(options1 != options2)

    def testComparison_017(self):
        """
        Test comparison of two identical objects, all attributes filled in, diagnostics different.
        """
        options1 = Options()
        options2 = Options()

        options1.help = True
        options1.version = True
        options1.verbose = True
        options1.quiet = True
        options1.config = "config"
        options1.full = True
        options1.managed = True
        options1.managedOnly = True
        options1.logfile = "logfile"
        options1.owner = ("a", "b")
        options1.mode = 0o631
        options1.output = True
        options1.debug = True
        options1.stacktrace = False
        options1.diagnostics = False
        options1.actions = [
            "collect",
        ]

        options2.help = True
        options2.version = True
        options2.verbose = True
        options2.quiet = True
        options2.config = "config"
        options2.full = True
        options2.managed = True
        options2.managedOnly = True
        options2.logfile = "logfile"
        options2.owner = ("a", "b")
        options2.mode = 0o631
        options2.output = True
        options2.debug = True
        options2.stacktrace = False
        options2.diagnostics = True
        options2.actions = [
            "collect",
        ]

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
        """Test with config set, validate=False."""
        options = Options()
        options.config = "stuff"
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--config", "stuff"], argumentList)

    def testBuildArgumentList_007(self):
        """Test with full set, validate=False."""
        options = Options()
        options.full = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--full"], argumentList)

    def testBuildArgumentList_008(self):
        """Test with logfile set, validate=False."""
        options = Options()
        options.logfile = "bogus"
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--logfile", "bogus"], argumentList)

    def testBuildArgumentList_009(self):
        """Test with owner set, validate=False."""
        options = Options()
        options.owner = ("ken", "group")
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--owner", "ken:group"], argumentList)

    def testBuildArgumentList_010(self):
        """Test with mode set, validate=False."""
        options = Options()
        options.mode = 0o644
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--mode", "644"], argumentList)

    def testBuildArgumentList_011(self):
        """Test with output set, validate=False."""
        options = Options()
        options.output = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--output"], argumentList)

    def testBuildArgumentList_012(self):
        """Test with debug set, validate=False."""
        options = Options()
        options.debug = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--debug"], argumentList)

    def testBuildArgumentList_013(self):
        """Test with stacktrace set, validate=False."""
        options = Options()
        options.stacktrace = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--stack"], argumentList)

    def testBuildArgumentList_014(self):
        """Test with actions containing one item, validate=False."""
        options = Options()
        options.actions = [
            "collect",
        ]
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["collect"], argumentList)

    def testBuildArgumentList_015(self):
        """Test with actions containing multiple items, validate=False."""
        options = Options()
        options.actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["collect", "stage", "store", "purge"], argumentList)

    def testBuildArgumentList_016(self):
        """Test with all values set, actions containing one item, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--config",
                "config",
                "--full",
                "--managed",
                "--managed-only",
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
                "collect",
            ],
            argumentList,
        )

    def testBuildArgumentList_017(self):
        """Test with all values set, actions containing multiple items, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--config",
                "config",
                "--full",
                "--managed",
                "--managed-only",
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
                "collect",
                "stage",
            ],
            argumentList,
        )

    def testBuildArgumentList_018(self):
        """Test with no values set, validate=True."""
        options = Options()
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_019(self):
        """Test with help set, validate=True."""
        options = Options()
        options.help = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--help"], argumentList)

    def testBuildArgumentList_020(self):
        """Test with version set, validate=True."""
        options = Options()
        options.version = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--version"], argumentList)

    def testBuildArgumentList_021(self):
        """Test with verbose set, validate=True."""
        options = Options()
        options.verbose = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_022(self):
        """Test with quiet set, validate=True."""
        options = Options()
        options.quiet = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_023(self):
        """Test with config set, validate=True."""
        options = Options()
        options.config = "stuff"
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_024(self):
        """Test with full set, validate=True."""
        options = Options()
        options.full = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_025(self):
        """Test with logfile set, validate=True."""
        options = Options()
        options.logfile = "bogus"
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_026(self):
        """Test with owner set, validate=True."""
        options = Options()
        options.owner = ("ken", "group")
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_027(self):
        """Test with mode set, validate=True."""
        options = Options()
        options.mode = 0o644
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_028(self):
        """Test with output set, validate=True."""
        options = Options()
        options.output = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_029(self):
        """Test with debug set, validate=True."""
        options = Options()
        options.debug = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_030(self):
        """Test with stacktrace set, validate=True."""
        options = Options()
        options.stacktrace = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_031(self):
        """Test with actions containing one item, validate=True."""
        options = Options()
        options.actions = [
            "collect",
        ]
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["collect"], argumentList)

    def testBuildArgumentList_032(self):
        """Test with actions containing multiple items, validate=True."""
        options = Options()
        options.actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["collect", "stage", "store", "purge"], argumentList)

    def testBuildArgumentList_033(self):
        """Test with all values set (except managed ones), actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--config",
                "config",
                "--full",
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
                "collect",
            ],
            argumentList,
        )

    def testBuildArgumentList_034(self):
        """Test with all values set (except managed ones), actions containing multiple items, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(
            [
                "--help",
                "--version",
                "--verbose",
                "--quiet",
                "--config",
                "config",
                "--full",
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
                "collect",
                "stage",
            ],
            argumentList,
        )

    def testBuildArgumentList_035(self):
        """Test with managed set, validate=False."""
        options = Options()
        options.managed = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--managed"], argumentList)

    def testBuildArgumentList_036(self):
        """Test with managed set, validate=True."""
        options = Options()
        options.managed = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_037(self):
        """Test with managedOnly set, validate=False."""
        options = Options()
        options.managedOnly = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--managed-only"], argumentList)

    def testBuildArgumentList_038(self):
        """Test with managedOnly set, validate=True."""
        options = Options()
        options.managedOnly = True
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_039(self):
        """Test with all values set, actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_040(self):
        """Test with all values set, actions containing multiple items, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        self.assertRaises(ValueError, options.buildArgumentList, validate=True)

    def testBuildArgumentList_041(self):
        """Test with diagnostics set, validate=False."""
        options = Options()
        options.diagnostics = True
        argumentList = options.buildArgumentList(validate=False)
        self.assertEqual(["--diagnostics"], argumentList)

    def testBuildArgumentList_042(self):
        """Test with diagnostics set, validate=True."""
        options = Options()
        options.diagnostics = True
        argumentList = options.buildArgumentList(validate=True)
        self.assertEqual(["--diagnostics"], argumentList)

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
        """Test with config set, validate=False."""
        options = Options()
        options.config = "stuff"
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('--config "stuff" ', argumentString)

    def testBuildArgumentString_007(self):
        """Test with full set, validate=False."""
        options = Options()
        options.full = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--full ", argumentString)

    def testBuildArgumentString_008(self):
        """Test with logfile set, validate=False."""
        options = Options()
        options.logfile = "bogus"
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('--logfile "bogus" ', argumentString)

    def testBuildArgumentString_009(self):
        """Test with owner set, validate=False."""
        options = Options()
        options.owner = ("ken", "group")
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('--owner "ken:group" ', argumentString)

    def testBuildArgumentString_010(self):
        """Test with mode set, validate=False."""
        options = Options()
        options.mode = 0o644
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--mode 644 ", argumentString)

    def testBuildArgumentString_011(self):
        """Test with output set, validate=False."""
        options = Options()
        options.output = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--output ", argumentString)

    def testBuildArgumentString_012(self):
        """Test with debug set, validate=False."""
        options = Options()
        options.debug = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--debug ", argumentString)

    def testBuildArgumentString_013(self):
        """Test with stacktrace set, validate=False."""
        options = Options()
        options.stacktrace = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--stack ", argumentString)

    def testBuildArgumentString_014(self):
        """Test with actions containing one item, validate=False."""
        options = Options()
        options.actions = [
            "collect",
        ]
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('"collect" ', argumentString)

    def testBuildArgumentString_015(self):
        """Test with actions containing multiple items, validate=False."""
        options = Options()
        options.actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual('"collect" "stage" "store" "purge" ', argumentString)

    def testBuildArgumentString_016(self):
        """Test with all values set, actions containing one item, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual(
            '--help --version --verbose --quiet --config "config" --full --managed --managed-only --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics "collect" ',
            argumentString,
        )

    def testBuildArgumentString_017(self):
        """Test with all values set, actions containing multiple items, validate=False."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual(
            '--help --version --verbose --quiet --config "config" --full --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics "collect" "stage" ',
            argumentString,
        )

    def testBuildArgumentString_018(self):
        """Test with no values set, validate=True."""
        options = Options()
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_019(self):
        """Test with help set, validate=True."""
        options = Options()
        options.help = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--help ", argumentString)

    def testBuildArgumentString_020(self):
        """Test with version set, validate=True."""
        options = Options()
        options.version = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--version ", argumentString)

    def testBuildArgumentString_021(self):
        """Test with verbose set, validate=True."""
        options = Options()
        options.verbose = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_022(self):
        """Test with quiet set, validate=True."""
        options = Options()
        options.quiet = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_023(self):
        """Test with config set, validate=True."""
        options = Options()
        options.config = "stuff"
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_024(self):
        """Test with full set, validate=True."""
        options = Options()
        options.full = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_025(self):
        """Test with logfile set, validate=True."""
        options = Options()
        options.logfile = "bogus"
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_026(self):
        """Test with owner set, validate=True."""
        options = Options()
        options.owner = ("ken", "group")
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_027(self):
        """Test with mode set, validate=True."""
        options = Options()
        options.mode = 0o644
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_028(self):
        """Test with output set, validate=True."""
        options = Options()
        options.output = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_029(self):
        """Test with debug set, validate=True."""
        options = Options()
        options.debug = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_030(self):
        """Test with stacktrace set, validate=True."""
        options = Options()
        options.stacktrace = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_031(self):
        """Test with actions containing one item, validate=True."""
        options = Options()
        options.actions = [
            "collect",
        ]
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual('"collect" ', argumentString)

    def testBuildArgumentString_032(self):
        """Test with actions containing multiple items, validate=True."""
        options = Options()
        options.actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual('"collect" "stage" "store" "purge" ', argumentString)

    def testBuildArgumentString_033(self):
        """Test with all values set (except managed ones), actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual(
            '--help --version --verbose --quiet --config "config" --full --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics "collect" ',
            argumentString,
        )

    def testBuildArgumentString_034(self):
        """Test with all values set (except managed ones), actions containing multiple items, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual(
            '--help --version --verbose --quiet --config "config" --full --logfile "logfile" --owner "a:b" --mode 631 --output --debug --stack --diagnostics "collect" "stage" ',
            argumentString,
        )

    def testBuildArgumentString_035(self):
        """Test with managed set, validate=False."""
        options = Options()
        options.managed = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--managed ", argumentString)

    def testBuildArgumentString_036(self):
        """Test with managed set, validate=True."""
        options = Options()
        options.managed = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_037(self):
        """Test with full set, validate=False."""
        options = Options()
        options.managedOnly = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--managed-only ", argumentString)

    def testBuildArgumentString_038(self):
        """Test with managedOnly set, validate=True."""
        options = Options()
        options.managedOnly = True
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_039(self):
        """Test with all values set (except managed ones), actions containing one item, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
        ]
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_040(self):
        """Test with all values set (except managed ones), actions containing multiple items, validate=True."""
        options = Options()
        options.help = True
        options.version = True
        options.verbose = True
        options.quiet = True
        options.config = "config"
        options.full = True
        options.managed = True
        options.managedOnly = True
        options.logfile = "logfile"
        options.owner = ("a", "b")
        options.mode = "631"
        options.output = True
        options.debug = True
        options.stacktrace = True
        options.diagnostics = True
        options.actions = [
            "collect",
            "stage",
        ]
        self.assertRaises(ValueError, options.buildArgumentString, validate=True)

    def testBuildArgumentString_041(self):
        """Test with diagnostics set, validate=False."""
        options = Options()
        options.diagnostics = True
        argumentString = options.buildArgumentString(validate=False)
        self.assertEqual("--diagnostics ", argumentString)

    def testBuildArgumentString_042(self):
        """Test with diagnostics set, validate=True."""
        options = Options()
        options.diagnostics = True
        argumentString = options.buildArgumentString(validate=True)
        self.assertEqual("--diagnostics ", argumentString)


######################
# TestActionSet class
######################


class TestActionSet(unittest.TestCase):

    """Tests for the _ActionSet class."""

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

    #######################################
    # Test constructor, "index" order mode
    #######################################

    def testActionSet_001(self):
        """
        Test with actions=None, extensions=None.
        """
        actions = None
        extensions = ExtensionsConfig(None, None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_002(self):
        """
        Test with actions=[], extensions=None.
        """
        actions = []
        extensions = ExtensionsConfig(None, None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_003(self):
        """
        Test with actions=[], extensions=[].
        """
        actions = []
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_004(self):
        """
        Test with actions=[ collect ], extensions=[].
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_005(self):
        """
        Test with actions=[ stage ], extensions=[].
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testActionSet_006(self):
        """
        Test with actions=[ store ], extensions=[].
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testActionSet_007(self):
        """
        Test with actions=[ purge ], extensions=[].
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)

    def testActionSet_008(self):
        """
        Test with actions=[ all ], extensions=[].
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testActionSet_009(self):
        """
        Test with actions=[ rebuild ], extensions=[].
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("rebuild", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeRebuild, actionSet.actionSet[0].function)

    def testActionSet_010(self):
        """
        Test with actions=[ validate ], extensions=[].
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("validate", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeValidate, actionSet.actionSet[0].function)

    def testActionSet_011(self):
        """
        Test with actions=[ collect, collect ], extensions=[].
        """
        actions = [
            "collect",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_012(self):
        """
        Test with actions=[ collect, stage ], extensions=[].
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testActionSet_013(self):
        """
        Test with actions=[ collect, store ], extensions=[].
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_014(self):
        """
        Test with actions=[ collect, purge ], extensions=[].
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_015(self):
        """
        Test with actions=[ collect, all ], extensions=[].
        """
        actions = [
            "collect",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_016(self):
        """
        Test with actions=[ collect, rebuild ], extensions=[].
        """
        actions = [
            "collect",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_017(self):
        """
        Test with actions=[ collect, validate ], extensions=[].
        """
        actions = [
            "collect",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_018(self):
        """
        Test with actions=[ stage, collect ], extensions=[].
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testActionSet_019(self):
        """
        Test with actions=[ stage, stage ], extensions=[].
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testActionSet_020(self):
        """
        Test with actions=[ stage, store ], extensions=[].
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_021(self):
        """
        Test with actions=[ stage, purge ], extensions=[].
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_022(self):
        """
        Test with actions=[ stage, all ], extensions=[].
        """
        actions = [
            "stage",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_023(self):
        """
        Test with actions=[ stage, rebuild ], extensions=[].
        """
        actions = [
            "stage",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_024(self):
        """
        Test with actions=[ stage, validate ], extensions=[].
        """
        actions = [
            "stage",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_025(self):
        """
        Test with actions=[ store, collect ], extensions=[].
        """
        actions = [
            "store",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_026(self):
        """
        Test with actions=[ store, stage ], extensions=[].
        """
        actions = [
            "store",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_027(self):
        """
        Test with actions=[ store, store ], extensions=[].
        """
        actions = [
            "store",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_028(self):
        """
        Test with actions=[ store, purge ], extensions=[].
        """
        actions = [
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_029(self):
        """
        Test with actions=[ store, all ], extensions=[].
        """
        actions = [
            "store",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_030(self):
        """
        Test with actions=[ store, rebuild ], extensions=[].
        """
        actions = [
            "store",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_031(self):
        """
        Test with actions=[ store, validate ], extensions=[].
        """
        actions = [
            "store",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_032(self):
        """
        Test with actions=[ purge, collect ], extensions=[].
        """
        actions = [
            "purge",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_033(self):
        """
        Test with actions=[ purge, stage ], extensions=[].
        """
        actions = [
            "purge",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_034(self):
        """
        Test with actions=[ purge, store ], extensions=[].
        """
        actions = [
            "purge",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_035(self):
        """
        Test with actions=[ purge, purge ], extensions=[].
        """
        actions = [
            "purge",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_036(self):
        """
        Test with actions=[ purge, all ], extensions=[].
        """
        actions = [
            "purge",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_037(self):
        """
        Test with actions=[ purge, rebuild ], extensions=[].
        """
        actions = [
            "purge",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_038(self):
        """
        Test with actions=[ purge, validate ], extensions=[].
        """
        actions = [
            "purge",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_039(self):
        """
        Test with actions=[ all, collect ], extensions=[].
        """
        actions = [
            "all",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_040(self):
        """
        Test with actions=[ all, stage ], extensions=[].
        """
        actions = [
            "all",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_041(self):
        """
        Test with actions=[ all, store ], extensions=[].
        """
        actions = [
            "all",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_042(self):
        """
        Test with actions=[ all, purge ], extensions=[].
        """
        actions = [
            "all",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_043(self):
        """
        Test with actions=[ all, all ], extensions=[].
        """
        actions = [
            "all",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_044(self):
        """
        Test with actions=[ all, rebuild ], extensions=[].
        """
        actions = [
            "all",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_045(self):
        """
        Test with actions=[ all, validate ], extensions=[].
        """
        actions = [
            "all",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_046(self):
        """
        Test with actions=[ rebuild, collect ], extensions=[].
        """
        actions = [
            "rebuild",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_047(self):
        """
        Test with actions=[ rebuild, stage ], extensions=[].
        """
        actions = [
            "rebuild",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_048(self):
        """
        Test with actions=[ rebuild, store ], extensions=[].
        """
        actions = [
            "rebuild",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_049(self):
        """
        Test with actions=[ rebuild, purge ], extensions=[].
        """
        actions = [
            "rebuild",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_050(self):
        """
        Test with actions=[ rebuild, all ], extensions=[].
        """
        actions = [
            "rebuild",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_051(self):
        """
        Test with actions=[ rebuild, rebuild ], extensions=[].
        """
        actions = [
            "rebuild",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_052(self):
        """
        Test with actions=[ rebuild, validate ], extensions=[].
        """
        actions = [
            "rebuild",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_053(self):
        """
        Test with actions=[ validate, collect ], extensions=[].
        """
        actions = [
            "validate",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_054(self):
        """
        Test with actions=[ validate, stage ], extensions=[].
        """
        actions = [
            "validate",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_055(self):
        """
        Test with actions=[ validate, store ], extensions=[].
        """
        actions = [
            "validate",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_056(self):
        """
        Test with actions=[ validate, purge ], extensions=[].
        """
        actions = [
            "validate",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_057(self):
        """
        Test with actions=[ validate, all ], extensions=[].
        """
        actions = [
            "validate",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_058(self):
        """
        Test with actions=[ validate, rebuild ], extensions=[].
        """
        actions = [
            "validate",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_059(self):
        """
        Test with actions=[ validate, validate ], extensions=[].
        """
        actions = [
            "validate",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_060(self):
        """
        Test with actions=[ bogus ], extensions=[].
        """
        actions = [
            "bogus",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_061(self):
        """
        Test with actions=[ bogus, collect ], extensions=[].
        """
        actions = [
            "bogus",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_062(self):
        """
        Test with actions=[ bogus, stage ], extensions=[].
        """
        actions = [
            "bogus",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_063(self):
        """
        Test with actions=[ bogus, store ], extensions=[].
        """
        actions = [
            "bogus",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_064(self):
        """
        Test with actions=[ bogus, purge ], extensions=[].
        """
        actions = [
            "bogus",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_065(self):
        """
        Test with actions=[ bogus, all ], extensions=[].
        """
        actions = [
            "bogus",
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_066(self):
        """
        Test with actions=[ bogus, rebuild ], extensions=[].
        """
        actions = [
            "bogus",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_067(self):
        """
        Test with actions=[ bogus, validate ], extensions=[].
        """
        actions = [
            "bogus",
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_068(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_069(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testActionSet_070(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_071(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "purge",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_072(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "all",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_073(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_074(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "validate",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_075(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_076(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testActionSet_077(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_078(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "purge",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_079(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "all",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_080(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_081(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, index 150) ].
        """
        actions = [
            "validate",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_082(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(250, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_083(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(250, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_084(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(250, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testActionSet_085(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "purge",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(250, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_086(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "all",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_087(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_088(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, index 250) ].
        """
        actions = [
            "validate",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 250)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_089(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(350, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_090(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(350, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_091(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(350, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_092(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "purge",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(350, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testActionSet_093(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "all",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_094(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_095(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, index 350) ].
        """
        actions = [
            "validate",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 350)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_096(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(450, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_097(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(450, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_098(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(450, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_099(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "purge",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)
        self.assertEqual(450, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_100(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "all",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_101(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_102(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "validate",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testActionSet_103(self):
        """
        Test with actions=[ one, one ], extensions=[ (one, index 450) ].
        """
        actions = [
            "one",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 450)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(450, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(450, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testActionSet_104(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[].
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testActionSet_105(self):
        """
        Test with actions=[ stage, purge, collect, store ], extensions=[].
        """
        actions = [
            "stage",
            "purge",
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testActionSet_106(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four, five ], extensions=[ (index 50, 150, 250, 350, 450)].
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual(150, actionSet.actionSet[2].index)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual(200, actionSet.actionSet[3].index)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual(250, actionSet.actionSet[4].index)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual(300, actionSet.actionSet[5].index)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual(350, actionSet.actionSet[6].index)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(None, actionSet.actionSet[6].preHooks)
        self.assertEqual(None, actionSet.actionSet[6].postHooks)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual(400, actionSet.actionSet[7].index)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual(450, actionSet.actionSet[8].index)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(None, actionSet.actionSet[8].preHooks)
        self.assertEqual(None, actionSet.actionSet[8].postHooks)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testActionSet_107(self):
        """
        Test with actions=[ one, five, collect, store, three, stage, four, purge, two ], extensions=[ (index 50, 150, 250, 350, 450)].
        """
        actions = [
            "one",
            "five",
            "collect",
            "store",
            "three",
            "stage",
            "four",
            "purge",
            "two",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual(150, actionSet.actionSet[2].index)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual(200, actionSet.actionSet[3].index)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual(250, actionSet.actionSet[4].index)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual(300, actionSet.actionSet[5].index)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual(350, actionSet.actionSet[6].index)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(None, actionSet.actionSet[6].preHooks)
        self.assertEqual(None, actionSet.actionSet[6].postHooks)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual(400, actionSet.actionSet[7].index)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual(450, actionSet.actionSet[8].index)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(None, actionSet.actionSet[8].preHooks)
        self.assertEqual(None, actionSet.actionSet[8].postHooks)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testActionSet_108(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ].
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_109(self):
        """
        Test with actions=[ collect ], extensions=[], hooks=[]
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_110(self):
        """
        Test with actions=[ collect ], extensions=[], pre-hook on 'stage' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = [PreActionHook("stage", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_111(self):
        """
        Test with actions=[ collect ], extensions=[], post-hook on 'stage' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = [PostActionHook("stage", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_112(self):
        """
        Test with actions=[ collect ], extensions=[], pre-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = [PreActionHook("collect", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("collect", "something")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_113(self):
        """
        Test with actions=[ collect ], extensions=[], post-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = [PostActionHook("collect", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("collect", "something")], actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_114(self):
        """
        Test with actions=[ collect ], extensions=[], pre- and post-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.hooks = [PreActionHook("collect", "something1"), PostActionHook("collect", "something2")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("collect", "something1")], actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("collect", "something2")], actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testActionSet_115(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], hooks=[]
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_116(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], pre-hook on "store" action.
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("store", "whatever"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_117(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], post-hook on "store" action.
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("store", "whatever"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_118(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], pre-hook on "one" action.
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_119(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], post-hook on "one" action.
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_120(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], pre- and post-hook on "one" action.
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension2"),
            PreActionHook("one", "extension1"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension1")], actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension2")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testActionSet_121(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], hooks=[]
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_122(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], pre-hook on "purge" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("purge", "rm -f"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_123(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], post-hook on "purge" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("purge", "rm -f"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_124(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], pre-hook on "collect" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("collect", "something"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual([PreActionHook("collect", "something")], actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_125(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], post-hook on "collect" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("collect", "something"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual([PostActionHook("collect", "something")], actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_126(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], pre-hook on "one" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_127(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], post-hook on "one" action
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_128(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ], set of various pre- and post hooks.
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
            PreActionHook("collect", "something1"),
            PreActionHook("collect", "something2"),
            PostActionHook("stage", "whatever1"),
            PostActionHook("stage", "whatever2"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(
            [PreActionHook("collect", "something1"), PreActionHook("collect", "something2")], actionSet.actionSet[1].preHooks
        )
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testActionSet_129(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, index 50) ], set of various pre- and post hooks.
        """
        actions = [
            "stage",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
            PreActionHook("collect", "something1"),
            PreActionHook("collect", "something2"),
            PostActionHook("stage", "whatever1"),
            PostActionHook("stage", "whatever2"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(
            [PostActionHook("stage", "whatever1"), PostActionHook("stage", "whatever2")], actionSet.actionSet[1].postHooks
        )
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    ############################################
    # Test constructor, "dependency" order mode
    ############################################

    def testDependencyMode_001(self):
        """
        Test with actions=None, extensions=None.
        """
        actions = None
        extensions = ExtensionsConfig(None, "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_002(self):
        """
        Test with actions=[], extensions=None.
        """
        actions = []
        extensions = ExtensionsConfig(None, "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_003(self):
        """
        Test with actions=[], extensions=[].
        """
        actions = []
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_004(self):
        """
        Test with actions=[ collect ], extensions=[].
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_005(self):
        """
        Test with actions=[ stage ], extensions=[].
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testDependencyMode_006(self):
        """
        Test with actions=[ store ], extensions=[].
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testDependencyMode_007(self):
        """
        Test with actions=[ purge ], extensions=[].
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)

    def testDependencyMode_008(self):
        """
        Test with actions=[ all ], extensions=[].
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testDependencyMode_009(self):
        """
        Test with actions=[ rebuild ], extensions=[].
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("rebuild", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeRebuild, actionSet.actionSet[0].function)

    def testDependencyMode_010(self):
        """
        Test with actions=[ validate ], extensions=[].
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("validate", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeValidate, actionSet.actionSet[0].function)

    def testDependencyMode_011(self):
        """
        Test with actions=[ collect, collect ], extensions=[].
        """
        actions = [
            "collect",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_012(self):
        """
        Test with actions=[ collect, stage ], extensions=[].
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_013(self):
        """
        Test with actions=[ collect, store ], extensions=[].
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_014(self):
        """
        Test with actions=[ collect, purge ], extensions=[].
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_015(self):
        """
        Test with actions=[ collect, all ], extensions=[].
        """
        actions = [
            "collect",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_016(self):
        """
        Test with actions=[ collect, rebuild ], extensions=[].
        """
        actions = [
            "collect",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_017(self):
        """
        Test with actions=[ collect, validate ], extensions=[].
        """
        actions = [
            "collect",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_018(self):
        """
        Test with actions=[ stage, collect ], extensions=[].
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_019(self):
        """
        Test with actions=[ stage, stage ], extensions=[].
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_020(self):
        """
        Test with actions=[ stage, store ], extensions=[].
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_021(self):
        """
        Test with actions=[ stage, purge ], extensions=[].
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_022(self):
        """
        Test with actions=[ stage, all ], extensions=[].
        """
        actions = [
            "stage",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_023(self):
        """
        Test with actions=[ stage, rebuild ], extensions=[].
        """
        actions = [
            "stage",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_024(self):
        """
        Test with actions=[ stage, validate ], extensions=[].
        """
        actions = [
            "stage",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_025(self):
        """
        Test with actions=[ store, collect ], extensions=[].
        """
        actions = [
            "store",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_026(self):
        """
        Test with actions=[ store, stage ], extensions=[].
        """
        actions = [
            "store",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_027(self):
        """
        Test with actions=[ store, store ], extensions=[].
        """
        actions = [
            "store",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_028(self):
        """
        Test with actions=[ store, purge ], extensions=[].
        """
        actions = [
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_029(self):
        """
        Test with actions=[ store, all ], extensions=[].
        """
        actions = [
            "store",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_030(self):
        """
        Test with actions=[ store, rebuild ], extensions=[].
        """
        actions = [
            "store",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_031(self):
        """
        Test with actions=[ store, validate ], extensions=[].
        """
        actions = [
            "store",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_032(self):
        """
        Test with actions=[ purge, collect ], extensions=[].
        """
        actions = [
            "purge",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_033(self):
        """
        Test with actions=[ purge, stage ], extensions=[].
        """
        actions = [
            "purge",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_034(self):
        """
        Test with actions=[ purge, store ], extensions=[].
        """
        actions = [
            "purge",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_035(self):
        """
        Test with actions=[ purge, purge ], extensions=[].
        """
        actions = [
            "purge",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_036(self):
        """
        Test with actions=[ purge, all ], extensions=[].
        """
        actions = [
            "purge",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_037(self):
        """
        Test with actions=[ purge, rebuild ], extensions=[].
        """
        actions = [
            "purge",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_038(self):
        """
        Test with actions=[ purge, validate ], extensions=[].
        """
        actions = [
            "purge",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_039(self):
        """
        Test with actions=[ all, collect ], extensions=[].
        """
        actions = [
            "all",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_040(self):
        """
        Test with actions=[ all, stage ], extensions=[].
        """
        actions = [
            "all",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_041(self):
        """
        Test with actions=[ all, store ], extensions=[].
        """
        actions = [
            "all",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_042(self):
        """
        Test with actions=[ all, purge ], extensions=[].
        """
        actions = [
            "all",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_043(self):
        """
        Test with actions=[ all, all ], extensions=[].
        """
        actions = [
            "all",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_044(self):
        """
        Test with actions=[ all, rebuild ], extensions=[].
        """
        actions = [
            "all",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_045(self):
        """
        Test with actions=[ all, validate ], extensions=[].
        """
        actions = [
            "all",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_046(self):
        """
        Test with actions=[ rebuild, collect ], extensions=[].
        """
        actions = [
            "rebuild",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_047(self):
        """
        Test with actions=[ rebuild, stage ], extensions=[].
        """
        actions = [
            "rebuild",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_048(self):
        """
        Test with actions=[ rebuild, store ], extensions=[].
        """
        actions = [
            "rebuild",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_049(self):
        """
        Test with actions=[ rebuild, purge ], extensions=[].
        """
        actions = [
            "rebuild",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_050(self):
        """
        Test with actions=[ rebuild, all ], extensions=[].
        """
        actions = [
            "rebuild",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_051(self):
        """
        Test with actions=[ rebuild, rebuild ], extensions=[].
        """
        actions = [
            "rebuild",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_052(self):
        """
        Test with actions=[ rebuild, validate ], extensions=[].
        """
        actions = [
            "rebuild",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_053(self):
        """
        Test with actions=[ validate, collect ], extensions=[].
        """
        actions = [
            "validate",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_054(self):
        """
        Test with actions=[ validate, stage ], extensions=[].
        """
        actions = [
            "validate",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_055(self):
        """
        Test with actions=[ validate, store ], extensions=[].
        """
        actions = [
            "validate",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_056(self):
        """
        Test with actions=[ validate, purge ], extensions=[].
        """
        actions = [
            "validate",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_057(self):
        """
        Test with actions=[ validate, all ], extensions=[].
        """
        actions = [
            "validate",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_058(self):
        """
        Test with actions=[ validate, rebuild ], extensions=[].
        """
        actions = [
            "validate",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_059(self):
        """
        Test with actions=[ validate, validate ], extensions=[].
        """
        actions = [
            "validate",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_060(self):
        """
        Test with actions=[ bogus ], extensions=[].
        """
        actions = [
            "bogus",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_061(self):
        """
        Test with actions=[ bogus, collect ], extensions=[].
        """
        actions = [
            "bogus",
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_062(self):
        """
        Test with actions=[ bogus, stage ], extensions=[].
        """
        actions = [
            "bogus",
            "stage",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_063(self):
        """
        Test with actions=[ bogus, store ], extensions=[].
        """
        actions = [
            "bogus",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_064(self):
        """
        Test with actions=[ bogus, purge ], extensions=[].
        """
        actions = [
            "bogus",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_065(self):
        """
        Test with actions=[ bogus, all ], extensions=[].
        """
        actions = [
            "bogus",
            "all",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_066(self):
        """
        Test with actions=[ bogus, rebuild ], extensions=[].
        """
        actions = [
            "bogus",
            "rebuild",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_067(self):
        """
        Test with actions=[ bogus, validate ], extensions=[].
        """
        actions = [
            "bogus",
            "validate",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_068(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_069(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, before stage) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_070(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, before store) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_071(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, before purge) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(["purge"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_072(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, before collect) ].
        """
        actions = [
            "all",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_073(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, before collect) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_074(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, before collect) ].
        """
        actions = [
            "validate",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_075(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies([], ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_076(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(None, ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_077(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies([], ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_078(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(None, ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_079(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, before stage) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_080(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, before stage ) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_081(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, before stage) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_082(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "all",
            "one",
        ]
        dependencies = ActionDependencies(None, ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_083(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        dependencies = ActionDependencies([], ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_084(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, after collect) ].
        """
        actions = [
            "validate",
            "one",
        ]
        dependencies = ActionDependencies(None, ["collect"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_085(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies([], ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_086(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies([], ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_087(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(None, ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_088(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies([], ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_089(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before store) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["store"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_090(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, before store) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_091(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, before store) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(["store"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_092(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, before store) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_093(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "all",
            "one",
        ]
        dependencies = ActionDependencies(None, ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_094(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        dependencies = ActionDependencies([], ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_095(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, after stage) ].
        """
        actions = [
            "validate",
            "one",
        ]
        dependencies = ActionDependencies(None, ["stage"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_096(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_097(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(["store"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_098(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testDependencyMode_099(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(["store"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testDependencyMode_100(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before purge) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_101(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, before purge) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testDependencyMode_102(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, before purge) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testDependencyMode_103(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, before purge) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_104(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "all",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_105(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        dependencies = ActionDependencies(["store"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_106(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, after store) ].
        """
        actions = [
            "validate",
            "one",
        ]
        dependencies = ActionDependencies(["store"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_107(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_108(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testDependencyMode_109(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "store",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testDependencyMode_110(self):
        """
        Test with actions=[ purge, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "purge",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_111(self):
        """
        Test with actions=[ all, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "all",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_112(self):
        """
        Test with actions=[ rebuild, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "rebuild",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_113(self):
        """
        Test with actions=[ validate, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "validate",
            "one",
        ]
        dependencies = ActionDependencies(None, ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_114(self):
        """
        Test with actions=[ one, one ], extensions=[ (one, after purge) ].
        """
        actions = [
            "one",
            "one",
        ]
        dependencies = ActionDependencies([], ["purge"])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testDependencyMode_115(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[].
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testDependencyMode_116(self):
        """
        Test with actions=[ stage, purge, collect, store ], extensions=[].
        """
        actions = [
            "stage",
            "purge",
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testDependencyMode_117(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four, five ],
        extensions=[ one before collect, two before stage, etc. ].
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        dependencies1 = ActionDependencies(["collect", "stage", "store", "purge"], None)
        dependencies2 = ActionDependencies(["stage", "store", "purge"], ["collect"])
        dependencies3 = ActionDependencies(["store", "purge"], ["collect", "stage"])
        dependencies4 = ActionDependencies(["purge"], ["collect", "stage", "store"])
        dependencies5 = ActionDependencies([], ["collect", "stage", "store", "purge"])
        eaction1 = ExtendedAction("one", "os.path", "isdir", dependencies=dependencies1)
        eaction2 = ExtendedAction("two", "os.path", "isfile", dependencies=dependencies2)
        eaction3 = ExtendedAction("three", "os.path", "islink", dependencies=dependencies3)
        eaction4 = ExtendedAction("four", "os.path", "isabs", dependencies=dependencies4)
        eaction5 = ExtendedAction("five", "os.path", "exists", dependencies=dependencies5)
        extensions = ExtensionsConfig([eaction1, eaction2, eaction3, eaction4, eaction5], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(None, actionSet.actionSet[6].preHooks)
        self.assertEqual(None, actionSet.actionSet[6].postHooks)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(None, actionSet.actionSet[8].preHooks)
        self.assertEqual(None, actionSet.actionSet[8].postHooks)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testDependencyMode_118(self):
        """
        Test with actions=[ one, five, collect, store, three, stage, four, purge, two ],
        extensions=[ one before collect, two before stage, etc. ].
        """
        actions = [
            "one",
            "five",
            "collect",
            "store",
            "three",
            "stage",
            "four",
            "purge",
            "two",
        ]
        dependencies1 = ActionDependencies(["collect", "stage", "store", "purge"], [])
        dependencies2 = ActionDependencies(["stage", "store", "purge"], ["collect"])
        dependencies3 = ActionDependencies(["store", "purge"], ["collect", "stage"])
        dependencies4 = ActionDependencies(["purge"], ["collect", "stage", "store"])
        dependencies5 = ActionDependencies(None, ["collect", "stage", "store", "purge"])
        eaction1 = ExtendedAction("one", "os.path", "isdir", dependencies=dependencies1)
        eaction2 = ExtendedAction("two", "os.path", "isfile", dependencies=dependencies2)
        eaction3 = ExtendedAction("three", "os.path", "islink", dependencies=dependencies3)
        eaction4 = ExtendedAction("four", "os.path", "isabs", dependencies=dependencies4)
        eaction5 = ExtendedAction("five", "os.path", "exists", dependencies=dependencies5)
        extensions = ExtensionsConfig([eaction1, eaction2, eaction3, eaction4, eaction5], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(None, actionSet.actionSet[6].preHooks)
        self.assertEqual(None, actionSet.actionSet[6].postHooks)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(None, actionSet.actionSet[8].preHooks)
        self.assertEqual(None, actionSet.actionSet[8].postHooks)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testDependencyMode_119(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ].
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_120(self):
        """
        Test with actions=[ collect ], extensions=[], hooks=[]
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_121(self):
        """
        Test with actions=[ collect ], extensions=[], pre-hook on 'stage' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = [PreActionHook("stage", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_122(self):
        """
        Test with actions=[ collect ], extensions=[], post-hook on 'stage' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = [PostActionHook("stage", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_123(self):
        """
        Test with actions=[ collect ], extensions=[], pre-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = [PreActionHook("collect", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("collect", "something")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_124(self):
        """
        Test with actions=[ collect ], extensions=[], post-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = [PostActionHook("collect", "something")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("collect", "something")], actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_125(self):
        """
        Test with actions=[ collect ], extensions=[], pre- and post-hook on 'collect' action.
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], "dependency")
        options = OptionsConfig()
        options.hooks = [PreActionHook("collect", "something1"), PostActionHook("collect", "something2")]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("collect", "something1")], actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("collect", "something2")], actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testDependencyMode_126(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], hooks=[]
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_127(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], pre-hook on "store" action.
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("store", "whatever"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_128(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], post-hook on "store" action.
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("store", "whatever"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_129(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], pre-hook on "one" action.
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_130(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], post-hook on "one" action.
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_131(self):
        """
        Test with actions=[ one ], extensions=[ (one, before collect) ], pre- and post-hook on "one" action.
        """
        actions = [
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension2"),
            PreActionHook("one", "extension1"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension1")], actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension2")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testDependencyMode_132(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], hooks=[]
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = []
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_133(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], pre-hook on "purge" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("purge", "rm -f"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_134(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], post-hook on "purge" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("purge", "rm -f"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_135(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], pre-hook on "collect" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("collect", "something"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual([PreActionHook("collect", "something")], actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_136(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], post-hook on "collect" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("collect", "something"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual([PostActionHook("collect", "something")], actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_137(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], pre-hook on "one" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PreActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual([PreActionHook("one", "extension")], actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_138(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], post-hook on "one" action
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], [])
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_139a(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, before collect) ], set of various pre- and post hooks.
        """
        actions = [
            "collect",
            "one",
        ]
        dependencies = ActionDependencies(["collect"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
            PreActionHook("collect", "something1"),
            PreActionHook("collect", "something2"),
            PostActionHook("stage", "whatever"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(
            [PreActionHook("collect", "something1"), PreActionHook("collect", "something2")], actionSet.actionSet[1].preHooks
        )
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testDependencyMode_139b(self):
        """
        Test with actions=[ stage, one ], extensions=[ (one, before stage) ], set of various pre- and post hooks.
        """
        actions = [
            "stage",
            "one",
        ]
        dependencies = ActionDependencies(["stage"], None)
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", dependencies=dependencies)], "dependency")
        options = OptionsConfig()
        options.hooks = [
            PostActionHook("one", "extension"),
            PreActionHook("collect", "something1"),
            PostActionHook("stage", "whatever1"),
            PostActionHook("stage", "whatever2"),
        ]
        actionSet = _ActionSet(actions, extensions, options, None, False, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual([PostActionHook("one", "extension")], actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(
            [PostActionHook("stage", "whatever1"), PostActionHook("stage", "whatever2")], actionSet.actionSet[1].postHooks
        )
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testDependencyMode_140(self):
        """
        Test with actions=[ one, five, collect, store, three, stage, four, purge, two ],
        extensions= [recursive loop].
        """
        actions = [
            "one",
            "five",
            "collect",
            "store",
            "three",
            "stage",
            "four",
            "purge",
            "two",
        ]
        dependencies1 = ActionDependencies(["collect", "stage", "store", "purge"], [])
        dependencies2 = ActionDependencies(["stage", "store", "purge"], ["collect"])
        dependencies3 = ActionDependencies(["store", "purge"], ["collect", "stage"])
        dependencies4 = ActionDependencies(["purge"], ["collect", "stage", "store"])
        dependencies5 = ActionDependencies(["one"], ["collect", "stage", "store", "purge"])
        eaction1 = ExtendedAction("one", "os.path", "isdir", dependencies=dependencies1)
        eaction2 = ExtendedAction("two", "os.path", "isfile", dependencies=dependencies2)
        eaction3 = ExtendedAction("three", "os.path", "islink", dependencies=dependencies3)
        eaction4 = ExtendedAction("four", "os.path", "isabs", dependencies=dependencies4)
        eaction5 = ExtendedAction("five", "os.path", "exists", dependencies=dependencies5)
        extensions = ExtensionsConfig([eaction1, eaction2, eaction3, eaction4, eaction5], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    def testDependencyMode_141(self):
        """
        Test with actions=[ one, five, collect, store, three, stage, four, purge, two ],
        and one extension for which a dependency does not exist.
        """
        actions = [
            "one",
            "five",
            "collect",
            "store",
            "three",
            "stage",
            "four",
            "purge",
            "two",
        ]
        dependencies1 = ActionDependencies(["collect", "stage", "store", "purge"], [])
        dependencies2 = ActionDependencies(["stage", "store", "purge"], ["collect"])
        dependencies3 = ActionDependencies(["store", "bogus"], ["collect", "stage"])
        dependencies4 = ActionDependencies(["purge"], ["collect", "stage", "store"])
        dependencies5 = ActionDependencies([], ["collect", "stage", "store", "purge"])
        eaction1 = ExtendedAction("one", "os.path", "isdir", dependencies=dependencies1)
        eaction2 = ExtendedAction("two", "os.path", "isfile", dependencies=dependencies2)
        eaction3 = ExtendedAction("three", "os.path", "islink", dependencies=dependencies3)
        eaction4 = ExtendedAction("four", "os.path", "isabs", dependencies=dependencies4)
        eaction5 = ExtendedAction("five", "os.path", "exists", dependencies=dependencies5)
        extensions = ExtensionsConfig([eaction1, eaction2, eaction3, eaction4, eaction5], "dependency")
        options = OptionsConfig()
        self.assertRaises(ValueError, _ActionSet, actions, extensions, options, None, False, True)

    #########################################
    # Test constructor, with managed peers
    #########################################

    def testManagedPeer_001(self):
        """
        Test with actions=[ collect ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testManagedPeer_002(self):
        """
        Test with actions=[ stage ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testManagedPeer_003(self):
        """
        Test with actions=[ store ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testManagedPeer_004(self):
        """
        Test with actions=[ purge ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)

    def testManagedPeer_005(self):
        """
        Test with actions=[ all ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testManagedPeer_006(self):
        """
        Test with actions=[ rebuild ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("rebuild", actionSet.actionSet[0].name)
        self.assertEqual(executeRebuild, actionSet.actionSet[0].function)

    def testManagedPeer_007(self):
        """
        Test with actions=[ validate ], extensions=[], peers=None, managed=True,
        local=True
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("validate", actionSet.actionSet[0].name)
        self.assertEqual(executeValidate, actionSet.actionSet[0].function)

    def testManagedPeer_008(self):
        """
        Test with actions=[ collect, stage ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_009(self):
        """
        Test with actions=[ collect, store ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_010(self):
        """
        Test with actions=[ collect, purge ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testManagedPeer_011(self):
        """
        Test with actions=[ stage, collect ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_012(self):
        """
        Test with actions=[ stage, stage ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_013(self):
        """
        Test with actions=[ stage, store ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_014(self):
        """
        Test with actions=[ stage, purge ], extensions=[], peers=None,
        managed=True, local=True
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testManagedPeer_015(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        peers=None, managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testManagedPeer_016(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        peers=None, managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_017(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        peers=None, managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testManagedPeer_018(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        peers=None, managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_019(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        peers=None, managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testManagedPeer_020(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], peers=None,
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual(150, actionSet.actionSet[2].index)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual(200, actionSet.actionSet[3].index)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual(250, actionSet.actionSet[4].index)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual(300, actionSet.actionSet[5].index)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual(350, actionSet.actionSet[6].index)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual(400, actionSet.actionSet[7].index)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual(450, actionSet.actionSet[8].index)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testManagedPeer_021(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], peers=None,
        managed=True, local=True
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        actionSet = _ActionSet(actions, extensions, options, None, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testManagedPeer_022(self):
        """
        Test with actions=[ collect ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

    def testManagedPeer_023(self):
        """
        Test with actions=[ stage ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testManagedPeer_024(self):
        """
        Test with actions=[ store ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testManagedPeer_025(self):
        """
        Test with actions=[ purge ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)

    def testManagedPeer_026(self):
        """
        Test with actions=[ all ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testManagedPeer_027(self):
        """
        Test with actions=[ rebuild ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("rebuild", actionSet.actionSet[0].name)
        self.assertEqual(executeRebuild, actionSet.actionSet[0].function)

    def testManagedPeer_028(self):
        """
        Test with actions=[ validate ], extensions=[], no peers, managed=True,
        local=True
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("validate", actionSet.actionSet[0].name)
        self.assertEqual(executeValidate, actionSet.actionSet[0].function)

    def testManagedPeer_029(self):
        """
        Test with actions=[ collect, stage ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_030(self):
        """
        Test with actions=[ collect, store ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_031(self):
        """
        Test with actions=[ collect, purge ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testManagedPeer_032(self):
        """
        Test with actions=[ stage, collect ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_033(self):
        """
        Test with actions=[ stage, stage ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_034(self):
        """
        Test with actions=[ stage, store ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_035(self):
        """
        Test with actions=[ stage, purge ], extensions=[], no peers,
        managed=True, local=True
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)
        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

    def testManagedPeer_036(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        no peers, managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)

    def testManagedPeer_037(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        no peers, managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_038(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        no peers, managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertEqual(isdir, actionSet.actionSet[1].function)

    def testManagedPeer_039(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        no peers, managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_040(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        no peers, managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 4)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)
        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)
        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)
        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertEqual(executePurge, actionSet.actionSet[3].function)

    def testManagedPeer_041(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], no peers,
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 9)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)
        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertEqual(executeCollect, actionSet.actionSet[1].function)
        self.assertEqual(150, actionSet.actionSet[2].index)
        self.assertEqual("two", actionSet.actionSet[2].name)
        self.assertEqual(isfile, actionSet.actionSet[2].function)
        self.assertEqual(200, actionSet.actionSet[3].index)
        self.assertEqual("stage", actionSet.actionSet[3].name)
        self.assertEqual(executeStage, actionSet.actionSet[3].function)
        self.assertEqual(250, actionSet.actionSet[4].index)
        self.assertEqual("three", actionSet.actionSet[4].name)
        self.assertEqual(islink, actionSet.actionSet[4].function)
        self.assertEqual(300, actionSet.actionSet[5].index)
        self.assertEqual("store", actionSet.actionSet[5].name)
        self.assertEqual(executeStore, actionSet.actionSet[5].function)
        self.assertEqual(350, actionSet.actionSet[6].index)
        self.assertEqual("four", actionSet.actionSet[6].name)
        self.assertEqual(isabs, actionSet.actionSet[6].function)
        self.assertEqual(400, actionSet.actionSet[7].index)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)
        self.assertEqual(450, actionSet.actionSet[8].index)
        self.assertEqual("five", actionSet.actionSet[8].name)
        self.assertEqual(exists, actionSet.actionSet[8].function)

    def testManagedPeer_042(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], no peers,
        managed=True, local=True
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

    def testManagedPeer_043(self):
        """
        Test with actions=[ collect ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_044(self):
        """
        Test with actions=[ stage ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_045(self):
        """
        Test with actions=[ store ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_046(self):
        """
        Test with actions=[ purge ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_047(self):
        """
        Test with actions=[ all ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_048(self):
        """
        Test with actions=[ rebuild ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_049(self):
        """
        Test with actions=[ validate ], extensions=[], no peers, managed=True,
        local=False
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_050(self):
        """
        Test with actions=[ collect, stage ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_051(self):
        """
        Test with actions=[ collect, store ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_052(self):
        """
        Test with actions=[ collect, purge ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_053(self):
        """
        Test with actions=[ stage, collect ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_054(self):
        """
        Test with actions=[ stage, stage ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_055(self):
        """
        Test with actions=[ stage, store ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_056(self):
        """
        Test with actions=[ stage, purge ], extensions=[], no peers,
        managed=True, local=False
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_057(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        no peers, managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_058(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        no peers, managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_059(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        no peers, managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_060(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        no peers, managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_061(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        no peers, managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_062(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], no peers,
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_063(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], no peers,
        managed=True, local=False
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_064(self):
        """
        Test with actions=[ collect ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_065(self):
        """
        Test with actions=[ stage ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_066(self):
        """
        Test with actions=[ store ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_067(self):
        """
        Test with actions=[ purge ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_068(self):
        """
        Test with actions=[ all ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_069(self):
        """
        Test with actions=[ rebuild ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_070(self):
        """
        Test with actions=[ validate ], extensions=[], one peer (not managed), managed=True,
        local=False
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_071(self):
        """
        Test with actions=[ collect, stage ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_072(self):
        """
        Test with actions=[ collect, store ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_073(self):
        """
        Test with actions=[ collect, purge ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_074(self):
        """
        Test with actions=[ stage, collect ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_075(self):
        """
        Test with actions=[ stage, stage ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_076(self):
        """
        Test with actions=[ stage, store ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_077(self):
        """
        Test with actions=[ stage, purge ], extensions=[], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_078(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        one peer (not managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_079(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        one peer (not managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_080(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        one peer (not managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_081(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        one peer (not managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_082(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        one peer (not managed), managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_083(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_084(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], one peer (not managed),
        managed=True, local=False
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_085(self):
        """
        Test with actions=[ collect ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", None, "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_086(self):
        """
        Test with actions=[ stage ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_087(self):
        """
        Test with actions=[ store ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_088(self):
        """
        Test with actions=[ purge ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_089(self):
        """
        Test with actions=[ all ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_090(self):
        """
        Test with actions=[ rebuild ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_091(self):
        """
        Test with actions=[ validate ], extensions=[], one peer (managed), managed=True,
        local=False
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_092(self):
        """
        Test with actions=[ collect, stage ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)

        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_093(self):
        """
        Test with actions=[ collect, store ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)

        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_094(self):
        """
        Test with actions=[ collect, purge ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_095(self):
        """
        Test with actions=[ stage, collect ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_096(self):
        """
        Test with actions=[ stage, stage ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_097(self):
        """
        Test with actions=[ stage, store ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_098(self):
        """
        Test with actions=[ stage, purge ], extensions=[], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_099(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        one peer (managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_100(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        one peer (managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_101(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        one peer (managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_102(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        one peer (managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_103(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        one peer (managed), managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_104(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[2].index)
        self.assertEqual("purge", actionSet.actionSet[2].name)
        self.assertFalse(actionSet.actionSet[2].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[2].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[2].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[2].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[2].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[2].remotePeers[0].cbackCommand)

    def testManagedPeer_105(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], one peer (managed),
        managed=True, local=False
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_106(self):
        """
        Test with actions=[ collect ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", None, "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_107(self):
        """
        Test with actions=[ stage ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_108(self):
        """
        Test with actions=[ store ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_109(self):
        """
        Test with actions=[ purge ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_110(self):
        """
        Test with actions=[ all ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_111(self):
        """
        Test with actions=[ rebuild ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_112(self):
        """
        Test with actions=[ validate ], extensions=[], two peers (one managed, one not), managed=True,
        local=False
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_113(self):
        """
        Test with actions=[ collect, stage ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_114(self):
        """
        Test with actions=[ collect, store ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_115(self):
        """
        Test with actions=[ collect, purge ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_116(self):
        """
        Test with actions=[ stage, collect ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_117(self):
        """
        Test with actions=[ stage, stage ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_118(self):
        """
        Test with actions=[ stage, store ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_119(self):
        """
        Test with actions=[ stage, purge ], extensions=[], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_120(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        two peers (one managed, one not), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_121(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        two peers (one managed, one not), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_122(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        two peers (one managed, one not), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_123(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        two peers (one managed, one not), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_124(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        two peers (one managed, one not), managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

    def testManagedPeer_125(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[2].index)
        self.assertEqual("purge", actionSet.actionSet[2].name)
        self.assertFalse(actionSet.actionSet[2].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[2].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[2].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[2].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[2].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[2].remotePeers[0].cbackCommand)

    def testManagedPeer_126(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], two peers (one managed, one not),
        managed=True, local=False
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=False),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)

    def testManagedPeer_127(self):
        """
        Test with actions=[ collect ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", None, "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_128(self):
        """
        Test with actions=[ stage ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_129(self):
        """
        Test with actions=[ store ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_130(self):
        """
        Test with actions=[ purge ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_131(self):
        """
        Test with actions=[ all ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 2)
        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_132(self):
        """
        Test with actions=[ rebuild ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_133(self):
        """
        Test with actions=[ validate ], extensions=[], two peers (both managed), managed=True,
        local=False
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_134(self):
        """
        Test with actions=[ collect, stage ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_135(self):
        """
        Test with actions=[ collect, store ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_136(self):
        """
        Test with actions=[ collect, purge ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_137(self):
        """
        Test with actions=[ stage, collect ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_138(self):
        """
        Test with actions=[ stage, stage ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_139(self):
        """
        Test with actions=[ stage, store ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 0)

    def testManagedPeer_140(self):
        """
        Test with actions=[ stage, purge ], extensions=[], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_141(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        two peers (both managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_142(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        two peers (both managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_143(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        two peers (both managed), managed=True, local=False
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_144(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        two peers (both managed), managed=True, local=False
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_145(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        two peers (both managed), managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_146(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
            "three",
            "four",
            "five",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[2].index)
        self.assertEqual("purge", actionSet.actionSet[2].name)
        self.assertFalse(actionSet.actionSet[2].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[2].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[2].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[2].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[2].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[2].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[2].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[2].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[2].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[2].remotePeers[1].cbackCommand)

    def testManagedPeer_147(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], two peers (both managed),
        managed=True, local=False
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, False)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertFalse(actionSet.actionSet[0].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[0].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[0].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[0].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[0].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[0].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[0].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[0].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[0].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[0].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[0].remotePeers[1].cbackCommand)

    def testManagedPeer_148(self):
        """
        Test with actions=[ collect ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", None, "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_149(self):
        """
        Test with actions=[ stage ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

    def testManagedPeer_150(self):
        """
        Test with actions=[ store ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(300, actionSet.actionSet[0].index)
        self.assertEqual("store", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[0].function)

    def testManagedPeer_151(self):
        """
        Test with actions=[ purge ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(400, actionSet.actionSet[0].index)
        self.assertEqual("purge", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[0].function)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_152(self):
        """
        Test with actions=[ all ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "all",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertFalse(actionSet.actionSet is None)
        self.assertTrue(len(actionSet.actionSet) == 6)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(200, actionSet.actionSet[2].index)
        self.assertEqual("stage", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[2].function)

        self.assertEqual(300, actionSet.actionSet[3].index)
        self.assertEqual("store", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[3].function)

        self.assertEqual(400, actionSet.actionSet[4].index)
        self.assertEqual("purge", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[4].function)

        self.assertEqual(400, actionSet.actionSet[5].index)
        self.assertEqual("purge", actionSet.actionSet[5].name)
        self.assertFalse(actionSet.actionSet[5].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[5].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[5].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[5].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[5].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[5].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[5].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[5].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[5].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[5].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[5].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[5].remotePeers[1].cbackCommand)

    def testManagedPeer_153(self):
        """
        Test with actions=[ rebuild ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "rebuild",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("rebuild", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeRebuild, actionSet.actionSet[0].function)

    def testManagedPeer_154(self):
        """
        Test with actions=[ validate ], extensions=[], two peers (both managed), managed=True,
        local=True
        """
        actions = [
            "validate",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 1)

        self.assertEqual(0, actionSet.actionSet[0].index)
        self.assertEqual("validate", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeValidate, actionSet.actionSet[0].function)

    def testManagedPeer_155(self):
        """
        Test with actions=[ collect, stage ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(200, actionSet.actionSet[2].index)
        self.assertEqual("stage", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[2].function)

    def testManagedPeer_156(self):
        """
        Test with actions=[ collect, store ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "collect",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)

    def testManagedPeer_157(self):
        """
        Test with actions=[ collect, purge ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "collect",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 4)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(400, actionSet.actionSet[2].index)
        self.assertEqual("purge", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[2].function)

        self.assertEqual(400, actionSet.actionSet[3].index)
        self.assertEqual("purge", actionSet.actionSet[3].name)
        self.assertFalse(actionSet.actionSet[3].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[3].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[3].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[3].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[3].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[3].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[3].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[3].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[3].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[3].remotePeers[1].cbackCommand)

    def testManagedPeer_158(self):
        """
        Test with actions=[ stage, collect ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "stage",
            "collect",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(200, actionSet.actionSet[2].index)
        self.assertEqual("stage", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[2].function)

    def testManagedPeer_159(self):
        """
        Test with actions=[ stage, stage ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "stage",
            "stage",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

        self.assertEqual(200, actionSet.actionSet[1].index)
        self.assertEqual("stage", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[1].function)

    def testManagedPeer_160(self):
        """
        Test with actions=[ stage, store ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "stage",
            "store",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

        self.assertEqual(300, actionSet.actionSet[1].index)
        self.assertEqual("store", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[1].function)

    def testManagedPeer_161(self):
        """
        Test with actions=[ stage, purge ], extensions=[], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "stage",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(200, actionSet.actionSet[0].index)
        self.assertEqual("stage", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[0].function)

        self.assertEqual(400, actionSet.actionSet[1].index)
        self.assertEqual("purge", actionSet.actionSet[1].name)
        self.assertEqual(None, actionSet.actionSet[1].preHooks)
        self.assertEqual(None, actionSet.actionSet[1].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[1].function)

        self.assertEqual(400, actionSet.actionSet[2].index)
        self.assertEqual("purge", actionSet.actionSet[2].name)
        self.assertFalse(actionSet.actionSet[2].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[2].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[2].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[2].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[2].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[2].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[2].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[2].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[2].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[2].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[2].remotePeers[1].cbackCommand)

    def testManagedPeer_162(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 50) ],
        two peers (both managed), managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 4)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(50, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[2].index)
        self.assertEqual("collect", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[2].function)

        self.assertEqual(100, actionSet.actionSet[3].index)
        self.assertEqual("collect", actionSet.actionSet[3].name)
        self.assertFalse(actionSet.actionSet[3].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[3].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[3].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[3].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[3].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[3].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[3].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[3].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[3].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[3].remotePeers[1].cbackCommand)

    def testManagedPeer_163(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 50) ],
        two peers (both managed), managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(50, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)

    def testManagedPeer_164(self):
        """
        Test with actions=[ collect, one ], extensions=[ (one, index 150) ],
        two peers (both managed), managed=True, local=True
        """
        actions = [
            "collect",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 4)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[2].index)
        self.assertEqual("one", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[2].function)

        self.assertEqual(150, actionSet.actionSet[3].index)
        self.assertEqual("one", actionSet.actionSet[3].name)
        self.assertFalse(actionSet.actionSet[3].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[3].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[3].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[3].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[3].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[3].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[3].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[3].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[3].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[3].remotePeers[1].cbackCommand)

    def testManagedPeer_165(self):
        """
        Test with actions=[ store, one ], extensions=[ (one, index 150) ],
        two peers (both managed), managed=True, local=True
        """
        actions = [
            "store",
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 150)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 3)

        self.assertEqual(150, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(150, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(300, actionSet.actionSet[2].index)
        self.assertEqual("store", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[2].function)

    def testManagedPeer_166(self):
        """
        Test with actions=[ collect, stage, store, purge ], extensions=[],
        two peers (both managed), managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
        ]
        extensions = ExtensionsConfig([], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 6)

        self.assertEqual(100, actionSet.actionSet[0].index)
        self.assertEqual("collect", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[0].function)

        self.assertEqual(100, actionSet.actionSet[1].index)
        self.assertEqual("collect", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(200, actionSet.actionSet[2].index)
        self.assertEqual("stage", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[2].function)

        self.assertEqual(300, actionSet.actionSet[3].index)
        self.assertEqual("store", actionSet.actionSet[3].name)
        self.assertEqual(None, actionSet.actionSet[3].preHooks)
        self.assertEqual(None, actionSet.actionSet[3].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[3].function)

        self.assertEqual(400, actionSet.actionSet[4].index)
        self.assertEqual("purge", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[4].function)

        self.assertEqual(400, actionSet.actionSet[5].index)
        self.assertEqual("purge", actionSet.actionSet[5].name)
        self.assertFalse(actionSet.actionSet[5].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[5].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[5].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[5].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[5].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[5].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[5].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[5].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[5].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[5].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[5].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[5].remotePeers[1].cbackCommand)

    def testManagedPeer_167(self):
        """
        Test with actions=[ collect, stage, store, purge, one, two, three, four,
        five ], extensions=[ (index 50, 150, 250, 350, 450)], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 9)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[2].index)
        self.assertEqual("collect", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[2].function)

        self.assertEqual(100, actionSet.actionSet[3].index)
        self.assertEqual("collect", actionSet.actionSet[3].name)
        self.assertFalse(actionSet.actionSet[3].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[3].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[3].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[3].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[3].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[3].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[3].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[3].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[3].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[3].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[3].remotePeers[1].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[4].index)
        self.assertEqual("two", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[4].function)

        self.assertEqual(200, actionSet.actionSet[5].index)
        self.assertEqual("stage", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[5].function)

        self.assertEqual(300, actionSet.actionSet[6].index)
        self.assertEqual("store", actionSet.actionSet[6].name)
        self.assertEqual(None, actionSet.actionSet[6].preHooks)
        self.assertEqual(None, actionSet.actionSet[6].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[6].function)

        self.assertEqual(400, actionSet.actionSet[7].index)
        self.assertEqual("purge", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[7].function)

        self.assertEqual(400, actionSet.actionSet[8].index)
        self.assertEqual("purge", actionSet.actionSet[8].name)
        self.assertFalse(actionSet.actionSet[8].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[8].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[8].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[8].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[8].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[8].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[8].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[8].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[8].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[8].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[8].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[8].remotePeers[1].cbackCommand)

    def testManagedPeer_168(self):
        """
        Test with actions=[ one ], extensions=[ (one, index 50) ], two peers (both managed),
        managed=True, local=True
        """
        actions = [
            "one",
        ]
        extensions = ExtensionsConfig([ExtendedAction("one", "os.path", "isdir", 50)], None)
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, "ruser", "rcp", "rsh", "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", "rcp2", "rsh2", "cback2", managed=True),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 2)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(50, actionSet.actionSet[1].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 2)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("ruser", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rsh", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)
        self.assertEqual("remote2", actionSet.actionSet[1].remotePeers[1].name)
        self.assertEqual("ruser2", actionSet.actionSet[1].remotePeers[1].remoteUser)
        self.assertEqual(None, actionSet.actionSet[1].remotePeers[1].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[1].remotePeers[1].rshCommand)
        self.assertEqual("cback2", actionSet.actionSet[1].remotePeers[1].cbackCommand)

    def testManagedPeer_169(self):
        """
        Test to make sure that various options all seem to be pulled from the right places with mixed data.
        """
        actions = [
            "collect",
            "stage",
            "store",
            "purge",
            "one",
            "two",
        ]
        extensions = ExtensionsConfig(
            [
                ExtendedAction("one", "os.path", "isdir", 50),
                ExtendedAction("two", "os.path", "isfile", 150),
                ExtendedAction("three", "os.path", "islink", 250),
                ExtendedAction("four", "os.path", "isabs", 350),
                ExtendedAction("five", "os.path", "exists", 450),
            ],
            None,
        )
        options = OptionsConfig()
        options.managedActions = [
            "collect",
            "purge",
            "one",
        ]
        options.backupUser = "userZ"
        options.rshCommand = "rshZ"
        options.cbackCommand = "cbackZ"
        peers = PeersConfig()
        peers.localPeers = [
            LocalPeer("local", "/collect"),
        ]
        peers.remotePeers = [
            RemotePeer("remote", None, None, None, None, "cback", managed=True),
            RemotePeer("remote2", None, "ruser2", None, "rsh2", None, managed=True, managedActions=["stage"]),
        ]
        actionSet = _ActionSet(actions, extensions, options, peers, True, True)
        self.assertTrue(len(actionSet.actionSet) == 10)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[0].name)
        self.assertEqual(None, actionSet.actionSet[0].preHooks)
        self.assertEqual(None, actionSet.actionSet[0].postHooks)
        self.assertEqual(isdir, actionSet.actionSet[0].function)

        self.assertEqual(50, actionSet.actionSet[0].index)
        self.assertEqual("one", actionSet.actionSet[1].name)
        self.assertFalse(actionSet.actionSet[1].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[1].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[1].remotePeers[0].name)
        self.assertEqual("userZ", actionSet.actionSet[1].remotePeers[0].remoteUser)
        self.assertEqual("userZ", actionSet.actionSet[1].remotePeers[0].localUser)
        self.assertEqual("rshZ", actionSet.actionSet[1].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[1].remotePeers[0].cbackCommand)

        self.assertEqual(100, actionSet.actionSet[2].index)
        self.assertEqual("collect", actionSet.actionSet[2].name)
        self.assertEqual(None, actionSet.actionSet[2].preHooks)
        self.assertEqual(None, actionSet.actionSet[2].postHooks)
        self.assertEqual(executeCollect, actionSet.actionSet[2].function)

        self.assertEqual(100, actionSet.actionSet[3].index)
        self.assertEqual("collect", actionSet.actionSet[3].name)
        self.assertFalse(actionSet.actionSet[3].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[3].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[3].remotePeers[0].name)
        self.assertEqual("userZ", actionSet.actionSet[3].remotePeers[0].remoteUser)
        self.assertEqual("userZ", actionSet.actionSet[3].remotePeers[0].localUser)
        self.assertEqual("rshZ", actionSet.actionSet[3].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[3].remotePeers[0].cbackCommand)

        self.assertEqual(150, actionSet.actionSet[4].index)
        self.assertEqual("two", actionSet.actionSet[4].name)
        self.assertEqual(None, actionSet.actionSet[4].preHooks)
        self.assertEqual(None, actionSet.actionSet[4].postHooks)
        self.assertEqual(isfile, actionSet.actionSet[4].function)

        self.assertEqual(200, actionSet.actionSet[5].index)
        self.assertEqual("stage", actionSet.actionSet[5].name)
        self.assertEqual(None, actionSet.actionSet[5].preHooks)
        self.assertEqual(None, actionSet.actionSet[5].postHooks)
        self.assertEqual(executeStage, actionSet.actionSet[5].function)

        self.assertEqual(200, actionSet.actionSet[6].index)
        self.assertEqual("stage", actionSet.actionSet[6].name)
        self.assertFalse(actionSet.actionSet[6].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[6].remotePeers) == 1)
        self.assertEqual("remote2", actionSet.actionSet[6].remotePeers[0].name)
        self.assertEqual("ruser2", actionSet.actionSet[6].remotePeers[0].remoteUser)
        self.assertEqual("userZ", actionSet.actionSet[6].remotePeers[0].localUser)
        self.assertEqual("rsh2", actionSet.actionSet[6].remotePeers[0].rshCommand)
        self.assertEqual("cbackZ", actionSet.actionSet[6].remotePeers[0].cbackCommand)

        self.assertEqual(300, actionSet.actionSet[7].index)
        self.assertEqual("store", actionSet.actionSet[7].name)
        self.assertEqual(None, actionSet.actionSet[7].preHooks)
        self.assertEqual(None, actionSet.actionSet[7].postHooks)
        self.assertEqual(executeStore, actionSet.actionSet[7].function)

        self.assertEqual(400, actionSet.actionSet[8].index)
        self.assertEqual("purge", actionSet.actionSet[8].name)
        self.assertEqual(None, actionSet.actionSet[8].preHooks)
        self.assertEqual(None, actionSet.actionSet[8].postHooks)
        self.assertEqual(executePurge, actionSet.actionSet[8].function)

        self.assertEqual(400, actionSet.actionSet[9].index)
        self.assertEqual("purge", actionSet.actionSet[9].name)
        self.assertFalse(actionSet.actionSet[9].remotePeers is None)
        self.assertTrue(len(actionSet.actionSet[9].remotePeers) == 1)
        self.assertEqual("remote", actionSet.actionSet[9].remotePeers[0].name)
        self.assertEqual("userZ", actionSet.actionSet[9].remotePeers[0].remoteUser)
        self.assertEqual("userZ", actionSet.actionSet[9].remotePeers[0].localUser)
        self.assertEqual("rshZ", actionSet.actionSet[9].remotePeers[0].rshCommand)
        self.assertEqual("cback", actionSet.actionSet[9].remotePeers[0].cbackCommand)
