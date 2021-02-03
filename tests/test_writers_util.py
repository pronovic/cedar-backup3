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
# Copyright (c) 2004-2007,2010,2011,2015 Kenneth J. Pronovici.
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
# Purpose  : Tests writer utility functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/writers/util.py.

Code Coverage
=============

   This module contains individual tests for the public functions and classes
   implemented in writers/util.py.

   I usually prefer to test only the public interface to a class, because that
   way the regression tests don't depend on the internal implementation.  In
   this case, I've decided to test some of the private methods, because their
   "privateness" is more a matter of presenting a clean external interface than
   anything else (most of the private methods are static).  Being able to test
   these methods also makes it easier to gain some reasonable confidence in the
   code even if some tests are not run because WRITERSUTILTESTS_FULL is not set to
   "Y" in the environment (see below).

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
   want to run all of the tests, set WRITERSUTILTESTS_FULL to "Y" in the environment.

   In this module, there are three dependencies: the system must have
   ``mkisofs`` installed, the kernel must allow ISO images to be mounted
   in-place via a loopback mechanism, and the current user must be allowed (via
   ``sudo``) to mount and unmount such loopback filesystems.  See documentation
   by the :any:`TestIsoImage.mountImage` and :any:`TestIsoImage.unmountImage` methods
   for more information on what ``sudo`` access is required.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import os
import tempfile
import time
import unittest

from CedarBackup3.filesystem import FilesystemList
from CedarBackup3.testutil import (
    buildPath,
    configureLogging,
    extractTar,
    findResources,
    platformMacOsX,
    platformSupportsLinks,
    removedir,
    setupOverrides,
)
from CedarBackup3.util import executeCommand, pathJoin
from CedarBackup3.writers.util import IsoImage, validateDriveSpeed, validateScsiId

#######################################################################
# Module-wide configuration and constants
#######################################################################

DATA_DIRS = ["./data", "./tests/data"]
RESOURCES = ["tree9.tar.gz"]
SUDO_CMD = ["sudo"]
HDIUTIL_CMD = ["hdiutil"]
GCONF_CMD = ["gconftool-2"]

INVALID_FILE = "bogus"  # This file name should never exist


#######################################################################
# Utility functions
#######################################################################


def runAllTests():
    """Returns true/false depending on whether the full test suite should be run."""
    if "WRITERSUTILTESTS_FULL" in os.environ:
        return os.environ["WRITERSUTILTESTS_FULL"] == "Y"
    else:
        return False


#######################################################################
# Test Case Classes
#######################################################################

######################
# TestFunctions class
######################


class TestFunctions(unittest.TestCase):

    """Tests for the various public functions."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

        # We absolutely need the overrides set properly for this test, since it
        # runs programs.  Since other tests might mess with the overrides and/or
        # singletons, and we don't control the order of execution, we need to set
        # them up here.
        setupOverrides()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ########################
    # Test validateScsiId()
    ########################

    def testValidateScsiId_001(self):
        """
        Test with simple scsibus,target,lun address.
        """
        scsiId = "0,0,0"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_002(self):
        """
        Test with simple scsibus,target,lun address containing spaces.
        """
        scsiId = " 0,   0, 0 "
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_003(self):
        """
        Test with simple ATA address.
        """
        scsiId = "ATA:3,2,1"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_004(self):
        """
        Test with simple ATA address containing spaces.
        """
        scsiId = "ATA: 3, 2,1  "
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_005(self):
        """
        Test with simple ATAPI address.
        """
        scsiId = "ATAPI:1,2,3"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_006(self):
        """
        Test with simple ATAPI address containing spaces.
        """
        scsiId = "  ATAPI:1,   2, 3"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_007(self):
        """
        Test with default-device Mac address.
        """
        scsiId = "IOCompactDiscServices"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_008(self):
        """
        Test with an alternate-device Mac address.
        """
        scsiId = "IOCompactDiscServices/2"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_009(self):
        """
        Test with an alternate-device Mac address.
        """
        scsiId = "IOCompactDiscServices/12"
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    def testValidateScsiId_010(self):
        """
        Test with an invalid address with a missing field.
        """
        scsiId = "1,2"
        self.assertRaises(ValueError, validateScsiId, scsiId)

    def testValidateScsiId_011(self):
        """
        Test with an invalid Mac-style address with a backslash.
        """
        scsiId = "IOCompactDiscServices\\3"
        self.assertRaises(ValueError, validateScsiId, scsiId)

    def testValidateScsiId_012(self):
        """
        Test with an invalid address with an invalid prefix separator.
        """
        scsiId = "ATAPI;1,2,3"
        self.assertRaises(ValueError, validateScsiId, scsiId)

    def testValidateScsiId_013(self):
        """
        Test with an invalid address with an invalid prefix separator.
        """
        scsiId = "ATA-1,2,3"
        self.assertRaises(ValueError, validateScsiId, scsiId)

    def testValidateScsiId_014(self):
        """
        Test with a None SCSI id.
        """
        scsiId = None
        result = validateScsiId(scsiId)
        self.assertEqual(scsiId, result)

    ############################
    # Test validateDriveSpeed()
    ############################

    def testValidateDriveSpeed_001(self):
        """
        Test for a valid drive speed.
        """
        speed = 1
        result = validateDriveSpeed(speed)
        self.assertEqual(result, speed)
        speed = 2
        result = validateDriveSpeed(speed)
        self.assertEqual(result, speed)
        speed = 30
        result = validateDriveSpeed(speed)
        self.assertEqual(result, speed)
        speed = 2.0
        result = validateDriveSpeed(speed)
        self.assertEqual(result, speed)
        speed = 1.3
        result = validateDriveSpeed(speed)
        self.assertEqual(result, 1)  # truncated

    def testValidateDriveSpeed_002(self):
        """
        Test for a None drive speed (special case).
        """
        speed = None
        result = validateDriveSpeed(speed)
        self.assertEqual(result, speed)

    def testValidateDriveSpeed_003(self):
        """
        Test for an invalid drive speed (zero)
        """
        speed = 0
        self.assertRaises(ValueError, validateDriveSpeed, speed)

    def testValidateDriveSpeed_004(self):
        """
        Test for an invalid drive speed (negative)
        """
        speed = -1
        self.assertRaises(ValueError, validateDriveSpeed, speed)

    def testValidateDriveSpeed_005(self):
        """
        Test for an invalid drive speed (not integer)
        """
        speed = "ken"
        self.assertRaises(ValueError, validateDriveSpeed, speed)


#####################
# TestIsoImage class
#####################


class TestIsoImage(unittest.TestCase):

    """Tests for the IsoImage class."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    def setUp(self):
        try:
            self.disableGnomeAutomount()
            self.mounted = False
            self.tmpdir = tempfile.mkdtemp()
            self.resources = findResources(RESOURCES, DATA_DIRS)
        except Exception as e:
            self.fail(e)

    def tearDown(self):
        if self.mounted:
            self.unmountImage()
        removedir(self.tmpdir)
        self.enableGnomeAutomount()

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

    def mountImage(self, imagePath):
        """
        Mounts an ISO image at ``self.tmpdir/mnt`` using loopback.

        This function chooses the correct operating system-specific function and
        calls it.  If there is no operating-system-specific function, we fall
        back to the generic function, which uses 'sudo mount'.

        Returns:
            Path the image is mounted at
        Raises:
           IOError: If the command cannot be executed
        """
        if platformMacOsX():
            return self.mountImageDarwin(imagePath)
        else:
            return self.mountImageGeneric(imagePath)

    def mountImageDarwin(self, imagePath):
        """
        Mounts an ISO image at ``self.tmpdir/mnt`` using Darwin's ``hdiutil`` program.

        Darwin (Mac OS X) uses the ``hdiutil`` program to mount volumes.  The
        mount command doesn't really exist (or rather, doesn't know what to do
        with ISO 9660 volumes).

        *Note:* According to the manpage, the mountpoint path can't be any longer
        than MNAMELEN characters (currently 90?) so you might have problems with
        this depending on how your test environment is set up.

        Returns:
            Path the image is mounted at
        Raises:
           IOError: If the command cannot be executed
        """
        mountPath = self.buildPath(["mnt"])
        os.mkdir(mountPath)
        args = [
            "attach",
            "-mountpoint",
            mountPath,
            imagePath,
        ]
        (result, output) = executeCommand(HDIUTIL_CMD, args, returnOutput=True)
        if result != 0:
            raise IOError("Error (%d) executing command to mount image." % result)
        self.mounted = True
        return mountPath

    def mountImageGeneric(self, imagePath):
        """
        Mounts an ISO image at ``self.tmpdir/mnt`` using loopback.

        Note that this will fail unless the user has been granted permissions via
        sudo, using something like this:

           Cmnd_Alias LOOPMOUNT = /bin/mount -d -t iso9660 -o loop * *

        Keep in mind that this entry is a security hole, so you might not want to
        keep it in ``/etc/sudoers`` all of the time.

        Returns:
            Path the image is mounted at
        Raises:
           IOError: If the command cannot be executed
        """
        mountPath = self.buildPath(["mnt"])
        os.mkdir(mountPath)
        args = [
            "mount",
            "-t",
            "iso9660",
            "-o",
            "loop",
            imagePath,
            mountPath,
        ]
        (result, output) = executeCommand(SUDO_CMD, args, returnOutput=True)
        if result != 0:
            raise IOError("Error (%d) executing command to mount image." % result)
        self.mounted = True
        return mountPath

    def unmountImage(self):
        """
        Unmounts an ISO image from ``self.tmpdir/mnt``.

        This function chooses the correct operating system-specific function and
        calls it.  If there is no operating-system-specific function, we fall
        back to the generic function, which uses 'sudo unmount'.

        Raises:
           IOError: If the command cannot be executed
        """
        if platformMacOsX():
            self.unmountImageDarwin()
        else:
            self.unmountImageGeneric()

    def unmountImageDarwin(self):
        """
        Unmounts an ISO image from ``self.tmpdir/mnt`` using Darwin's ``hdiutil`` program.

        Darwin (Mac OS X) uses the ``hdiutil`` program to mount volumes.  The
        mount command doesn't really exist (or rather, doesn't know what to do
        with ISO 9660 volumes).

        *Note:* According to the manpage, the mountpoint path can't be any longer
        than MNAMELEN characters (currently 90?) so you might have problems with
        this depending on how your test environment is set up.

        Raises:
           IOError: If the command cannot be executed
        """
        mountPath = self.buildPath(["mnt"])
        args = [
            "detach",
            mountPath,
        ]
        (result, output) = executeCommand(HDIUTIL_CMD, args, returnOutput=True)
        if result != 0:
            raise IOError("Error (%d) executing command to unmount image." % result)
        self.mounted = False

    def unmountImageGeneric(self):
        """
        Unmounts an ISO image from ``self.tmpdir/mnt``.

        Sometimes, multiple tries are needed because the ISO filesystem is still
        in use.  We try twice with a 1-second pause between attempts.  If this
        isn't successful, you may run out of loopback devices.  Check for leftover
        mounts using 'losetup -a' as root.  You can remove a leftover mount using
        something like 'losetup -d /dev/loop0'.

        Note that this will fail unless the user has been granted permissions via
        sudo, using something like this:

           Cmnd_Alias LOOPUNMOUNT  = /bin/umount -d -t iso9660 *

        Keep in mind that this entry is a security hole, so you might not want to
        keep it in ``/etc/sudoers`` all of the time.

        Raises:
           IOError: If the command cannot be executed
        """
        mountPath = self.buildPath(["mnt"])
        args = [
            "umount",
            "-d",
            "-t",
            "iso9660",
            mountPath,
        ]
        (result, output) = executeCommand(SUDO_CMD, args, returnOutput=True)
        if result != 0:
            time.sleep(1)
            (result, output) = executeCommand(SUDO_CMD, args, returnOutput=True)
            if result != 0:
                raise IOError("Error (%d) executing command to unmount image." % result)
        self.mounted = False

    def disableGnomeAutomount(self):
        """
        Disables GNOME auto-mounting of ISO volumes when full tests are enabled.

        As of this writing (October 2011), recent versions of GNOME in Debian
        come pre-configured to auto-mount various kinds of media (like CDs and
        thumb drives).  Besides auto-mounting the media, GNOME also often opens
        up a Nautilus browser window to explore the newly-mounted media.

        This causes lots of problems for these unit tests, which assume that they
        have complete control over the mounting and unmounting process.  So, for
        these tests to work, we need to disable GNOME auto-mounting.
        """
        self.origMediaAutomount = None
        self.origMediaAutomountOpen = None
        if runAllTests():
            args = [
                "--get",
                "/apps/nautilus/preferences/media_automount",
            ]
            (result, output) = executeCommand(GCONF_CMD, args, returnOutput=True)
            if result == 0:
                self.origMediaAutomount = output[0][:-1]  # pylint: disable=W0201
                if self.origMediaAutomount == "true":
                    args = [
                        "--type",
                        "bool",
                        "--set",
                        "/apps/nautilus/preferences/media_automount",
                        "false",
                    ]
                    executeCommand(GCONF_CMD, args)
            args = [
                "--get",
                "/apps/nautilus/preferences/media_automount_open",
            ]
            (result, output) = executeCommand(GCONF_CMD, args, returnOutput=True)
            if result == 0:
                self.origMediaAutomountOpen = output[0][:-1]  # pylint: disable=W0201
                if self.origMediaAutomountOpen == "true":
                    args = [
                        "--type",
                        "bool",
                        "--set",
                        "/apps/nautilus/preferences/media_automount_open",
                        "false",
                    ]
                    executeCommand(GCONF_CMD, args)

    def enableGnomeAutomount(self):
        """
        Resets GNOME auto-mounting options back to their state prior to disableGnomeAutomount().
        """
        if self.origMediaAutomount == "true":
            args = [
                "--type",
                "bool",
                "--set",
                "/apps/nautilus/preferences/media_automount",
                "true",
            ]
            executeCommand(GCONF_CMD, args)
        if self.origMediaAutomountOpen == "true":
            args = [
                "--type",
                "bool",
                "--set",
                "/apps/nautilus/preferences/media_automount_open",
                "true",
            ]
            executeCommand(GCONF_CMD, args)

    ###################
    # Test constructor
    ###################

    def testConstructor_001(self):
        """
        Test the constructor using all default arguments.
        """
        isoImage = IsoImage()
        self.assertEqual(None, isoImage.device)
        self.assertEqual(None, isoImage.boundaries)
        self.assertEqual(None, isoImage.graftPoint)
        self.assertEqual(True, isoImage.useRockRidge)
        self.assertEqual(None, isoImage.applicationId)
        self.assertEqual(None, isoImage.biblioFile)
        self.assertEqual(None, isoImage.publisherId)
        self.assertEqual(None, isoImage.preparerId)
        self.assertEqual(None, isoImage.volumeId)

    def testConstructor_002(self):
        """
        Test the constructor using non-default arguments.
        """
        isoImage = IsoImage("/dev/cdrw", boundaries=(1, 2), graftPoint="/france")
        self.assertEqual("/dev/cdrw", isoImage.device)
        self.assertEqual((1, 2), isoImage.boundaries)
        self.assertEqual("/france", isoImage.graftPoint)
        self.assertEqual(True, isoImage.useRockRidge)
        self.assertEqual(None, isoImage.applicationId)
        self.assertEqual(None, isoImage.biblioFile)
        self.assertEqual(None, isoImage.publisherId)
        self.assertEqual(None, isoImage.preparerId)
        self.assertEqual(None, isoImage.volumeId)

    ################################
    # Test IsoImage utility methods
    ################################

    def testUtilityMethods_001(self):
        """
        Test _buildDirEntries() with an empty entries dictionary.
        """
        entries = {}
        result = IsoImage._buildDirEntries(entries)
        self.assertEqual(0, len(result))

    def testUtilityMethods_002(self):
        """
        Test _buildDirEntries() with an entries dictionary that has no graft points.
        """
        entries = {}
        entries["/one/two/three"] = None
        entries["/four/five/six"] = None
        entries["/seven/eight/nine"] = None
        result = IsoImage._buildDirEntries(entries)
        self.assertEqual(3, len(result))
        self.assertTrue("/one/two/three" in result)
        self.assertTrue("/four/five/six" in result)
        self.assertTrue("/seven/eight/nine" in result)

    def testUtilityMethods_003(self):
        """
        Test _buildDirEntries() with an entries dictionary that has all graft points.
        """
        entries = {}
        entries["/one/two/three"] = "/backup1"
        entries["/four/five/six"] = "backup2"
        entries["/seven/eight/nine"] = "backup3"
        result = IsoImage._buildDirEntries(entries)
        self.assertEqual(3, len(result))
        self.assertTrue("backup1/=/one/two/three" in result)
        self.assertTrue("backup2/=/four/five/six" in result)
        self.assertTrue("backup3/=/seven/eight/nine" in result)

    def testUtilityMethods_004(self):
        """
        Test _buildDirEntries() with an entries dictionary that has mixed graft points and not.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        entries["/four/five/six"] = None
        entries["/seven/eight/nine"] = "/backup3"
        result = IsoImage._buildDirEntries(entries)
        self.assertEqual(3, len(result))
        self.assertTrue("backup1/=/one/two/three" in result)
        self.assertTrue("/four/five/six" in result)
        self.assertTrue("backup3/=/seven/eight/nine" in result)

    def testUtilityMethods_005(self):
        """
        Test _buildGeneralArgs() with all optional values as None.
        """
        isoImage = IsoImage()
        result = isoImage._buildGeneralArgs()
        self.assertEqual(0, len(result))

    def testUtilityMethods_006(self):
        """
        Test _buildGeneralArgs() with applicationId set.
        """
        isoImage = IsoImage()
        isoImage.applicationId = "one"
        result = isoImage._buildGeneralArgs()
        self.assertEqual(["-A", "one"], result)

    def testUtilityMethods_007(self):
        """
        Test _buildGeneralArgs() with biblioFile set.
        """
        isoImage = IsoImage()
        isoImage.biblioFile = "two"
        result = isoImage._buildGeneralArgs()
        self.assertEqual(["-biblio", "two"], result)

    def testUtilityMethods_008(self):
        """
        Test _buildGeneralArgs() with publisherId set.
        """
        isoImage = IsoImage()
        isoImage.publisherId = "three"
        result = isoImage._buildGeneralArgs()
        self.assertEqual(["-publisher", "three"], result)

    def testUtilityMethods_009(self):
        """
        Test _buildGeneralArgs() with preparerId set.
        """
        isoImage = IsoImage()
        isoImage.preparerId = "four"
        result = isoImage._buildGeneralArgs()
        self.assertEqual(["-p", "four"], result)

    def testUtilityMethods_010(self):
        """
        Test _buildGeneralArgs() with volumeId set.
        """
        isoImage = IsoImage()
        isoImage.volumeId = "five"
        result = isoImage._buildGeneralArgs()
        self.assertEqual(["-V", "five"], result)

    def testUtilityMethods_011(self):
        """
        Test _buildSizeArgs() with device and boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "-r", "backup1/=/one/two/three"], result)

    def testUtilityMethods_012(self):
        """
        Test _buildSizeArgs() with useRockRidge set to True and device and
        boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        isoImage.useRockRidge = True
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "-r", "backup1/=/one/two/three"], result)

    def testUtilityMethods_013(self):
        """
        Test _buildSizeArgs() with useRockRidge set to False and device and
        boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        isoImage.useRockRidge = False
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "backup1/=/one/two/three"], result)

    def testUtilityMethods_014(self):
        """
        Test _buildSizeArgs() with device as None and boundaries as non-None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device=None, boundaries=(1, 2))
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "-r", "backup1/=/one/two/three"], result)

    def testUtilityMethods_015(self):
        """
        Test _buildSizeArgs() with device as non-None and boundaries as None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device="/dev/cdrw", boundaries=None)
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "-r", "backup1/=/one/two/three"], result)

    def testUtilityMethods_016(self):
        """
        Test _buildSizeArgs() with device and boundaries as non-None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device="/dev/cdrw", boundaries=(1, 2))
        result = isoImage._buildSizeArgs(entries)
        self.assertEqual(["-print-size", "-graft-points", "-r", "-C", "1,2", "-M", "/dev/cdrw", "backup1/=/one/two/three"], result)

    def testUtilityMethods_017(self):
        """
        Test _buildWriteArgs() with device and boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(["-graft-points", "-r", "-o", "/tmp/file.iso", "backup1/=/one/two/three"], result)

    def testUtilityMethods_018(self):
        """
        Test _buildWriteArgs() with useRockRidge set to True and device and
        boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        isoImage.useRockRidge = True
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(["-graft-points", "-r", "-o", "/tmp/file.iso", "backup1/=/one/two/three"], result)

    def testUtilityMethods_019(self):
        """
        Test _buildWriteArgs() with useRockRidge set to False and device and
        boundaries at defaults.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage()
        isoImage.useRockRidge = False
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(["-graft-points", "-o", "/tmp/file.iso", "backup1/=/one/two/three"], result)

    def testUtilityMethods_020(self):
        """
        Test _buildWriteArgs() with device as None and boundaries as non-None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device=None, boundaries=(3, 4))
        isoImage.useRockRidge = False
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(["-graft-points", "-o", "/tmp/file.iso", "backup1/=/one/two/three"], result)

    def testUtilityMethods_021(self):
        """
        Test _buildWriteArgs() with device as non-None and boundaries as None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device="/dev/cdrw", boundaries=None)
        isoImage.useRockRidge = False
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(["-graft-points", "-o", "/tmp/file.iso", "backup1/=/one/two/three"], result)

    def testUtilityMethods_022(self):
        """
        Test _buildWriteArgs() with device and boundaries as non-None.
        """
        entries = {}
        entries["/one/two/three"] = "backup1"
        isoImage = IsoImage(device="/dev/cdrw", boundaries=(3, 4))
        isoImage.useRockRidge = False
        result = isoImage._buildWriteArgs(entries, "/tmp/file.iso")
        self.assertEqual(
            ["-graft-points", "-o", "/tmp/file.iso", "-C", "3,4", "-M", "/dev/cdrw", "backup1/=/one/two/three"], result
        )

    ##################
    # Test addEntry()
    ##################

    def testAddEntry_001(self):
        """
        Attempt to add a non-existent entry.
        """
        file1 = self.buildPath([INVALID_FILE])
        isoImage = IsoImage()
        self.assertRaises(ValueError, isoImage.addEntry, file1)

    @unittest.skipUnless(platformSupportsLinks(), "Requires soft links")
    def testAddEntry_002(self):
        """
        Attempt to add a an entry that is a soft link to a file.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "dir002", "link003"])
        isoImage = IsoImage()
        self.assertRaises(ValueError, isoImage.addEntry, file1)

    @unittest.skipUnless(platformSupportsLinks(), "Requires soft links")
    def testAddEntry_003(self):
        """
        Attempt to add a an entry that is a soft link to a directory
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "link001"])
        isoImage = IsoImage()
        self.assertRaises(ValueError, isoImage.addEntry, file1)

    def testAddEntry_004(self):
        """
        Attempt to add a file, no graft point set.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1)
        self.assertEqual({file1: None}, isoImage.entries)

    def testAddEntry_005(self):
        """
        Attempt to add a file, graft point set on the object level.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1)
        self.assertEqual({file1: "whatever"}, isoImage.entries)

    def testAddEntry_006(self):
        """
        Attempt to add a file, graft point set on the method level.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="stuff")
        self.assertEqual({file1: "stuff"}, isoImage.entries)

    def testAddEntry_007(self):
        """
        Attempt to add a file, graft point set on the object and method levels.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="stuff")
        self.assertEqual({file1: "stuff"}, isoImage.entries)

    def testAddEntry_008(self):
        """
        Attempt to add a file, graft point set on the object and method levels,
        where method value is None (which can't be distinguished from the method
        value being unset).
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint=None)
        self.assertEqual({file1: "whatever"}, isoImage.entries)

    def testAddEntry_009(self):
        """
        Attempt to add a directory, no graft point set.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1)
        self.assertEqual({dir1: os.path.basename(dir1)}, isoImage.entries)

    def testAddEntry_010(self):
        """
        Attempt to add a directory, graft point set on the object level.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage(graftPoint="p")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1)
        self.assertEqual({dir1: pathJoin("p", "tree9")}, isoImage.entries)

    def testAddEntry_011(self):
        """
        Attempt to add a directory, graft point set on the method level.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, graftPoint="s")
        self.assertEqual({dir1: pathJoin("s", "tree9")}, isoImage.entries)

    def testAddEntry_012(self):
        """
        Attempt to add a file, no graft point set, contentsOnly=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, contentsOnly=True)
        self.assertEqual({file1: None}, isoImage.entries)

    def testAddEntry_013(self):
        """
        Attempt to add a file, graft point set on the object level,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, contentsOnly=True)
        self.assertEqual({file1: "whatever"}, isoImage.entries)

    def testAddEntry_014(self):
        """
        Attempt to add a file, graft point set on the method level,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="stuff", contentsOnly=True)
        self.assertEqual({file1: "stuff"}, isoImage.entries)

    def testAddEntry_015(self):
        """
        Attempt to add a file, graft point set on the object and method levels,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="stuff", contentsOnly=True)
        self.assertEqual({file1: "stuff"}, isoImage.entries)

    def testAddEntry_016(self):
        """
        Attempt to add a file, graft point set on the object and method levels,
        where method value is None (which can't be distinguished from the method
        value being unset), contentsOnly=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint=None, contentsOnly=True)
        self.assertEqual({file1: "whatever"}, isoImage.entries)

    def testAddEntry_017(self):
        """
        Attempt to add a directory, no graft point set, contentsOnly=True.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, contentsOnly=True)
        self.assertEqual({dir1: None}, isoImage.entries)

    def testAddEntry_018(self):
        """
        Attempt to add a directory, graft point set on the object level,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage(graftPoint="p")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, contentsOnly=True)
        self.assertEqual({dir1: "p"}, isoImage.entries)

    def testAddEntry_019(self):
        """
        Attempt to add a directory, graft point set on the method level,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, graftPoint="s", contentsOnly=True)
        self.assertEqual({dir1: "s"}, isoImage.entries)

    def testAddEntry_020(self):
        """
        Attempt to add a directory, graft point set on the object and methods
        levels, contentsOnly=True.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage(graftPoint="p")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, graftPoint="s", contentsOnly=True)
        self.assertEqual({dir1: "s"}, isoImage.entries)

    def testAddEntry_021(self):
        """
        Attempt to add a directory, graft point set on the object and methods
        levels, contentsOnly=True.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage(graftPoint="p")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(dir1, graftPoint="s", contentsOnly=True)
        self.assertEqual({dir1: "s"}, isoImage.entries)

    def testAddEntry_022(self):
        """
        Attempt to add a file that has already been added, override=False.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1)
        self.assertEqual({file1: None}, isoImage.entries)
        self.assertRaises(ValueError, isoImage.addEntry, file1, override=False)
        self.assertEqual({file1: None}, isoImage.entries)

    def testAddEntry_023(self):
        """
        Attempt to add a file that has already been added, override=True.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage()
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1)
        self.assertEqual({file1: None}, isoImage.entries)
        isoImage.addEntry(file1, override=True)
        self.assertEqual({file1: None}, isoImage.entries)

    def testAddEntry_024(self):
        """
        Attempt to add a directory that has already been added, override=False, changing the graft point.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="one")
        self.assertEqual({file1: "one"}, isoImage.entries)
        self.assertRaises(ValueError, isoImage.addEntry, file1, graftPoint="two", override=False)
        self.assertEqual({file1: "one"}, isoImage.entries)

    def testAddEntry_025(self):
        """
        Attempt to add a directory that has already been added, override=True, changing the graft point.
        """
        self.extractTar("tree9")
        file1 = self.buildPath(["tree9", "file001"])
        isoImage = IsoImage(graftPoint="whatever")
        self.assertEqual({}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="one")
        self.assertEqual({file1: "one"}, isoImage.entries)
        isoImage.addEntry(file1, graftPoint="two", override=True)
        self.assertEqual({file1: "two"}, isoImage.entries)

    ##########################
    # Test getEstimatedSize()
    ##########################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testGetEstimatedSize_001(self):
        """
        Test with an empty list.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        self.assertRaises(ValueError, isoImage.getEstimatedSize)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testGetEstimatedSize_002(self):
        """
        Test with non-empty empty list.
        """
        self.extractTar("tree9")
        dir1 = self.buildPath(["tree9"])
        isoImage = IsoImage()
        isoImage.addEntry(dir1, graftPoint="base")
        result = isoImage.getEstimatedSize()
        self.assertTrue(result > 0)

    ####################
    # Test writeImage()
    ####################

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_001(self):
        """
        Attempt to write an image containing no entries.
        """
        isoImage = IsoImage()
        imagePath = self.buildPath(["image.iso"])
        self.assertRaises(ValueError, isoImage.writeImage, imagePath)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_002(self):
        """
        Attempt to write an image containing only an empty directory, no graft point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(2, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_003(self):
        """
        Attempt to write an image containing only an empty directory, with a graft point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint="base")
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(3, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_004(self):
        """
        Attempt to write an image containing only a non-empty directory, no graft
        point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(10, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_005(self):
        """
        Attempt to write an image containing only a non-empty directory, with a
        graft point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint=pathJoin("something", "else"))
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(12, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "something") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_006(self):
        """
        Attempt to write an image containing only a file, no graft point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(2, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_007(self):
        """
        Attempt to write an image containing only a file, with a graft point.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint="point")
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(3, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "point") in fsList)
        self.assertTrue(pathJoin(mountPath, "point", "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_008(self):
        """
        Attempt to write an image containing a file and an empty directory, no
        graft points.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1)
        isoImage.addEntry(dir1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(3, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_009(self):
        """
        Attempt to write an image containing a file and an empty directory, with
        graft points.
        """
        self.extractTar("tree9")
        isoImage = IsoImage(graftPoint="base")
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint="other")
        isoImage.addEntry(dir1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(5, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "other") in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "other", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_010(self):
        """
        Attempt to write an image containing a file and a non-empty directory,
        mixed graft points.
        """
        self.extractTar("tree9")
        isoImage = IsoImage(graftPoint="base")
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint=None)
        isoImage.addEntry(dir1)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(11, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_011(self):
        """
        Attempt to write an image containing several files and a non-empty
        directory, mixed graft points.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        file2 = self.buildPath(["tree9", "file002"])
        dir1 = self.buildPath(["tree9", "dir001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1)
        isoImage.addEntry(file2, graftPoint="other")
        isoImage.addEntry(dir1, graftPoint="base")
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(13, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "other") in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "other", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_012(self):
        """
        Attempt to write an image containing a deeply-nested directory.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint="something")
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(24, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "something") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir001", "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "tree9", "dir002", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_013(self):
        """
        Attempt to write an image containing only an empty directory, no graft
        point, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(1, len(fsList))
        self.assertTrue(mountPath in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_014(self):
        """
        Attempt to write an image containing only an empty directory, with a
        graft point, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint="base", contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(2, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_015(self):
        """
        Attempt to write an image containing only a non-empty directory, no graft
        point, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(9, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_016(self):
        """
        Attempt to write an image containing only a non-empty directory, with a
        graft point, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint=pathJoin("something", "else"), contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(11, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "something") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "else", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_017(self):
        """
        Attempt to write an image containing only a file, no graft point,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(2, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_018(self):
        """
        Attempt to write an image containing only a file, with a graft point,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint="point", contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(3, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "point") in fsList)
        self.assertTrue(pathJoin(mountPath, "point", "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_019(self):
        """
        Attempt to write an image containing a file and an empty directory, no
        graft points, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, contentsOnly=True)
        isoImage.addEntry(dir1, contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(2, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_020(self):
        """
        Attempt to write an image containing a file and an empty directory, with
        graft points, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage(graftPoint="base")
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001", "dir002"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint="other", contentsOnly=True)
        isoImage.addEntry(dir1, contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(4, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "other") in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "other", "file001") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_021(self):
        """
        Attempt to write an image containing a file and a non-empty directory,
        mixed graft points, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage(graftPoint="base")
        file1 = self.buildPath(["tree9", "file001"])
        dir1 = self.buildPath(["tree9", "dir001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, graftPoint=None, contentsOnly=True)
        isoImage.addEntry(dir1, contentsOnly=True)
        self.assertRaises(IOError, isoImage.writeImage, imagePath)  # ends up with a duplicate name

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_022(self):
        """
        Attempt to write an image containing several files and a non-empty
        directory, mixed graft points, contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        file1 = self.buildPath(["tree9", "file001"])
        file2 = self.buildPath(["tree9", "file002"])
        dir1 = self.buildPath(["tree9", "dir001"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(file1, contentsOnly=True)
        isoImage.addEntry(file2, graftPoint="other", contentsOnly=True)
        isoImage.addEntry(dir1, graftPoint="base", contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(12, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "base") in fsList)
        self.assertTrue(pathJoin(mountPath, "other") in fsList)
        self.assertTrue(pathJoin(mountPath, "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "other", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "base", "dir002") in fsList)

    @unittest.skipUnless(runAllTests(), "Limited test suite")
    def testWriteImage_023(self):
        """
        Attempt to write an image containing a deeply-nested directory,
        contentsOnly=True.
        """
        self.extractTar("tree9")
        isoImage = IsoImage()
        dir1 = self.buildPath(["tree9"])
        imagePath = self.buildPath(["image.iso"])
        isoImage.addEntry(dir1, graftPoint="something", contentsOnly=True)
        isoImage.writeImage(imagePath)
        mountPath = self.mountImage(imagePath)
        fsList = FilesystemList()
        fsList.addDirContents(mountPath)
        self.assertEqual(23, len(fsList))
        self.assertTrue(mountPath in fsList)
        self.assertTrue(pathJoin(mountPath, "something") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir001", "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "file001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "file002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "link001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "link002") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "link003") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "link004") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "dir001") in fsList)
        self.assertTrue(pathJoin(mountPath, "something", "dir002", "dir002") in fsList)
