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
# Copyright (c) 2004-2006,2008,2010,2015 Kenneth J. Pronovici.
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
:any:`removedir`) do what they are supposed to, but I don't want responsibility for
making them available to others.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import getpass
import logging
import os
import platform
import random
import string  # pylint: disable=W0402
import sys
import tarfile
import time
from io import StringIO

from CedarBackup3.cli import setupPathResolver
from CedarBackup3.config import Config, OptionsConfig
from CedarBackup3.customize import customizeOverrides
from CedarBackup3.util import encodePath, executeCommand, nullDevice, pathJoin

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
    logger = logging.getLogger("CedarBackup3")
    logger.setLevel(logging.DEBUG)  # let the logger see all messages
    formatter = logging.Formatter(fmt="%(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)


def configureLogging():
    """Optionally disable system logging based on configuration in the environment."""
    if "FULL_LOGGING" not in os.environ or os.environ["FULL_LOGGING"] == "N":
        devnull = nullDevice()
        handler = logging.FileHandler(filename=devnull)
        handler.setLevel(logging.NOTSET)
        logger = logging.getLogger("CedarBackup3")
        logger.setLevel(logging.NOTSET)
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
    Args:
       resources: List of required resources
       dataDirs: List of data directories to search within for resources
    Returns:
        Dictionary mapping resource name to resource path
    Raises:
       Exception: If some resource cannot be found
    """
    mapping = {}
    for resource in resources:
        for resourceDir in dataDirs:
            path = pathJoin(resourceDir, resource)
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
    Args:
       command: Commang to search for
    Returns:
        Boolean true/false depending on whether command is available
    """
    if "PATH" in os.environ:
        for path in os.environ["PATH"].split(os.sep):
            if os.path.exists(pathJoin(path, command)):
                return True
    return False


#######################
# buildPath() function
#######################


def buildPath(components):
    """
    Builds a complete path from a list of components.
    For instance, constructs ``"/a/b/c"`` from ``["/a", "b", "c"]``.
    Args:
       components: List of components
    Returns:
        String path constructed from components
    Raises:
       ValueError: If a path cannot be encoded properly
    """
    path = components[0]
    for component in components[1:]:
        path = pathJoin(path, component)
    return encodePath(path)


#######################
# removedir() function
#######################


def removedir(tree):
    """
    Recursively removes an entire directory.
    This is basically taken from an example on python.com.
    Args:
       tree: Directory tree to remove
    Raises:
       ValueError: If a path cannot be encoded properly
    """
    tree = encodePath(tree)
    for root, dirs, files in os.walk(tree, topdown=False):
        for name in files:
            path = pathJoin(root, name)
            if os.path.islink(path):
                os.remove(path)
            elif os.path.isfile(path):
                os.remove(path)
        for name in dirs:
            path = pathJoin(root, name)
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
    Args:
       tmpdir: Temp directory to extract to
       filepath: Path to tarfile to extract
    Raises:
       ValueError: If a path cannot be encoded properly
    """
    # pylint: disable=E1101
    tmpdir = encodePath(tmpdir)
    filepath = encodePath(filepath)
    with tarfile.open(filepath) as tar:
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
    Changes a file age using the ``os.utime`` function.

    *Note:* Some platforms don't seem to be able to set an age precisely.  As a
    result, whereas we might have intended to set an age of 86400 seconds, we
    actually get an age of 86399.375 seconds.  When util.calculateFileAge()
    looks at that the file, it calculates an age of 0.999992766204 days, which
    then gets truncated down to zero whole days.  The tests get very confused.
    To work around this, I always subtract off one additional second as a fudge
    factor.  That way, the file age will be *at least* as old as requested
    later on.

    Args:
       filename: File to operate on
       subtract: Number of seconds to subtract from the current time
    Raises:
       ValueError: If a path cannot be encoded properly
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
    Returns:
        Umask converted to a mode, as an integer
    """
    umask = os.umask(0o777)
    os.umask(umask)
    return int(~umask & 0o777)  # invert, then use only lower bytes


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
    @return Random filename
    """
    characters = [None] * length
    for i in range(length):
        characters[i] = random.choice(string.ascii_uppercase)
    if prefix is None:
        prefix = ""
    if suffix is None:
        suffix = ""
    return "%s%s%s" % (prefix, "".join(characters), suffix)


####################################
# failUnlessAssignRaises() function
####################################

# pylint: disable=W0613
def failUnlessAssignRaises(testCase, exception, obj, prop, value):
    """
    Equivalent of ``failUnlessRaises``, but used for property assignments instead.

    It's nice to be able to use ``failUnlessRaises`` to check that a method call
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

    fails with a ``ValueError`` exception.  The failure message differentiates
    between the case where no exception was raised and the case where the wrong
    exception was raised.

    *Note:* Internally, the ``missed`` and ``instead`` variables are used rather
    than directly calling ``testCase.fail`` upon noticing a problem because the
    act of "failure" itself generates an exception that would be caught by the
    general ``except`` clause.

    Args:
       testCase: PyUnit test case object (i.e. self)
       exception: Exception that is expected to be raised
       obj: Object whose property is to be assigned to
       prop: Name of the property, as a string
       value: Value that is to be assigned to the property

    @see: ``unittest.TestCase.failUnlessRaises``
    """
    missed = False
    instead = None
    try:
        exec("obj.%s = value" % prop)  # pylint: disable=W0122
        missed = True
    except exception:
        pass
    except Exception as e:
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
    target by the callable function, rather than ``stdout`` or ``stderr``.

    *Note:* This method assumes that ``callable`` doesn't take any arguments
    besides keyword argument ``fd`` to specify the file descriptor.

    Args:
       c: Callable function or method

    Returns:
        Output of function, as one big string
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
    Args:
       name: Platform name to check, currently one of "windows" or "macosx"
    """
    if name == "windows":
        return sys.platform == "win32"
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


####################################
# platformSupportsLinks() function
####################################


def platformSupportsLinks():
    """Whether the platform supports soft links"""
    return not platformWindows()


##############################
# availableLocales() function
##############################


def availableLocales():
    """
    Returns a list of available locales on the system
    Returns:
        List of string locale names
    """
    locales = []
    output = executeCommand(["locale"], ["-a"], returnOutput=True, ignoreStderr=True)[1]
    for line in output:
        locales.append(line.rstrip())  # pylint: disable=E1101
    return locales
