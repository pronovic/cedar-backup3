#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vim: set ft=python ts=3 sw=3 expandtab:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Copyright (c) 2004-2008,2010,2014,2015 Kenneth J. Pronovici.
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
# Language : Python 3 (>= 3.4.2)
# Project  : Cedar Backup, release 3
# Purpose  : Run all of the unit tests for the project.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Notes
########################################################################

"""
Run the CedarBackup3 unit tests.

This script runs all of the unit tests at once so we can get one big success or
failure result, rather than 20 different smaller results that we somehow have
to aggregate together to get the "big picture".  This is done by creating and
running one big unit test suite based on the suites in the individual unit test
modules.

The composite suite is always run using the TextTestRunner at verbosity level
1, which prints one dot (".") on the screen for each test run.  This output is
the same as one would get when using unittest.main() in an individual test.

Generally, I'm trying to keep all of the "special" validation logic (i.e. did
we find the right Python, did we find the right libraries, etc.) in this code
rather than in the individual unit tests so they're more focused on what to
test than how their environment should be configured.

We want to make sure the tests use the modules in the current source tree, not
any versions previously-installed elsewhere, if possible.  We don't actually
import the modules here, but we warn if the wrong ones would be found.  We also
want to make sure we are running the correct 'test' package - not one found
elsewhere on the user's path - since 'test' could be a relatively common name
for a package.

Most people will want to run the script with no arguments.  This will result in
a "reduced feature set" test suite that covers all of the available test
suites, but executes only those tests with no surprising system, kernel or
network dependencies.

If "full" is specified as one of the command-line arguments, then all of the
unit tests will be run, including those that require a specialized environment.
For instance, some tests require remote connectivity, a loopback filesystem,
etc.

Other arguments on the command line are assumed to be named tests, so for
instance passing "config" runs only the tests for config.py.  Any number of
individual tests may be listed on the command line, and unknown values will
simply be ignored.

@note: Even if you run this test with the C{python3} interpreter, some of the
individual unit tests require the C{python} interpreter.  In particular, the
utility tests (in test/utiltests.py) use brief Python script snippets with
known results to verify the behavior of C{executeCommand}.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import sys
import os
import logging
import unittest


##################
# main() function
##################

def main():

   """
   Main routine for program.
   @return: Integer 0 upon success, integer 1 upon failure.
   """

   # Check the Python version.  We require 3.4 or greater.
   try:
      if map(int, [sys.version_info[0], sys.version_info[1]]) < [2, 5]:
         print "Python version 3.4 or greater required, sorry."
         return 1
   except:
      # sys.version_info isn't available before 2.0
      print "Python version 3.4 or greater required, sorry."
      return 1

   # Check for the correct CedarBackup3 location and import utilities
   try:
      if os.path.exists(os.path.join(".", "CedarBackup3", "filesystem.py")):
         sys.path.insert(0, ".")
      elif os.path.basename(os.getcwd()) == "testcase" and os.path.exists(os.path.join("..", "CedarBackup3", "filesystem.py")):
         sys.path.insert(0, "..")
      else:
         print "WARNING: CedarBackup3 modules were not found in the expected"
         print "location.  If the import succeeds, you may be using an"
         print "unexpected version of CedarBackup3."
         print ""
      from CedarBackup3.util import nullDevice, Diagnostics
   except ImportError, e:
      print "Failed to import CedarBackup3 util module: %s" % e
      print "You must either run the unit tests from the CedarBackup3 source"
      print "tree, or properly set the PYTHONPATH enviroment variable."
      return 1

   # Setup platform-specific command overrides
   from CedarBackup3.testutil import setupOverrides
   setupOverrides()

   # Import the unit test modules
   try:
      if os.path.exists(os.path.join(".", "testcase", "filesystemtests.py")):
         sys.path.insert(0, ".")
      elif os.path.basename(os.getcwd()) == "testcase" and os.path.exists(os.path.join("..", "testcase", "filesystemtests.py")):
         sys.path.insert(0, "..")
      else:
         print "WARNING: CedarBackup3 unit test modules were not found in"
         print "the expected location.  If the import succeeds, you may be"
         print "using an unexpected version of the test suite."
         print ""
      from testcase import utiltests
      from testcase import knapsacktests
      from testcase import filesystemtests
      from testcase import peertests
      from testcase import actionsutiltests
      from testcase import writersutiltests
      from testcase import cdwritertests
      from testcase import dvdwritertests
      from testcase import configtests
      from testcase import clitests
      from testcase import mysqltests
      from testcase import postgresqltests
      from testcase import subversiontests
      from testcase import mboxtests
      from testcase import encrypttests
      from testcase import amazons3tests
      from testcase import splittests
      from testcase import spantests
      from testcase import synctests
      from testcase import capacitytests
      from testcase import customizetests
   except ImportError, e:
      print "Failed to import CedarBackup3 unit test module: %s" % e
      print "You must either run the unit tests from the CedarBackup3 source"
      print "tree, or properly set the PYTHONPATH enviroment variable."
      return 1

   # Set up logging to discard everything
   devnull = nullDevice()
   handler = logging.FileHandler(filename=devnull)
   handler.setLevel(logging.NOTSET)
   logger = logging.getLogger("CedarBackup3")
   logger.setLevel(logging.NOTSET)
   logger.addHandler(handler)

   # Get a list of program arguments
   args = sys.argv[1:]

   # Set flags in the environment to control tests
   if "full" in args:
      full = True
      os.environ["PEERTESTS_FULL"] = "Y"
      os.environ["WRITERSUTILTESTS_FULL"] = "Y"
      os.environ["ENCRYPTTESTS_FULL"] = "Y"
      os.environ["SPLITTESTS_FULL"] = "Y"
      args.remove("full") # remainder of list will be specific tests to run, if any
   else:
      full = False
      os.environ["PEERTESTS_FULL"] = "N"
      os.environ["WRITERSUTILTESTS_FULL"] = "N"
      os.environ["ENCRYPTTESTS_FULL"] = "N"
      os.environ["SPLITTESTS_FULL"] = "N"

   # Print a starting banner
   print "\n*** Running CedarBackup3 unit tests."
   if not full:
      print "*** Using reduced feature set suite with minimum system requirements."

   # Make a list of tests to run
   unittests = { }
   if args == [] or "util" in args: unittests["util"] = utiltests.suite()
   if args == [] or "knapsack" in args: unittests["knapsack"] = knapsacktests.suite()
   if args == [] or "filesystem" in args: unittests["filesystem"] = filesystemtests.suite()
   if args == [] or "peer" in args: unittests["peer"] = peertests.suite()
   if args == [] or "actionsutil" in args: unittests["actionsutil"] = actionsutiltests.suite()
   if args == [] or "writersutil" in args: unittests["writersutil"] = writersutiltests.suite()
   if args == [] or "cdwriter" in args: unittests["cdwriter"] = cdwritertests.suite()
   if args == [] or "dvdwriter" in args: unittests["dvdwriter"] = dvdwritertests.suite()
   if args == [] or "config" in args: unittests["config"] = configtests.suite()
   if args == [] or "cli" in args: unittests["cli"] = clitests.suite()
   if args == [] or "mysql" in args: unittests["mysql"] = mysqltests.suite()
   if args == [] or "postgresql" in args: unittests["postgresql"] = postgresqltests.suite()
   if args == [] or "subversion" in args: unittests["subversion"] = subversiontests.suite()
   if args == [] or "mbox" in args: unittests["mbox"] = mboxtests.suite()
   if args == [] or "split" in args: unittests["split"] = splittests.suite()
   if args == [] or "encrypt" in args: unittests["encrypt"] = encrypttests.suite()
   if args == [] or "amazons3" in args: unittests["amazons3"] = amazons3tests.suite()
   if args == [] or "span" in args: unittests["span"] = spantests.suite()
   if args == [] or "sync" in args: unittests["sync"] = synctests.suite()
   if args == [] or "capacity" in args: unittests["capacity"] = capacitytests.suite()
   if args == [] or "customize" in args: unittests["customize"] = customizetests.suite()
   if args != []: print "*** Executing specific tests: %s" % unittests.keys()

   # Print some diagnostic information
   print ""
   Diagnostics().printDiagnostics(prefix="*** ")

   # Create and run the test suite
   print ""
   suite = unittest.TestSuite(unittests.values())
   suiteResult = unittest.TextTestRunner(verbosity=1).run(suite)
   print ""
   if not suiteResult.wasSuccessful():
      return 1
   else:
      return 0


########################################################################
# Module entry point
########################################################################

# Run the main routine if the module is executed rather than sourced
if __name__ == '__main__':
   result = main()
   sys.exit(result)

