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
# Purpose  : Tests span tool functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/tools/span.py.

Code Coverage
=============

   This module contains individual tests for the many of the public functions
   and classes implemented in tools/span.py.  Where possible, we test functions
   that print output by passing a custom file descriptor.  Sometimes, we only
   ensure that a function or method runs without failure, and we don't validate
   what its result is or what it prints out.

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
   build environment.  There is a no need to use a SPANTESTS_FULL environment
   variable to provide a "reduced feature set" test suite as for some of the
   other test modules.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.testutil import captureOutput, configureLogging
from CedarBackup3.tools.span import Options, _usage, _version

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


########################
# TestSpanOptions class
########################


class TestSpanOptions(unittest.TestCase):

    """Tests for the SpanOptions class."""

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
