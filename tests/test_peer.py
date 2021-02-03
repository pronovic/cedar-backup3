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
# Copyright (c) 2004-2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests peer functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/peer.py.

Code Coverage
=============

   This module contains individual tests for most of the public functions and
   classes implemented in peer.py, including the ``LocalPeer`` and ``RemotePeer``
   classes.

   Unfortunately, some of the code can't be tested.  In particular, the stage
   code allows the caller to change ownership on files.  Generally, this can
   only be done by root, and most people won't be running these tests as root.
   As such, we can't test this functionality.  There are also some other pieces
   of functionality that can only be tested in certain environments (see
   below).

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

   Some Cedar Backup regression tests require a specialized environment in
   order to run successfully.  This environment won't necessarily be available
   on every build system out there (for instance, on a Debian autobuilder).
   Because of this, the default behavior is to run a "reduced feature set" test
   suite that has no surprising system, kernel or network requirements.  If you
   want to run all of the tests, set PEERTESTS_FULL to "Y" in the environment.

   In this module, network-related testing is what causes us our biggest
   problems.  In order to test the RemotePeer, we need a "remote" host that we
   can rcp to and from.  We want to fall back on using localhost and the
   current user, but that might not be safe or appropriate.  As such, we'll
   only run these tests if PEERTESTS_FULL is set to "Y" in the environment.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

# Import standard modules
import os
import stat
import tempfile
import unittest

from CedarBackup3.peer import DEF_COLLECT_INDICATOR, DEF_RCP_COMMAND, DEF_RSH_COMMAND, DEF_STAGE_INDICATOR, LocalPeer, RemotePeer
from CedarBackup3.testutil import (
    buildPath,
    configureLogging,
    extractTar,
    failUnlessAssignRaises,
    findResources,
    getLogin,
    getMaskAsMode,
    platformWindows,
    removedir,
)
from CedarBackup3.util import isRunningAsRoot, pathJoin

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "tree1.tar.gz",
    "tree2.tar.gz",
    "tree9.tar.gz",
]

REMOTE_HOST = "localhost"  # Always use login@localhost as our "remote" host
NONEXISTENT_FILE = "bogus"  # This file name should never exist
NONEXISTENT_HOST = "hostname.invalid"  # RFC 2606 reserves the ".invalid" TLD for "obviously invalid" names
NONEXISTENT_USER = "unittestuser"  # This user name should never exist on localhost
NONEXISTENT_CMD = "/bogus/~~~ZZZZ/bad/not/there"  # This command should never exist in the filesystem

SAFE_RCP_COMMAND = "/usr/bin/scp -B -q -C -o ConnectTimeout=1"  # set a connection timeout so invalid hosts don't hang
SAFE_RSH_COMMAND = "/usr/bin/ssh -o ConnectTimeout=1"  # set a connection timeout so invalid hosts don't hang


#######################################################################
# Utility functions
#######################################################################


def runAllTests():
    """Returns true/false depending on whether the full test suite should be run."""
    if "PEERTESTS_FULL" in os.environ:
        return os.environ["PEERTESTS_FULL"] == "Y"
    else:
        return False


#######################################################################
# Test Case Classes
#######################################################################

######################
# TestLocalPeer class
######################


class TestLocalPeer(unittest.TestCase):

    """Tests for the LocalPeer class."""

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

    def getFileMode(self, components):
        """Calls buildPath on components and then returns file mode for the file."""
        return stat.S_IMODE(os.stat(self.buildPath(components)).st_mode)

    def failUnlessAssignRaises(self, exception, obj, prop, value):
        """Equivalent of :any:`failUnlessRaises`, but used for property assignments instead."""
        failUnlessAssignRaises(self, exception, obj, prop, value)

    ###########################
    # Test basic functionality
    ###########################

    def testBasic_001(self):
        """
        Make sure exception is thrown for non-absolute collect directory.
        """
        name = "peer1"
        collectDir = "whatever/something/else/not/absolute"
        self.assertRaises(ValueError, LocalPeer, name, collectDir)

    def testBasic_002(self):
        """
        Make sure attributes are set properly for valid constructor input.
        """
        name = "peer1"
        collectDir = "/absolute/path/name"
        ignoreFailureMode = "all"
        peer = LocalPeer(name, collectDir, ignoreFailureMode)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)
        self.assertEqual(ignoreFailureMode, peer.ignoreFailureMode)

    def testBasic_003(self):
        """
        Make sure attributes are set properly for valid constructor input, with
        spaces in the collect directory path.
        """
        name = "peer1"
        collectDir = "/ absolute / path/   name "
        peer = LocalPeer(name, collectDir)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)

    def testBasic_004(self):
        """
        Make sure assignment works for all valid failure modes.
        """
        name = "peer1"
        collectDir = "/absolute/path/name"
        ignoreFailureMode = "all"
        peer = LocalPeer(name, collectDir, ignoreFailureMode)
        self.assertEqual("all", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "none"
        self.assertEqual("none", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "daily"
        self.assertEqual("daily", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "weekly"
        self.assertEqual("weekly", peer.ignoreFailureMode)
        self.failUnlessAssignRaises(ValueError, peer, "ignoreFailureMode", "bogus")

    ###############################
    # Test checkCollectIndicator()
    ###############################

    def testCheckCollectIndicator_001(self):
        """
        Attempt to check collect indicator with non-existent collect directory.
        """
        name = "peer1"
        collectDir = self.buildPath([NONEXISTENT_FILE])
        self.assertTrue(not os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    def testCheckCollectIndicator_002(self):
        """
        Attempt to check collect indicator with non-readable collect directory.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        os.chmod(collectDir, 0o200)  # user can't read his own directory
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)
        os.chmod(collectDir, 0o777)  # so we can remove it safely

    def testCheckCollectIndicator_003(self):
        """
        Attempt to check collect indicator collect indicator file that does not exist.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        collectIndicator = self.buildPath(["collect", DEF_COLLECT_INDICATOR])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    def testCheckCollectIndicator_004(self):
        """
        Attempt to check collect indicator collect indicator file that does not exist, custom name.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        collectIndicator = self.buildPath(["collect", NONEXISTENT_FILE])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator(collectIndicator=NONEXISTENT_FILE)
        self.assertEqual(False, result)

    def testCheckCollectIndicator_005(self):
        """
        Attempt to check collect indicator collect indicator file that does exist.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        collectIndicator = self.buildPath(["collect", DEF_COLLECT_INDICATOR])
        os.mkdir(collectDir)
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator()
        self.assertEqual(True, result)

    def testCheckCollectIndicator_006(self):
        """
        Attempt to check collect indicator collect indicator file that does exist, custom name.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        collectIndicator = self.buildPath(["collect", "different"])
        os.mkdir(collectDir)
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator(collectIndicator="different")
        self.assertEqual(True, result)

    def testCheckCollectIndicator_007(self):
        """
        Attempt to check collect indicator collect indicator file that does exist,
        with spaces in the collect directory path.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect directory here"])
        collectIndicator = self.buildPath(["collect directory here", DEF_COLLECT_INDICATOR])
        os.mkdir(collectDir)
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator()
        self.assertEqual(True, result)

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testCheckCollectIndicator_008(self):
        """
        Attempt to check collect indicator collect indicator file that does exist, custom name,
        with spaces in the collect directory path and collect indicator file name.
        """
        name = "peer1"
        collectDir = self.buildPath([" collect dir "])
        collectIndicator = self.buildPath([" collect dir ", "different, file"])
        os.mkdir(collectDir)
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(collectIndicator))
        peer = LocalPeer(name, collectDir)
        result = peer.checkCollectIndicator(collectIndicator="different, file")
        self.assertEqual(True, result)

    #############################
    # Test writeStageIndicator()
    #############################

    def testWriteStageIndicator_001(self):
        """
        Attempt to write stage indicator with non-existent collect directory.
        """
        name = "peer1"
        collectDir = self.buildPath([NONEXISTENT_FILE])
        self.assertTrue(not os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(ValueError, peer.writeStageIndicator)

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testWriteStageIndicator_002(self):
        """
        Attempt to write stage indicator with non-writable collect directory.
        """
        if not isRunningAsRoot():  # root doesn't get this error
            name = "peer1"
            collectDir = self.buildPath(["collect"])
            os.mkdir(collectDir)
            self.assertTrue(os.path.exists(collectDir))
            os.chmod(collectDir, 0o500)  # read-only for user
            peer = LocalPeer(name, collectDir)
            self.assertRaises((IOError, OSError), peer.writeStageIndicator)
            os.chmod(collectDir, 0o777)  # so we can remove it safely

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testWriteStageIndicator_003(self):
        """
        Attempt to write stage indicator with non-writable collect directory, custom name.
        """
        if not isRunningAsRoot():  # root doesn't get this error
            name = "peer1"
            collectDir = self.buildPath(["collect"])
            os.mkdir(collectDir)
            self.assertTrue(os.path.exists(collectDir))
            os.chmod(collectDir, 0o500)  # read-only for user
            peer = LocalPeer(name, collectDir)
            self.assertRaises((IOError, OSError), peer.writeStageIndicator, stageIndicator="something")
            os.chmod(collectDir, 0o777)  # so we can remove it safely

    def testWriteStageIndicator_004(self):
        """
        Attempt to write stage indicator in a valid directory.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        stageIndicator = self.buildPath(["collect", DEF_STAGE_INDICATOR])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        peer.writeStageIndicator()
        self.assertTrue(os.path.exists(stageIndicator))

    def testWriteStageIndicator_005(self):
        """
        Attempt to write stage indicator in a valid directory, custom name.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        stageIndicator = self.buildPath(["collect", "whatever"])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        peer.writeStageIndicator(stageIndicator="whatever")
        self.assertTrue(os.path.exists(stageIndicator))

    def testWriteStageIndicator_006(self):
        """
        Attempt to write stage indicator in a valid directory, with spaces
        in the directory name.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect from this directory"])
        stageIndicator = self.buildPath(["collect from this directory", DEF_STAGE_INDICATOR])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        peer.writeStageIndicator()
        self.assertTrue(os.path.exists(stageIndicator))

    def testWriteStageIndicator_007(self):
        """
        Attempt to write stage indicator in a valid directory, custom name,
        with spaces in the directory name and the file name.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect ME"])
        stageIndicator = self.buildPath(["collect ME", "   whatever-it-takes you"])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        peer.writeStageIndicator(stageIndicator="   whatever-it-takes you")
        self.assertTrue(os.path.exists(stageIndicator))

    ###################
    # Test stagePeer()
    ###################

    def testStagePeer_001(self):
        """
        Attempt to stage files with non-existent collect directory.
        """
        name = "peer1"
        collectDir = self.buildPath([NONEXISTENT_FILE])
        targetDir = self.buildPath(["target"])
        os.mkdir(targetDir)
        self.assertTrue(not os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    def testStagePeer_002(self):
        """
        Attempt to stage files with non-readable collect directory.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        targetDir = self.buildPath(["target"])
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        os.chmod(collectDir, 0o200)  # user can't read his own directory
        peer = LocalPeer(name, collectDir)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        os.chmod(collectDir, 0o777)  # so we can remove it safely

    def testStagePeer_003(self):
        """
        Attempt to stage files with non-absolute target directory.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        targetDir = "this/is/not/absolute"
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    def testStagePeer_004(self):
        """
        Attempt to stage files with non-existent target directory.
        """
        name = "peer1"
        collectDir = self.buildPath(["collect"])
        targetDir = self.buildPath(["target"])
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(targetDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testStagePeer_005(self):
        """
        Attempt to stage files with non-writable target directory.
        """
        if not isRunningAsRoot():  # root doesn't get this error
            self.extractTar("tree1")
            name = "peer1"
            collectDir = self.buildPath(["tree1"])
            targetDir = self.buildPath(["target"])
            os.mkdir(targetDir)
            self.assertTrue(os.path.exists(collectDir))
            self.assertTrue(os.path.exists(targetDir))
            os.chmod(targetDir, 0o500)  # read-only for user
            peer = LocalPeer(name, collectDir)
            self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
            os.chmod(targetDir, 0o777)  # so we can remove it safely
            self.assertEqual(0, len(os.listdir(targetDir)))

    def testStagePeer_006(self):
        """
        Attempt to stage files with empty collect directory.
        *Note:* This test assumes that scp returns an error if the directory is empty.
        """
        self.extractTar("tree2")
        name = "peer1"
        collectDir = self.buildPath(["tree2", "dir001"])
        targetDir = self.buildPath(["target"])
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(IOError, peer.stagePeer, targetDir=targetDir)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual([], stagedFiles)

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testStagePeer_007(self):
        """
        Attempt to stage files with empty collect directory, where the target
        directory name contains spaces.
        """
        self.extractTar("tree2")
        name = "peer1"
        collectDir = self.buildPath(["tree2", "dir001"])
        targetDir = self.buildPath([" target directory "])  # windows doesn't like paths that start or end with a space
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(IOError, peer.stagePeer, targetDir=targetDir)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual([], stagedFiles)

    def testStagePeer_008(self):
        """
        Attempt to stage files with non-empty collect directory.
        """
        self.extractTar("tree1")
        name = "peer1"
        collectDir = self.buildPath(["tree1"])
        targetDir = self.buildPath(["target"])
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = LocalPeer(name, collectDir)
        count = peer.stagePeer(targetDir=targetDir)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)

    def testStagePeer_009(self):
        """
        Attempt to stage files with non-empty collect directory, where the
        target directory name contains spaces.
        """
        self.extractTar("tree1")
        name = "peer1"
        collectDir = self.buildPath(["tree1"])
        targetDir = self.buildPath(["target directory place"])
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = LocalPeer(name, collectDir)
        count = peer.stagePeer(targetDir=targetDir)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)

    def testStagePeer_010(self):
        """
        Attempt to stage files with non-empty collect directory containing links and directories.
        """
        self.extractTar("tree9")
        name = "peer1"
        collectDir = self.buildPath(["tree9"])
        targetDir = self.buildPath(["target"])
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = LocalPeer(name, collectDir)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    @unittest.skipIf(platformWindows(), "Behavior differs on Windows")
    def testStagePeer_011(self):
        """
        Attempt to stage files with non-empty collect directory and attempt to set valid permissions.
        """
        self.extractTar("tree1")
        name = "peer1"
        collectDir = self.buildPath(["tree1"])
        targetDir = self.buildPath(["target"])
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = LocalPeer(name, collectDir)
        if getMaskAsMode() == 0o400:
            permissions = 0o642  # arbitrary, but different than umask would give
        else:
            permissions = 0o400  # arbitrary
        count = peer.stagePeer(targetDir=targetDir, permissions=permissions)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)
        self.assertEqual(permissions, self.getFileMode(["target", "file001"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file002"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file003"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file004"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file005"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file006"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file007"]))


######################
# TestRemotePeer class
######################


class TestRemotePeer(unittest.TestCase):

    """Tests for the RemotePeer class."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

        # Full tests require configured SSH connectivity, so I want to use my own
        # scp/ssh scripts that are set up to use an SSH agent.  This means other
        # people won't be able to run the full tests... but that's always been
        # true, since I don't document the system setup needed to make them work.
        if runAllTests():
            from CedarBackup3.util import PathResolverSingleton

            mapping = {}
            mapping["/usr/bin/ssh"] = pathJoin(os.environ["HOME"], "util", "ssh")
            mapping["/usr/bin/scp"] = pathJoin(os.environ["HOME"], "util", "scp")
            singleton = PathResolverSingleton.getInstance()
            singleton.fill(mapping)

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

    def getFileMode(self, components):
        """Calls buildPath on components and then returns file mode for the file."""
        return stat.S_IMODE(os.stat(self.buildPath(components)).st_mode)

    def failUnlessAssignRaises(self, exception, obj, prop, value):
        """Equivalent of :any:`failUnlessRaises`, but used for property assignments instead."""
        failUnlessAssignRaises(self, exception, obj, prop, value)

    ############################
    # Tests basic functionality
    ############################

    def testBasic_001(self):
        """
        Make sure exception is thrown for non-absolute collect or working directory.
        """
        name = REMOTE_HOST
        collectDir = "whatever/something/else/not/absolute"
        workingDir = "/tmp"
        remoteUser = getLogin()
        self.assertRaises(ValueError, RemotePeer, name, collectDir, workingDir, remoteUser)

        name = REMOTE_HOST
        collectDir = "/whatever/something/else/not/absolute"
        workingDir = "tmp"
        remoteUser = getLogin()
        self.assertRaises(ValueError, RemotePeer, name, collectDir, workingDir, remoteUser)

    def testBasic_002(self):
        """
        Make sure attributes are set properly for valid constructor input.
        """
        name = REMOTE_HOST
        collectDir = "/absolute/path/name"
        workingDir = "/tmp"
        remoteUser = getLogin()
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)
        self.assertEqual(workingDir, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(None, peer.localUser)
        self.assertEqual(None, peer.rcpCommand)
        self.assertEqual(None, peer.rshCommand)
        self.assertEqual(None, peer.cbackCommand)
        self.assertEqual(DEF_RCP_COMMAND, peer._rcpCommandList)
        self.assertEqual(DEF_RSH_COMMAND, peer._rshCommandList)
        self.assertEqual(None, peer.ignoreFailureMode)

    def testBasic_003(self):
        """
        Make sure attributes are set properly for valid constructor input, where
        the collect directory contains spaces.
        """
        name = REMOTE_HOST
        collectDir = "/absolute/path/to/ a large directory"
        workingDir = "/tmp"
        remoteUser = getLogin()
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)
        self.assertEqual(workingDir, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(None, peer.localUser)
        self.assertEqual(None, peer.rcpCommand)
        self.assertEqual(None, peer.rshCommand)
        self.assertEqual(None, peer.cbackCommand)
        self.assertEqual(DEF_RCP_COMMAND, peer._rcpCommandList)
        self.assertEqual(DEF_RSH_COMMAND, peer._rshCommandList)

    def testBasic_004(self):
        """
        Make sure attributes are set properly for valid constructor input, custom rcp command.
        """
        name = REMOTE_HOST
        collectDir = "/absolute/path/name"
        workingDir = "/tmp"
        remoteUser = getLogin()
        rcpCommand = "rcp -one --two three \"four five\" 'six seven' eight"
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)
        self.assertEqual(workingDir, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(None, peer.localUser)
        self.assertEqual(rcpCommand, peer.rcpCommand)
        self.assertEqual(None, peer.rshCommand)
        self.assertEqual(None, peer.cbackCommand)
        self.assertEqual(["rcp", "-one", "--two", "three", "four five", "'six", "seven'", "eight"], peer._rcpCommandList)
        self.assertEqual(DEF_RSH_COMMAND, peer._rshCommandList)

    def testBasic_005(self):
        """
        Make sure attributes are set properly for valid constructor input, custom local user command.
        """
        name = REMOTE_HOST
        collectDir = "/absolute/path/to/ a large directory"
        workingDir = "/tmp"
        remoteUser = getLogin()
        localUser = "pronovic"
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, localUser=localUser)
        self.assertEqual(name, peer.name)
        self.assertEqual(collectDir, peer.collectDir)
        self.assertEqual(workingDir, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(localUser, peer.localUser)
        self.assertEqual(None, peer.rcpCommand)
        self.assertEqual(DEF_RCP_COMMAND, peer._rcpCommandList)
        self.assertEqual(DEF_RSH_COMMAND, peer._rshCommandList)

    def testBasic_006(self):
        """
        Make sure attributes are set properly for valid constructor input, custom rsh command.
        """
        name = REMOTE_HOST
        remoteUser = getLogin()
        rshCommand = 'rsh --whatever -something "a b" else'
        peer = RemotePeer(name, remoteUser=remoteUser, rshCommand=rshCommand)
        self.assertEqual(name, peer.name)
        self.assertEqual(None, peer.collectDir)
        self.assertEqual(None, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(None, peer.localUser)
        self.assertEqual(None, peer.rcpCommand)
        self.assertEqual(rshCommand, peer.rshCommand)
        self.assertEqual(None, peer.cbackCommand)
        self.assertEqual(DEF_RCP_COMMAND, peer._rcpCommandList)
        self.assertEqual(DEF_RCP_COMMAND, peer._rcpCommandList)
        self.assertEqual(["rsh", "--whatever", "-something", "a b", "else"], peer._rshCommandList)

    def testBasic_007(self):
        """
        Make sure attributes are set properly for valid constructor input, custom cback command.
        """
        name = REMOTE_HOST
        remoteUser = getLogin()
        cbackCommand = "cback --config=whatever --logfile=whatever --mode=064"
        peer = RemotePeer(name, remoteUser=remoteUser, cbackCommand=cbackCommand)
        self.assertEqual(name, peer.name)
        self.assertEqual(None, peer.collectDir)
        self.assertEqual(None, peer.workingDir)
        self.assertEqual(remoteUser, peer.remoteUser)
        self.assertEqual(None, peer.localUser)
        self.assertEqual(None, peer.rcpCommand)
        self.assertEqual(None, peer.rshCommand)
        self.assertEqual(cbackCommand, peer.cbackCommand)

    def testBasic_008(self):
        """
        Make sure assignment works for all valid failure modes.
        """
        peer = RemotePeer(name="name", remoteUser="user", ignoreFailureMode="all")
        self.assertEqual("all", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "none"
        self.assertEqual("none", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "daily"
        self.assertEqual("daily", peer.ignoreFailureMode)
        peer.ignoreFailureMode = "weekly"
        self.assertEqual("weekly", peer.ignoreFailureMode)
        self.failUnlessAssignRaises(ValueError, peer, "ignoreFailureMode", "bogus")

    ###############################
    # Test checkCollectIndicator()
    ###############################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_001(self):
        """
        Attempt to check collect indicator with invalid hostname.
        """
        name = NONEXISTENT_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        remoteUser = getLogin()
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_002(self):
        """
        Attempt to check collect indicator with invalid remote user.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = NONEXISTENT_USER
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_003(self):
        """
        Attempt to check collect indicator with invalid rcp command.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = getLogin()
        rcpCommand = NONEXISTENT_CMD
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_004(self):
        """
        Attempt to check collect indicator with non-existent collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = getLogin()
        self.assertTrue(not os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_005(self):
        """
        Attempt to check collect indicator with non-readable collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        os.chmod(collectDir, 0o200)  # user can't read his own directory
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)
        os.chmod(collectDir, 0o777)  # so we can remove it safely

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_006(self):
        """
        Attempt to check collect indicator collect indicator file that does not exist.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect", DEF_COLLECT_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_007(self):
        """
        Attempt to check collect indicator collect indicator file that does not exist, custom name.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect", NONEXISTENT_FILE])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_008(self):
        """
        Attempt to check collect indicator collect indicator file that does not
        exist, where the collect directory contains spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect directory path"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect directory path", DEF_COLLECT_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_009(self):
        """
        Attempt to check collect indicator collect indicator file that does not
        exist, custom name, where the collect directory contains spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["  you collect here   "])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["  you collect here   ", NONEXISTENT_FILE])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(False, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_010(self):
        """
        Attempt to check collect indicator collect indicator file that does exist.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect", DEF_COLLECT_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(True, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_011(self):
        """
        Attempt to check collect indicator collect indicator file that does exist, custom name.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect", "whatever"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator(collectIndicator="whatever")
        self.assertEqual(True, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_012(self):
        """
        Attempt to check collect indicator collect indicator file that does exist,
        where the collect directory contains spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect NOT"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath(["collect NOT", DEF_COLLECT_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator()
        self.assertEqual(True, result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testCheckCollectIndicator_013(self):
        """
        Attempt to check collect indicator collect indicator file that does
        exist, custom name, where the collect directory and indicator file
        contain spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath([" from here collect!"])
        workingDir = "/tmp"
        collectIndicator = self.buildPath([" from here collect!", "whatever, dude"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        with open(collectIndicator, "w") as f:
            f.write("")  # touch the file
        self.assertTrue(os.path.exists(collectIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        result = peer.checkCollectIndicator(collectIndicator="whatever, dude")
        self.assertEqual(True, result)

    #############################
    # Test writeStageIndicator()
    #############################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_001(self):
        """
        Attempt to write stage indicator with invalid hostname.
        """
        name = NONEXISTENT_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        remoteUser = getLogin()
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        self.assertRaises((IOError, OSError), peer.writeStageIndicator)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_002(self):
        """
        Attempt to write stage indicator with invalid remote user.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = NONEXISTENT_USER
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        self.assertRaises((IOError, OSError), peer.writeStageIndicator)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_003(self):
        """
        Attempt to write stage indicator with invalid rcp command.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = getLogin()
        rcpCommand = NONEXISTENT_CMD
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand)
        self.assertRaises((IOError, OSError), peer.writeStageIndicator)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_004(self):
        """
        Attempt to write stage indicator with non-existent collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        remoteUser = getLogin()
        self.assertTrue(not os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises(IOError, peer.writeStageIndicator)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_005(self):
        """
        Attempt to write stage indicator with non-writable collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        stageIndicator = self.buildPath(["collect", DEF_STAGE_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(stageIndicator))
        os.chmod(collectDir, 0o400)  # read-only for user
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.writeStageIndicator)
        self.assertTrue(not os.path.exists(stageIndicator))
        os.chmod(collectDir, 0o777)  # so we can remove it safely

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_006(self):
        """
        Attempt to write stage indicator in a valid directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        stageIndicator = self.buildPath(["collect", DEF_STAGE_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(stageIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        peer.writeStageIndicator()
        self.assertTrue(os.path.exists(stageIndicator))

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_007(self):
        """
        Attempt to write stage indicator in a valid directory, custom name.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        stageIndicator = self.buildPath(["collect", "newname"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(stageIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        peer.writeStageIndicator(stageIndicator="newname")
        self.assertTrue(os.path.exists(stageIndicator))

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_008(self):
        """
        Attempt to write stage indicator in a valid directory that contains
        spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["with spaces collect"])
        workingDir = "/tmp"
        stageIndicator = self.buildPath(["with spaces collect", DEF_STAGE_INDICATOR])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(stageIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        peer.writeStageIndicator()
        self.assertTrue(os.path.exists(stageIndicator))

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteStageIndicator_009(self):
        """
        Attempt to write stage indicator in a valid directory, custom name, where
        the collect directory and the custom name contain spaces.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect, soon"])
        workingDir = "/tmp"
        stageIndicator = self.buildPath(["collect, soon", "new name with spaces"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(stageIndicator))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        peer.writeStageIndicator(stageIndicator="new name with spaces")
        self.assertTrue(os.path.exists(stageIndicator))

    ###################
    # Test stagePeer()
    ###################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_001(self):
        """
        Attempt to stage files with invalid hostname.
        """
        name = NONEXISTENT_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_002(self):
        """
        Attempt to stage files with invalid remote user.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = NONEXISTENT_USER
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand=SAFE_RCP_COMMAND, rshCommand=SAFE_RSH_COMMAND)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_003(self):
        """
        Attempt to stage files with invalid rcp command.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        rcpCommand = NONEXISTENT_CMD
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser, rcpCommand)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_004(self):
        """
        Attempt to stage files with non-existent collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(targetDir)
        self.assertTrue(not os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_005(self):
        """
        Attempt to stage files with non-readable collect directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        os.chmod(collectDir, 0o200)  # user can't read his own directory
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        os.chmod(collectDir, 0o777)  # so we can remove it safely

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_006(self):
        """
        Attempt to stage files with non-absolute target directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = "non/absolute/target"
        remoteUser = getLogin()
        self.assertTrue(not os.path.exists(collectDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_007(self):
        """
        Attempt to stage files with non-existent target directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(not os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises(ValueError, peer.stagePeer, targetDir=targetDir)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_008(self):
        """
        Attempt to stage files with non-writable target directory.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        os.chmod(targetDir, 0o400)  # read-only for user
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        os.chmod(collectDir, 0o777)  # so we can remove it safely
        self.assertEqual(0, len(os.listdir(targetDir)))

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_009(self):
        """
        Attempt to stage files with empty collect directory.
        *Note:* This test assumes that scp returns an error if the directory is empty.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual([], stagedFiles)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_010(self):
        """
        Attempt to stage files with empty collect directory, with a target
        directory that contains spaces.
        *Note:* This test assumes that scp returns an error if the directory is empty.
        """
        name = REMOTE_HOST
        collectDir = self.buildPath(["collect"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target DIR"])
        remoteUser = getLogin()
        os.mkdir(collectDir)
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual([], stagedFiles)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_011(self):
        """
        Attempt to stage files with non-empty collect directory.
        """
        self.extractTar("tree1")
        name = REMOTE_HOST
        collectDir = self.buildPath(["tree1"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        count = peer.stagePeer(targetDir=targetDir)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_012(self):
        """
        Attempt to stage files with non-empty collect directory, with a target
        directory that contains spaces.
        """
        self.extractTar("tree1")
        name = REMOTE_HOST
        collectDir = self.buildPath(["tree1"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["write the target here, now!"])
        remoteUser = getLogin()
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        count = peer.stagePeer(targetDir=targetDir)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_013(self):
        """
        Attempt to stage files with non-empty collect directory containing links and directories.
        *Note:* We assume that scp copies the files even though it returns an error due to directories.
        """
        self.extractTar("tree9")
        name = REMOTE_HOST
        collectDir = self.buildPath(["tree9"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        self.assertRaises((IOError, OSError), peer.stagePeer, targetDir=targetDir)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(2, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testStagePeer_014(self):
        """
        Attempt to stage files with non-empty collect directory and attempt to set valid permissions.
        """
        self.extractTar("tree1")
        name = REMOTE_HOST
        collectDir = self.buildPath(["tree1"])
        workingDir = "/tmp"
        targetDir = self.buildPath(["target"])
        remoteUser = getLogin()
        os.mkdir(targetDir)
        self.assertTrue(os.path.exists(collectDir))
        self.assertTrue(os.path.exists(targetDir))
        self.assertEqual(0, len(os.listdir(targetDir)))
        peer = RemotePeer(name, collectDir, workingDir, remoteUser)
        if getMaskAsMode() == 0o400:
            permissions = 0o642  # arbitrary, but different than umask would give
        else:
            permissions = 0o400  # arbitrary
        count = peer.stagePeer(targetDir=targetDir, permissions=permissions)
        self.assertEqual(7, count)
        stagedFiles = os.listdir(targetDir)
        self.assertEqual(7, len(stagedFiles))
        self.assertTrue("file001" in stagedFiles)
        self.assertTrue("file002" in stagedFiles)
        self.assertTrue("file003" in stagedFiles)
        self.assertTrue("file004" in stagedFiles)
        self.assertTrue("file005" in stagedFiles)
        self.assertTrue("file006" in stagedFiles)
        self.assertTrue("file007" in stagedFiles)
        self.assertEqual(permissions, self.getFileMode(["target", "file001"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file002"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file003"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file004"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file005"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file006"]))
        self.assertEqual(permissions, self.getFileMode(["target", "file007"]))

    ##############################
    # Test executeRemoteCommand()
    ##############################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testExecuteRemoteCommand(self):
        """
        Test that a simple remote command succeeds.
        """
        target = self.buildPath(["test.txt"])
        name = REMOTE_HOST
        remoteUser = getLogin()
        command = "touch %s" % target
        self.assertFalse(os.path.exists(target))
        peer = RemotePeer(name=name, remoteUser=remoteUser)
        peer.executeRemoteCommand(command)
        self.assertTrue(os.path.exists(target))

    ############################
    # Test _buildCbackCommand()
    ############################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testBuildCbackCommand_001(self):
        """
        Test with None for cbackCommand and action, False for fullBackup.
        """
        self.assertRaises(ValueError, RemotePeer._buildCbackCommand, None, None, False)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testBuildCbackCommand_002(self):
        """
        Test with None for cbackCommand, "collect" for action, False for fullBackup.
        """
        result = RemotePeer._buildCbackCommand(None, "collect", False)
        self.assertEqual("/usr/bin/cback3 collect", result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testBuildCbackCommand_003(self):
        """
        Test with "cback" for cbackCommand, "collect" for action, False for fullBackup.
        """
        result = RemotePeer._buildCbackCommand("cback", "collect", False)
        self.assertEqual("cback collect", result)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testBuildCbackCommand_004(self):
        """
        Test with "cback" for cbackCommand, "collect" for action, True for fullBackup.
        """
        result = RemotePeer._buildCbackCommand("cback", "collect", True)
        self.assertEqual("cback --full collect", result)
