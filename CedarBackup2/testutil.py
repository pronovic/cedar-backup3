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
# Copyright (c) 2004-2006,2008,2010 Kenneth J. Pronovici.
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
# Language : Python (>= 2.5)
# Project  : Cedar Backup, release 2
# Revision : $Id: testutil.py 1023 2011-10-11 23:44:50Z pronovic $
# Purpose  : Provides unit-testing utilities.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides unit-testing utilities. 

These utilities are kept here, separate from util.py, because they provide
common functionality that I do not want exported "publicly" once Cedar Backup
is installed on a system.  They are only used for unit testing, and are only
useful within the source tree.

Many of these functions are in here because they are "good enough" for unit
test work but are not robust enough to be real public functions.  Others (like
L{removedir}) do what they are supposed to, but I don't want responsibility for
making them available to others.

@sort: findResources, commandAvailable,
       buildPath, removedir, extractTar, changeFileAge,
       getMaskAsMode, getLogin, failUnlessAssignRaises, runningAsRoot,
       platformDebian, platformMacOsX, platformCygwin, platformWindows, 
       platformHasEcho, platformSupportsLinks, platformSupportsPermissions,
       platformRequiresBinaryRead

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import sys
import os
import tarfile
import time
import getpass
import random
import string # pylint: disable=W0402
import platform
import logging
from StringIO import StringIO

from CedarBackup2.util import encodePath, executeCommand
from CedarBackup2.config import Config, OptionsConfig
from CedarBackup2.customize import customizeOverrides
from CedarBackup2.cli import setupPathResolver


########################################################################
# Public functions
########################################################################

##############################
# setupDebugLogger() function
##############################

def setupDebugLogger():
   """
   Sets up a screen logger for debugging purposes.

   Normally, the CLI functionality configures the logger so that
   things get written to the right place.  However, for debugging
   it's sometimes nice to just get everything -- debug information
   and output -- dumped to the screen.  This function takes care
   of that.
   """
   logger = logging.getLogger("CedarBackup2")
   logger.setLevel(logging.DEBUG)    # let the logger see all messages
   formatter = logging.Formatter(fmt="%(message)s")
   handler = logging.StreamHandler(strm=sys.stdout)
   handler.setFormatter(formatter)
   handler.setLevel(logging.DEBUG)
   logger.addHandler(handler)


#################
# setupOverrides
#################

def setupOverrides():
   """
   Set up any platform-specific overrides that might be required.

   When packages are built, this is done manually (hardcoded) in customize.py
   and the overrides are set up in cli.cli().  This way, no runtime checks need
   to be done.  This is safe, because the package maintainer knows exactly
   which platform (Debian or not) the package is being built for.  

   Unit tests are different, because they might be run anywhere.  So, we
   attempt to make a guess about plaform using platformDebian(), and use that
   to set up the custom overrides so that platform-specific unit tests continue
   to work.
   """
   config = Config()
   config.options = OptionsConfig()
   if platformDebian():
      customizeOverrides(config, platform="debian")
   else:
      customizeOverrides(config, platform="standard")
   setupPathResolver(config)


###########################
# findResources() function
###########################

def findResources(resources, dataDirs):
   """
   Returns a dictionary of locations for various resources.
   @param resources: List of required resources.
   @param dataDirs: List of data directories to search within for resources.
   @return: Dictionary mapping resource name to resource path.
   @raise Exception: If some resource cannot be found.
   """
   mapping = { }
   for resource in resources:
      for resourceDir in dataDirs:
         path = os.path.join(resourceDir, resource)
         if os.path.exists(path):
            mapping[resource] = path
            break
      else:
         raise Exception("Unable to find resource [%s]." % resource)
   return mapping


##############################
# commandAvailable() function
##############################

def commandAvailable(command):
   """
   Indicates whether a command is available on $PATH somewhere.
   This should work on both Windows and UNIX platforms.
   @param command: Commang to search for
   @return: Boolean true/false depending on whether command is available.
   """
   if os.environ.has_key("PATH"):
      for path in os.environ["PATH"].split(os.sep):
         if os.path.exists(os.path.join(path, command)):
            return True
   return False


#######################
# buildPath() function
#######################

def buildPath(components):
   """
   Builds a complete path from a list of components.
   For instance, constructs C{"/a/b/c"} from C{["/a", "b", "c",]}.
   @param components: List of components.
   @returns: String path constructed from components.
   @raise ValueError: If a path cannot be encoded properly.
   """
   path = components[0]
   for component in components[1:]:
      path = os.path.join(path, component)
   return encodePath(path)


#######################
# removedir() function
#######################

def removedir(tree):
   """
   Recursively removes an entire directory.
   This is basically taken from an example on python.com.  
   @param tree: Directory tree to remove.
   @raise ValueError: If a path cannot be encoded properly.
   """
   tree = encodePath(tree)
   for root, dirs, files in os.walk(tree, topdown=False):
      for name in files:
         path = os.path.join(root, name)
         if os.path.islink(path):
            os.remove(path)
         elif os.path.isfile(path):
            os.remove(path)
      for name in dirs:
         path = os.path.join(root, name)
         if os.path.islink(path):
            os.remove(path)
         elif os.path.isdir(path):
            os.rmdir(path)
   os.rmdir(tree)


########################
# extractTar() function
########################

def extractTar(tmpdir, filepath):
   """
   Extracts the indicated tar file to the indicated tmpdir.
   @param tmpdir: Temp directory to extract to.
   @param filepath: Path to tarfile to extract.
   @raise ValueError: If a path cannot be encoded properly.
   """
   # pylint: disable=E1101
   tmpdir = encodePath(tmpdir)
   filepath = encodePath(filepath)
   tar = tarfile.open(filepath)
   try:
      tar.format = tarfile.GNU_FORMAT
   except AttributeError:
      tar.posix = False
   for tarinfo in tar:
      tar.extract(tarinfo, tmpdir)


###########################
# changeFileAge() function
###########################

def changeFileAge(filename, subtract=None):
   """
   Changes a file age using the C{os.utime} function.

   @note: Some platforms don't seem to be able to set an age precisely.  As a
   result, whereas we might have intended to set an age of 86400 seconds, we
   actually get an age of 86399.375 seconds.  When util.calculateFileAge()
   looks at that the file, it calculates an age of 0.999992766204 days, which
   then gets truncated down to zero whole days.  The tests get very confused.
   To work around this, I always subtract off one additional second as a fudge
   factor.  That way, the file age will be I{at least} as old as requested
   later on.

   @param filename: File to operate on.
   @param subtract: Number of seconds to subtract from the current time.
   @raise ValueError: If a path cannot be encoded properly.
   """
   filename = encodePath(filename)
   newTime = time.time() - 1
   if subtract is not None:
      newTime -= subtract
   os.utime(filename, (newTime, newTime))


###########################
# getMaskAsMode() function
###########################

def getMaskAsMode():
   """
   Returns the user's current umask inverted to a mode.
   A mode is mostly a bitwise inversion of a mask, i.e. mask 002 is mode 775.
   @return: Umask converted to a mode, as an integer.
   """
   umask = os.umask(0777)
   os.umask(umask)
   return int(~umask & 0777)  # invert, then use only lower bytes


######################
# getLogin() function
######################

def getLogin():
   """
   Returns the name of the currently-logged in user.  This might fail under
   some circumstances - but if it does, our tests would fail anyway.
   """
   return getpass.getuser()


############################
# randomFilename() function
############################

def randomFilename(length, prefix=None, suffix=None):
   """
   Generates a random filename with the given length.
   @param length: Length of filename.
   @return Random filename.
   """
   characters = [None] * length
   for i in xrange(length):
      characters[i] = random.choice(string.ascii_uppercase)
   if prefix is None:
      prefix = ""
   if suffix is None:
      suffix = ""
   return "%s%s%s" % (prefix, "".join(characters), suffix)


####################################
# failUnlessAssignRaises() function
####################################

def failUnlessAssignRaises(testCase, exception, obj, prop, value):
   """
   Equivalent of C{failUnlessRaises}, but used for property assignments instead.

   It's nice to be able to use C{failUnlessRaises} to check that a method call
   raises the exception that you expect.  Unfortunately, this method can't be
   used to check Python propery assignments, even though these property
   assignments are actually implemented underneath as methods.

   This function (which can be easily called by unit test classes) provides an
   easy way to wrap the assignment checks.  It's not pretty, or as intuitive as
   the original check it's modeled on, but it does work.

   Let's assume you make this method call::

      testCase.failUnlessAssignRaises(ValueError, collectDir, "absolutePath", absolutePath)

   If you do this, a test case failure will be raised unless the assignment::

      collectDir.absolutePath = absolutePath

   fails with a C{ValueError} exception.  The failure message differentiates
   between the case where no exception was raised and the case where the wrong
   exception was raised.

   @note: Internally, the C{missed} and C{instead} variables are used rather
   than directly calling C{testCase.fail} upon noticing a problem because the
   act of "failure" itself generates an exception that would be caught by the
   general C{except} clause.

   @param testCase: PyUnit test case object (i.e. self).
   @param exception: Exception that is expected to be raised.
   @param obj: Object whose property is to be assigned to.
   @param prop: Name of the property, as a string.
   @param value: Value that is to be assigned to the property.

   @see: C{unittest.TestCase.failUnlessRaises}
   """
   missed = False
   instead = None
   try:
      exec "obj.%s = value" % prop    # pylint: disable=W0122
      missed = True
   except exception: pass
   except Exception, e: 
      instead = e
   if missed:
      testCase.fail("Expected assignment to raise %s, but got no exception." % (exception.__name__))
   if instead is not None:
      testCase.fail("Expected assignment to raise %s, but got %s instead." % (ValueError, instead.__class__.__name__))


###########################
# captureOutput() function
###########################

def captureOutput(c):
   """
   Captures the output (stdout, stderr) of a function or a method.

   Some of our functions don't do anything other than just print output.  We
   need a way to test these functions (at least nominally) but we don't want
   any of the output spoiling the test suite output.

   This function just creates a dummy file descriptor that can be used as a
   target by the callable function, rather than C{stdout} or C{stderr}.

   @note: This method assumes that C{callable} doesn't take any arguments
   besides keyword argument C{fd} to specify the file descriptor.

   @param c: Callable function or method.

   @return: Output of function, as one big string.
   """
   fd = StringIO()
   c(fd=fd)
   result = fd.getvalue()
   fd.close()
   return result


#########################
# _isPlatform() function
#########################

def _isPlatform(name):
   """
   Returns boolean indicating whether we're running on the indicated platform.
   @param name: Platform name to check, currently one of "windows" or "macosx"
   """
   if name == "windows":
      return platform.platform(True, True).startswith("Windows")
   elif name == "macosx":
      return sys.platform == "darwin"
   elif name == "debian":
      return platform.platform(False, False).find("debian") > 0
   elif name == "cygwin":
      return platform.platform(True, True).startswith("CYGWIN")
   else:
      raise ValueError("Unknown platform [%s]." % name)


############################
# platformDebian() function
############################

def platformDebian():
   """
   Returns boolean indicating whether this is the Debian platform.
   """
   return _isPlatform("debian")


############################
# platformMacOsX() function
############################

def platformMacOsX():
   """
   Returns boolean indicating whether this is the Mac OS X platform.
   """
   return _isPlatform("macosx")


#############################
# platformWindows() function
#############################

def platformWindows():
   """
   Returns boolean indicating whether this is the Windows platform.
   """
   return _isPlatform("windows")


############################
# platformCygwin() function
############################

def platformCygwin():
   """
   Returns boolean indicating whether this is the Cygwin platform.
   """
   return _isPlatform("cygwin")


###################################
# platformSupportsLinks() function
###################################

def platformSupportsLinks():
   """
   Returns boolean indicating whether the platform supports soft-links.
   Some platforms, like Windows, do not support links, and tests need to take
   this into account.
   """
   return not platformWindows()


#########################################
# platformSupportsPermissions() function
#########################################

def platformSupportsPermissions():
   """
   Returns boolean indicating whether the platform supports UNIX-style file permissions.
   Some platforms, like Windows, do not support permissions, and tests need to take
   this into account.
   """
   return not platformWindows()


########################################
# platformRequiresBinaryRead() function
########################################

def platformRequiresBinaryRead():
   """
   Returns boolean indicating whether the platform requires binary reads.
   Some platforms, like Windows, require a special flag to read binary data
   from files.
   """
   return platformWindows()


#############################
# platformHasEcho() function
#############################

def platformHasEcho():
   """
   Returns boolean indicating whether the platform has a sensible echo command.
   On some platforms, like Windows, echo doesn't really work for tests.
   """
   return not platformWindows()
   

###########################
# runningAsRoot() function
###########################

def runningAsRoot():
   """
   Returns boolean indicating whether the effective user id is root.
   This is always true on platforms that have no concept of root, like Windows.
   """
   if platformWindows():
      return True
   else:
      return os.geteuid() == 0


##############################
# availableLocales() function
##############################

def availableLocales():
   """
   Returns a list of available locales on the system
   @return: List of string locale names
   """
   locales = []
   output = executeCommand(["locale"], [ "-a", ], returnOutput=True, ignoreStderr=True)[1]
   for line in output:
      locales.append(line.rstrip())
   return locales


####################################
# hexFloatLiteralAllowed() function
####################################

def hexFloatLiteralAllowed():
   """
   Indicates whether hex float literals are allowed by the interpreter.

   As far back as 2004, some Python documentation indicated that octal and hex
   notation applied only to integer literals.  However, prior to Python 2.5, it
   was legal to construct a float with an argument like 0xAC on some platforms.
   This check provides a an indication of whether the current interpreter
   supports that behavior.

   This check exists so that unit tests can continue to test the same thing as
   always for pre-2.5 interpreters (i.e. making sure backwards compatibility
   doesn't break) while still continuing to work for later interpreters.

   The returned value is True if hex float literals are allowed, False otherwise.
   """
   if map(int, [sys.version_info[0], sys.version_info[1]]) < [2, 5] and not platformWindows():
      return True
   return False

