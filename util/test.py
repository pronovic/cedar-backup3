#!/usr/bin/python3
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
# Copyright (c) 2004-2008,2010,2014,2015,2020 Kenneth J. Pronovici.
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
# Language : Python 3 (>= 3.4)
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
      if list(map(int, [sys.version_info[0], sys.version_info[1]])) < [3, 4]:
         print("Python 3 version 3.4 or greater required, sorry.")
         return 1
   except:
      # sys.version_info isn't available before 2.0
      print("Python 3 version 3.4 or greater required, sorry.")
      return 1

   # Check for the correct CedarBackup3 location and import utilities
   try:
      if os.path.exists(os.path.join(".", "src", "CedarBackup3", "filesystem.py")):
         sys.path.insert(0, ".")
      elif os.path.basename(os.getcwd()) == "tests" and os.path.exists(os.path.join("..", "src", "CedarBackup3", "filesystem.py")):
         sys.path.insert(0, "..")
      else:
         print("WARNING: CedarBackup3 modules were not found in the expected")
         print("location.  If the import succeeds, you may be using an")
         print("unexpected version of CedarBackup3.")
         print("")
      from CedarBackup3.util import nullDevice, Diagnostics
   except ImportError as e:
      print(("Failed to import CedarBackup3 util module: %s" % e))
      print("You must either run the unit tests from the CedarBackup3 source")
      print("tree, or properly set the PYTHONPATH enviroment variable.")
      return 1

   # Import the unit test modules
   try:
      if os.path.exists(os.path.join(".", "tests", "filesystemtests.py")):
         sys.path.insert(0, ".")
      elif os.path.basename(os.getcwd()) == "tests" and os.path.exists(os.path.join("..", "tests", "filesystemtests.py")):
         sys.path.insert(0, "..")
      else:
         print("WARNING: CedarBackup3 unit test modules were not found in")
         print("the expected location.  If the import succeeds, you may be")
         print("using an unexpected version of the test suite.")
         print("")
      from tests import utiltests
      from tests import knapsacktests
      from tests import filesystemtests
      from tests import peertests
      from tests import actionsutiltests
      from tests import writersutiltests
      from tests import cdwritertests
      from tests import dvdwritertests
      from tests import configtests
      from tests import clitests
      from tests import mysqltests
      from tests import postgresqltests
      from tests import subversiontests
      from tests import mboxtests
      from tests import encrypttests
      from tests import amazons3tests
      from tests import splittests
      from tests import spantests
      from tests import synctests
      from tests import capacitytests
      from tests import customizetests
   except ImportError as e:
      print(("Failed to import CedarBackup3 unit test module: %s" % e))
      print("You must either run the unit tests from the CedarBackup3 source")
      print("tree, or properly set the PYTHONPATH enviroment variable.")
      return 1

   # Get a list of program arguments
   args = sys.argv[1:]

   # Set verbosity for the test runner
   if "verbose" in args:
      verbosity = 2   # prints each test name
      args.remove("verbose")
   else:
      verbosity = 1   # prints a . for each test

   # Set up logging, where "debug" sends all output to stderr
   if "debug" in args:
      handler = logging.StreamHandler(sys.stdout)
      handler.setLevel(logging.DEBUG)
      logger = logging.getLogger("CedarBackup3")
      logger.setLevel(logging.DEBUG)
      logger.addHandler(handler)
      args.remove("debug")
   else:
      devnull = nullDevice()
      handler = logging.FileHandler(filename=devnull)
      handler.setLevel(logging.NOTSET)
      logger = logging.getLogger("CedarBackup3")
      logger.setLevel(logging.NOTSET)
      logger.addHandler(handler)

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
   print("\n*** Running CedarBackup3 unit tests.")
   if not full:
      print("*** Using reduced feature set suite with minimum system requirements.")

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
   if args != []: print(("*** Executing specific tests: %s" % list(unittests.keys())))

   # Print some diagnostic information
   print("")
   Diagnostics().printDiagnostics(prefix="*** ")

   # Create and run the test suite
   print("")
   suite = unittest.TestSuite(list(unittests.values()))
   suiteResult = unittest.TextTestRunner(verbosity=verbosity).run(suite)
   print("")
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

